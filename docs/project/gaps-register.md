# Open Problems and Literature Gaps Register

**Status:** Living document. Companion to the Project Charter.
**Version:** 0.8 — established 2026-08-07, revised 2026-09-09 (v0.2: side-project status; capture over ranking. v0.3 (2026-09-06): Phase 1 pass-1 foundations sweep — A3 → PARTIAL with prior art named and the open sub-question narrowed; E1 upheld, UNVERIFIED leaning CONFIRMED, with the upholding evidence cited; "leaning" annotation defined; adjacency notes on entries the foundations reading bears on, statuses untouched; calibration ledger opened. **v0.4 (2026-09-07): resolution-limit formula in the B1 and D3 notes aligned with charter v0.8's harness-verified form (acquisition window, arccosh); no status changes. **v0.5 (2026-09-07): Phase 0 numerical notes on A1 (spacing at fixed window), A3 (joint-σ cost under the correct Rician likelihood), D1 (the finite-window count is now measured, not asymptotic); no status changes. **v0.6 (2026-09-07): E3 added — an open, cited, machine-readable table of multi-component tissue compositions; harness dictionary seeded with 13 `RECALLED` entries. **v0.7 (2026-09-07): E3 updated to dictionary v2 (18 entries, 37 of 54 component values from opened literature, abdominal splits labelled THEORY); A1 note corrected — Part II of the Bertero series is Bertero, Boccacci & Pike 1984, Brianzi is on Part III (1985); Eric's decisions recorded: adjacency notes kept, E1 list kept with its flag. **v0.8 (2026-09-09): header version label corrected (it had stayed at 0.4 while the history ran to v0.7); E3 updated to dictionary v2.1 (adipose, lipid mass fraction and PDFF, four primaries read) and the missing abdominal multi-component measurements recorded as a *potential future research project, not current focus* (Eric); E1 note: licenses chosen and GitHub mirror requested, the two release preconditions; B1/D3 notes carry Istratov & Vyvenko's printed constant (π·SNR²) next to the harness's relative form; no status changes**)
**Purpose:** Capture specific questions that appear unaddressed, unpublished, or never posed — as candidate original contributions.
**Priority:** Background. The charter is the work; this register collects what surfaces while doing it (§6).

---

## 0. How to read this document

### 0.1 Epistemic warning

**Every entry here is a hypothesis, not a finding.** Each is a claim that something is missing from the literature, made from prior knowledge with a training cutoff of May 2026. Claims of absence are the hardest kind to make and the easiest to get wrong. Some of these are certainly already published — possibly in a field whose vocabulary differs enough that I did not recognize the overlap, which is the specific failure mode this project is most exposed to, since the underlying problem is shared across four disciplines that barely cite each other.

**The first job of this document is to be falsified where it is wrong.** Phase 1's literature sweep (charter G1) validates or kills each entry. An entry that turns out to be occupied is a success of the process, not a failure — it converts to a bibliography entry and saves the effort of rediscovery.

*First instance, 2026-09-06:* the pass-1 sweep found that A3's broad claim was partly occupied — by a 1967 radar paper and a 2004 MR paper, exactly the cross-vocabulary failure mode described above. The narrowed claim survives. That is the process working.

### 0.2 Status values

| Status | Meaning |
|---|---|
| `UNVERIFIED` | Gap hypothesis, not yet checked against the literature |
| `CONFIRMED` | Sweep completed, no prior work found; safe to pursue as original |
| `PARTIAL` | Related work exists but leaves a specific identified sub-question open |
| `OCCUPIED` | Already published; converted to bibliography entry, closed here |
| `IN PROGRESS` | Being actively worked |
| `RESOLVED` | Our own result exists; see linked output |

All entries begin at `UNVERIFIED`. No entry may be worked past exploratory scoping while still `UNVERIFIED` — that is this document's version of charter guardrail G4.

**Lean annotations.** *(Added in v0.3.)* A status may carry a parenthetical lean — e.g. `UNVERIFIED (leaning CONFIRMED)` — when a sweep pass has looked in the entry's neighbourhood and found nothing, but did not cover the entry's full search space. The lean is an annotation, not a status: it records evidence, it does not lift the exploratory-scoping restriction, and it is dropped or converted the moment a pass actually checks the entry. A status is changed only by the sweep pass that checks the entry itself.

### 0.3 Scoring

