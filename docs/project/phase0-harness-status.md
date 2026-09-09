# Phase 0 harness — status (2026-09-09, revision 7)

Companion to `claude/phase0-findings.md` (revision 2 + addenda through revision 5) and charter v0.14. Short, operational; update when the harness moves.

## Where the code is
Git repository in the connected folder `~/Documents/ExponentialParameterEstimation/` (charter §7, v0.10):
`mexp-harness/` is the code, `docs/project/` mirrors the living documents. Python ≥ 3.10, numpy/scipy;
`pip install -e ".[dev]" && pytest` inside `mexp-harness/` (71 tests, ~25 s). Public mirror: `github.com/esd100/ExponentialParameterEstimation` (created and pushed by Eric 2026-09-09; tags `charter-v0.10`–`charter-v0.14`; a PAT on the Mac's remote URL lets the Cowork VM push, the cloud container cannot). Licenses: Apache-2.0 (code), CC BY 4.0 (dictionary and documents) — repository root `LICENSE`, `LICENSE-DOCS`. The local Cowork VM has no scipy, so
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
  Mellin / BBP continuum expressions, `r_min` and `k_max` in three constant conventions (`istratov` = the printed π·SNR² form, `arccosh` = relative criterion, `charter` = large-SNR limit), `ISTRATOV_TABLE_I` reproduced (closed form and finite-domain SVD), Ostrowsky spacing.
- `mexp.crlb` (revision 2) — Fisher information / CRLB for Gaussian real, Gaussian complex and Rician
  noise, σ known or jointly estimated; exact Rician per-sample blocks; delta-method functional bounds; not an estimator.
- `mexp.tissue_data` + `mexp.tissues` (v2.2) — tissue and organ dictionary: 19 entries; bulk properties (water, relative PD, T1, T2 at 1.5/3 T, ADC, lipid mass fraction, PDFF), components per modality, theory block, status per value (**23 PRIMARY / 17 SECONDARY / 1 TERTIARY / 1 RECALLED / 14 THEORY** component values after the 2026-09-09 verification pass — brain WM/GM, cord, muscle, WM T1, tendon and prostate sets now on the papers' own tables; every Stanisz 2005 value on the publisher copy; no RECALLED component set remains; the one RECALLED value is the renal-medulla IVIM D*); `data/tissue_dictionary.json` and `docs/tissue-dictionary.md` are generated (`scripts/export_tissue_dictionary.py`, `scripts/render_tissue_dictionary_doc.py`); `scripts/phase0_threshold_tissues.py` evaluates the §1.2 clauses over it.
- Scripts: `scripts/phase0_conditioning.py` (sweep, figures), `scripts/phase0_threshold.py` (charter §1.2
  threshold at the reference configuration), `scripts/provenance/lanczos_two_exp_approximant.py`.
- Correctness test #1 (Lanczos) passes under charter v0.7's (a)/(b) criteria and is **locked against the primary** (pp. 272–279 read 2026-09-07; eight Lanczos-specific tests incl. Varah 1985 Table 2 and Istratov & Vyvenko Fig. 2, both read 2026-09-09).

## SNR conventions in use
Harness axis default: SNR = S_ref / σ₁ (S_ref = unattenuated magnetisation sum; σ₁ from the R = 1 single-coil
reconstruction of the same k-space noise) — logged in charter §8. Charter §1.2 threshold and the CRLB tables:
first-echo SNR, σ = S(t₁)/SNR. `mexp.crlb.sigma_from_first_echo_snr` / `sigma_from_reference_snr` convert.

## Open items carried forward
1. **Home for the code.** Resolved: the repository above; license resolved 2026-09-09 (Apache-2.0 code, CC BY 4.0 dictionary/documents); **public mirror created and pushed by Eric 2026-09-09** (`origin` = `github.com/esd100/ExponentialParameterEstimation`). Session practice: the cloud session clones the mirror, works and tests there, writes the changed files back to the connected folder, and the commit/tag/push happens on the Mac (the container has no GitHub credentials).
2. **Lanczos book check.** Closed 2026-09-07 (primary read). **Varah 1985 closed 2026-09-09:** does not quote the coefficients; his own fit reproduced.
3. **Istratov & Vyvenko constant convention.** **Closed 2026-09-09:** amplitude SNR confirmed; printed constant is π·SNR² inside the arccosh (charter §1.2 v0.12); Table I reproduced.
4. **Threshold framing.** Accepted by Eric 2026-09-07 (two-level: kernel-level vectors + tissue-level dictionary).
5. **Dictionary verification pass** (charter §10 step 8): **priority 1 done 2026-09-09** — Sabouri 2017 ×2, Whittall 1997, MacKay 1994, Saab 1999, Araujo 2014, Stanisz 2005 (publisher copy), MacMillan 2011, Labadie 2014, Prasloski 2012, Du 2012, Bouhrara 2015 read and applied (dictionary v2.2; `results/threshold_tissues.md` re-run; two class changes in charter §8: prostate at the reference train down, cord under K = 2 up). **PDFF ranges:** not movable from the original 57 PDFs, but Eric has since placed a curated water–fat set of fifteen papers in `literature/` (`literature-requests.md` v4, #58–#72: Szczepaniak 2005, Reeder 2011, Hamilton 2011, Bydder 2008, Yu 2008, Liu 2007, Hernando 2012, Yokoo 2011, Tang 2015, Schwimmer 2015, Idilman 2015, Kühn 2015, Guglielmo 2023, Armstrong 2018, Hu 2011). **Next:** read them, move the `pdff` values to PRIMARY, then the pathology axis with steatotic liver at PDFF 10 / 25 % built from those primaries (charter §10 step 8e), then the priority-2 bulk-property reads (T1 at 3 T, relative PD). The estimability labels of `results/threshold_tissues.md` are now defined in charter §1.2 (v0.14); a per-tissue clinical criterion (SD ≤ |Δ|/3) is scheduled with the pathology axis. The abdominal THEORY splits stay: measuring them is a recorded future research project (register E3), not current focus.
6. Next Phase 0 items in charter order: CRLB map (K = 2, 3 × separation × SNR × three arms × noise-knowledge ladder, over the dictionary); joint (θ, σ) analytic work aimed at the misspecified / offset / χ-pipeline / external-σ rungs; k-space-first simulator (E2); EPG physical-truth path; `crlb_optimal`; Bates–Watts curvature with the §6.2 calibration metric.
