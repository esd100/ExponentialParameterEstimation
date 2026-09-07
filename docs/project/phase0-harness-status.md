# Phase 0 harness — status (2026-09-07, revision 3)

Companion to `claude/phase0-findings.md` (revision 2) and charter v0.10. Short, operational; update when the harness moves.

## Where the code is
Git repository in the connected folder `~/Documents/ExponentialParameterEstimation/` (charter §7, v0.10):
`mexp-harness/` is the code, `docs/project/` mirrors the living documents. Python ≥ 3.10, numpy/scipy;
`pip install -e ".[dev]" && pytest` inside `mexp-harness/` (60 tests, ~15 s). The local Cowork VM has no scipy, so
tests run in the cloud session or on the Mac itself.

## What exists
- `mexp.axes` — all §6.1 axes as enums, `Cell`, `enumerate_cells`, physical-meaningfulness rules.
- `mexp.design` — named multi-dimensional encoding points; uniform / subset-of-grid / sparse-ruler (complete
  rulers n = 2..10, brute-force verified) / co-prime / nested / log / scattered; `crlb_optimal` is an explicit
  `NotImplementedError` (needs a design loop on top of `mexp.crlb`).
- `mexp.params` — `ParamSpec`, `Theta` (amplitudes, (K,p) nonlinear, nuisance, fixed), one flat packing.
- `mexp.kernels` — `Kernel` ABC with a single abstract method `atoms`; **only `t2_cpmg` registered**. IR /
  Look-Locker / complex T2* / T1ρ-dispersion / b-tensor kernels are exercised on the unchanged base class in
  `tests/test_kernel_interface.py` and deliberately not registered (G2).
- `mexp.truth`, `mexp.representation`, `mexp.metrics` (§6.2 vocabulary), `mexp.estimators` (protocol only).
- `mexp.sim` — k-space-first **interface** only; `add_kspace_noise` is the sole noise entry point;
  `tests/test_kspace_first_rule.py` fails the suite if noise is *generated* outside `mexp/sim` (naming a
  likelihood is allowed — the CRLB module needs the Rician one).
- `mexp.conditioning` — SVD, effective rank, Picard (raw + Hansen-smoothed), TSVD resolution kernels,
  Mellin / BBP continuum expressions, `r_min` and `k_max` in both constant conventions, Ostrowsky spacing.
- `mexp.crlb` (revision 2) — Fisher information / CRLB for Gaussian real, Gaussian complex and Rician
  noise, σ known or jointly estimated; exact Rician per-sample blocks; delta-method functional bounds; not an estimator.
- `mexp.tissues` (revision 3) — tissue and organ dictionary, 13 entries, all `RECALLED`; `scripts/phase0_threshold_tissues.py`.
- Scripts: `scripts/phase0_conditioning.py` (sweep, figures), `scripts/phase0_threshold.py` (charter §1.2
  threshold at the reference configuration), `scripts/provenance/lanczos_two_exp_approximant.py`.
- Correctness test #1 (Lanczos) passes under charter v0.7's (a)/(b) criteria; marked
  `provisional_pending_primary`.

## SNR conventions in use
Harness axis default: SNR = S_ref / σ₁ (S_ref = unattenuated magnetisation sum; σ₁ from the R = 1 single-coil
reconstruction of the same k-space noise) — logged in charter §8. Charter §1.2 threshold and the CRLB tables:
first-echo SNR, σ = S(t₁)/SNR. `mexp.crlb.sigma_from_first_echo_snr` / `sigma_from_reference_snr` convert.

## Open items carried forward
1. **Home for the code.** Resolved: the repository above.
2. **Lanczos book check** (*Applied Analysis* 1956, ch. IV, ~p. 276): record Δt, number of points, decimals in
   the table, and whether Lanczos claims a number or "within the accuracy of the data"; the quoted pair
   (2.202, 4.45; 0.305, 1.58) fits a Δt = 0.1 long-window table slightly better than NIST's Δt = 0.05 grid.
   No test depends on it. Also check whether Varah (1985, journal version) actually quotes the coefficients —
   the 1982 tech report does not.
3. **Istratov & Vyvenko constant convention** for the resolvable ratio: harness carries both
   exp(π²/arccosh(SNR²)) (exact from the Mellin gain) and exp(π²/(2 ln SNR)); indistinguishable by the count.
4. **Charter v0.9/v0.10 threshold wording** (kernel-level two vectors + tissue-level dictionary): accept or amend.
5. **Dictionary verification pass** (charter §10 step 8): open each source in `mexp/tissues.py`, move entries from `RECALLED`; re-run the tissue threshold; add organs.
6. Next Phase 0 items in charter order: joint (θ, σ) analytic work aimed at the misspecified / offset /
   χ-pipeline / external-σ rungs (§3.2 probe shows the clean-likelihood cost is < 2 %); k-space-first
   simulator (E2); EPG physical-truth path; `crlb_optimal`; Bates–Watts curvature with the §6.2 calibration metric.
