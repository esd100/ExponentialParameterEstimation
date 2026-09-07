# §1.2 threshold over the tissue dictionary

Rician CRLB with σ known, first-echo SNR as stated; components below the first echo dropped and fractions renormalised. 'K estimable' = every visible T2 under 25% relative SD; 'functional estimable' = the entry's clinical functional under 10% relative SD (delta method). **All dictionary values are RECALLED (unverified) — see `mexp/tissues.py`; the table shapes the question, it does not yet settle it.**

## Reference acquisition: 32 echoes × 10 ms, first-echo SNR 100

| tissue | visible K (of K) | composition (fraction @ T2 ms) | rel SD of T2 (%) | rel SD of fractions (%) | functional | value | SD (abs) | rel SD (%) | K estimable | functional estimable |
|---|---|---|---|---|---|---|---|---|---|---|
| white matter (brain) | 3 (of 3) | 0.12@15, 0.86@75, 0.02@2000 | 105, 20, 2324 | 62, 5, 408 | myelin water fraction (mass below 40 ms) | 0.120 | 0.076 | 63 | no | no |
| cortical grey matter (brain) | 3 (of 3) | 0.03@15, 0.94@90, 0.03@2000 | 403, 22, 2302 | 209, 7, 442 | myelin water fraction (mass below 40 ms) | 0.030 | 0.063 | 210 | no | no |
| white matter (dorsal/lateral columns) (spinal cord) | 3 (of 3) | 0.25@15, 0.72@80, 0.03@2000 | 46, 24, 1653 | 26, 6, 299 | myelin water fraction (mass below 40 ms) | 0.250 | 0.068 | 27 | no | no |
| skeletal muscle (calf/thigh) (musculoskeletal) | 2 (of 3) | 0.89@33, 0.11@130 | 6, 26 | 4, 41 | extracellular fraction (mass above 60 ms, i.e. 1 - mass below 60 ms) | 0.105 | 0.042 | 40 | no | no |
| articular cartilage (knee) | 2 (of 3) | 0.21@25, 0.79@90 | 31, 4 | 21, 7 | short/intermediate fraction (mass below 45 ms) | 0.211 | 0.046 | 22 | no | no |
| peripheral zone, normal (prostate) | 2 (of 2) | 0.65@60, 0.35@500 | 8, 19 | 5, 11 | luminal water fraction (1 - mass below 200 ms) | 0.350 | 0.037 | 11 | yes | no |
| fibroglandular tissue with fat partial volume (breast) | 2 (of 2) | 0.60@50, 0.40@100 | 25, 28 | 56, 86 | fat fraction (1 - mass below 75 ms) | 0.400 | 0.341 | 85 | no | no |
| left-ventricular myocardium (heart) | 1 (of 1) | 1.00@48 | 1 | 1 | T2 (mono-exponential) | — | — | — | yes | — |
| parenchyma (normal iron) (liver) | 2 (of 2) | 0.90@45, 0.10@200 | 6, 35 | 4, 45 | long-T2 fraction (1 - mass below 100 ms) | 0.100 | 0.044 | 44 | no | no |

## Entry-specific typical acquisition

