# §1.2 threshold over the tissue dictionary

Rician CRLB with σ known, first-echo SNR as stated; components below the first echo dropped and fractions renormalised. 'K estimable' = every visible T2 under 25% relative SD; 'functional estimable' = the entry's clinical functional under 10% relative SD (delta method). The status column is the provenance of the component set (`mexp/tissue_data.py`): PRIMARY / SECONDARY are read from the literature this project opened; THEORY rows are working configurations for organs with no multi-component study reached (abdominal T2 splits); RECALLED rows are from memory. Rows marked THEORY or RECALLED shape the question, they do not settle it.

## Reference acquisition: 32 echoes × 10 ms, first-echo SNR 100

| tissue | status | visible K (of K) | composition (fraction @ T2 ms) | rel SD of T2 (%) | rel SD of fractions (%) | functional | value | SD (abs) | rel SD (%) | K estimable | functional estimable |
|---|---|---|---|---|---|---|---|---|---|---|---|
| white matter (brain) | PRIMARY | 3 (of 3) | 0.11@15, 0.87@77, 0.02@2000 | 111, 20, 2452 | 64, 5, 436 | myelin water fraction (mass below 40 ms) | 0.113 | 0.074 | 65 | no | no |
| cortical grey matter (brain) | PRIMARY | 3 (of 3) | 0.03@15, 0.94@80, 0.03@2000 | 410, 20, 1821 | 230, 5, 330 | myelin water fraction (mass below 40 ms) | 0.031 | 0.072 | 231 | no | no |
| cerebrospinal fluid (ventricular) (brain) | TERTIARY | 1 (of 1) | 1.00@2000 | 4 | 0 | T2 (mono-exponential) | — | — | — | yes | — |
| cervical cord white matter (lateral/dorsal columns) (spinal cord) | PRIMARY | 3 (of 3) | 0.30@20, 0.67@100, 0.03@2000 | 43, 47, 3309 | 38, 14, 688 | myelin water fraction (mass below 40 ms) | 0.296 | 0.117 | 40 | no | no |
| skeletal muscle (calf / forearm / paravertebral) (musculoskeletal) | PRIMARY | 3 (of 4) | 0.33@20.8, 0.54@38.9, 0.13@114.3 | 206, 188, 106 | 662, 346, 279 | extracellular fraction (1 - mass below 60 ms) | 0.133 | 0.369 | 277 | no | no |
| articular (hyaline) cartilage (knee) | PRIMARY | 2 (of 3) | 0.15@25.2, 0.85@96.3 | 40, 3 | 26, 6 | short/intermediate fraction (mass below 45 ms) | 0.155 | 0.041 | 26 | no | no |
| vertebral (red / haematopoietic) bone marrow (bone) | SECONDARY | 2 (of 2) | 0.67@45, 0.33@130 | 11, 15 | 14, 31 | fat fraction (1 - mass below 75 ms) | 0.330 | 0.099 | 30 | yes | no |
| left-ventricular myocardium (heart) | SECONDARY | 1 (of 1) | 1.00@48 | 1 | 1 | T2 (mono-exponential) | — | — | — | yes | — |
| arterial blood (Hct ~ 0.42, Y ~ 0.98) (vascular) | SECONDARY | 1 (of 1) | 1.00@250 | 1 | 0 | T2 (mono-exponential; oxygenation via Luz-Meiboom) | — | — | — | yes | — |
| parenchyma (normal iron, no steatosis) (liver) | THEORY | 2 (of 2) | 0.78@42, 0.22@150 | 7, 17 | 7, 27 | vascular/long-T2 fraction (1 - mass below 90 ms) | 0.220 | 0.059 | 27 | yes | no |
| splenic parenchyma (spleen) | THEORY | 2 (of 2) | 0.65@65, 0.35@130 | 27, 42 | 66, 125 | blood/long-T2 fraction (1 - mass below 95 ms) | 0.350 | 0.436 | 125 | no | no |
| renal cortex (kidney) | THEORY | 2 (of 2) | 0.75@70, 0.25@200 | 15, 40 | 23, 71 | tubular/vascular long-T2 fraction (1 - mass below 120 ms) | 0.250 | 0.176 | 70 | no | no |
| renal medulla (kidney) | THEORY | 2 (of 2) | 0.70@75, 0.30@220 | 16, 37 | 26, 63 | luminal/vascular long-T2 fraction (1 - mass below 120 ms) | 0.300 | 0.187 | 62 | no | no |
| pancreatic parenchyma (pancreas) | THEORY | 2 (of 2) | 0.78@45, 0.22@160 | 8, 18 | 7, 30 | vascular/long-T2 fraction (1 - mass below 90 ms) | 0.220 | 0.063 | 29 | yes | no |
| peripheral zone, normal (prostate) | PRIMARY | 2 (of 2) | 0.76@90, 0.24@545 | 12, 65 | 13, 44 | luminal water fraction (1 - mass below 200 ms) | 0.240 | 0.105 | 44 | no | no |
| fibroglandular tissue (with fat partial volume) (breast) | SECONDARY | 2 (of 2) | 0.60@57, 0.40@110 | 29, 34 | 72, 110 | fat fraction (1 - mass below 80 ms) | 0.400 | 0.437 | 109 | no | no |
| subcutaneous white adipose tissue (adipose) | THEORY | 2 (of 2) | 0.10@40, 0.90@140 | 66, 4 | 60, 7 | water fraction (mass below 75 ms) | 0.100 | 0.060 | 60 | no | no |

