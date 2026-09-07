# Phase 0 findings — harness skeleton, Lanczos test, conditioning map, §1.2 threshold

Revision 2, 2026-09-07. The first revision (2026-09-06) was written against charter v0.6 because v0.7 had not
been saved to the project; this revision was started against **v0.7** and, while it was under way, a **v0.8**
that already integrated revision 1 landed in the project. The work below is therefore reconciled with v0.8, and
the edits it calls for were written back as **charter v0.9** (with gaps register v0.5 and a changelog entry) in
the same session — the v0.8 §7 practice. §0 lists the v0.7/v0.8 items and what was redone.
Everything here is reproducible from `pytest` (60 tests), `python scripts/phase0_conditioning.py` and
`python scripts/phase0_threshold.py`. No noise realisation is drawn anywhere (charter §4 standing rule;
enforced by `tests/test_kspace_first_rule.py`). SNR conventions: the §1.2 threshold and the CRLB tables
use **first-echo SNR** (σ = S(t₁)/SNR) as the charter does; the harness axis default is S_ref/σ with
S_ref = Σ|a| (`mexp.crlb.sigma_from_*` convert).

## 0. What v0.7 changed for this work, and what was redone

| v0.7 item | Consequence | Done |
|---|---|---|
| §1.2/§4: Lanczos restated as 3-exp matched by 2-exp; pass criteria (a) harness's *own* best 2-exp fit < 0.001, quoted coefficients checked separately; (b) indistinguishability above the residual; provenance flag with the grid inconsistency | Test restructured around (a)/(b); marked `provisional_pending_primary`; grid inconsistency investigated numerically (§1) | yes |
| §1.2: effective rank restated as R_min(SNR), K_max(Γ, SNR) with a **falsifiable threshold** at a reference configuration, two CRLB clauses | CRLB module added (Gaussian real/complex, Rician with σ known or joint); threshold evaluated, all four clauses (§4) | yes |
| §1.2: constant-convention flag on R_min (amplitude vs power SNR, O(ln 2) term) | Both conventions implemented and compared with the numerics (§3.3) | yes |
| §4: "checked against the closed-form singular values (Epstein & Schotland 2008; McWhirter & Pike 1978)" | Covering-window check done; result: the closed form is a check on the count and decay rate, not per index (§3.3) | yes |
| §4: foundational-results table (E&S, Ostrowsky, Transtrum, Bates–Watts, Rife–Boorstyn) | Encoded where Phase 0 can: exponential-sampling spacing helper, FIM-spectrum test, Rife–Boorstyn contrast test; Bates–Watts deferred to the §6.2 calibration work (§5) | partly |
| §7: provenance discipline | Applied: locked (NIST) vs provisional (Lanczos 2-exp, R_min constant) separated in code and tests | yes |
| §10 step 6: build the conditioning map and evaluate the threshold, log in §8 | Done; outcome in §4; written into charter v0.9 (§1.2 outcome paragraph, §8 rows) | yes |
| Housekeeping: seven families / §4 cross-reference fixed in v0.7 | My v0.6-based contradiction items 4 are withdrawn | — |

Two of the first revision's findings stand unchanged and matter for v0.7's text: the echo-train **window**, not
the T-range, sets the singular-value count (§3.2), and the SVD count is in units of singular directions, not
components (§4).

## 1. Lanczos degeneracy example

**Locked (NIST StRD Lanczos1, certified to 1e-10):** `f(t) = 0.0951e^{−t} + 0.8607e^{−3t} + 1.5576e^{−5t}`,
24 points `t = 0, 0.05, …, 1.15`. The T2 kernel reproduces NIST's 14-digit table to 4.8e-13.

**Criterion (a), harness's own fit — passes.** The best two-exponential approximant on the NIST grid,
computed inside the test with `scipy.optimize.least_squares` driven by the kernel's forward model and analytic
Jacobian (multistart, positivity bounds), is `2.06878 e^{−4.63964t} + 0.44401 e^{−1.87247t}`, **max deviation
8.8e-4, RMS 4.2e-4** — better than 0.001, matching v0.7's own numerical check (2.069, 4.64, 0.444, 1.87,
0.00088). The frozen constant in `mexp/datasets/lanczos.py` equals it to 1e-5 and is verified estimator-free
by the stationarity condition Jᵀr = 0. Nothing in `mexp/` imports an optimiser (G2).