**Effort:** S (weeks) · M (months) · L (long, open-ended)
**Payoff:** how much it advances the project's core question if it works
**Confidence:** my current credence that this is genuinely a gap, stated explicitly so it can be checked against outcomes later. Calibration matters — if the `CONFIRMED` rate diverges badly from these numbers, my judgment about the literature is miscalibrated and later entries should be discounted accordingly. The original confidence is never overwritten when an entry's status changes; it is kept as the number to be scored, and a separate confidence may be stated for any narrowed sub-question (see §7, calibration ledger).

---

## 1. Category A — Empirical and methodological gaps

Tractable, well-posed, publishable as methods work. These are the near-term targets.

### A1. Co-array and sparse-ruler sampling design for relaxometry
**Status:** `UNVERIFIED` · **Effort:** S · **Payoff:** High · **Confidence:** 0.75

Array processing solves sparse spatial sampling with co-prime, nested, and sparse-ruler geometries, where a small non-uniform sample set has a difference set covering a dense uniform grid. Echo times, inversion times, spin-lock times, and b-values are all freely choosable. Optimal-design work in MR exists (CRLB-optimal TE selection, D-optimal design), but the specific difference-set framing — placing samples so that difference-domain methods see a virtual full grid — appears absent.

**What would fill it:** CRLB comparison of sparse-ruler vs. uniform vs. log-spaced vs. CRLB-optimal placement at matched budget, across modalities. Clinically realizable immediately.
**Risk:** the design-theoretic advantage may not survive the fact that MR sample counts are small (8, not 80), where asymptotic co-array arguments are weak.

*Adjacency note (2026-09-06, from the pass-1 foundations reading; A1 itself not checked, status unchanged):* Bertero, Boccacci & Pike (*Proc. R. Soc. A* 393:51, 1984, Part II; *corrected 2026-09-07 from "Brianzi", who is on Part III, A 398:23, 1985, on sampling and truncation*) treat the optimum choice of experimental sampling points for Laplace inversion — geometric sampling in t — and Ostrowsky et al. (1981) give the exponential-sampling theorem in the solution domain. A1's difference-set framing must be positioned against the geometric-sampling optimum as the comparator, not only against uniform and CRLB-optimal placement.

*Phase 0 numerical note (2026-09-07; A1 not checked, status unchanged):* at fixed echo count and fixed window the informative-direction count moves by at most one across uniform, log-spaced, Chebyshev, early-dense, late-dense and end-clustered placements (N = 8–32, T2 support 10–300 ms, SNR 30–1000); log-spaced and early-dense placements never lose to uniform, late-dense and end-clustered placements lose one at high SNR. So the count is not where a placement design will show its value — the CRLB at a named amplitude vector is (charter §1.2 threshold, v0.9), and the co-array question should be posed in those units from the start.

### A2. Value of phase, in information units
**Status:** `UNVERIFIED` · **Effort:** S · **Payoff:** High · **Confidence:** 0.7

Rician bias correction and complex fitting each have literature. A systematic CRLB accounting of what phase is *worth* — across complex, phase-corrected real, and magnitude representations, as a function of SNR, frequency separation, and component count — appears not to have been done for multi-exponential decay.

**What would fill it:** the charter's value-of-phase sub-study. Directly actionable: it tells you whether sequence modifications to retain complex data are justified before you write them.

### A3. Joint (θ, σ) Fisher information and the σ / long-T degeneracy manifold
**Status:** `PARTIAL` *(from `UNVERIFIED`, 2026-09-06, Phase 1 pass-1 sweep)* · **Effort:** S · **Payoff:** Very high · **Confidence (original, broad claim):** 0.8 → outcome `PARTIAL` · **Confidence (narrowed sub-question):** 0.7

**Original claim (v0.1–v0.2, retained for the record):** Fitting a free constant offset is standard practice; Rician ML is standard practice. But an analytic characterization of the degeneracy manifold — the set of (θ, σ) pairs producing near-identical data — with proven identifiability conditions and the Schur-complement precision cost quantified, appears absent.

**Prior art found by the pass-1 sweep — what is occupied:**