## Entry-specific typical acquisition

| tissue | status | visible K (of K) | composition (fraction @ T2 ms) | rel SD of T2 (%) | rel SD of fractions (%) | functional | value | SD (abs) | rel SD (%) | K estimable | functional estimable |
|---|---|---|---|---|---|---|---|---|---|---|---|
| white matter (brain) (32×10 ms, SNR 100) | PRIMARY | 3 (of 3) | 0.11@15, 0.87@77, 0.02@2000 | 111, 20, 2452 | 64, 5, 436 | myelin water fraction (mass below 40 ms) | 0.113 | 0.074 | 65 | no | no |
| cortical grey matter (brain) (32×10 ms, SNR 100) | PRIMARY | 3 (of 3) | 0.03@15, 0.94@80, 0.03@2000 | 410, 20, 1821 | 230, 5, 330 | myelin water fraction (mass below 40 ms) | 0.031 | 0.072 | 231 | no | no |
| cerebrospinal fluid (ventricular) (brain) (32×10 ms, SNR 100) | TERTIARY | 1 (of 1) | 1.00@2000 | 4 | 0 | T2 (mono-exponential) | — | — | — | yes | — |
| cervical cord white matter (lateral/dorsal columns) (spinal cord) (32×10 ms, SNR 100) | PRIMARY | 3 (of 3) | 0.30@20, 0.67@100, 0.03@2000 | 43, 47, 3309 | 38, 14, 688 | myelin water fraction (mass below 40 ms) | 0.296 | 0.117 | 40 | no | no |
| skeletal muscle (calf / forearm / paravertebral) (musculoskeletal) (32×10 ms, SNR 100) | PRIMARY | 3 (of 4) | 0.33@20.8, 0.54@38.9, 0.13@114.3 | 206, 188, 106 | 662, 346, 279 | extracellular fraction (1 - mass below 60 ms) | 0.133 | 0.369 | 277 | no | no |
| articular (hyaline) cartilage (knee) (32×6 ms, SNR 100) | PRIMARY | 2 (of 3) | 0.15@25.2, 0.85@96.3 | 40, 5 | 34, 7 | short/intermediate fraction (mass below 45 ms) | 0.155 | 0.053 | 34 | no | no |
| vertebral (red / haematopoietic) bone marrow (bone) (32×10 ms, SNR 100) | SECONDARY | 2 (of 2) | 0.67@45, 0.33@130 | 11, 15 | 14, 31 | fat fraction (1 - mass below 75 ms) | 0.330 | 0.099 | 30 | yes | no |
| left-ventricular myocardium (heart) (8×12 ms, SNR 60) | SECONDARY | 1 (of 1) | 1.00@48 | 3 | 2 | T2 (mono-exponential) | — | — | — | yes | — |
| arterial blood (Hct ~ 0.42, Y ~ 0.98) (vascular) (32×10 ms, SNR 60) | SECONDARY | 1 (of 1) | 1.00@250 | 2 | 1 | T2 (mono-exponential; oxygenation via Luz-Meiboom) | — | — | — | yes | — |
| parenchyma (normal iron, no steatosis) (liver) (16×8 ms, SNR 60) | THEORY | 2 (of 2) | 0.78@42, 0.22@150 | 47, 223 | 73, 268 | vascular/long-T2 fraction (1 - mass below 90 ms) | 0.220 | 0.586 | 266 | no | no |
| splenic parenchyma (spleen) (16×8 ms, SNR 60) | THEORY | 2 (of 2) | 0.65@65, 0.35@130 | 275, 644 | 858, 1599 | blood/long-T2 fraction (1 - mass below 95 ms) | 0.350 | 5.590 | 1597 | no | no |
| renal cortex (kidney) (16×8 ms, SNR 60) | THEORY | 2 (of 2) | 0.75@70, 0.25@200 | 164, 796 | 369, 1115 | tubular/vascular long-T2 fraction (1 - mass below 120 ms) | 0.250 | 2.783 | 1113 | no | no |
| renal medulla (kidney) (16×8 ms, SNR 50) | THEORY | 2 (of 2) | 0.70@75, 0.30@220 | 240, 953 | 541, 1269 | luminal/vascular long-T2 fraction (1 - mass below 120 ms) | 0.300 | 3.799 | 1266 | no | no |
| pancreatic parenchyma (pancreas) (16×8 ms, SNR 50) | THEORY | 2 (of 2) | 0.78@45, 0.22@160 | 64, 319 | 104, 378 | vascular/long-T2 fraction (1 - mass below 90 ms) | 0.220 | 0.826 | 375 | no | no |
| peripheral zone, normal (prostate) (64×25 ms, SNR 100) | PRIMARY | 2 (of 2) | 0.76@90, 0.24@545 | 4, 5 | 2, 6 | luminal water fraction (1 - mass below 200 ms) | 0.240 | 0.013 | 5 | yes | yes |
| fibroglandular tissue (with fat partial volume) (breast) (32×10 ms, SNR 100) | SECONDARY | 2 (of 2) | 0.60@57, 0.40@110 | 29, 34 | 72, 110 | fat fraction (1 - mass below 80 ms) | 0.400 | 0.437 | 109 | no | no |
| subcutaneous white adipose tissue (adipose) (32×10 ms, SNR 100) | THEORY | 2 (of 2) | 0.10@40, 0.90@140 | 66, 4 | 60, 7 | water fraction (mass below 75 ms) | 0.100 | 0.060 | 60 | no | no |

