"""
Evaluate the charter v0.7 §1.2 falsifiable threshold at the reference clinical
configuration, and check the §1.2 closed forms against the numerics.

Reference configuration (charter §1.2): 32 echoes at 10 ms spacing, T2 support
10–300 ms, first-echo SNR 100, Rician magnitude.

Clauses (charter §1.2):
  UP-1   #singular values of the SNR-scaled discretised kernel exceeding unity >= 4
  UP-2   joint CRLB gives < 10 % relative SD on all three decay constants of a K = 3 truth
         with adjacent ratio 3
  DOWN-1 that count <= 1
  DOWN-2 K = 2 CRLB with adjacent ratio 4 exceeds 25 % relative SD on either decay constant

The charter does not fix the amplitude vector for UP-2 / DOWN-2, nor the
normalisation behind "SNR-scaled"; both are swept here and the sensitivity is
reported rather than hidden.  No noise is drawn.

Output: results/threshold_evaluation.md
"""
from __future__ import annotations

import pathlib

import numpy as np

from mexp import conditioning as C, crlb as CR
from mexp.design import uniform
from mexp.kernels import get
from mexp.params import Theta

OUT = pathlib.Path(__file__).resolve().parents[1] / "results"
OUT.mkdir(exist_ok=True)

k = get("t2_cpmg")
d = uniform(32, 10.0)                      # t = 10 .. 320 ms
TMIN, TMAX, SNR0 = 10.0, 300.0, 100.0
GAMMA = TMAX / TMIN
grid = C.log_grid(TMIN, TMAX, 300)
lines = ["# §1.2 falsifiable threshold — evaluation at the reference clinical configuration", "",
         "Configuration: 32 echoes, ΔTE = 10 ms (t ∈ [10, 320] ms), T2 support [10, 300] ms (Γ = 30), first-echo SNR 100, "
         "Rician magnitude with σ known (joint-σ and Gaussian shown for comparison). No noise realisations; "
         "SNR enters as σ = S(t₁)/SNR.", ""]

# ---------------------------------------------------------------------------------------
# UP-1 / DOWN-1: the SVD count
# ---------------------------------------------------------------------------------------
lines += ["## UP-1 / DOWN-1 — singular-value count", ""]
A = k.discretize(d, grid)
weightings = {"log-uniform grid, unweighted (≡ L²(d ln T))": np.ones(grid.size),
              "L²(dT) column weights": np.gradient(grid),
              "L²(d ln T / T) column weights": np.gradient(np.log(grid)) / grid}
lines.append("| column normalisation of the discretised kernel | σᵢ/σ₁ (i = 1..6) | count, SNR 50 | count, SNR 100 | count, SNR 200 |")
lines.append("|---|---|---|---|---|")
counts_ref = {}
for name, w in weightings.items():
    s = C.singular_spectrum(A * np.sqrt(w)[None, :])
    cts = [C.effective_rank(s, x) for x in (50, 100, 200)]
    counts_ref[name] = cts[1]
    lines.append(f"| {name} | {', '.join(f'{x:.4g}' for x in s[:6] / s[0])} | {cts[0]} | {cts[1]} | {cts[2]} |")
lines.append("")
lines.append("Reading of 'SNR-scaled kernel exceeding unity' used: σᵢ/σ₁ > 1/SNR (the kernel scaled so its leading "
             "singular value is SNR). An absolute reading (σᵢ(A) > σ with unit-amplitude columns) gives 7 and is "
             "grid-size dependent, so it is not a usable clause.")
lines.append("")
# Picard counts for the reference truths
truths = {
    "K=3 (20, 60, 180) ms, equal amplitudes": Theta([1 / 3] * 3, [[20.0], [60.0], [180.0]]),
    "K=3 (20, 60, 180) ms, 0.2/0.6/0.2": Theta([0.2, 0.6, 0.2], [[20.0], [60.0], [180.0]]),
    "K=2 (20, 80) ms, equal amplitudes": Theta([0.5, 0.5], [[20.0], [80.0]]),
    "K=2 (20, 80) ms, 0.2/0.8": Theta([0.2, 0.8], [[20.0], [80.0]]),
}
lines.append("| truth | Picard count (smoothed) | raw leading run | energy-convention count |")
lines.append("|---|---|---|---|")
Aw = C.discretized_operator(k, d, grid, column_weights="sqrt_dlog")
for name, th in truths.items():
    b = k.forward(th, d)
    sig = CR.sigma_from_first_echo_snr(k, th, d, SNR0)
    pr = C.picard(Aw, b, sig, per_sample_snr=SNR0)
    lines.append(f"| {name} | {pr.n_picard} | {pr.n_above_noise} | {pr.n_energy} |")
