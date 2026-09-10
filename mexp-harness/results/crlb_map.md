# CRLB map over the tissue dictionary

Rician CRLB, σ known unless stated, first-echo SNR convention, components below the first echo dropped and fractions renormalised. For each row: the first-echo SNR at the reference 32 × 10 ms train at which the row crosses each of the three §1.2 labels (25 % on every visible T2; 10 % relative on the functional; SD ≤ |Δ|/3 with Δ the recorded clinical change), by log–log interpolation on the SNR grid 20–3000; and the echo count at 10 ms spacing (window = N × 10 ms) at SNR 100 at which it crosses them. '> 3000' means the label is not reached on the grid; '—' means the row has no functional or no recorded Δ. Rows with a > 1 s component are shown twice: free, and with that component's T2 fixed ('constrained'), because the unpinned long component is what decides the myelin rows (results/threshold_tissues.md). No noise realisation is drawn; no estimator is used.

## 1. SNR at which each row crosses the labels (32 × 10 ms)

| tissue | condition | K vis. | functional | value | Δ | SNR for K (25 %) | SNR for functional (10 %) | SNR for clinical (\|Δ\|/3) | SD at SNR 100 | SD at SNR 300 |
|---|---|---|---|---|---|---|---|---|---|---|
| white matter | normal | 3 | myelin water fraction (mass below 40 ms) | 0.113 | -0.060 | > 3000 | 650 | 364 | 0.074 | 0.024 |
| white matter (constrained: long T2 fixed) | normal | 3 | myelin water fraction (mass below 40 ms) | 0.113 | -0.060 | 306 | 335 | 188 | 0.038 | 0.013 |
| cortical grey matter | normal | 3 | myelin water fraction (mass below 40 ms) | 0.031 | — | > 3000 | 2303 | — | 0.072 | 0.024 |
| cortical grey matter (constrained: long T2 fixed) | normal | 3 | myelin water fraction (mass below 40 ms) | 0.031 | — | 1132 | 1256 | — | 0.039 | 0.013 |
| cerebrospinal fluid (ventricular) | normal | 1 | — | — | — | ≤ 20 | — | — | — | — |
| cervical cord white matter (lateral/dorsal columns) | normal | 3 | myelin water fraction (mass below 40 ms) | 0.296 | -0.030 | > 3000 | 395 | 1150 | 0.117 | 0.039 |
| cervical cord white matter (lateral/dorsal columns) (constrained: long T2 fixed) | normal | 3 | myelin water fraction (mass below 40 ms) | 0.296 | -0.030 | 102 | 152 | 442 | 0.045 | 0.015 |
| skeletal muscle (calf / forearm / paravertebral) | normal | 3 | extracellular fraction (1 - mass below 60 ms) | 0.133 | +0.062 | 792 | 2531 | 1631 | 0.369 | 0.113 |
| articular (hyaline) cartilage | normal | 2 | short/intermediate fraction (mass below 45 ms) | 0.155 | — | 161 | 262 | — | 0.041 | 0.013 |
| vertebral (red / haematopoietic) bone marrow | normal | 2 | fat fraction (1 - mass below 75 ms) | 0.330 | — | 63 | 298 | — | 0.099 | 0.033 |
| left-ventricular myocardium | normal | 1 | — | — | — | ≤ 20 | — | — | — | — |
| arterial blood (Hct ~ 0.42, Y ~ 0.98) | normal | 1 | — | — | — | ≤ 20 | — | — | — | — |
| parenchyma (normal iron, no steatosis) | normal | 2 | vascular/long-T2 fraction (1 - mass below 90 ms) | 0.220 | — | 68 | 265 | — | 0.059 | 0.019 |
| splenic parenchyma | normal | 2 | blood/long-T2 fraction (1 - mass below 95 ms) | 0.350 | — | 168 | 1241 | — | 0.436 | 0.145 |
| renal cortex | normal | 2 | tubular/vascular long-T2 fraction (1 - mass below 120 ms) | 0.250 | — | 159 | 701 | — | 0.176 | 0.058 |
| renal medulla | normal | 2 | luminal/vascular long-T2 fraction (1 - mass below 120 ms) | 0.300 | — | 149 | 622 | — | 0.187 | 0.062 |
| pancreatic parenchyma | normal | 2 | vascular/long-T2 fraction (1 - mass below 90 ms) | 0.220 | — | 74 | 286 | — | 0.063 | 0.021 |
| peripheral zone, normal | normal | 2 | luminal water fraction (1 - mass below 200 ms) | 0.240 | -0.140 | 258 | 436 | 224 | 0.105 | 0.035 |
| fibroglandular tissue (with fat partial volume) | normal | 2 | fat fraction (1 - mass below 80 ms) | 0.400 | — | 136 | 1083 | — | 0.437 | 0.145 |
| subcutaneous white adipose tissue | normal | 2 | water fraction (mass below 75 ms) | 0.100 | — | 262 | 601 | — | 0.060 | 0.020 |
| parenchyma, hepatic steatosis at PDFF 10 % (histologic grade 1) | hepatic steatosis, grade 1 | 2 | fat fraction (1 - mass below 55 ms) | 0.100 | +0.081 | 351 | 2490 | 933 | 0.339 | 0.091 |
| parenchyma, hepatic steatosis at PDFF 25 % (histologic grade 3) | hepatic steatosis, grade 3 | 2 | fat fraction (1 - mass below 55 ms) | 0.250 | +0.231 | 145 | 1013 | 335 | 0.293 | 0.086 |
| peripheral zone, prostate cancer (malignant PZ) | prostate cancer, peripheral zone | 2 | luminal water fraction (1 - mass below 200 ms) | 0.100 | -0.140 | 487 | 766 | 164 | 0.077 | 0.026 |
| skeletal muscle (soleus) under venous filling - oedema surrogate | venous filling (vascular compartment expanded) | 2 | extracellular / vascular fraction (1 - mass below 60 ms) | 0.142 | +0.062 | 61 | 165 | 113 | 0.023 | 0.008 |
| white matter, chronic multiple-sclerosis lesion (demyelinated) | multiple sclerosis lesion (chronic, demyelinated) | 3 | myelin water fraction (mass below 40 ms) | 0.052 | -0.060 | > 3000 | 1080 | 281 | 0.057 | 0.019 |
| white matter, chronic multiple-sclerosis lesion (demyelinated) (constrained: long T2 fixed) | multiple sclerosis lesion (chronic, demyelinated) | 3 | myelin water fraction (mass below 40 ms) | 0.052 | -0.060 | 600 | 653 | 170 | 0.034 | 0.011 |