## Myelin-type functional under three parameterisations (32 × 10 ms)

| tissue | SNR | MWF | SD, free K = 3 | SD, long T2 fixed | SD, long component dropped (K = 2) | myelin T2 rel SD in the K = 2 model (%) |
|---|---|---|---|---|---|---|
| white matter | 100 | 0.11 | 0.074 | 0.038 | 0.030 | 60 |
| white matter | 300 | 0.11 | 0.024 | 0.013 | 0.010 | 20 |
| cortical grey matter | 100 | 0.03 | 0.072 | 0.039 | 0.033 | 219 |
| cortical grey matter | 300 | 0.03 | 0.024 | 0.013 | 0.011 | 73 |
| cervical cord white matter (lateral/dorsal columns) | 100 | 0.30 | 0.117 | 0.045 | 0.024 | 18 |
| cervical cord white matter (lateral/dorsal columns) | 300 | 0.30 | 0.039 | 0.015 | 0.008 | 6 |

## Reading (dictionary v2.2 — the priority-1 primaries applied; class changes against v2.1 are marked)

- At the reference acquisition no myelin-type entry is 'estimable' by either criterion under a free K = 3 model: the free long component (2000 ms, unpinned by a 320 ms window) roughly doubles the bound on the myelin water fraction (white matter: 0.074 free vs 0.038 with the long T2 fixed vs 0.030 with it dropped, at SNR 100, for the Whittall 1997 MWF of 0.113). With the long component fixed or dropped the white-matter MWF bound is about ±0.03 (1σ) at SNR 100 and ±0.01 at SNR 300 — the familiar experience that myelin water imaging needs high SNR or averaging, now as a bound. **Class change (cord):** with MacMillan 2011's MWF 0.296 and IE T2 100 ms the cervical cord under the K = 2 model is estimable at SNR 100 on both criteria (myelin T2 18 % relative, MWF 0.296 ± 0.024, i.e. 8 %), where the v2.1 numbers (0.23 at 20 ms, IE 75 ms) gave 29 % and 18 %; it stays unestimable under the free K = 3 model.
- The functional is better determined than the parameters (white matter MWF ~27 % relative vs myelin T2 60 % in the K = 2 model at SNR 100): a first sighting of charter Phase 3's 'estimate functionals, not spectra', at the level of the bound.
- Minor components under ~5 % (grey-matter myelin water, 3.1 % in Whittall 1997) fail outright; muscle's four-component structure (Saab 1999 Table 1, measured at SNR ~3200 with 1.2 ms echoes at 1.89 T) collapses to an unestimable three-component fit at clinical SNR — the clinical protocol sees one ~30 ms pool and, at best, the ~115-160 ms vascular/extracellular tail (Saab's 11 %, Araujo 2014's 8 % at 3 T); well-separated two-component tissues (prostate luminal water, Sabouri 2017: 0.24 at 545 ms against 0.76 at 90 ms, ratio ~6) are estimable to ~5 % relative on the LWF at their own 64 × 25 ms train. **Class change (prostate):** at the *reference* 32 × 10 ms train the prostate row is no longer 'K estimable' (long T2 65 % relative, LWF 0.24 ± 0.105) — the 545 ms component is unpinned by a 320 ms window, and the v2.1 row (0.35 at 500 ms, 'yes') rested on a recalled fraction that was too large; Sabouri's own protocol, with its 1600 ms window, is what makes luminal water imaging work, which is the window rule of charter §1.2 in a clinical protocol.
- The abdominal THEORY rows (liver, pancreas: ratio ~3.5, minor fraction ~0.2) come out 'K estimable' at the reference acquisition but not at their own shorter, noisier protocols; spleen and kidney (ratio ~2-3) are not estimable anywhere. These rows test whether T2 can see the vascular compartment that IVIM sees; the physics (fast exchange) says it mostly cannot.
- The entry-specific acquisitions move results mostly through the window (prostate's train reaches 1600 ms; the 16 × 8 ms abdominal trains lose the 150-220 ms components; the 8 × 12 ms myocardial train is a K = 1 null case), consistent with the window rule in charter §1.2.
- The adipose row (v2.1) is a 90/10 fat/water mixture at ratio 3.5: the 10 % water fraction is not estimable at the reference acquisition (relative SD ~ 60 %) even under the pure-exponential model the row is known to violate (J-coupled, chemically shifted fat) — so it fails twice, once by information and once by model, which is why it is the misspecification row and not a K test.
- Provenance: the brain, cord, muscle, cartilage, bone, tendon and prostate component sets rest on the papers' own tables (PRIMARY, v2.2); marrow, breast and blood on opened secondary sources; the abdominal T2 splits (liver, spleen, kidney, pancreas) are THEORY rows built from bulk T2 and IVIM perfusion fractions because no in vivo multi-component T2 study of those organs was reached; no RECALLED component set remains. Verification moved numbers and two classes (cord under K = 2 up, prostate at the reference train down); the structure of the conclusion, set by ratios and minor-fraction sizes, stands.