lines.append("")
up1 = counts_ref["log-uniform grid, unweighted (≡ L²(d ln T))"] >= 4
down1 = counts_ref["log-uniform grid, unweighted (≡ L²(d ln T))"] <= 1
lines.append(f"**UP-1 fires: {up1}** (count = {counts_ref['log-uniform grid, unweighted (≡ L²(d ln T))']} under the natural normalisation; "
             f"σ₄/σ₁ = 0.024 vs 1/SNR = 0.010, σ₅/σ₁ = 0.006 — the count is 4 for SNR 42–159 and sits exactly on the clause boundary). "
             f"**DOWN-1 fires: {down1}.**")
lines.append("")

# ---------------------------------------------------------------------------------------
# UP-2 / DOWN-2: CRLB clauses
# ---------------------------------------------------------------------------------------
def rel_T(th, model, joint=False, snr=SNR0):
    sig = CR.sigma_from_first_echo_snr(k, th, d, snr)
    r = CR.crlb(k, th, d, sig, model, joint)
    return [100 * v for v in r.relative_sd_of("T2").values()]

lines += ["## UP-2 — K = 3, adjacent ratio 3: relative SD (%) of the three decay constants", ""]
lines.append("| placement (ms) | amplitudes | Gaussian | Rician, σ known | Rician, σ jointly estimated |")
lines.append("|---|---|---|---|---|")
up2_any = False
for T in ([15, 45, 135], [20, 60, 180], [30, 90, 270]):
    for amps, lab in (([1 / 3] * 3, "equal"), ([0.2, 0.6, 0.2], "0.2/0.6/0.2"), ([0.6, 0.2, 0.2], "0.6/0.2/0.2")):
        th = Theta(amps, [[t] for t in T])
        g = rel_T(th, "gaussian_real"); r = rel_T(th, "rician"); j = rel_T(th, "rician", True)
        up2_any |= all(v < 10 for v in j)
        lines.append(f"| {T} | {lab} | {', '.join(f'{v:.0f}' for v in g)} | {', '.join(f'{v:.0f}' for v in r)} | {', '.join(f'{v:.0f}' for v in j)} |")
lines.append("")
lines.append(f"**UP-2 fires: {up2_any}.** The best single constant reaches 30 %; the best all-three case is 70 / 103 / 30 % — nowhere near 10 %, and most cases exceed 100 % on at least one constant. "
             "K = 3 at ratio 3 is not estimable at this configuration.")
lines.append("")

lines += ["## DOWN-2 — K = 2, adjacent ratio 4: relative SD (%) of the two decay constants", ""]
lines.append("| placement (ms) | amplitudes | Gaussian | Rician, σ known | Rician, σ jointly estimated | > 25 % on either? |")
lines.append("|---|---|---|---|---|---|")
down2 = {}
for T in ([15, 60], [20, 80], [30, 120], [50, 200]):
    for amps, lab in (([0.5, 0.5], "equal"), ([0.2, 0.8], "0.2/0.8"), ([0.8, 0.2], "0.8/0.2")):
        th = Theta(amps, [[t] for t in T])
        g = rel_T(th, "gaussian_real"); r = rel_T(th, "rician"); j = rel_T(th, "rician", True)
        fire = any(v > 25 for v in r)
        down2[(tuple(T), lab)] = fire
        lines.append(f"| {T} | {lab} | {', '.join(f'{v:.1f}' for v in g)} | {', '.join(f'{v:.1f}' for v in r)} | {', '.join(f'{v:.1f}' for v in j)} | {'yes' if fire else 'no'} |")
lines.append("")
n_fire = sum(down2.values())
lines.append(f"**DOWN-2 fires in {n_fire} of {len(down2)} placement × amplitude cases** — never for equal amplitudes, "
             "always when the short component carries 20 % of the signal (its T2 then has 30–40 % relative SD). "
             "The clause's outcome is decided by the amplitude vector, which the charter does not specify.")
lines.append("")

# ---------------------------------------------------------------------------------------
# closed forms vs numerics at Γ = 30
# ---------------------------------------------------------------------------------------
lines += ["## §1.2 closed forms against the numerical count (Γ = 30 = in-window range; window γ_t = 32)", ""]
lines.append("| SNR | R_min, charter exp(π²/2 ln SNR) | R_min, arccosh form | K_max, charter 1 + 2 ln SNR ln Γ/π² | (ln Γ/π²)·arccosh(SNR²) + 1 | numerical count | γ^(1/count) |")
lines.append("|---|---|---|---|---|---|---|")
s_ref = C.singular_spectrum(Aw)
for snr in (30, 50, 100, 200, 1000):
    n = C.effective_rank(s_ref, snr)
    lines.append(f"| {snr} | {C.r_min(snr, 'charter'):.2f} | {C.r_min(snr, 'arccosh'):.2f} | {C.k_max(GAMMA, snr, 'charter'):.2f} | "
                 f"{C.k_max(GAMMA, snr, 'arccosh'):.2f} | {n} | {C.resolution_ratio_from_count(GAMMA, n):.2f} |")
