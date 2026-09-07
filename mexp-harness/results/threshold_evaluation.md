# §1.2 falsifiable threshold — evaluation at the reference clinical configuration

Configuration: 32 echoes, ΔTE = 10 ms (t ∈ [10, 320] ms), T2 support [10, 300] ms (Γ = 30), first-echo SNR 100, Rician magnitude with σ known (joint-σ and Gaussian shown for comparison). No noise realisations; SNR enters as σ = S(t₁)/SNR.

## UP-1 / DOWN-1 — singular-value count

| column normalisation of the discretised kernel | σᵢ/σ₁ (i = 1..6) | count, SNR 50 | count, SNR 100 | count, SNR 200 |
|---|---|---|---|---|
| log-uniform grid, unweighted (≡ L²(d ln T)) | 1, 0.2724, 0.08412, 0.02422, 0.006291, 0.001479 | 4 | 4 | 5 |
| L²(dT) column weights | 1, 0.1784, 0.04494, 0.01202, 0.003035, 0.0006998 | 3 | 4 | 4 |
| L²(d ln T / T) column weights | 1, 0.3767, 0.1264, 0.03794, 0.01016, 0.002451 | 4 | 5 | 5 |

Reading of 'SNR-scaled kernel exceeding unity' used: σᵢ/σ₁ > 1/SNR (the kernel scaled so its leading singular value is SNR). An absolute reading (σᵢ(A) > σ with unit-amplitude columns) gives 7 and is grid-size dependent, so it is not a usable clause.

| truth | Picard count (smoothed) | raw leading run | energy-convention count |
|---|---|---|---|
| K=3 (20, 60, 180) ms, equal amplitudes | 3 | 3 | 5 |
| K=3 (20, 60, 180) ms, 0.2/0.6/0.2 | 4 | 4 | 5 |
| K=2 (20, 80) ms, equal amplitudes | 3 | 4 | 5 |
| K=2 (20, 80) ms, 0.2/0.8 | 4 | 4 | 5 |

**UP-1 fires: True** (count = 4 under the natural normalisation; σ₄/σ₁ = 0.024 vs 1/SNR = 0.010, σ₅/σ₁ = 0.006 — the count is 4 for SNR 42–159 and sits exactly on the clause boundary). **DOWN-1 fires: False.**

## UP-2 — K = 3, adjacent ratio 3: relative SD (%) of the three decay constants

| placement (ms) | amplitudes | Gaussian | Rician, σ known | Rician, σ jointly estimated |
|---|---|---|---|---|
| [15, 45, 135] | equal | 70, 103, 30 | 70, 103, 30 | 70, 103, 30 |
| [15, 45, 135] | 0.2/0.6/0.2 | 120, 59, 51 | 121, 59, 52 | 121, 59, 52 |
| [15, 45, 135] | 0.6/0.2/0.2 | 34, 150, 43 | 34, 151, 44 | 34, 151, 44 |
| [20, 60, 180] | equal | 72, 155, 60 | 72, 156, 60 | 72, 156, 60 |
| [20, 60, 180] | 0.2/0.6/0.2 | 123, 88, 103 | 123, 89, 103 | 123, 89, 103 |
| [20, 60, 180] | 0.6/0.2/0.2 | 36, 234, 91 | 36, 235, 91 | 36, 235, 91 |
| [30, 90, 270] | equal | 102, 399, 230 | 102, 400, 231 | 102, 400, 231 |
| [30, 90, 270] | 0.2/0.6/0.2 | 173, 226, 391 | 173, 226, 391 | 173, 226, 391 |
| [30, 90, 270] | 0.6/0.2/0.2 | 53, 622, 359 | 53, 622, 359 | 53, 622, 359 |

**UP-2 fires: False.** The best single constant reaches 30 %; the best all-three case is 70 / 103 / 30 % — nowhere near 10 %, and most cases exceed 100 % on at least one constant. K = 3 at ratio 3 is not estimable at this configuration.

## DOWN-2 — K = 2, adjacent ratio 4: relative SD (%) of the two decay constants

| placement (ms) | amplitudes | Gaussian | Rician, σ known | Rician, σ jointly estimated | > 25 % on either? |
|---|---|---|---|---|---|
| [15, 60] | equal | 14.1, 5.0 | 14.5, 5.2 | 14.6, 5.3 | no |
| [15, 60] | 0.2/0.8 | 40.6, 3.6 | 41.2, 3.7 | 41.5, 3.7 | yes |
| [15, 60] | 0.8/0.2 | 7.5, 10.6 | 8.0, 12.0 | 8.2, 12.6 | no |
| [20, 80] | equal | 11.9, 4.7 | 12.0, 4.9 | 12.1, 4.9 | no |
| [20, 80] | 0.2/0.8 | 32.9, 3.3 | 33.1, 3.3 | 33.2, 3.4 | yes |
| [20, 80] | 0.8/0.2 | 6.6, 10.5 | 6.9, 11.6 | 7.1, 12.3 | no |
| [30, 120] | equal | 10.6, 5.2 | 10.6, 5.2 | 10.6, 5.3 | no |
| [30, 120] | 0.2/0.8 | 28.4, 3.5 | 28.4, 3.5 | 28.4, 3.5 | yes |
| [30, 120] | 0.8/0.2 | 6.1, 12.1 | 6.2, 12.4 | 6.2, 12.6 | no |
| [50, 200] | equal | 12.2, 9.2 | 12.3, 9.2 | 12.3, 9.2 | no |
| [50, 200] | 0.2/0.8 | 32.0, 6.0 | 32.0, 6.0 | 32.0, 6.0 | yes |
| [50, 200] | 0.8/0.2 | 7.3, 21.9 | 7.3, 22.0 | 7.3, 22.0 | no |