## 2. Echo count (window) at which each row crosses the labels (ΔTE 10 ms, first-echo SNR 100)

| tissue | condition | K vis. | N for K (25 %) | N for functional (10 %) | N for clinical (\|Δ\|/3) | functional SD at N = 8 / 32 / 128 / 256 |
|---|---|---|---|---|---|---|
| white matter | normal | 3 | > 256 | > 256 | > 256 | ∞ / 0.074 / 0.033 / 0.032 |
| white matter (constrained: long T2 fixed) | normal | 3 | > 256 | > 256 | > 256 | 0.810 / 0.038 / 0.031 / 0.031 |
| cortical grey matter | normal | 3 | > 256 | > 256 | — | ∞ / 0.072 / 0.035 / 0.034 |
| cortical grey matter (constrained: long T2 fixed) | normal | 3 | > 256 | > 256 | — | 0.806 / 0.039 / 0.033 / 0.033 |
| cerebrospinal fluid (ventricular) | normal | 1 | 12 | — | — | — |
| cervical cord white matter (lateral/dorsal columns) | normal | 3 | 192 | 128 | > 256 | ∞ / 0.117 / 0.028 / 0.025 |
| cervical cord white matter (lateral/dorsal columns) (constrained: long T2 fixed) | normal | 3 | 48 | 64 | > 256 | 1.751 / 0.045 / 0.024 / 0.023 |
| skeletal muscle (calf / forearm / paravertebral) | normal | 3 | > 256 | > 256 | > 256 | 105.054 / 0.369 / 0.267 / 0.267 |
| articular (hyaline) cartilage | normal | 2 | > 256 | > 256 | — | 0.469 / 0.041 / 0.037 / 0.037 |
| vertebral (red / haematopoietic) bone marrow | normal | 2 | 32 | > 256 | — | 2.602 / 0.099 / 0.070 / 0.070 |
| left-ventricular myocardium | normal | 1 | 8 | — | — | — |
| arterial blood (Hct ~ 0.42, Y ~ 0.98) | normal | 1 | 8 | — | — | — |
| parenchyma (normal iron, no steatosis) | normal | 2 | 32 | > 256 | — | 1.549 / 0.059 / 0.040 / 0.040 |
| splenic parenchyma | normal | 2 | 64 | > 256 | — | 15.991 / 0.436 / 0.257 / 0.257 |
| renal cortex | normal | 2 | 48 | > 256 | — | 8.359 / 0.176 / 0.063 / 0.063 |
| renal medulla | normal | 2 | 48 | > 256 | — | 9.681 / 0.187 / 0.055 / 0.055 |
| pancreatic parenchyma | normal | 2 | 32 | > 256 | — | 1.861 / 0.063 / 0.039 / 0.039 |
| peripheral zone, normal | normal | 2 | 48 | 64 | 48 | 7.475 / 0.105 / 0.010 / 0.009 |
| fibroglandular tissue (with fat partial volume) | normal | 2 | 48 | > 256 | — | 12.874 / 0.437 / 0.318 / 0.318 |
| subcutaneous white adipose tissue | normal | 2 | > 256 | > 256 | — | 1.567 / 0.060 / 0.040 / 0.040 |
| parenchyma, hepatic steatosis at PDFF 10 % (histologic grade 1) | hepatic steatosis, grade 1 | 2 | > 256 | > 256 | > 256 | 3.282 / 0.339 / 0.338 / 0.338 |
| parenchyma, hepatic steatosis at PDFF 25 % (histologic grade 3) | hepatic steatosis, grade 3 | 2 | > 256 | > 256 | > 256 | 3.352 / 0.293 / 0.290 / 0.290 |
| peripheral zone, prostate cancer (malignant PZ) | prostate cancer, peripheral zone | 2 | 64 | 128 | 48 | 5.127 / 0.077 / 0.009 / 0.009 |
| skeletal muscle (soleus) under venous filling - oedema surrogate | venous filling (vascular compartment expanded) | 2 | 24 | > 256 | 48 | 0.505 / 0.023 / 0.016 / 0.016 |
| white matter, chronic multiple-sclerosis lesion (demyelinated) | multiple sclerosis lesion (chronic, demyelinated) | 3 | > 256 | > 256 | > 256 | ∞ / 0.057 / 0.032 / 0.032 |
| white matter, chronic multiple-sclerosis lesion (demyelinated) (constrained: long T2 fixed) | multiple sclerosis lesion (chronic, demyelinated) | 3 | > 256 | > 256 | > 256 | 0.680 / 0.034 / 0.032 / 0.032 |