- **Joint single-amplitude / σ estimation.** Benedict & Soong, *The joint estimation of signal and noise from the sum envelope*, IEEE Trans. Inf. Theory 13(3):447–454 (1967) — the radar-envelope original. Sijbers & den Dekker, *Maximum likelihood estimation of signal amplitude and noise variance from MR data*, MRM 51:586–594 (2004) — the joint ML estimator and joint CRLB for the single-amplitude Rician MR case. Between them, the K = 1 joint (a, σ) problem is solved, including its Fisher information.
- **Rician-correct CRLBs for decay models.** Karlsen, Verhagen & Bovée, MRM 41:614–623 (1999) — Rician ML and bounds for T1 and perfusion. Bouhrara, Reiter, Celik, Bonny, Lukas, Fishbein & Spencer, *Incorporation of Rician noise in the analysis of biexponential transverse relaxation in cartilage using a multiple gradient echo sequence at 3 and 7 Tesla*, MRM 73(1):352–366 (online 2014) — Rician-correct treatment of the biexponential T2 case. The Rician CRLB for a multi-exponential decay is therefore not new in itself.
- **The free-offset practice, documented.** Milford, Rosbach, Bendszus & Heiland, *Mono-exponential fitting in T2-relaxometry: relevance of offset and first echo*, PLoS ONE 10(12):e0145255 (2015) — measures what a free offset term does to T2 fits. This is the handling of the σ / long-T degeneracy the original claim called "implicit and inefficient"; Milford et al. characterize its *effect* without deriving its *information cost*, which is precisely what leaves the sub-question below open.

**What remains open — the narrowed gap:**

1. The joint Fisher information for the **multi-exponential** parameter vector (a_1..a_K, T_1..T_K) with σ as a nuisance parameter, for K ≥ 2, under Rician and non-central-χ likelihoods.
2. Its **block inverse** — the Schur complement of σ against (a_k, T_k) — as a closed-form or semi-closed-form statement of the precision cost of not knowing σ, and how that cost concentrates on the longest-T component.
3. An **analytic description of the degeneracy manifold**: the set of (θ, σ) that produce near-identical magnitude data, with identifiability conditions stated and proved, and the free-offset estimator located on it as a specific (inefficient) projection.
4. The value-of-noise-knowledge CRLB ladder — σ known / σ jointly estimated / σ externally estimated with its own error — for K ≥ 2, which none of the prior art above computes.

**What would fill it:** direct derivation plus numerical confirmation, positioned explicitly as the extension of Sijbers & den Dekker to K ≥ 2 and of Bouhrara et al. to the σ-unknown case. Small, self-contained, high leverage.
**Why this is still the best first target:** cheapest entry in the register, needs no infrastructure, and it calibrates how load-bearing charter §3 actually is. If the degeneracy turns out to be mild at realistic SNR, a large part of the noise track can be de-prioritized — which is valuable to learn early and cheaply. The charter's §3.2 and §10 step 4 were narrowed to match this entry in v0.7.
**What would move it to OCCUPIED:** a later sweep pass finding items 1–3 already derived for K ≥ 2. Step 4 in the charter would then become a reproduction.

*Phase 0 numerical note (2026-09-07; bound-level, status unchanged):* the numerical K ≥ 2 joint (θ, σ) Fisher block exists in the harness (`mexp/crlb.py`, exact Rician per-sample blocks pushed through the multi-exponential Jacobian). At 32 echoes, single coil, under the correct Rician likelihood, jointly estimating σ costs < 2% in decay-constant precision at first-echo SNR 100 and 30, including with a 2000 ms component present; the data pin σ to ≈ 12.5% on their own. Item 2 (the Schur-complement cost) is therefore small in this regime, and items 3–4 should be aimed where the cost can be large: the free-offset estimator located on the manifold, misspecified (Gaussian-on-Rician) fits, χ and non-stationary pipelines, and externally estimated σ. Charter §3.2 carries the same note.

### A4. Cost of reconstruction in parameter-variance units
**Status:** `UNVERIFIED` · **Effort:** M · **Payoff:** High · **Confidence:** 0.8

g-factor quantifies acceleration cost in image SNR. Acceleration and reconstruction choices are justified on image appearance. There appears to be no framework expressing reconstruction cost in the units that matter for quantitative MR: *variance of the estimated parameter*.

**What would fill it:** paired k-space and image-domain estimation on identical acquisitions across acceleration factors and reconstruction algorithms. Requires the k-space-first simulator, so it follows Phase 0.

### A5. End-to-end uncertainty propagation through CS reconstruction into parameter estimates
**Status:** `UNVERIFIED` · **Effort:** M–L · **Payoff:** Very high · **Confidence:** 0.85

Parameter maps derived from accelerated, CS-reconstructed acquisitions are reported with uncertainties that implicitly assume the reconstruction was noiseless. AMP state evolution offers a theoretical handle for suitable operators; Monte-Carlo replica offers a brute-force one. Neither appears to have been carried through to relaxometry parameter uncertainty.

**Why it matters beyond this project:** this is a correctness problem in currently published quantitative MR, not only an opportunity.

