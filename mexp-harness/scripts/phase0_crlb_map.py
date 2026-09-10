"""
The CRLB map over the tissue dictionary (charter §10 item 6 of the harness status; §1.2 v0.14: "the CRLB map of §10
replaces the labels with the SNR and window at which each row crosses them").

For every T2-kernel entry of the dictionary (normal and pathology rows), the Rician CRLB (σ known) is evaluated on

    axis 1  first-echo SNR  {20 ... 3000} at the reference 32 × 10 ms train,
    axis 2  echo count      {8 ... 256} × 10 ms (window 80 ms – 2.56 s) at first-echo SNR 100,

and the three §1.2 labels are turned into the SNR and the window at which the row crosses them:

    'K'           every visible T2 under 25 % relative SD,
    'functional'  the clinical functional under 10 % relative SD (delta method),
    'clinical'    the functional's SD ≤ |Δ|/3, Δ the dictionary's recorded normal-to-disease change (schema 2.3).

Two further axes are reported at the reference train for the functional's SD: the data-representation arm
(phase-corrected real Gaussian vs Rician magnitude — for a real-valued kernel the complex arm's FIM equals the real
arm's, so the value of phase is zero by construction here and is a T2* question, charter §2.3) and the
noise-knowledge rung (σ known vs σ jointly estimated, Rician).  For rows with a > 1 s component the map is also given
with that component's T2 fixed (the 'constrained' parameterisation of results/threshold_tissues.md), because that is
what decides the myelin rows.

Crossings are found by log-log interpolation of SD against SNR (the CRLB is ∝ 1/SNR to within the Rician floor
correction on this grid) and by the first passing echo count on the window grid.  No noise realisation is drawn; no
estimator is used.  Outputs: results/crlb_map.md, results/crlb_map.csv.
"""
from __future__ import annotations

import csv
import pathlib

import numpy as np

from mexp import crlb as CR, tissues as TS
from mexp.design import uniform
from mexp.kernels import get
from mexp.params import Theta

OUT = pathlib.Path(__file__).resolve().parents[1] / "results"
OUT.mkdir(exist_ok=True)
k = get("t2_cpmg")

K_OK, F_OK = 0.25, 0.10
SNR_GRID = np.array([20, 30, 50, 70, 100, 150, 200, 300, 500, 700, 1000, 1500, 2000, 3000], dtype=float)
N_GRID = [8, 12, 16, 24, 32, 48, 64, 96, 128, 160, 192, 256]
DTE = 10.0
LONG_MS = 1000.0            # components above this are 'the long component' a constrained parameterisation fixes


def bounds(th: Theta, n: int, dte: float, snr: float, threshold, noise="rician", joint=False, fix_long=False):
    """(max relative SD over T2s, functional SD, functional value) at one design point."""
    d = uniform(n, dte)
    sigma = CR.sigma_from_first_echo_snr(k, th, d, snr)
    r = CR.crlb(k, th, d, sigma, noise, joint_sigma=joint)
    labels = r.labels                                   # 'a0', 'a1', ..., 'T20', 'T21', ... (0-based component index)
    t2_idx = [i for i, l in enumerate(labels) if l.startswith("T2")]
    long_idx = [i for i in t2_idx if th.nonlinear[int(labels[i][2:]), 0] > LONG_MS]
    if fix_long and long_idx:
        keep = [i for i in range(len(labels)) if i not in long_idx]
        cov = np.linalg.pinv(r.fim[np.ix_(keep, keep)])
        sd = np.sqrt(np.maximum(np.diag(cov), 0))
        flat = np.concatenate([r.theta_flat, [sigma]]) if joint else r.theta_flat
        rel = {labels[i]: sd[j] / abs(flat[i]) for j, i in enumerate(keep)}
        relT = max(v for l, v in rel.items() if l.startswith("T2"))
        if threshold is None or th.K < 2:
            return relT, None, None
        g = CR.mass_below_gradient(th, threshold, joint_sigma=joint)[keep]
        f_sd = float(np.sqrt(max(g @ cov @ g, 0.0)))
    else:
        relT = max(r.relative_sd_of("T2").values())
        if threshold is None or th.K < 2:
            return relT, None, None
        g = CR.mass_below_gradient(th, threshold, joint_sigma=joint)
        f_sd = CR.functional_sd(r, g)
    a = th.amplitudes
    f_true = float((a * (th.nonlinear[:, 0] < threshold)).sum() / a.sum())
    if f_true > 0.5:
        f_true = 1.0 - f_true
    if not np.isfinite(f_sd):                           # singular FIM (e.g. K = 3 on 8 echoes): no information, not zero variance
        f_sd = np.inf
    if not np.isfinite(relT):
        relT = np.inf
    return relT, f_sd, f_true


