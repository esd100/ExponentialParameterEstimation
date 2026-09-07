"""
The charter §1.2 threshold, evaluated over the tissue dictionary (charter v0.10).

For every T2-kernel entry in mexp.tissues, at (i) the reference acquisition
(32 x 10 ms, first-echo SNR 100) and (ii) the entry's typical acquisition,
compute the Rician (sigma known) CRLB for the visible components and the
delta-method bound on the entry's clinical functional.  Components below the
first echo are dropped and the fractions renormalised (the harness does not
pretend to see a 3 ms component with a 10 ms first echo).

No noise realisation is drawn.  Output: results/threshold_tissues.md
"""
from __future__ import annotations

import pathlib

import numpy as np

from mexp import crlb as CR, tissues as TS
from mexp.design import uniform
from mexp.kernels import get

OUT = pathlib.Path(__file__).resolve().parents[1] / "results"
OUT.mkdir(exist_ok=True)
k = get("t2_cpmg")

K_OK, F_OK = 0.25, 0.10   # "estimable": every visible T2 < 25 % rel SD; functional < 10 % rel SD


def evaluate(e: TS.ComponentSet, n: int, dte: float, snr: float):
    d = uniform(n, dte)
    th = e.theta(min_value=dte)
    sigma = CR.sigma_from_first_echo_snr(k, th, d, snr)
    r = CR.crlb(k, th, d, sigma, "rician")
    relT = np.array(list(r.relative_sd_of("T2").values()))
    rela = np.array(list(r.relative_sd_of("a").values()))
    f_true = f_sd = None
    if e.functional_threshold is not None and th.K > 1:
        g = CR.mass_below_gradient(th, e.functional_threshold)
        f_sd = CR.functional_sd(r, g)
        a = th.amplitudes
        f_true = float((a * (th.nonlinear[:, 0] < e.functional_threshold)).sum() / a.sum())
        if f_true > 0.5:                  # report the minor side (LWF, fat fraction, extracellular fraction)
            f_true = 1.0 - f_true
    return th, relT, rela, f_true, f_sd


lines = ["# §1.2 threshold over the tissue dictionary", "",
         "Rician CRLB with σ known, first-echo SNR as stated; components below the first echo dropped and fractions renormalised. "
         f"'K estimable' = every visible T2 under {K_OK:.0%} relative SD; 'functional estimable' = the entry's clinical "
         f"functional under {F_OK:.0%} relative SD (delta method). The status column is the provenance of the component "
         "set (`mexp/tissue_data.py`): PRIMARY / SECONDARY are read from the literature this project opened; THEORY rows are "
         "working configurations for organs with no multi-component study reached (abdominal T2 splits); RECALLED rows are "
         "from memory. Rows marked THEORY or RECALLED shape the question, they do not settle it.", ""]