**Criterion (a), quoted coefficients — do not meet 0.001, on any grid.** `2.202e^{−4.45t} + 0.305e^{−1.58t}`
deviates from f by **0.0064 at t = 0**, and t = 0 is on every candidate grid, so the "better than 0.001" claim
cannot refer to these coefficients regardless of how the grid question resolves. What they *are* consistent
with is a **two-decimal table**: on the NIST grid the two-decimal roundings agree at 23 of 24 points (the
exception is t = 0.2, 1.12 vs 1.13), and on the Δt = 0.1 grids the maximum deviation from the two-decimal
table is 0.0068–0.0069. My own recollection of *Applied Analysis* is that the tabulated values are given to
two decimals and Lanczos's claim is agreement "within the accuracy of the data"; that is a recollection,
not a check.

**The grid question (v0.7 flag), narrowed numerically.** v0.7's observation is confirmed: the LS-optimal
two-exponential on a Δt = 0.1 grid over [0, 2.3] is `2.1885e^{−4.5035t} + 0.3236e^{−1.5963t}` (max deviation
0.0024), and on Varah's 33-point Δt = 0.1 grid over [0, 3.2] it is `2.2156e^{−4.4682t} + 0.2961e^{−1.5247t}`
(0.0030) — both closer to the quoted numbers than the NIST-grid optimum is, and a hand Prony computation on
two-decimal data would land near but not on any LS optimum. So the quoted coefficients point to a Δt = 0.1,
longer-window table, and the 0.001 figure belongs to the *optimal* fit on the *NIST* grid, i.e. to the two
secondaries' different objects having been merged. Note also that Varah's 1982 tech-report version, which I
could fetch, does **not** quote the two-exponential coefficients (it says Lanczos's Δt = 0.5 example decays too
fast and generates its own data at Δt = 0.1, n = 33) — so the v0.7 statement that the coefficients were
"verified against Varah (1985)" may itself need checking against the journal version.

**What the primary must settle** (unchanged in kind, now specific): (i) Δt and the number of points;
(ii) the number of decimals in the table; (iii) whether Lanczos states a numerical agreement or "within the
accuracy of the data"; (iv) the two-exponential coefficients as he prints them. Until then the test carries the
`provisional_pending_primary` marker and the pass criterion is applied to the harness's own fit, exactly as
v0.7 §4 prescribes.

**Criterion (b) — passes.** With Δ = f₃ − f₂,best (‖Δ‖₂ = 2.07e-3), for every σ ≥ 8.8e-4 the expected excess
χ² of the two-component model, ‖Δ‖²/σ² ≤ 5.5, is below the χ²₂ 95 % critical value 5.99, so a likelihood-ratio
test cannot prefer K = 3; and the Gaussian CRLB relative SDs of the three decay constants are ≥ 271 %, 110 %,
22 % — two of three not estimable — while the two-exponential description is determined to < 3 %. The
operating point at which the models separate (d′ = 3) is SNR ≈ 3.6e3 relative to f(0). NIST Lanczos3 (five
significant digits, SNR ≈ 9e4) shows the other side: the certified three-exponential fit moves the slow
component to `0.0868e^{−0.955t}` with SDs 0.017 / 0.097 and fits the rounded data better than the truth does.

**Recommended §1.2 / §4 wording.** "…is matched over 24 sampled points by a two-exponential sum: the optimal
two-exponential approximant agrees to 8.8e-4 (better than 0.001); the coefficients Lanczos reports,
`2.202e^{−4.45t} + 0.305e^{−1.58t}`, agree to 0.0064, i.e. within a two-decimal tabulation." The "better than
0.001 … by the two-exponential sum 2.202…" sentence in v0.7 §1.2 and §4 conflated the two; v0.8 adopted the
split, and v0.9 adds the grid note and the Varah caveat to the provenance flag.

## 2. Interface, and the CRLB module added in this revision

Interface unchanged from revision 1 (see `docs/kernel-interface.md`): one abstract method `atoms`, `(K, p)`
non-linear parameters, named multi-dimensional design coordinates, `AmplitudeField`/`SignalField`, nuisance
and fixed-atom blocks; IR, Look-Locker, complex T2*, T1ρ-dispersion and b-tensor diffusion kernels exercised
on the unchanged base class in the test file, none registered.