def crossing_snr(snrs, values, target):
    """Smallest SNR at which `values` (decreasing in SNR) falls below `target`, by log-log interpolation."""
    v = np.asarray(values, dtype=float)
    ok = np.isfinite(v) & (v > 0)
    if not ok.any():
        return np.inf
    s, v = np.log(snrs[ok]), np.log(v[ok])
    below = v <= np.log(target)
    if not below.any():
        return np.inf
    j = int(np.argmax(below))
    if j == 0:
        return float(np.exp(s[0]))                      # already passing at the smallest SNR of the grid
    # interpolate between grid points j-1 (above target) and j (below)
    t = (np.log(target) - v[j - 1]) / (v[j] - v[j - 1])
    return float(np.exp(s[j - 1] + t * (s[j] - s[j - 1])))


def fmt_snr(x):
    if not np.isfinite(x):
        return f"> {SNR_GRID[-1]:.0f}"
    if x <= SNR_GRID[0] + 1e-9:
        return f"≤ {SNR_GRID[0]:.0f}"
    return f"{x:.0f}"


rows = []          # csv
md = ["# CRLB map over the tissue dictionary", "",
      "Rician CRLB, σ known unless stated, first-echo SNR convention, components below the first echo dropped and fractions renormalised. "
      "For each row: the first-echo SNR at the reference 32 × 10 ms train at which the row crosses each of the three §1.2 labels "
      "(25 % on every visible T2; 10 % relative on the functional; SD ≤ |Δ|/3 with Δ the recorded clinical change), by log–log "
      "interpolation on the SNR grid 20–3000; and the echo count at 10 ms spacing (window = N × 10 ms) at SNR 100 at which it crosses "
      "them. '> 3000' means the label is not reached on the grid; '—' means the row has no functional or no recorded Δ. Rows with a > 1 s "
      "component are shown twice: free, and with that component's T2 fixed ('constrained'), because the unpinned long component is "
      "what decides the myelin rows (results/threshold_tissues.md). No noise realisation is drawn; no estimator is used.", ""]

# ---------------------------------------------------------------- axis 1: SNR crossings at the reference train
md += ["## 1. SNR at which each row crosses the labels (32 × 10 ms)", "",
       "| tissue | condition | K vis. | functional | value | Δ | SNR for K (25 %) | SNR for functional (10 %) | SNR for clinical (\\|Δ\\|/3) | SD at SNR 100 | SD at SNR 300 |",
       "|---|---|---|---|---|---|---|---|---|---|---|"]
for cs in TS.entries(kernel="t2_cpmg"):
    entry = TS.get(cs.tissue_key)
    delta = entry.delta()
    th = cs.theta(min_value=DTE)
    has_long = bool(np.any(th.nonlinear[:, 0] > LONG_MS)) and th.K > 1
    for fix in ([False, True] if has_long else [False]):
        relT, fsd, ftrue = [], [], None
        for snr in SNR_GRID:
            a, b, c = bounds(th, 32, DTE, snr, cs.functional_threshold, fix_long=fix)
            relT.append(a); fsd.append(b); ftrue = c
        s_k = crossing_snr(SNR_GRID, relT, K_OK)
        if ftrue is not None and ftrue > 0:
            s_f = crossing_snr(SNR_GRID, fsd, F_OK * ftrue)
            s_c = crossing_snr(SNR_GRID, fsd, abs(delta) / 3) if delta is not None else None
            sd100 = float(np.interp(np.log(100), np.log(SNR_GRID), np.log(fsd)))
            sd300 = float(np.interp(np.log(300), np.log(SNR_GRID), np.log(fsd)))
            sd100, sd300 = np.exp(sd100), np.exp(sd300)
        else:
            s_f = s_c = None; sd100 = sd300 = None
        name = cs.tissue + (" (constrained: long T2 fixed)" if fix else "")
        md.append(f"| {name} | {entry.condition['name']} | {th.K} | {cs.functional if ftrue is not None else '—'} | "
                  f"{'—' if ftrue is None else f'{ftrue:.3f}'} | {'—' if delta is None else f'{delta:+.3f}'} | {fmt_snr(s_k)} | "
                  f"{'—' if s_f is None else fmt_snr(s_f)} | {'—' if s_c is None else fmt_snr(s_c)} | "
                  f"{'—' if sd100 is None else f'{sd100:.3f}'} | {'—' if sd300 is None else f'{sd300:.3f}'} |")
        for snr, a, b in zip(SNR_GRID, relT, fsd):
            rows.append({"axis": "snr", "tissue_key": cs.tissue_key, "condition": entry.condition["name"], "constrained": int(fix),
                         "n_echoes": 32, "dTE_ms": DTE, "snr": snr, "noise": "rician", "sigma_joint": 0,
                         "max_relSD_T2": a, "functional": cs.functional, "functional_value": ftrue, "functional_SD": b, "delta": delta})