### A6. Blind reconstruction-pipeline identification from magnitude images
**Status:** `UNVERIFIED` · **Effort:** M · **Payoff:** High · **Confidence:** 0.65

Components exist — Aja-Fernández's effective-DOF and local σ estimators recover pieces of this. The integrated framing, *recover enough of the forward pipeline from magnitude data alone to write down a usable likelihood*, appears not to have been posed. This is the bridge that lets access level L6 borrow machinery built for L0, and L6 is where most retrospective and multi-site data lives.

### A7. Multi-component T1 identifiability boundary as a function of exchange rate
**Status:** `UNVERIFIED` · **Effort:** S–M · **Payoff:** Medium-high · **Confidence:** 0.6

The fast-exchange averaging argument is widely repeated qualitatively. A quantitative map — for what combinations of exchange rate, pool fraction, T1 separation, SNR, and acquisition scheme is multi-component T1 identifiable — appears not to exist. Lankford & Does did this for mcDESPOT specifically; the general version is the gap.

**Publication value:** answers a question the field currently settles by assertion.

---

## 2. Category B — Mathematical theory gaps

Harder, slower, and where the project's stated ambition actually lives. These are applied-mathematics contributions, not MR methods papers.

### B1. Sharp super-resolution limits for the Laplace kernel under non-negativity
**Status:** `UNVERIFIED` · **Effort:** L · **Payoff:** Very high · **Confidence:** 0.75

Candès–Fernandez-Granda give minimum-separation conditions for the Fourier case. Non-negativity is known to improve recovery limits for sparse measures substantially (Denoyelle, Duval, Peyré and related). The Laplace kernel with sharp constants and an explicit separation condition appears open.

**Why it is the right theory target:** it answers the project's foundational question — *what is actually recoverable* — rather than proposing another estimator. A sharp result here bounds everything else in the project.

*Adjacency note (2026-09-06, from the pass-1 foundations reading; B1 itself not checked, status unchanged; formula aligned 2026-09-07):* the positivity-free baseline any B1 result must beat is now explicit — the McWhirter–Pike / Bertero et al. resolution limit — as printed by Istratov & Vyvenko 1999 (read 2026-09-09) δ(SNR) = exp(π²/arccosh(π·SNR²)), 2.44 at SNR 100, or in the harness's relative-singular-value form exp(π²/arccosh(SNR²)), 2.71 — and the harness's measured 3.16 for a 32 × 10 ms train (charter §1.2 v0.12), with Epstein & Schotland (2008) supplying the closed-form singular functions a sharp-constant statement would be written in. A B1 result that does not improve on δ by a stated factor attributable to positivity is not a result.

### B2. Moment-SOS certificates of global optimality for multi-exponential fitting
**Status:** `UNVERIFIED` · **Effort:** L · **Payoff:** Very high · **Confidence:** 0.7

Under the substitution x = e^(−Δt/T), the samples are moments of a positive measure on (0,1) — a Hausdorff moment problem. Lasserre's moment-SOS hierarchy provides global optimality certificates for polynomial optimization. Applying it to the VARPRO objective would produce **the first certified global optima in multi-exponential MR fitting**, where the field currently relies on multistart and hope.

**Risk:** hierarchy size may be prohibitive beyond K=2 or 3. But K=2–3 is the clinically relevant range, which makes even a limited result useful.

### B3. Structured random matrix theory: MP-PCA on Vandermonde-constrained matrices
**Status:** `UNVERIFIED` · **Effort:** L · **Payoff:** Very high · **Confidence:** 0.8

MP-PCA estimates noise level and signal rank simultaneously by separating Marchenko–Pastur bulk eigenvalues from signal eigenvalues, assuming *unstructured* low-rank plus noise. A voxels × echoes decay matrix is not unstructured: its columns lie on a Vandermonde-like manifold. RMT for structured random matrices is active but has not, as far as I know, been pushed onto this constraint.

**Payoff if it works:** simultaneous, theoretically grounded estimation of K and σ from data already being acquired — resolving model-order selection and noise estimation in one stroke.

### B4. Backus–Gilbert resolution theory for MR relaxometry functionals
**Status:** `UNVERIFIED` · **Effort:** M · **Payoff:** Very high · **Confidence:** 0.85

Backus–Gilbert (1968) constructs the best-resolved linear functional of an unknowable model, with an explicit resolution-variance tradeoff. Myelin water fraction *is* a functional of f(T). Applying BG averaging-kernel theory to determine which relaxometry functionals are well-posed — and what the achievable resolution actually is — appears not to have been done in MR at all.