`mexp/crlb.py` (new): Fisher information and CRLB for `gaussian_real`, `gaussian_complex` and `rician`
noise, with σ known or as a joint nuisance parameter. The Rician per-sample blocks I_AA, I_Aσ, I_σσ are
computed from the exact likelihood in the scaled variable (Gaussian limits g→1, c→0, h→2 and the Rayleigh
limit h→4 are tested) and pushed through the kernel Jacobian — which is the numerical K ≥ 2 joint (θ, σ)
block that §3.2 / gaps A3 name. It is not an estimator; nothing fits data.

## 3. Conditioning map

Setup as in revision 1: `A_ij = exp(−TE_i/T_j)`, 300-point log grid, CPMG designs with TE₁ = ΔTE; count =
#{i : σᵢ/σ₁ > 1/SNR}. Full sweep in `results/conditioning_sweep.csv`, figures `results/fig1–5`.

### 3.1 Reference configuration (v0.7): 32 × 10 ms, T2 support [10, 300] ms, first-echo SNR 100

σᵢ/σ₁ = 1, 0.272, 0.084, **0.0242**, 0.0063, 0.0015, … → count **4** (4 for SNR 42–159; 3 below, 5 above).
Picard (smoothed) counts for the reference truths: 3–4. Weighting the columns by dT instead of d ln T gives
3/4/4 at SNR 50/100/200 instead of 4/4/5.

### 3.2 The window sets the count (unchanged from revision 1, and load-bearing for §1.2)

With the 32 × 10 ms train fixed, the count is identical for T-grids of ratio 100, 400 and 10⁴ (3/4/5/6 at
SNR 30/100/300/1000); the narrow Γ = 10 grid loses one at SNR 1000. With a wide T-grid and a dense window
[t₀, t₁], the count tracks the continuum expression evaluated with the **window's** ratio t₁/t₀. For CPMG with
TE₁ = ΔTE, t₁/t₀ = N exactly, so the count depends on echo *number* and SNR, not on echo spacing except
through which T2 values the window covers. Over the 144-cell sweep the residual "numerical − continuum(Γ_T)"
spans −9.5 to +2.6; with Γ → min(Γ_T, t₁/t₀) it spans −0.3 to +2.6 (mean +0.9); with a further +1 edge term,
±1.6. **v0.7 §1.2's K_max must therefore be read with Γ = the in-window range** — which its worked example
already does ("in-window T2 range of roughly 10–300 ms") but its formula does not say.

### 3.3 The closed forms and the constant convention (v0.7 flag)

From the Mellin gain √(π/cosh πω) without approximation: ω_max = (1/π)·arccosh(SNR²) = (2/π)ln SNR + (ln 2)/π,
hence R_min = exp(π²/arccosh(SNR²)) ≈ exp(π²/ln(2·SNR²)). The charter's exp(π²/(2 ln SNR)) is the
2 ln SNR ≫ ln 2 limit — the O(ln 2) term it flags. SNR is an amplitude ratio in both. Numbers:

| SNR | R_min charter | R_min arccosh | K_max charter (Γ = 30) | (ln Γ/π²)·arccosh(SNR²) + 1 | numerical count |
|---|---|---|---|---|---|
| 30 | 4.27 | 3.73 | 3.34 | 3.58 | 3 |
| 100 | 2.92 | 2.71 | 4.17 | 4.41 | 4 |
| 1000 | 2.04 | 1.97 | 5.76 | 6.00 | 6 |

Both forms reproduce the numerical count to ±0.8 at the reference configuration and cannot be told apart by
it (the ln 2 term is 0.24 of a singular value there). The primary check of Istratov & Vyvenko's convention is
still owed; the harness carries both (`conditioning.r_min(snr, convention)`).

**Epstein–Schotland / McWhirter–Pike as the analytic reference — what it checks.** With a covering window
(t from 0.01·T_min to 30·T_max, dense) and L²(d ln T) weighting, the numerical count agrees with
(ln Γ/π²)·arccosh(SNR²) to within about ±2 over Γ = 100–10⁴ and SNR 30–1000. The **per-index** prediction
σₙ/σ₀ = 1/√cosh(nπ²/ln Γ) does not hold at low index: σ₁/σ₀ ≈ 0.33 numerically for every covering-window
Γ ≥ 100 against 0.48–0.78 predicted, with the implied log-length approaching ln Γ from below only for n ≳ 5.
The weighting of f (L²(dT) vs L²(d ln T)) moves the count by 1–3. So the closed form is a check on the
*decay rate and count*, which is what §1.2 uses it for; §4's phrase "checked against the closed-form singular
values" should not be read as σᵢ-by-σᵢ agreement.