md.append("")

# ---------------------------------------------------------------- axis 2: window crossings at SNR 100
md += ["## 2. Echo count (window) at which each row crosses the labels (ΔTE 10 ms, first-echo SNR 100)", "",
       "| tissue | condition | K vis. | N for K (25 %) | N for functional (10 %) | N for clinical (\\|Δ\\|/3) | functional SD at N = 8 / 32 / 128 / 256 |",
       "|---|---|---|---|---|---|---|"]
for cs in TS.entries(kernel="t2_cpmg"):
    entry = TS.get(cs.tissue_key)
    delta = entry.delta()
    th = cs.theta(min_value=DTE)
    has_long = bool(np.any(th.nonlinear[:, 0] > LONG_MS)) and th.K > 1
    for fix in ([False, True] if has_long else [False]):
        relT, fsd, ftrue = [], [], None
        for n in N_GRID:
            a, b, c = bounds(th, n, DTE, 100.0, cs.functional_threshold, fix_long=fix)
            relT.append(a); fsd.append(b); ftrue = c
        def first_n(vals, target):
            for n, v in zip(N_GRID, vals):
                if v is not None and np.isfinite(v) and v <= target:
                    return str(n)
            return f"> {N_GRID[-1]}"
        n_k = first_n(relT, K_OK)
        n_f = first_n(fsd, F_OK * ftrue) if ftrue else "—"
        n_c = first_n(fsd, abs(delta) / 3) if (ftrue and delta is not None) else "—"
        sds = "—" if ftrue is None else " / ".join(("∞" if not np.isfinite(fsd[N_GRID.index(n)]) else f"{fsd[N_GRID.index(n)]:.3f}") for n in (8, 32, 128, 256))
        name = cs.tissue + (" (constrained: long T2 fixed)" if fix else "")
        md.append(f"| {name} | {entry.condition['name']} | {th.K} | {n_k} | {n_f} | {n_c} | {sds} |")
        for n, a, b in zip(N_GRID, relT, fsd):
            rows.append({"axis": "window", "tissue_key": cs.tissue_key, "condition": entry.condition["name"], "constrained": int(fix),
                         "n_echoes": n, "dTE_ms": DTE, "snr": 100.0, "noise": "rician", "sigma_joint": 0,
                         "max_relSD_T2": a, "functional": cs.functional, "functional_value": ftrue, "functional_SD": b, "delta": delta})
md.append("")

# ---------------------------------------------------------------- axes 3-4: representation arm and noise knowledge
md += ["## 3. Data-representation arm and noise-knowledge rung (32 × 10 ms, SNR 100): functional SD", "",
       "| tissue | condition | Gaussian real (phase-corrected), σ known | Rician, σ known | Rician, σ joint | Rician joint / known | Rician / Gaussian |",
       "|---|---|---|---|---|---|---|"]
