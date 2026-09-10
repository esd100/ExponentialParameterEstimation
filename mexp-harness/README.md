# mexp — Phase 0 harness skeleton

Benchmark harness for multi-exponential MR parameter estimation, built against the project charter
(§6.1 axes, §4 Phase 0, guardrails G2/G5, k-space-first standing rule).

```
pip install -e ".[dev]"
pytest                                   # 80 tests, ~70 s
python scripts/phase0_conditioning.py    # SVD / Picard / truncation sweep -> results/
python scripts/phase0_threshold.py       # charter §1.2 falsifiable threshold at the reference configuration
python scripts/phase0_threshold_tissues.py  # the same clauses over the tissue dictionary (three labels, incl. SD ≤ |Δ|/3)
python scripts/phase0_crlb_map.py           # CRLB map over the dictionary: SNR / window crossings, arms, noise-knowledge rung
python scripts/export_tissue_dictionary.py  # regenerate data/tissue_dictionary.json
python scripts/render_tissue_dictionary_doc.py  # regenerate docs/tissue-dictionary.md
```

| Where | What |
|---|---|
| `mexp/axes.py` | every §6.1 axis as an enum; `Cell` = one benchmark address; `enumerate_cells` |
| `mexp/design.py` | encoding-point designs; uniform / subset / sparse-ruler / co-prime / nested / log / scattered |
| `mexp/params.py` | `ParamSpec`, `Theta` (amplitudes, per-component xi, nuisance, fixed), one flat packing |
| `mexp/kernels/` | `Kernel` ABC (one abstract method: `atoms`); `t2_cpmg` registered; `OffsetAugmented` wrapper |
| `mexp/truth.py` | discrete / continuous / physical ground truths with `signal()` and `mass_below()` |
| `mexp/representation.py` | complex · phase-corrected real · magnitude arms |
| `mexp/sim/` | k-space-first simulator **interface**; the only noise entry point is `add_kspace_noise` |
| `mexp/conditioning.py` | SVD, effective rank, Picard (raw + smoothed), TSVD resolution, Mellin/BBP reference, `r_min`/`k_max` in both constant conventions, Ostrowsky spacing |
| `mexp/crlb.py` | Fisher information / CRLB: Gaussian real & complex, Rician with σ known or jointly estimated; functional (delta-method) bounds; not an estimator |
| `mexp/tissue_data.py`, `mexp/tissues.py` | tissue and organ dictionary (v2.3, 19 normal entries + 5 pathology rows — steatotic liver at PDFF 10 / 25 %, malignant prostate PZ, venous-filled muscle, MS-lesion WM — with `condition` and `clinical_delta` on every entry; component sets on the papers' own tables after the 2026-09-09 and 2026-09-10 passes): bulk properties (water, PD, T1, T2, ADC, lipid mass fraction, PDFF), components per modality, theory block, provenance status on every value; API and JSON/document generators |
| `data/tissue_dictionary.json` | generated JSON release of the dictionary |
| `docs/tissue-dictionary.md` | generated human-readable dictionary with the pool/exchange framework |
| `mexp/estimators/` | `Estimator` protocol; **no implementations** (charter G2) |
| `mexp/datasets/lanczos.py` | NIST StRD Lanczos1/3 data, certified values, frozen 2-exp approximant, provenance |
| `tests/test_lanczos_degeneracy.py` | correctness test #1 (charter v0.7 criteria (a)/(b); locked against Lanczos 1956 pp. 272–279) |
| `tests/test_crlb.py` | CRLB limits, Rife–Boorstyn contrast, sloppy FIM spectrum |
| `tests/test_kernel_interface.py` | T2 conformance + IR / Look-Locker / T2* / T1ρ-dispersion / b-tensor kernels on the unchanged base class |
| `tests/test_kspace_first_rule.py` | fails if any module outside `mexp/sim` touches an RNG or image-domain noise model |
| `tests/test_tissues.py`, `tests/test_crlb_map.py` | dictionary consistency incl. the pathology axis; the CRLB map's crossing machinery and locked numbers |
| `docs/kernel-interface.md` | design note: how each modality maps onto the interface |
| `docs/phase0-findings.md` | Lanczos verification, conditioning results, threshold outcomes, charter reconciliation |
| `../docs/project/bibliography.md` | the one annotated bibliography (charter G1; mirrored from the project) |
| `results/` | sweep CSV, summary tables, figures 1–5, `threshold_evaluation.md`, `threshold_tissues.md` (three labels), `crlb_map.md` / `.csv` |

License: Apache-2.0 (`../LICENSE`); the dictionary document and JSON are CC BY 4.0 (`../LICENSE-DOCS`).

Nothing in this package draws a noise realisation. SNR enters Phase 0 only as a threshold on singular values (conditioning) or as σ in a Fisher information (CRLB).