### 3.4 Picard and truncation (unchanged)

Smoothed Picard count is the operational diagnostic (raw leading run is brittle to accidental zeros); an
out-of-grid component shows up as non-decaying Picard coefficients. TSVD averaging-kernel widths on
[5, 2000] ms: T2-ratio 44 / 20 / 8.7 / 6.0 / 4.7 / 3.4 / 3.0 / 2.8 for k = 1…8 against noise gains
1 / 4 / 14 / 45 / 145 / 500 / 1800 / 7000; at SNR 100 the admissible k is 4 (a factor ≈ 6 in T2).

## 4. The §1.2 falsifiable threshold — outcome at the reference configuration

Full tables in `results/threshold_evaluation.md`. Amplitude vectors and the "SNR-scaled" normalisation are not
fixed by the charter; both were swept.

| Clause | Result | Fires? |
|---|---|---|
| UP-1: SVD count ≥ 4 | count = 4 (σ₄/σ₁ = 0.024 > 0.010 > σ₅/σ₁ = 0.006); 3–5 under other column weightings | **yes, on the boundary** |
| UP-2: K = 3, adjacent ratio 3, all three T2 < 10 % rel SD (Rician, σ known or joint) | best all-three case (15/45/135 ms, equal amplitudes) 70 / 103 / 30 %; (20/60/180) 72 / 156 / 60 %; most cases > 100 % on one constant | no, by ×3–15 |
| DOWN-1: count ≤ 1 | — | no |
| DOWN-2: K = 2, adjacent ratio 4, > 25 % rel SD on either T2 | equal amplitudes: 11–14 % / 5–9 % → no; 20/80 split: 28–41 % on the short T2 → yes; 80/20: no | **depends on amplitudes** (4 of 12 cases) |

Rician vs Gaussian and σ-known vs σ-joint change these numbers by < 2 % (relative) at first-echo SNR 100.

**Verdict.** The ~2–3 figure survives in component units: K = 2 is estimable (3–40 % on the decay constants,
set by the amplitude split), K = 3 at ratio 3 is not. But the threshold as written is internally inconsistent —
UP-1 and UP-2 point in opposite directions because UP-1 counts informative singular *directions* (a
K-component fit needs at least 2K of them; 4 supports K = 2) while UP-2 counts *components*; and DOWN-2 is
decided by an unspecified amplitude vector. **What v0.8 had already done, and what v0.9 adds.** v0.8 (which landed mid-session) had already dropped the
SVD clause in favour of the two CRLB clauses plus a window-rule clause, so UP-1 above is evaluated against
v0.7's wording for the record only. Against v0.8's clauses: the upward clause does not fire; the downward clause
fires for the 20/80 split and not for equal amplitudes; the window-rule clause holds (six spacings at N = 8–32
over a fixed window move the count by at most one; log-spaced and early-dense never lose to uniform, late-dense
and end-clustered lose one at high SNR). v0.9 therefore names the two amplitude vectors in the clauses and
fires the downward clause on the equal-amplitude case only; under that wording nothing fires and the figure is
retained, with the precision behind it measured.

## 5. The foundational-results table — Phase 0 status

| Row | Encoded in the harness as | Status |
|---|---|---|
| McWhirter–Pike / BBP / Istratov–Vyvenko | `conditioning.bbp_count`, `r_min` (both conventions), `k_max`; count checks in tests and scripts | done; constant convention awaits the primary |
| Epstein & Schotland | covering-window count and decay-rate check (§3.3); per-index form kept as `mellin_closed_form_ratios` with the caveat | done, with the finding that it is not per-index |
| Ostrowsky et al. exponential sampling | `conditioning.ostrowsky_spacing(snr)` = ln R_min: the geometric solution-grid ratio below which grid points carry no independent information | helper only; to be used when regularised-inversion grids are chosen in Phase 1 |
| Transtrum–Machta–Sethna | `CRLBResult.fim_eigenvalues`; test that the K = 3 FIM spectrum spans > 6 decades roughly evenly in log | done (diagnostic only) |
| Bates & Watts curvature | — | not yet; belongs with the §6.2 uncertainty-calibration metric, which needs estimators |
| Rife & Boorstyn | test: single-tone frequency CRLB scales as 1/N³ (measured 8.0 ± 0.1 from N = 32 → 64) while the T2 CRLB improves < 10 % over the same doubling once the window exceeds 6 T2 | done |