for cs in TS.entries(kernel="t2_cpmg"):
    entry = TS.get(cs.tissue_key)
    th = cs.theta(min_value=DTE)
    if cs.functional_threshold is None or th.K < 2:
        continue
    _, g_sd, _ = bounds(th, 32, DTE, 100.0, cs.functional_threshold, noise="gaussian_real")
    _, r_sd, _ = bounds(th, 32, DTE, 100.0, cs.functional_threshold, noise="rician")
    _, j_sd, _ = bounds(th, 32, DTE, 100.0, cs.functional_threshold, noise="rician", joint=True)
    md.append(f"| {cs.tissue} | {entry.condition['name']} | {g_sd:.4f} | {r_sd:.4f} | {j_sd:.4f} | {j_sd / r_sd:.3f} | {r_sd / g_sd:.3f} |")
    for noise, joint, v in (("gaussian_real", 0, g_sd), ("rician", 0, r_sd), ("rician", 1, j_sd)):
        rows.append({"axis": "arm", "tissue_key": cs.tissue_key, "condition": entry.condition["name"], "constrained": 0,
                     "n_echoes": 32, "dTE_ms": DTE, "snr": 100.0, "noise": noise, "sigma_joint": joint,
                     "max_relSD_T2": None, "functional": cs.functional, "functional_value": None, "functional_SD": v, "delta": entry.delta()})
md.append("")
md.append("The complex arm is not tabulated: for the real-valued T2 kernel its Fisher information equals the phase-corrected real arm's "
          "(`gaussian_complex` reduces to `gaussian_real` when the Jacobian is real), so the value of phase is zero by construction here and "
          "is a question for the complex T2* kernel (charter §2.3), which is not registered (G2).")
md.append("")

md += ["## 4. Reading", "",
       "- **SNR is the myelin axis; the window is the prostate axis.** White matter's MWF bound at 32 × 10 ms falls as 1/SNR and saturates "
       "against the window only above N ≈ 128: the demyelination change (|Δ|/3 = 0.020) is a 3σ event above first-echo SNR ≈ 360 under a free "
       "K = 3 model and ≈ 190 with the CSF-like T2 fixed, while no echo count at SNR 100 reaches it (the floor is 0.031–0.033 at N ≥ 128, set by "
       "the first few echoes that carry the 15 ms component). The prostate is the converse: at SNR 100 the luminal water fraction crosses the "
       "clinical label at N = 48 (window 480 ms) and the 10 % label at N = 64, and at 32 echoes it needs SNR ≈ 220 (normal) / 160 (cancer) — "
       "the window rule of §1.2 as a design statement.",
       "- **The labels order the tissues the same way, but the clinical label moves the boundary.** For the prostate rows the clinical "
       "label (Δ = −0.14) is reached at roughly half the SNR of the 10 % label (224 vs 436 normal; 164 vs 766 cancer); for white matter it "
       "is reached earlier than the 10 % label too (364 vs 650), because a 30 % relative change on a small functional is a wide interval in "
       "absolute terms; for the cord the age change is small (Δ = −0.03) and the clinical label is the hardest of the three (SNR 1150 free, "
       "440 constrained). A per-tissue criterion re-orders what 'estimable' means, which is why v0.14 scheduled it.",
       "- **Amplitude vector at fixed ratio.** Prostate cancer (LWF 0.24 → 0.10 at the same T2 pair) roughly doubles the SNR needed for 'K' and "
       "for the 10 % label but *lowers* it for the clinical label (164 vs 224), because |Δ| is the same while the bound on a smaller fraction is "
       "smaller in absolute terms. The muscle pair (0.08 → 0.14 vascular fraction at ratio 5.5) is the easy oedema case: the venous-filled row "
       "crosses the clinical label at SNR ≈ 110 or N = 48.",
       "- **Steatosis on the T2 axis is where the Rician floor and the σ nuisance first cost something.** Water at 36 ms decays to the noise floor "
       "within the 320 ms window, so the fat rows are the only dictionary rows for which the magnitude arm costs 16–37 % over the phase-corrected "
       "arm and joint σ costs 6–10 % (§3.2's bound-level probe found < 2 % elsewhere, and the map confirms that everywhere the signal stays above "
       "the floor). Even so the fat fraction needs SNR ≈ 900 (10 %) / 340 (25 %) to be a 3σ change and no window helps (ratio 2): the wrong-tool "
       "verdict of results/threshold_tissues.md, in SNR units.",
       "- **What the map does not contain.** The complex arm (value of phase) needs the T2* kernel; other spacings than 10 ms and other "
       "placements are the sampling-design study (§6.1); the χ, g-factor and CS rungs of the noise ladder need the k-space-first simulator (E2). "
       "Each is a column to add to this table, not a new table."]
md.append("")

(OUT / "crlb_map.md").write_text("\n".join(md) + "\n")
with (OUT / "crlb_map.csv").open("w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)
print("\n".join(md))
print("wrote", OUT / "crlb_map.md", OUT / "crlb_map.csv", len(rows), "rows")