| tissue | visible K (of K) | composition (fraction @ T2 ms) | rel SD of T2 (%) | rel SD of fractions (%) | functional | value | SD (abs) | rel SD (%) | K estimable | functional estimable |
|---|---|---|---|---|---|---|---|---|---|---|
| white matter (brain) (32×10 ms, SNR 100) | 3 (of 3) | 0.12@15, 0.86@75, 0.02@2000 | 105, 20, 2324 | 62, 5, 408 | myelin water fraction (mass below 40 ms) | 0.120 | 0.076 | 63 | no | no |
| cortical grey matter (brain) (32×10 ms, SNR 100) | 3 (of 3) | 0.03@15, 0.94@90, 0.03@2000 | 403, 22, 2302 | 209, 7, 442 | myelin water fraction (mass below 40 ms) | 0.030 | 0.063 | 210 | no | no |
| white matter (dorsal/lateral columns) (spinal cord) (32×10 ms, SNR 100) | 3 (of 3) | 0.25@15, 0.72@80, 0.03@2000 | 46, 24, 1653 | 26, 6, 299 | myelin water fraction (mass below 40 ms) | 0.250 | 0.068 | 27 | no | no |
| skeletal muscle (calf/thigh) (musculoskeletal) (32×10 ms, SNR 100) | 2 (of 3) | 0.89@33, 0.11@130 | 6, 26 | 4, 41 | extracellular fraction (mass above 60 ms, i.e. 1 - mass below 60 ms) | 0.105 | 0.042 | 40 | no | no |
| articular cartilage (knee) (32×6 ms, SNR 100) | 2 (of 3) | 0.21@25, 0.79@90 | 30, 5 | 27, 8 | short/intermediate fraction (mass below 45 ms) | 0.211 | 0.059 | 28 | no | no |
| peripheral zone, normal (prostate) (64×8 ms, SNR 80) | 2 (of 2) | 0.65@60, 0.35@500 | 5, 7 | 3, 5 | luminal water fraction (1 - mass below 200 ms) | 0.350 | 0.017 | 5 | yes | yes |
| fibroglandular tissue with fat partial volume (breast) (32×10 ms, SNR 100) | 2 (of 2) | 0.60@50, 0.40@100 | 25, 28 | 56, 86 | fat fraction (1 - mass below 75 ms) | 0.400 | 0.341 | 85 | no | no |
| left-ventricular myocardium (heart) (8×12 ms, SNR 60) | 1 (of 1) | 1.00@48 | 3 | 2 | T2 (mono-exponential) | — | — | — | yes | — |
| parenchyma (normal iron) (liver) (16×8 ms, SNR 60) | 2 (of 2) | 0.90@45, 0.10@200 | 39, 571 | 55, 517 | long-T2 fraction (1 - mass below 100 ms) | 0.100 | 0.515 | 515 | no | no |

## Myelin-type functional under three parameterisations (32 × 10 ms)

| tissue | SNR | MWF | SD, free K = 3 | SD, long T2 fixed | SD, long component dropped (K = 2) | myelin T2 rel SD in the K = 2 model (%) |
|---|---|---|---|---|---|---|
| white matter | 100 | 0.12 | 0.076 | 0.039 | 0.030 | 57 |
| white matter | 300 | 0.12 | 0.025 | 0.013 | 0.010 | 19 |
| cortical grey matter | 100 | 0.03 | 0.063 | 0.036 | 0.033 | 211 |
| cortical grey matter | 300 | 0.03 | 0.021 | 0.012 | 0.011 | 70 |
| white matter (dorsal/lateral columns) | 100 | 0.25 | 0.068 | 0.034 | 0.025 | 25 |
| white matter (dorsal/lateral columns) | 300 | 0.25 | 0.023 | 0.011 | 0.008 | 8 |

## Reading

- At the reference acquisition no myelin-type entry is 'estimable' by either criterion under a free K = 3 model: the free long component (2000 ms, unpinned by a 320 ms window) roughly doubles the bound on the myelin water fraction. With the long component fixed or dropped, the MWF bound is ±0.030 (1σ) for white matter at SNR 100 and ±0.010 at SNR 300 — the familiar experience that myelin water imaging needs high SNR or averaging, now as a bound.
- The functional is better determined than the parameters (white matter MWF 25 % relative vs myelin T2 57 % in the K = 2 model): a first sighting of charter Phase 3's 'estimate functionals, not spectra', at the level of the bound.
- Minor components under ~5 % (grey-matter myelin water, the liver vascular fraction) are the failure cases; well-separated two-component tissues (prostate luminal water, ratio ~8) are estimable, and at their own 64 × 8 ms acquisition the luminal water fraction reaches 5 % relative.
- The entry-specific acquisitions move results mostly through the window (prostate's train reaches 500 ms; the 16 × 8 ms liver train loses the 200 ms component entirely; the 8 × 12 ms myocardial train is a K = 1 null case), consistent with the window rule in charter §1.2.
- Everything here inherits the RECALLED status of the dictionary; the verification pass may move numbers, not the structure of the conclusion, which is set by component ratios and minor-fraction sizes.