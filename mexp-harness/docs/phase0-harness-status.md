# Phase 0 harness — status (2026-09-10, revision 8)

Companion to `claude/phase0-findings.md` (revision 2 + addenda through revision 6) and charter v0.15. Short, operational; update when the harness moves.

## Where the code is
Git repository in the connected folder `~/Documents/ExponentialParameterEstimation/` (charter §7, v0.10):
`mexp-harness/` is the code, `docs/project/` mirrors the living documents. Python ≥ 3.10, numpy/scipy;
`pip install -e ".[dev]" && pytest` inside `mexp-harness/` (80 tests, ~70 s). Public mirror: `github.com/esd100/ExponentialParameterEstimation` (created and pushed by Eric 2026-09-09; tags `charter-v0.10`–`charter-v0.15`; a PAT on the Mac's remote URL lets the Cowork VM push, the cloud container cannot). Licenses: Apache-2.0 (code), CC BY 4.0 (dictionary and documents) — repository root `LICENSE`, `LICENSE-DOCS`. The local Cowork VM has no scipy, so
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
- `mexp.tissue_data` + `mexp.tissues` (v2.3) — tissue and organ dictionary: 19 normal entries + 5 pathology rows (steatotic liver at PDFF 10 / 25 %, malignant prostate PZ, venous-filled muscle, MS-lesion WM); `condition` and `clinical_delta` on every entry (schema 2.3), `variant()` builds disease rows on their base row's bulk properties; bulk properties (water, relative PD, T1, T2 at 1.5/3 T, ADC, lipid mass fraction, PDFF — liver / pancreas / kidney PDFF PRIMARY after the 2026-09-10 water–fat pass), components per modality, theory block, status per value (**32 PRIMARY / 17 SECONDARY / 1 TERTIARY / 1 RECALLED / 16 THEORY** component values; the one RECALLED value is the renal-medulla IVIM D*); `data/tissue_dictionary.json` and `docs/tissue-dictionary.md` are generated (`scripts/export_tissue_dictionary.py`, `scripts/render_tissue_dictionary_doc.py`); `scripts/phase0_threshold_tissues.py` evaluates the §1.2 clauses over it with three labels (25 % on T2s, 10 % on the functional, SD ≤ |Δ|/3); `scripts/phase0_crlb_map.py` turns the labels into SNR and window crossings per row (`results/crlb_map.md`, `.csv`).
- Scripts: `scripts/phase0_conditioning.py` (sweep, figures), `scripts/phase0_threshold.py` (charter §1.2
  threshold at the reference configuration), `scripts/phase0_threshold_tissues.py`, `scripts/phase0_crlb_map.py`, `scripts/provenance/lanczos_two_exp_approximant.py`.
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
5. **Dictionary verification pass** (charter §10 step 8): **priority 1 done 2026-09-09** — Sabouri 2017 ×2, Whittall 1997, MacKay 1994, Saab 1999, Araujo 2014, Stanisz 2005 (publisher copy), MacMillan 2011, Labadie 2014, Prasloski 2012, Du 2012, Bouhrara 2015 read and applied (dictionary v2.2; `results/threshold_tissues.md` re-run; two class changes in charter §8: prostate at the reference train down, cord under K = 2 up). **Water–fat pass done 2026-09-10 (v0.15):** the fifteen papers (#58–#72) read; liver, pancreas, kidney-cortex PDFF → PRIMARY, adipose → SECONDARY; muscle, myocardium, spleen, breast stay RECALLED (Hu 2011 has no organ table; Grimm 2018 and Szczepaniak 2003 re-requested, `literature-requests.md` v5 #73–#74). **Pathology axis opened (dictionary v2.3)** with five rows and the third label evaluated; **CRLB map built**. **Next:** the priority-2 bulk-property reads (T1 at 3 T, relative PD) and #73–#74 when retrieved; further pathology rows as primaries arrive (iron-loaded liver, fatty pancreas / muscle / myocardium, degenerated cartilage, marrow infiltration, cord lesions). The abdominal THEORY splits stay: measuring them is a recorded future research project (register E3), not current focus.
6. **CRLB map over the dictionary — done 2026-09-10** (`results/crlb_map.md`: SNR and window crossings of the three labels per row, free and constrained; Gaussian-real vs Rician; σ known vs joint. Findings in charter §1.2 / §8: myelin is an SNR axis, the prostate a window axis, the steatotic rows the only place the magnitude arm and joint σ cost anything). Columns still to add as their prerequisites arrive: the complex arm (T2* kernel), sampling designs (§6.1 study), the χ / g-factor / CS rungs (E2). Next Phase 0 items in charter order: joint (θ, σ) analytic work aimed at the misspecified / offset / χ-pipeline / external-σ rungs (the fat rows are the first physical case where the cost is visible); k-space-first simulator (E2); EPG physical-truth path; `crlb_optimal`; Bates–Watts curvature with the §6.2 calibration metric.