**Best effort-to-payoff ratio in the register.** The theory is mature and sitting in geophysics; the transfer is not conceptually difficult; and it addresses the charter's "change the question" strategy directly. It could reframe MWF from a poorly-identified spectral integral into a well-posed estimand with a stated resolution.

### B5. Numerical algebraic geometry for the VARPRO landscape
**Status:** `UNVERIFIED` · **Effort:** M–L · **Payoff:** Medium-high · **Confidence:** 0.7

Homotopy continuation can enumerate *all* critical points of a polynomial system. Applied to the VARPRO objective for K=2,3, this would characterize the full landscape — how many local minima exist, where, and how the count varies with SNR and separation — replacing folklore about local minima with an exact census.

*Adjacency note (2026-09-06, from the pass-1 foundations reading; B5 itself not checked, status unchanged):* Transtrum, Machta & Sethna's model-manifold geometry (2010, 2011) already describes the sum-of-exponentials landscape qualitatively — boundaries where components merge or vanish, and the sloppy directions along which minima are shallow. B5's census would be the exact, enumerative version; it must be positioned as that, and its findings checked against the manifold-boundary predictions.

### B6. Minimax and optimal-recovery confidence sets for the inverse Laplace problem
**Status:** `UNVERIFIED` · **Effort:** L · **Payoff:** High · **Confidence:** 0.65