## 3. Data-representation arm and noise-knowledge rung (32 × 10 ms, SNR 100): functional SD

| tissue | condition | Gaussian real (phase-corrected), σ known | Rician, σ known | Rician, σ joint | Rician joint / known | Rician / Gaussian |
|---|---|---|---|---|---|---|
| white matter | normal | 0.0734 | 0.0737 | 0.0737 | 1.000 | 1.003 |
| cortical grey matter | normal | 0.0714 | 0.0715 | 0.0715 | 1.000 | 1.002 |
| cervical cord white matter (lateral/dorsal columns) | normal | 0.1169 | 0.1171 | 0.1171 | 1.000 | 1.001 |
| skeletal muscle (calf / forearm / paravertebral) | normal | 0.3370 | 0.3688 | 0.3748 | 1.016 | 1.094 |
| articular (hyaline) cartilage | normal | 0.0405 | 0.0406 | 0.0407 | 1.001 | 1.004 |
| vertebral (red / haematopoietic) bone marrow | normal | 0.0983 | 0.0990 | 0.0991 | 1.001 | 1.007 |
| parenchyma (normal iron, no steatosis) | normal | 0.0583 | 0.0587 | 0.0588 | 1.001 | 1.008 |
| splenic parenchyma | normal | 0.4343 | 0.4365 | 0.4367 | 1.001 | 1.005 |
| renal cortex | normal | 0.1753 | 0.1757 | 0.1757 | 1.000 | 1.002 |
| renal medulla | normal | 0.1867 | 0.1869 | 0.1869 | 1.000 | 1.001 |
| pancreatic parenchyma | normal | 0.0629 | 0.0633 | 0.0634 | 1.001 | 1.006 |
| peripheral zone, normal | normal | 0.1046 | 0.1046 | 0.1046 | 1.000 | 1.000 |
| fibroglandular tissue (with fat partial volume) | normal | 0.4331 | 0.4374 | 0.4381 | 1.002 | 1.010 |
| subcutaneous white adipose tissue | normal | 0.0601 | 0.0602 | 0.0602 | 1.000 | 1.001 |
| parenchyma, hepatic steatosis at PDFF 10 % (histologic grade 1) | hepatic steatosis, grade 1 | 0.2485 | 0.3392 | 0.3724 | 1.098 | 1.365 |
| parenchyma, hepatic steatosis at PDFF 25 % (histologic grade 3) | hepatic steatosis, grade 3 | 0.2526 | 0.2934 | 0.3111 | 1.060 | 1.161 |
| peripheral zone, prostate cancer (malignant PZ) | prostate cancer, peripheral zone | 0.0766 | 0.0767 | 0.0767 | 1.000 | 1.001 |
| skeletal muscle (soleus) under venous filling - oedema surrogate | venous filling (vascular compartment expanded) | 0.0233 | 0.0235 | 0.0235 | 1.001 | 1.009 |
| white matter, chronic multiple-sclerosis lesion (demyelinated) | multiple sclerosis lesion (chronic, demyelinated) | 0.0567 | 0.0568 | 0.0568 | 1.000 | 1.001 |