lines.append("")
lines.append("Both closed forms reproduce the numerical count to within ±0.8 at this configuration. They cannot be told apart "
             "by the count (the O(ln 2) difference in ω_max is 0.24 of a singular value here); the arccosh form is the one that "
             "follows from the Mellin gain without approximation, and the charter's form is its 2 ln SNR ≫ ln 2 limit. "
             "Neither is a per-index prediction: individual singular values do not follow uniform Mellin quantisation "
             "(σ₁/σ₀ ≈ 0.33 numerically for every covering-window γ ≥ 100, against 0.48–0.78 predicted), so the "
             "Epstein–Schotland / McWhirter–Pike closed form is a check on the *count and decay rate*, not on σᵢ one by one.")
lines.append("")

# ---------------------------------------------------------------------------------------
# preliminary probe of §3.2 (value of noise knowledge), because the machinery is now here
# ---------------------------------------------------------------------------------------
lines += ["## Preliminary: cost of not knowing σ (charter §3.2, §10 step 4) — 32 echoes, single-coil Rician, σ known vs jointly estimated", ""]
lines.append("| SNR (first echo) | truth | Rician σ known: rel SD T2 (%) | Rician σ joint: rel SD T2 (%) | σ rel SD (%) |")
lines.append("|---|---|---|---|---|")
for snr in (100, 30):
    for name, th in (("K=2 (20, 80), 0.2/0.8", Theta([0.2, 0.8], [[20.0], [80.0]])),
                     ("K=3 (20, 80, 2000), 0.15/0.7/0.15", Theta([0.15, 0.7, 0.15], [[20.0], [80.0], [2000.0]]))):
        sig = CR.sigma_from_first_echo_snr(k, th, d, snr)
        rk = CR.crlb(k, th, d, sig, "rician"); rj = CR.crlb(k, th, d, sig, "rician", True)
        lines.append(f"| {snr} | {name} | {', '.join(f'{100*v:.0f}' for v in rk.relative_sd_of('T2').values())} | "
                     f"{', '.join(f'{100*v:.0f}' for v in rj.relative_sd_of('T2').values())} | {100*rj.relative_sd[-1]:.1f} |")
lines.append("")
lines.append("At 32 echoes the data pin σ to ≈ 1/√(2N) = 12.5 % on their own and the (A, σ) cross-information is small at ν ≫ 1, "
             "so *under the correct Rician likelihood* joint estimation of σ costs < 2 % in decay-constant precision even with a "
             "2000 ms component present (which is itself unrecoverable, 450–1500 % rel SD). This is a bound-level statement "
             "for L2/L5 single-coil data with the right likelihood; it says nothing yet about the bias of a Gaussian fit to Rician "
             "data, about a free-offset model, about χ / non-stationary pipelines, or about σ estimated by an external procedure — "
             "the rungs of the §3.2 ladder that remain.")
lines.append("")

# ---------------------------------------------------------------------------------------
# verdict
# ---------------------------------------------------------------------------------------
lines += ["## Verdict", "",
          "- UP-1 (SVD count ≥ 4): **fires**, at the boundary (count = 4). But it counts informative singular directions, "
          "of which a K-component fit needs ≥ 2K; a count of 4 supports K = 2, not K = 3, and so does not contradict '2–3'.",
          "- UP-2 (K = 3 at ratio 3 under 10 %): **does not fire**, by a factor of 3–15.",
          "- DOWN-1 (count ≤ 1): does not fire.",
          "- DOWN-2 (K = 2 at ratio 4 over 25 %): **fires for a 20/80 amplitude split, not for equal amplitudes.**",
          "",
          "So the ~2–3 figure survives in component units (K = 2 estimable at 3–40 % depending on the amplitude split; K = 3 not), "
          "but the threshold as written is internally inconsistent: its SVD clause and its K = 3 clause point in opposite directions "
          "because they count different things, and its K = 2 clause is decided by an unspecified amplitude vector. Recommended "
          "recalibration (for the charter, not applied here): state UP-1 in component units (count ≥ 2K = 6 informative directions before K = 3 is even conceivable), fix the "
          "amplitude vectors for UP-2 / DOWN-2 (report equal and 20/80), and state the normalisation (σᵢ/σ₁ > 1/SNR on a log-uniform grid)."]

(OUT / "threshold_evaluation.md").write_text("\n".join(lines))
print("\n".join(lines))