for label, acq_of in (("Reference acquisition: 32 echoes × 10 ms, first-echo SNR 100", lambda e: (32, 10.0, 100.0)),
                      ("Entry-specific typical acquisition", lambda e: (int(e.typical_acquisition["n_echoes"]),
                                                                        float(e.typical_acquisition["dTE_ms"]),
                                                                        float(e.typical_acquisition["first_echo_snr"])))):
    lines += [f"## {label}", "",
              "| tissue | status | visible K (of K) | composition (fraction @ T2 ms) | rel SD of T2 (%) | rel SD of fractions (%) | functional | value | SD (abs) | rel SD (%) | K estimable | functional estimable |",
              "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for e in TS.entries(kernel="t2_cpmg"):
        n, dte, snr = acq_of(e)
        th, relT, rela, f_true, f_sd = evaluate(e, n, dte, snr)
        comp = ", ".join(f"{a:.2f}@{t:g}" for a, t in zip(th.amplitudes, th.nonlinear[:, 0]))
        acq = "" if label.startswith("Reference") else f" ({n}×{dte:g} ms, SNR {snr:g})"
        k_ok = "yes" if np.all(relT < K_OK) else "no"
        if f_sd is None:
            f_cells = f"{e.functional} | — | — | — | {k_ok} | —"
        else:
            frel = f_sd / f_true if f_true > 0 else np.inf
            f_cells = f"{e.functional} | {f_true:.3f} | {f_sd:.3f} | {100*frel:.0f} | {k_ok} | {'yes' if frel < F_OK else 'no'}"
        lines.append(f"| {e.tissue} ({e.organ}){acq} | {e.status.value} | {th.K} (of {e.K}) | {comp} | "
                     f"{', '.join(f'{100*v:.0f}' for v in relT)} | {', '.join(f'{100*v:.0f}' for v in rela)} | {f_cells} |")
    lines.append("")

# ---- what constraining the long component buys (the price of the free CSF-like component) ------------------
lines += ["## Myelin-type functional under three parameterisations (32 × 10 ms)", "",
          "| tissue | SNR | MWF | SD, free K = 3 | SD, long T2 fixed | SD, long component dropped (K = 2) | myelin T2 rel SD in the K = 2 model (%) |",
          "|---|---|---|---|---|---|---|"]
from mexp.params import Theta
for key in ("brain_wm", "brain_gm", "spinal_cord_wm"):
    e = TS.get(key).T2
    th3 = e.theta()
    a2 = th3.amplitudes[:2] / th3.amplitudes[:2].sum()
    th2 = Theta(a2, th3.nonlinear[:2])
    d = uniform(32, 10.0)
    for snr in (100, 300):
        sig = CR.sigma_from_first_echo_snr(k, th3, d, snr)
        r3 = CR.crlb(k, th3, d, sig, "rician")
        g3 = CR.mass_below_gradient(th3, e.functional_threshold)
        sd_free = CR.functional_sd(r3, g3)
        keep = [i for i, l in enumerate(r3.labels) if l != "T22"]
        cov_fix = np.linalg.pinv(r3.fim[np.ix_(keep, keep)])
        sd_fix = float(np.sqrt(g3[keep] @ cov_fix @ g3[keep]))
        sig2 = CR.sigma_from_first_echo_snr(k, th2, d, snr)
        r2 = CR.crlb(k, th2, d, sig2, "rician")
        sd_2 = CR.functional_sd(r2, CR.mass_below_gradient(th2, e.functional_threshold))
        relT0 = 100 * list(r2.relative_sd_of("T2").values())[0]
        lines.append(f"| {e.tissue} | {snr} | {th3.amplitudes[0]:.2f} | {sd_free:.3f} | {sd_fix:.3f} | {sd_2:.3f} | {relT0:.0f} |")
lines.append("")

lines += ["## Reading", "",
          "- At the reference acquisition no myelin-type entry is 'estimable' by either criterion under a free K = 3 model: the "
          "free long component (2000 ms, unpinned by a 320 ms window) roughly doubles the bound on the myelin water fraction "
          "(white matter: 0.072 free vs 0.037 with the long T2 fixed vs 0.029 with it dropped, at SNR 100). With the long "
          "component fixed or dropped the white-matter MWF bound is about ±0.03 (1σ) at SNR 100 and ±0.01 at SNR 300 — the "
          "familiar experience that myelin water imaging needs high SNR or averaging, now as a bound.",
          "- The functional is better determined than the parameters (white matter MWF ~20 % relative vs myelin T2 44 % in the "
          "K = 2 model at SNR 100): a first sighting of charter Phase 3's 'estimate functionals, not spectra', at the level of the bound.",
          "- Minor components under ~5 % (grey-matter myelin water) fail outright; muscle's four-component structure (Saab 1999, "
          "measured at SNR ~3500 with 1.2 ms echoes) collapses to an unestimable three-component fit at clinical SNR — the "
          "clinical protocol sees one ~30 ms pool and, at best, the ~120 ms extracellular tail; well-separated two-component "
          "tissues (prostate luminal water, ratio ~8) are estimable, to ~5 % relative at their own 64 × 8 ms train.",
          "- The abdominal THEORY rows (liver, pancreas: ratio ~3.5, minor fraction ~0.2) come out 'K estimable' at the reference "
          "acquisition but not at their own shorter, noisier protocols; spleen and kidney (ratio ~2-3) are not estimable anywhere. "
          "These rows test whether T2 can see the vascular compartment that IVIM sees; the physics (fast exchange) says it mostly cannot.",
          "- The entry-specific acquisitions move results mostly through the window (prostate's train reaches 500 ms; the 16 × 8 ms "
          "abdominal trains lose the 150-220 ms components; the 8 × 12 ms myocardial train is a K = 1 null case), consistent with "
          "the window rule in charter §1.2.",
          "- Provenance: the brain, cord, cartilage, bone, marrow, breast and blood rows rest on opened literature (SECONDARY/PRIMARY); "
          "the abdominal T2 splits (liver, spleen, kidney, pancreas) are THEORY rows built from bulk T2 and IVIM perfusion fractions "
          "because no in vivo multi-component T2 study of those organs was reached; prostate is RECALLED pending the luminal-water "
          "full text. Verification moves numbers, not the structure of the conclusion, which is set by ratios and minor-fraction sizes."]

(OUT / "threshold_tissues.md").write_text("\n".join(lines))
print("\n".join(lines))