The complex arm is not tabulated: for the real-valued T2 kernel its Fisher information equals the phase-corrected real arm's (`gaussian_complex` reduces to `gaussian_real` when the Jacobian is real), so the value of phase is zero by construction here and is a question for the complex T2* kernel (charter §2.3), which is not registered (G2).

## 4. Reading

- **SNR is the myelin axis; the window is the prostate axis.** White matter's MWF bound at 32 × 10 ms falls as 1/SNR and saturates against the window only above N ≈ 128: the demyelination change (|Δ|/3 = 0.020) is a 3σ event above first-echo SNR ≈ 360 under a free K = 3 model and ≈ 190 with the CSF-like T2 fixed, while no echo count at SNR 100 reaches it (the floor is 0.031–0.033 at N ≥ 128, set by the first few echoes that carry the 15 ms component). The prostate is the converse: at SNR 100 the luminal water fraction crosses the clinical label at N = 48 (window 480 ms) and the 10 % label at N = 64, and at 32 echoes it needs SNR ≈ 220 (normal) / 160 (cancer) — the window rule of §1.2 as a design statement.
- **The labels order the tissues the same way, but the clinical label moves the boundary.** For the prostate rows the clinical label (Δ = −0.14) is reached at roughly half the SNR of the 10 % label (224 vs 436 normal; 164 vs 766 cancer); for white matter it is reached earlier than the 10 % label too (364 vs 650), because a 30 % relative change on a small functional is a wide interval in absolute terms; for the cord the age change is small (Δ = −0.03) and the clinical label is the hardest of the three (SNR 1150 free, 440 constrained). A per-tissue criterion re-orders what 'estimable' means, which is why v0.14 scheduled it.
- **Amplitude vector at fixed ratio.** Prostate cancer (LWF 0.24 → 0.10 at the same T2 pair) roughly doubles the SNR needed for 'K' and for the 10 % label but *lowers* it for the clinical label (164 vs 224), because |Δ| is the same while the bound on a smaller fraction is smaller in absolute terms. The muscle pair (0.08 → 0.14 vascular fraction at ratio 5.5) is the easy oedema case: the venous-filled row crosses the clinical label at SNR ≈ 110 or N = 48.
- **Steatosis on the T2 axis is where the Rician floor and the σ nuisance first cost something.** Water at 36 ms decays to the noise floor within the 320 ms window, so the fat rows are the only dictionary rows for which the magnitude arm costs 16–37 % over the phase-corrected arm and joint σ costs 6–10 % (§3.2's bound-level probe found < 2 % elsewhere, and the map confirms that everywhere the signal stays above the floor). Even so the fat fraction needs SNR ≈ 900 (10 %) / 340 (25 %) to be a 3σ change and no window helps (ratio 2): the wrong-tool verdict of results/threshold_tissues.md, in SNR units.
- **What the map does not contain.** The complex arm (value of phase) needs the T2* kernel; other spacings than 10 ms and other placements are the sampling-design study (§6.1); the χ, g-factor and CS rungs of the noise ladder need the k-space-first simulator (E2). Each is a column to add to this table, not a new table.