Standard errors from the Hessian are asymptotic and assume the model is correct and the optimum is global — both routinely false here. Optimal recovery theory (Micchelli–Rivlin; Donoho's minimax work on linear inverse problems) constructs rigorous confidence sets over model classes. Instantiating it for the Laplace kernel with explicit constants appears open.

*Adjacency note (2026-09-06, from the pass-1 foundations reading; B6 itself not checked, status unchanged):* Bates & Watts (1980; 1988) is the classical, still-standard diagnostic of *when* Hessian-based confidence regions fail (intrinsic vs. parameter-effects curvature). A B6 result must be stated relative to it — what the curvature measures predict for the Laplace case, and by how much the minimax set differs from the curvature-corrected linearized region.

---

## 3. Category C — Cross-disciplinary transfer gaps

Known mathematics, absent application. Individually lower-risk than Category B and faster to execute, since the theory already exists and only the transfer is new.

| # | Transfer | From | Status | Effort | Confidence |
|---|---|---|---|---|---|
| **C1** | Generalized Prony (eigenfunctions of arbitrary operators) for non-uniform MR sampling | Numerical analysis (Peter & Plonka) | `UNVERIFIED` | S–M | 0.8 |
| **C2** | AAA rational approximation for decay-rate estimation | Numerical analysis (Nakatsukasa–Sète–Trefethen) | `UNVERIFIED` | S | 0.85 |
| **C3** | Finite Rate of Innovation theory for sampling-schedule design | Signal processing (Vetterli, Marziliano & Blu) | `UNVERIFIED` | M | 0.75 |
| **C4** | Hankel matrix completion for *parameter estimation* from sparse schedules (not image reconstruction) | Compressed sensing (EMaC, ALOHA) | `UNVERIFIED` | M | 0.6 |
| **C5** | Diffusion standard-model degeneracy methodology applied back to T2 | Diffusion MRI (Novikov, Jelescu, Veraart) | `UNVERIFIED` | M | 0.7 |
| **C6** | qMT/CEST multi-pool identifiability machinery applied to multi-component T1 | Magnetization transfer | `UNVERIFIED` | M | 0.65 |
| **C7** | Conformal prediction for quantitative parameter maps | Distribution-free inference | `UNVERIFIED` | S–M | 0.8 |
| **C8** | Christoffel–Darboux kernel methods for spectral localization | Orthogonal polynomials | `UNVERIFIED` | M–L | 0.75 |

C2 and C7 are the cheapest entries in the entire register and should be attempted early regardless of what else is prioritized.

*Adjacency note on C1–C3 (2026-09-06, from the pass-1 foundations reading; none checked, statuses unchanged):* every transfer claim in this table that originates on the Fourier/sinusoid side inherits the Rife–Boorstyn 1/(SNR·N³) scaling in its home setting. The charter's Phase 0 foundations table now requires each such transfer to state what replaces that scaling under the Laplace kernel before it is believed.

---

## 4. Category D — Negative results worth publishing

Underrated, and this project is unusually well-positioned to produce them: the benchmark harness makes rigorous impossibility claims cheap once it exists. A credible negative result stops other groups wasting effort, which is a real contribution even though it is harder to publish.

### D1. Formal impossibility results for the austere-budget regime
**Status:** `UNVERIFIED` · **Effort:** S–M · **Payoff:** Medium-high · **Confidence:** 0.7
K=3 from 5–8 samples at clinical SNR is widely attempted. A proof — not an empirical observation — of what is unrecoverable in that regime, with explicit conditions. Charter G5 requires this argument be written for every failing cell anyway; publishing it costs little extra.

*Adjacency note (2026-09-06, from the pass-1 foundations reading; D1 itself not checked, status unchanged):* the continuous-kernel impossibility results already exist — Bertero, Boccacci & Pike (1982) for the ln-SNR growth of the recoverable count and the restricted-support improvement, and the Istratov & Vyvenko (1999) closed form for R_min. What they do *not* cover is the finite-sample, finite-window, magnitude-data case at 5–8 samples, which is D1's actual regime. A D1 result is a sharpening of these, not a rediscovery, and must cite them as the starting point.

*Phase 0 numerical note (2026-09-07; D1 not checked, status unchanged):* the finite-window part of D1's regime is now measured for T2 rather than asymptotic — the informative-direction count is set by min(T-range, window) with an O(1) edge term (charter §1.2, v0.8–v0.9), and at 8 echoes over 40–320 ms it is 3 at SNR 30–100 and 4–5 at SNR 300–1000. A K = 3 fit needs ≥ 6 such directions, so the austere-budget impossibility D1 wants to prove has its linear-algebraic half on record; the nonlinear (CRLB / identifiability) half is what remains, and the CRLB module makes it cheap to state per configuration.

### D2. Registry of published performance claims that fail against the CRLB
**Status:** `UNVERIFIED` · **Effort:** M · **Payoff:** High · **Confidence:** 0.8
Phase 2 produces this as a byproduct. Some published methods almost certainly report precision below the information-theoretic floor, which is impossible and indicates a methodological error (usually an over-informative prior, a favorable simulation, or an unreported regularization).

**Handle with care.** This should be framed as a systematic re-evaluation with a shared benchmark, attributing discrepancies to methodology rather than to authors, and inviting correction. Written badly, it makes enemies and gets ignored; written well, it becomes the reference benchmark the field adopts.

### D3. The identifiability boundary itself, as a positive contribution
**Status:** `UNVERIFIED` · **Effort:** M · **Payoff:** High · **Confidence:** 0.7
The union of A7, B1, and D1: a map of where in parameter-acquisition space the problem is solvable. The field currently lacks this and substitutes optimism.

*Adjacency note (2026-09-06; updated 2026-09-07):* charter §1.2 now states the (SNR, acquisition window, T-range) → informative-direction map, measured by the harness for the T2 kernel and matched to the arccosh continuum form with γ_eff = min(T-range, window) (Istratov & Vyvenko's printed constant adds 0.4–0.8 to the count, charter v0.12), with a falsifiable threshold on the step to components. D3 is the multi-modality, exchange-aware, precision-stated extension of that map; the measured map is its zeroth-order term, not a competitor. Status unchanged.

---

## 5. Category E — Infrastructure gaps

### E1. An open benchmark for multi-exponential MR parameter estimation
**Status:** `UNVERIFIED (leaning CONFIRMED)` *(pass-1 sweep, 2026-09-06)* · **Effort:** M · **Payoff:** High · **Confidence:** 0.85

There appears to be no standard, open, ground-truth benchmark for this problem. Its absence is why method comparisons in the literature are largely incommensurable. The charter's Phase 0 harness *is* this, and releasing it is a resource contribution independent of any result obtained with it.

**Upheld by the pass-1 sweep — the nearest neighbours, and why each falls short:**

- **NIST StRD nonlinear-regression reference datasets (Lanczos1–3 and related).** Certified test problems for validating nonlinear least-squares *software* on exponential sums, generated at fixed precision from a known three-exponential model (24 points). Not an MR benchmark: no SNR axis, no Rician or χ noise, no unknown K, no continuous spectra, no acquisition model, and a single fixed grid.
- **The ISMRM/NIST system phantom.** Physical ground truth for T1 and T2 — but *single-component* by design. It calibrates scanners and mono-exponential fits; it says nothing about multi-component recovery.
- **The ISMRM reproducibility challenge on T1 mapping (2020).** Multi-site, single-component T1. Same limitation.
- **Diffusion-specific challenges (the 2015 ISMRM white-matter-modelling challenge; MEMENTO).** Modality-specific, and ground truth is either in-vivo (no truth) or a specific microstructure simulator; they do not serve relaxometry and were not designed to test multi-exponential estimation as such.
- **Per-group simulators and toolboxes (e.g. DECAES, the UBC MWI toolbox, qMRLab, MRiLab, JEMRIS, KomaMRI).** Each ships its own generator and, at most, its own test cases; none provides a shared ground-truth dataset with an agreed metric set that two independent methods papers have been scored on. This is the incommensurability the entry describes.

**Why not `CONFIRMED`:** pass 1 covered the foundations literature, not the seven method families or the four originating disciplines' own test-problem practices — geophysics/well-logging NMR relaxometry, chemical relaxation spectroscopy, and photon-correlation/DLS each have classic test distributions that could conceivably have been packaged as an open benchmark under a vocabulary this sweep did not search. Status is assigned by the pass that checks the entry, not by the pass that happens to look nearby.
**What would move it to `OCCUPIED`:** an open, multi-component, ground-truth benchmark with an SNR axis, in any of the four disciplines. The harness would then be positioned as an extension of it rather than a replacement.

*Release preconditions (2026-09-09):* licenses chosen — Apache-2.0 for the code, CC BY 4.0 for the dictionary and documents (charter §8, v0.12) — and a public GitHub mirror requested by Eric (to be created from the Mac; `README` §Remote). What still gates a release is content, not packaging: the k-space-first simulator (E2) and at least one scored estimator family (charter G2).

### E2. A k-space-first simulator running real reconstruction pipelines
**Status:** `UNVERIFIED` · **Effort:** M · **Payoff:** High · **Confidence:** 0.8
Required by charter §3.6. Simulators that add closed-form noise to synthetic images are common; one that synthesizes k-space, applies sensitivities, and runs actual SENSE/GRAPPA/CS reconstructions for relaxometry method development appears not to be available openly. Prerequisite for A4, A5, and A6, which makes it the highest-priority infrastructure item.

---

### E3. An open, cited, machine-readable table of multi-component tissue compositions
**Status:** `UNVERIFIED` · **Effort:** S–M · **Payoff:** Medium-high · **Confidence:** 0.6 *(raised to 0.7 in v0.7: the 2026-09-07 literature pass found no such table and found the abdominal multi-component measurements themselves missing; unchanged in v0.8)*

Method papers each carry their own "typical" compositions (myelin water ~0.1 at ~15 ms, and so on) drawn from a handful of classic studies, but no curated table appears to exist that lists, per tissue and organ, per modality and field strength, the component fractions and time constants *with their literature ranges and sources*, in a form a simulator can load. The charter's tissue dictionary (`mexp/tissue_data.py`, charter v0.10–v0.11) is a first draft of exactly this: version 2.1 (2026-09-09) has 19 entries (brain WM/GM, CSF, cord, muscle, cartilage, tendon, cortical bone, marrow, myocardium, blood, liver, spleen, kidney cortex/medulla, pancreas, prostate, breast, adipose tissue) with water content, relative PD, T1 and T2 at 1.5 and 3 T, ADC, **lipid mass fraction and PDFF as two distinct quantities** (Woodard & White 1986's chemical composition, PRIMARY, against the MR proton-density fat fraction — white matter is 18 % lipid by mass and 0 % PDFF), components per modality (T2, T1, IVIM/tensor/standard-model diffusion), a physical-pool theory block, and a provenance status on every value — 7 PRIMARY, 31 SECONDARY, 1 TERTIARY, 6 RECALLED, 11 THEORY component values, with the water-content column and the abdominal/pelvic T1/T2 columns now PRIMARY from Woodard & White 1986, de Bazelaire 2004, Gold 2004 and Le Ster 2016 (all 57 requested PDFs are in `literature/`; the rest of the verification pass is charter §10 step 8). The THEORY rows (liver, spleen, kidney, pancreas T2 splits) exist precisely because the literature search found *no* in vivo multi-component T2 study of those organs — which sharpens this entry: the gap is not only the table, it is the measurements the table would need for the abdomen.

**Future research project (recorded 2026-09-09, Eric's decision: not current focus).** *In vivo multi-component T2 relaxometry of liver, spleen, kidney and pancreas, acquired in the same session as IVIM, so that the T2-derived and diffusion-derived compartment fractions can be compared against each other and against the fast-exchange prediction that the T2 axis mostly cannot see the vascular pool.* It would supply the abdominal rows of this table from measurement, and it is the natural experimental companion of the harness's 'exchange-coupled ground truth' axis (charter §6.1). It is parked here so that it is neither lost nor pursued by accident; nothing in the charter's phases depends on it, and the THEORY labels stay until such a study exists. The pathology axis (one disease variant per organ; steatotic liver first, charter §10 step 8(e)) is the next dictionary revision.

**What would fill it:** the verification pass itself, extended across organs and modalities with the four originating disciplines' tissue tables (well-logging petrophysics has the analogous rock-typing tables), released with the harness (E1).
**Why it matters here:** the §1.2 falsifiable threshold turned out to be decided by the amplitude vector, so the question "what K does clinical data support" has no answer without such a table; and every Phase 2 comparison needs realistic truths, not one myelin split.
**What would move it to OCCUPIED:** an existing curated table with sources and ranges in any of the four disciplines — the dictionary then becomes an import.

---

## 6. Relationship to the charter work

**This document is a side project, not a work plan.** The charter is the work. This register is a capture buffer for publishable questions that surface *while* doing it, and its entries are expected to be resolved as byproducts rather than as dedicated efforts.

That relationship is the intended one for a specific reason: gaps identified from the armchair are unreliable, while gaps encountered mid-investigation are real by construction — you found them because something you needed did not exist. The best entries in this document will be ones added later, not the ones written on day one.

**How entries get worked, in practice:**

- **Naturally.** Charter work requires something; the something turns out to be missing; it gets built; it becomes a result. This is the default and the preferred path.
- **Opportunistically.** An entry sits close enough to work already underway that finishing it costs little extra. Fine to take.
- **Deliberately.** A dedicated effort on a register entry that charter work does not require. This needs justification against charter G4, and should be rare.

**The relationship already has an instance.** Entry A3 (joint Fisher information and the σ / long-T degeneracy) is also charter §10, next step 4 — not because it was prioritized from this document, but because the harness needs the joint CRLB regardless of whether anything is ever published about it. That is exactly the intended pattern: the charter demands the work, and the publishable result falls out. *Update 2026-09-06:* the pass-1 sweep narrowed A3 to `PARTIAL`, and the charter's §3.2 and §10 step 4 were narrowed in the same revision so that the work the harness demands and the claim the register makes are the same object.

If entries are ever ranked, the ripest are likely **B4** (Backus–Gilbert for relaxometry functionals), **A5** (uncertainty propagation through CS reconstruction), and **E2** (the k-space-first simulator, which the charter requires anyway). **C2** and **C7** are cheap enough to fold into other work without displacing anything. But this ranking is provisional and should be re-derived after the Phase 1 sweep completes — pass 1 alone does not warrant re-ranking — not treated as a queue.

---

## 7. Maintenance rules

- **Adding beats ranking.** The primary maintenance activity is capture: when charter work runs into something that should exist and doesn't, it gets an entry the same day, while the context is still fresh. Re-ranking existing entries is low-value by comparison.
- **Every entry starts `UNVERIFIED`.** Status is assigned by the Phase 1 sweep as a byproduct of reading, not by a dedicated verification pass. No entry is worked past exploratory scoping while unverified. A sweep pass changes the status only of entries it actually checks; entries it merely passes near get an *adjacency note* and a *lean* at most (§0.2).
- **Entries that turn out `OCCUPIED` are closed, not deleted.** Retain the entry with its resolution and the citation that killed it. The record of what was wrongly believed missing is itself information about where the literature is hard to see into. The same applies to the occupied portion of a `PARTIAL` entry: the original claim is kept verbatim above the narrowed one.
- **Confidence numbers are scored after the fact.** Once ~10 entries have been verified, compare the `CONFIRMED` rate against stated confidences. Systematic overconfidence means later entries should be discounted.

  **Calibration ledger** *(opened 2026-09-06)*:

  | Entry | Stated confidence | Outcome | Pass | Note |
  |---|---|---|---|---|
  | A3 | 0.8 | `PARTIAL` | 1 | Broad claim occupied at K = 1 (Benedict & Soong 1967; Sijbers & den Dekker 2004) and for Rician-correct decay CRLBs (Karlsen 1999; Bouhrara et al. 2014); K ≥ 2 joint block inverse and degeneracy manifold open |

  One of ~10 entries needed before scoring. A `PARTIAL` counts as a half-miss for calibration purposes: the gap was real but smaller than stated.
- **Anything reaching `RESOLVED` links to its output** and is cross-referenced in the charter's decision log.
- **No deadline pressure applies to this document.** It has no schedule and imposes none. If it is empty of progress for long stretches while the charter advances, that is the system working as designed.