## 6. Preliminary calibration of §3.2 (because the machinery now exists; bound-level only)

Under the *correct* Rician likelihood, single coil, 32 echoes: jointly estimating σ instead of knowing it costs
< 2 % in decay-constant precision at first-echo SNR 100 and SNR 30, for a 20/80 two-component truth and for a
three-component truth carrying a 2000 ms component (which is itself unrecoverable: 450–1500 % rel SD). The
data pin σ to ≈ 1/√(2N) = 12.5 % on their own, and the (A, σ) cross-information is small at ν ≫ 1. This says
nothing about the bias of a Gaussian fit to Rician data, a free-offset model, χ or non-stationary pipelines,
or an externally estimated σ — which is where the §3.2 ladder's cost must therefore live if it is large. It is
one data point for §10 step 4's question of how load-bearing §3 is, not an answer.

## 7. Tissue and organ dictionary (added after Eric's review; charter v0.10)

The threshold's dependence on the amplitude vector was the reason to stop using one myelin-like split.
`mexp/tissues.py` now carries 13 literature-derived compositions (brain WM/GM, spinal cord, muscle, cartilage,
prostate, breast, myocardium, liver on T2; cortical bone and tendon on UTE T2*; WM T1; liver IVIM), each with
its clinical functional, a typical acquisition, sources and a provenance status — **all `RECALLED`** until the
verification pass (charter §10 step 8). `scripts/phase0_threshold_tissues.py` evaluates the Rician CRLB and the
delta-method bound on each functional at the reference and at the entry's own acquisition
(`results/threshold_tissues.md`). Headline, subject to the flag: under a free K = 3 model no myelin-type entry
is estimable at SNR 100 — the unpinned 2000 ms component roughly doubles the MWF bound; with the long component
fixed or dropped, WM MWF is ±0.030 (1σ) at SNR 100 and ±0.010 at SNR 300 while myelin T2 is still 57 %
relative — the functional beats the parameters, as Phase 3 expects; minor components under ~5 % fail; prostate
luminal water (ratio ≈ 8) is estimable, to 5 % relative at its own 64 × 8 ms train. The per-tissue restatement
of "K = 2 comfortably, K = 3 marginal" is in charter §1.2.

## 8. Charter corrections — what landed where

Fixed by v0.7 (and so withdrawn from revision 1's list): version mismatch; "six families of §3"; Lanczos form.
Fixed by v0.8 (from revision 1's findings, before this revision): window rule and γ_eff = min(T-range, window)
in §1.2; "2–3" in component units via the 2K rule; arccosh form of δ; §2.3 few-samples bullet; "echo spacing" →
"echo count and window" in §4; k-space-first rule annotated as mechanically enforced; SNR definition logged; §7
"living documents are written back in place".
Applied in **v0.9** and **v0.10** (this revision; all marked, all reversible, logged in §8 and `claude/changelog.md`):
1. §1.2 threshold: evaluated; amplitude vectors written into the clauses; outcome paragraph.
2. §1.2: "CRLB module (next Phase 0 item)" → built.
3. §3.2: bound-level probe paragraph (joint-σ cost < 2 % under the correct Rician likelihood at 32 echoes).
4. §4 conditioning bullet: Epstein–Schotland check qualified to count and decay rate.
5. §4 Lanczos bullet: test restated for the (a)/(b) structure; provisional marker; provenance flag narrowed
   (grid-independent t = 0 deviation; Δt = 0.1 long-window optima; Varah tech-report caveat).
6. §4 CRLB bullet marked built; foundations table given a Phase 0 status line.
7. §8: two rows; §10: steps 2, 3, 5, 6 updated.
Gaps register v0.5: Phase 0 numerical notes on A1, A3, D1; v0.6: E3 (open tissue-composition table). `bibliography.md` v0.1 opened (G1).
v0.10 also: tissue dictionary (§1.2 tissue-level threshold, §4 bullet, §6.1 level, §10 step 8), repository/sync practice (§7), header version number fixed (v0.9 had left it at 0.8).
Still open (need the user or the primary): the Lanczos book check with its four fields; the Istratov–Vyvenko
constant convention; the dictionary verification pass; acceptance of the threshold wording.
