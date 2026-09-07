# Phase 0 harness — status (2026-09-07, revision 4)

Companion to `claude/phase0-findings.md` (revision 2 + addendum) and charter v0.11. Short, operational; update when the harness moves.

## Where the code is
Git repository in the connected folder `~/Documents/ExponentialParameterEstimation/` (charter §7, v0.10):
`mexp-harness/` is the code, `docs/project/` mirrors the living documents. Python ≥ 3.10, numpy/scipy;
`pip install -e ".[dev]" && pytest` inside `mexp-harness/` (64 tests, ~20 s). The local Cowork VM has no scipy, so
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
- `mexp.tissue_data` + `mexp.tissues` (v2) — tissue and organ dictionary: 18 entries; bulk properties (water/PD, T1, T2 at 1.5/3 T, ADC), components per modality, theory block, status per value (7 PRIMARY / 30 SECONDARY / 1 TERTIARY / 6 RECALLED / 10 THEORY component values); `data/tissue_dictionary.json` and `docs/tissue-dictionary.md` are generated (`scripts/export_tissue_dictionary.py`, `scripts/render_tissue_dictionary_doc.py`); `scripts/phase0_threshold_tissues.py` evaluates the §1.2 clauses over it.
- Scripts: `scripts/phase0_conditioning.py` (sweep, figures), `scripts/phase0_threshold.py` (charter §1.2
  threshold at the reference configuration), `scripts/provenance/lanczos_two_exp_approximant.py`.
- Correctness test #1 (Lanczos) passes under charter v0.7's (a)/(b) criteria and is **locked against the primary** (pp. 272–279 read 2026-09-07; six Lanczos-specific tests).

## SNR conventions in use
Harness axis default: SNR = S_ref / σ₁ (S_ref = unattenuated magnetisation sum; σ₁ from the R = 1 single-coil
reconstruction of the same k-space noise) — logged in charter §8. Charter §1.2 threshold and the CRLB tables:
first-echo SNR, σ = S(t₁)/SNR. `mexp.crlb.sigma_from_first_echo_snr` / `sigma_from_reference_snr` convert.

## Open items carried forward
1. **Home for the code.** Resolved: the repository above. **Still open: a license** (needed before the harness can be the E1 release; recommendation in the 2026-09-07 session summary — Apache-2.0 or BSD-3 for code, CC-BY-4.0 for the dictionary and documents).
2. **Lanczos book check.** Closed 2026-09-07 (primary read). Only Varah 1985's journal text remains a citation check (`literature-requests.md` #2).
3. **Istratov & Vyvenko constant convention.** Resolved in principle (amplitude SNR, arccosh form; charter §1.2); read the paper for the citation (`literature-requests.md` #1, DOI 10.1063/1.1149581).
4. **Threshold framing.** Accepted by Eric 2026-09-07 (two-level: kernel-level vectors + tissue-level dictionary).
5. **Dictionary verification pass** (charter §10 step 8): PDFs into `literature/` per `literature-requests.md` (priority 1: prostate luminal water, Whittall 1997, Saab 1999, Stanisz 2005); move values to PRIMARY; replace the abdominal THEORY splits when a study is found; add the pathology axis; then organs and fields.
6. Next Phase 0 items in charter order: CRLB map (K = 2, 3 × separation × SNR × three arms × noise-knowledge ladder, over the dictionary); joint (θ, σ) analytic work aimed at the misspecified / offset / χ-pipeline / external-σ rungs; k-space-first simulator (E2); EPG physical-truth path; `crlb_optimal`; Bates–Watts curvature with the §6.2 calibration metric.