**DOWN-2 fires in 4 of 12 placement × amplitude cases** — never for equal amplitudes, always when the short component carries 20 % of the signal (its T2 then has 30–40 % relative SD). The clause's outcome is decided by the amplitude vector, which the charter does not specify.

## §1.2 closed forms against the numerical count (Γ = 30 = in-window range; window γ_t = 32)

| SNR | R_min, charter exp(π²/2 ln SNR) | R_min, arccosh form | K_max, charter 1 + 2 ln SNR ln Γ/π² | (ln Γ/π²)·arccosh(SNR²) + 1 | numerical count | γ^(1/count) |
|---|---|---|---|---|---|---|
| 30 | 4.27 | 3.73 | 3.34 | 3.58 | 3 | 3.11 |
| 50 | 3.53 | 3.19 | 3.70 | 3.94 | 4 | 2.34 |
| 100 | 2.92 | 2.71 | 4.17 | 4.41 | 4 | 2.34 |
| 200 | 2.54 | 2.40 | 4.65 | 4.89 | 5 | 1.97 |
| 1000 | 2.04 | 1.97 | 5.76 | 6.00 | 6 | 1.76 |

Both closed forms reproduce the numerical count to within ±0.8 at this configuration. They cannot be told apart by the count (the O(ln 2) difference in ω_max is 0.24 of a singular value here); the arccosh form is the one that follows from the Mellin gain without approximation, and the charter's form is its 2 ln SNR ≫ ln 2 limit. Neither is a per-index prediction: individual singular values do not follow uniform Mellin quantisation (σ₁/σ₀ ≈ 0.33 numerically for every covering-window γ ≥ 100, against 0.48–0.78 predicted), so the Epstein–Schotland / McWhirter–Pike closed form is a check on the *count and decay rate*, not on σᵢ one by one.

## Preliminary: cost of not knowing σ (charter §3.2, §10 step 4) — 32 echoes, single-coil Rician, σ known vs jointly estimated

| SNR (first echo) | truth | Rician σ known: rel SD T2 (%) | Rician σ joint: rel SD T2 (%) | σ rel SD (%) |
|---|---|---|---|---|
| 100 | K=2 (20, 80), 0.2/0.8 | 33, 3 | 33, 3 | 12.8 |
| 100 | K=3 (20, 80, 2000), 0.15/0.7/0.15 | 103, 39, 450 | 103, 39, 450 | 12.5 |
| 30 | K=2 (20, 80), 0.2/0.8 | 115, 12 | 118, 13 | 13.3 |
| 30 | K=3 (20, 80, 2000), 0.15/0.7/0.15 | 343, 130, 1508 | 343, 130, 1508 | 12.6 |

At 32 echoes the data pin σ to ≈ 1/√(2N) = 12.5 % on their own and the (A, σ) cross-information is small at ν ≫ 1, so *under the correct Rician likelihood* joint estimation of σ costs < 2 % in decay-constant precision even with a 2000 ms component present (which is itself unrecoverable, 450–1500 % rel SD). This is a bound-level statement for L2/L5 single-coil data with the right likelihood; it says nothing yet about the bias of a Gaussian fit to Rician data, about a free-offset model, about χ / non-stationary pipelines, or about σ estimated by an external procedure — the rungs of the §3.2 ladder that remain.

## Verdict

- UP-1 (SVD count ≥ 4): **fires**, at the boundary (count = 4). But it counts informative singular directions, of which a K-component fit needs ≥ 2K; a count of 4 supports K = 2, not K = 3, and so does not contradict '2–3'.
- UP-2 (K = 3 at ratio 3 under 10 %): **does not fire**, by a factor of 3–15.
- DOWN-1 (count ≤ 1): does not fire.
- DOWN-2 (K = 2 at ratio 4 over 25 %): **fires for a 20/80 amplitude split, not for equal amplitudes.**

So the ~2–3 figure survives in component units (K = 2 estimable at 3–40 % depending on the amplitude split; K = 3 not), but the threshold as written is internally inconsistent: its SVD clause and its K = 3 clause point in opposite directions because they count different things, and its K = 2 clause is decided by an unspecified amplitude vector. Recommended recalibration (for the charter, not applied here): state UP-1 in component units (count ≥ 2K = 6 informative directions before K = 3 is even conceivable), fix the amplitude vectors for UP-2 / DOWN-2 (report equal and 20/80), and state the normalisation (σᵢ/σ₁ > 1/SNR on a log-uniform grid).