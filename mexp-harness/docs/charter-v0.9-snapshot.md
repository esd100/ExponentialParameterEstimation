# Multi-Exponential Parameter Estimation in MR: Project Charter

**Status:** Living document. Authoritative reference for all work in this project.
**Version:** 0.8 — established 2026-08-07, revised 2026-09-07 (v0.2: §2.3 corrections, G5, harness axes; v0.3: §3 noise track added, family 7, noise harness axes; v0.4: §3.6 two-arm architecture, access ladder, k-space-first simulator; v0.5: gaps register companion doc; v0.6: Phase 0 simulator rule rationale, register scoped as background; v0.7 (2026-09-06): Phase 1 pass-1 foundations sweep integrated — Lanczos example corrected, §1.2 effective rank restated as an SNR- and T-range-dependent quantity with a falsifiable threshold, joint-FIM novelty claim narrowed against prior art, foundational results added to Phase 0 scope, no-open-benchmark claim upheld with citations; **v0.8 (2026-09-07): §1.2 and §4 Phase 0 reconciled with the harness's Phase 0 findings (`claude/phase0-findings.md`) — acquisition window, not T-range, sets the informative-direction count; "2–3" stated in units of components with the measured rank behind it; Lanczos two-decimal tabulation resolves the coefficient discrepancy; SNR definition logged; Phase 0 status updated in §10; **v0.9 (2026-09-07): CRLB module built and the §1.2 threshold evaluated at the reference configuration — no clause fires once the amplitude vector is named (it is now named in the clauses), window-rule clause holds; Lanczos test restructured to v0.7's (a)/(b) criteria with the quoted coefficients checked separately and the grid question narrowed; Epstein–Schotland check qualified to count and decay rate; §3.2 bound-level probe recorded**)
**Scope:** Survey of all known mathematical approaches to estimating parameters from multi-component MR decay signals, followed by original advances.

---

## 1. The Problem

### 1.1 Discrete form

$$S(t_n) = \sum_{k=1}^{K} a_k\, e^{-t_n/T_k} + \varepsilon_n, \qquad a_k > 0,\ K \text{ unknown}$$

The positivity constraint is the T2 statement. For inversion-recovery magnitude data with polarity ambiguity the amplitudes are real, and for complex T2\* they are complex; the harness carries this as an amplitude-field attribute of each kernel (positive · real · complex), and the reuse claims in §2 rely on that generalization rather than on a_k > 0.

### 1.2 Continuum form

$$S(t) = \int_0^\infty f(T)\, e^{-t/T}\, dT, \qquad f \geq 0$$

This is a numerical inverse Laplace transform, and that is where the difficulty lives. The Laplace kernel's singular values decay exponentially. Epstein & Schotland (*SIAM Review*, 2008) give them in closed form; McWhirter & Pike (*J. Phys. A*, 1978) and Bertero, Boccacci & Pike (*Proc. R. Soc. A*, 1982) had already used the Mellin-domain diagonalization of the kernel to turn that decay into a resolution limit.

The canonical illustration is Lanczos's example (*Applied Analysis*, 1956, ch. IV, pp. 272–280): the **three**-exponential function

$$f(t) = 0.0951\,e^{-t} + 0.8607\,e^{-3t} + 1.5576\,e^{-5t},$$

sampled at 24 points t = 0, 0.05, …, 1.15 and tabulated to two decimals, is reproduced by a **two**-exponential sum. Lanczos's own two-term representation, 2.202·e^(−4.45t) + 0.305·e^(−1.58t), matches the two-decimal table at 23 of the 24 points (maximum deviation from f, 0.0064); the *optimal* two-exponential approximant on that grid, 2.0688·e^(−4.6396t) + 0.4440·e^(−1.8725t), agrees with f to a maximum deviation of 0.00088 — three decimal places against a peak of 2.51. Separating the two models needs a peak-to-σ SNR above roughly 3.6 × 10³ even for an oracle detector that knows both candidates (‖f₃ − f₂‖₂ = 2.07 × 10⁻³ over 24 samples, d′ ≈ 3). Neither the number of components nor any individual decay constant survives a perturbation at the third decimal place. *(v0.1–v0.6 mis-described this example as "two very different 3-exponential sums agreeing to 3 decimal places"; corrected in v0.7 and made precise in v0.8 from the harness's Phase 0 findings — the 0.001 agreement belongs to the optimal approximant, and Lanczos's own coefficients reproduce a two-decimal table. See §4 Phase 0 for the provenance flag that remains on the two-term coefficients.)*

**The effective numerical rank is not a constant.** Earlier versions of this charter stated that the discretized operator "has an effective numerical rank of roughly 2–3 over a physiological range at realistic SNR" and treated that number as a premise. That was the wrong shape for the claim. The recoverable information is a function of SNR and of the range of decay constants under consideration, and the ~2–3 figure is a *consequence* of evaluating that function at one operating point. Two results fix the dependence.

*Minimum resolvable ratio of adjacent time constants.* Istratov & Vyvenko (1999), following McWhirter & Pike and Bertero et al., give a closed form. The singular values of the Laplace transform on the Mellin axis are |Γ(½ + iω)| = √(π / cosh πω); noise truncates the recoverable solution at the ω_max where the singular value falls to 1/SNR of the leading one, i.e. cosh(πω_max) = SNR², and the solution's resolution in ln T is π/ω_max. Adjacent time constants can be separated only if

$$\frac{T_{k+1}}{T_k} \;\gtrsim\; \delta(\text{SNR}) = \exp\!\left(\frac{\pi^2}{\operatorname{arccosh}(\text{SNR}^2)}\right) \;\approx\; \exp\!\left(\frac{\pi^2}{2\ln \text{SNR} + \ln 2}\right).$$

At SNR 10³ this is a ratio of about 2.0; at SNR 100, about 2.7; at SNR 30, about 3.7. The dependence is on ln SNR, so a tenfold increase in SNR buys only a modest improvement in resolvable ratio — which is the precise form of the statement that brute force does not help. The harness's discretized operator for a 32-echo, 10 ms train reaches a resolvable ratio of 3.16 at SNR 100 and 2.15 at SNR 1000 — the finite window costs a further factor of roughly 1.1–1.2 over the continuum value. *(The arccosh form is the exact continuum expression and is what the harness implements; Istratov & Vyvenko's printed form should still be checked against it for their SNR convention before the resolution test is cited to them.)*

*Informative singular directions.* Bertero, Boccacci & Pike (1982) show that the number of singular values above the noise level grows only **logarithmically** with SNR, and that restricting the support of f(T) to a known finite interval slows the singular-value decay and raises the count. The harness's Phase 0 conditioning study (`claude/phase0-findings.md`, §3) sharpens this in a way the continuum argument does not anticipate: **for realistic echo trains, the acquisition window — not the T-range — sets the count.** The operator cannot see T-values the time window does not probe, so widening the T-grid adds columns that lie in the numerical null space, and sampling density inside the window barely matters (8 echoes and 2000 samples over the same 10–80 ms window give the same count). For a CPMG train with TE₁ = ΔTE, the window's dynamic range t_max/t_min is exactly the echo number. The statement that survives the numerics, to within about ±1.5, is

$$N_{\text{inf}} \;\approx\; \frac{\ln \gamma_{\text{eff}}}{\pi^2}\,\operatorname{arccosh}(\text{SNR}^2) + 1, \qquad \gamma_{\text{eff}} = \min\!\left(\frac{T_{\max}}{T_{\min}},\ \frac{t_{\max}}{t_{\min}}\right),$$

and for the reference 32-echo, 10 ms train the measured counts are **3, 4, 5, 6 informative directions at SNR 30, 100, 300, 1000** (per-sample SNR convention; the energy convention credits the √N gain and adds about one). The singular-value ratios for that design fall by a factor ≈ 3.2–3.5 per index, verified against a 40-digit SVD.

**The practical figure, as a consequence — and its unit.** A K-component model has 2K parameters and needs at least 2K informative directions, so counts of 4–6 support **K = 2 comfortably across clinical SNR and K = 3 only toward the top of the clinical range (SNR ~300–1000)**. That is the "roughly 2–3" earlier versions asserted — but it is a count of *components*, not of numerical rank (which is 3–6 over the same range), and earlier versions did not say which. It survives as a property of SNR and acquisition window at a stated operating point, not as a property of the kernel. Longer windows (more echoes, or a second encoding dimension as in 2D T1–T2 correlation) and research-grade SNR raise it; austere budgets and low SNR lower it. The 2K rule is the harness's working criterion, a necessary condition for the linearized problem rather than a theorem about the nonlinear fit; the CRLB module (built 2026-09-07, `mexp/crlb.py`) turns it into a precision statement — see the threshold outcome below.

**That dependence — the map from (SNR, acquisition window, T-range) to informative directions and hence supportable K — is the single most important quantity in this project.** Phase 0 has now measured it for the T2 kernel rather than accepting either the closed forms or the ~2–3 figure on faith; the measured map, not the closed form, is what everything downstream is calibrated against.

**Falsifiable threshold.** The singular-value count is now measured, so what remains falsifiable is the step from directions to components and from components to usable precision. The "K = 2 comfortably, K = 3 marginal at clinical SNR" statement is retained until the CRLB module contradicts it at the reference configuration (32 echoes at 10 ms spacing, first-echo SNR 100, Rician magnitude, T2 support 10–300 ms). *(v0.9: the amplitude vector is now part of each clause, because the evaluation showed the outcome depends on it more than on placement or noise model; two vectors are named — equal amplitudes, and a 20/80 split with the minor component the shortest, which is the clinically relevant myelin-like case.)*

- **Revise upward** if the CRLB (Rician, σ known or jointly estimated) yields < 10% relative standard deviation on all three decay constants of a K = 3 ground truth with adjacent ratio 3 at SNR 100, at either named amplitude vector — i.e. K = 3 is comfortably estimable where the 2K rule says it is marginal.
- **Revise downward** if the K = 2 CRLB with adjacent ratio 4 exceeds 25% relative standard deviation on either decay constant at SNR 100 at equal amplitudes. (At the 20/80 vector the short constant is expected near 30%; that number is reported alongside, not used to fire the clause.)
- **Revise the window rule** if any design with the same echo count and window but different spacing changes the informative-direction count by more than one.

Either outcome is logged in §8, with the configuration that triggered it.

*Outcome, 2026-09-07 (`results/threshold_evaluation.md`; §8):* **none of the three fires.** K = 3 at ratio 3: the best all-three case is 70 / 103 / 30% (15/45/135 ms, equal amplitudes) and 72 / 156 / 60% at 20/60/180 ms — K = 3 is not estimable here, by a factor of 3–15 against the clause. K = 2 at ratio 4 at equal amplitudes: 11–14% / 5–9% across placements from 15/60 to 50/200 ms; at the 20/80 vector the short constant reaches 28–41%, which is why the vector is now named — under v0.8's unspecified vector the downward clause fired for 4 of 12 placement × amplitude cases and did not fire for the other 8. Window rule: for N = 32, 16 and 8 over a fixed window, uniform, log-spaced, Chebyshev, early-dense, late-dense and end-clustered placements change the count by at most one (log-spaced and early-dense placements never lose to uniform; late-dense and end-clustered lose one at high SNR). Rician versus Gaussian, and σ known versus jointly estimated, move these CRLBs by under 2% (relative) at first-echo SNR 100. The figure stands, with the precision behind it now measured rather than inferred from the 2K rule.

### 1.3 The governing constraint

The ill-posedness is a theorem about the Laplace kernel, not an engineering shortfall. Brute force cannot fix an exponentially decaying singular spectrum. The sloppy-model geometry of Transtrum, Machta & Sethna (*PRL* 2010; *PRE* 2011; *J. Chem. Phys.* 2015) is the modern statement of the same fact from the fitting side: the sum of exponentials is their canonical example of a model whose Jacobian singular values are spread roughly uniformly in log across many decades, so that the fit is well-determined along a few stiff directions and essentially undetermined along the rest. Genuine advances must come from one of three moves:

1. **Add information** — extra encoding dimensions, priors, joint estimation across voxels.
2. **Change the question** — estimate well-posed functionals rather than the ill-posed spectrum.
3. **Sharpen guarantees** — certified optimality, rigorous uncertainty sets, exact recovery conditions.

Any Phase 3 proposal should be classifiable into one of these. A proposal that fits none of them is probably rediscovering a known impossibility.

---

## 2. Modality Scope

T2 multi-echo relaxometry is the **primary testbed** — densest data, cheapest simulation, cleanest instance of the pure problem. But the harness is built with a **pluggable-kernel abstraction from day one**, because the contrasts across modalities are informative and nearly free once the abstraction exists.

### 2.1 What is invariant

All five modalities reduce to a Laplace-type transform of a positive measure, and all inherit exponential ill-conditioning. The Phase 0 conditioning analysis, the CRLB machinery, the benchmark harness, and the Phase 1 taxonomy are therefore **reusable essentially unchanged** across all of them. This is the unifying claim of the project.

### 2.2 What changes — five axes

| Axis | T2 (CPMG) | T1 (IR) | T2* (mGRE) | T1ρ | Diffusion |
|---|---|---|---|---|---|
| **Kernel** | Real Laplace | Affine-shifted Laplace + nuisance asymptote | **Complex** damped exponential | Real Laplace | Scalar Laplace in *b*, or **matrix-variate** Laplace on the PSD cone |
| **Sampling — grid** | Uniform | Uniform *available* (Look-Locker); irregular in classic IR | Uniform | Uniform available | Uniform in *b* available |
| **Sampling — budget** | Dense (32–64 echoes) | Few per inversion in classic IR; dense under Look-Locker | Dense | Few (4–8 TSL), SAR-limited | Few, bounded *b* (SNR floor) |
| **Data/noise** | Rician magnitude | Rician + **polarity ambiguity at null** | Complex Gaussian if retained | Rician | Rician, hard SNR floor at high *b* |
| **Dominant confound** | Stimulated echoes, B1 | **Exchange** (fast on T1 timescale) | B0 inhomogeneity, mesoscopic fields | B1/B0 banding, SAR | Restriction, time-dependence |
| **Free extra dimension** | — | — | **Frequency offset** | **Dispersion in ω₁** | **Direction, b-tensor shape, diffusion time** |

### 2.3 Consequences that actually matter

**Sampling is a design variable, not a gate.** *(Corrected from v0.1, which wrongly conflated two distinct failure modes and excluded a family on that basis. See Decision Log.)*

Few samples and irregular samples are different problems with different remedies:

- **Few samples** is a *conditioning* limit. It compresses the effective rank and raises the CRLB. It cannot be argued away, but it does not invalidate any method family — it degrades all of them, and the degradation is measurable. *(Refined in v0.8 from the Phase 0 findings: what binds is the acquisition window, t_max/t_min, not the number of samples inside it — 8 echoes and 2000 samples over the same window give the same informative-direction count. "Few samples" costs conditioning only insofar as it shortens the window; a sparse set of samples spanning the same window costs mainly the √N energy gain. This is what makes the sparse-ruler and co-array designs below worth testing rather than dismissing.)*
- **Irregular samples** is a *structural* obstruction, and only to the textbook forms of the linear-algebraic family, which exploit Hankel shift-invariance. It has well-developed workarounds.

Three routes keep family 2 alive under irregular or sparse sampling, all realizable on a scanner:

1. **Acquire uniformly instead.** Look-Locker / TOMROP samples densely and uniformly along a single recovery curve after one inversion — which restores the entire Prony family to T1 outright. T1ρ spin-lock times and diffusion b-values can likewise be placed on a uniform grid; the binding constraints there are SAR and SNR, i.e. budget, not geometry.
2. **Sample on a subset of a uniform grid, then complete.** Missing entries in the Hankel matrix are recoverable by structured low-rank matrix completion (EMaC, Chen & Chi 2014; ALOHA, Jin & Ye). This is the natural fit for expensive, budget-limited acquisitions.
3. **Use genuinely non-uniform generalizations.** The generalized Prony method (Peter & Plonka 2013) replaces shift-invariance with eigenfunctions of an arbitrary linear operator; Potts & Tasche extend Prony-like estimation to scattered data; Finite Rate of Innovation (Vetterli, Marziliano & Blu) handles arbitrary sampling kernels via annihilating filters.

There is also a design opportunity here worth pursuing on its own. Array processing solves the sparse-sampling problem with **co-array** geometries — co-prime, nested, and sparse-ruler arrays (Pal & Vaidyanathan) — where a small non-uniform sample set has a *difference set* that fills a dense uniform grid, and difference-domain methods then see a virtual full grid. TIs, TSLs, and b-values are freely choosable, so this transfers directly. A sparse-ruler placement of eight inversion times is a concrete, clinically realizable design that no one in the MR literature appears to have tested.

**Consequence for the plan:** sampling design becomes a first-class harness axis (§6.1), not a modality property. Every method family is scored across grid type × sample count × baseline extent, and irregularity is met with an adapted variant rather than an exclusion (guardrail G5).

**T2\* is structurally easier in one specific sense — but the comparison must be run, not assumed.** Retaining complex data with per-compartment frequency offsets converts the problem from real Laplace to sum-of-damped-complex-exponentials. The poles spread into the complex plane rather than crowding the real axis. Conditioning improves materially; Prony/ESPRIT/AAA/MUSIC become genuinely powerful rather than marginal; and Fourier-case super-resolution theory (Candès–Fernandez-Granda) applies far more directly than it does to the Laplace case.

That is a theoretical expectation, and it comes with costs that could plausibly cancel it. Phase is corrupted by things magnitude is immune to: B0 drift, motion, physiological noise, eddy currents, gradient delays, and coil-combination phase errors. Complex fitting also requires a field map and phase unwrapping, each with its own failure modes. So the practical question — how much does phase actually buy, under realistic corruption — is empirical.

**Three data representations are therefore a first-class harness axis, and every method is scored on all three:**

| Arm | Noise model | Requires | Notes |
|---|---|---|---|
| **Complex** | Gaussian | Raw/complex save, phase-preserving coil combine, B0 map, unwrapping | Best case; frequency dimension retained |
| **Phase-corrected real** | Gaussian | Phase correction only | Middle ground; kills Rician floor bias and IR polarity ambiguity without full complex modeling |
| **Magnitude** | Rician | Nothing | What clinical data is; the default deployment target |

The magnitude arm is not a fallback to be tolerated — it is the realistic deployment condition and gets equal weight. It also carries its own sub-taxonomy that belongs in the survey: Rician and non-central-χ likelihood fitting, noise-floor offset models, squared-magnitude/power-image bias correction, and Koay–Basser correction.

The clean quantitative deliverable is a **CRLB comparison across the three arms** as a function of SNR, frequency separation, and component count. That answers "what is phase worth" in information units, independent of any estimator, and tells you whether sequence modifications to save complex data are justified for a given application. If the gap is large, that is a concrete argument for the sequence work; if small, it is a saved effort.

**T1 has a physics problem alongside the math problem — but it is a statement about a regime, not an impossibility.** *(Reframed from v0.1, which overstated this. See Decision Log.)*

Water exchange between compartments is fast relative to T1 recovery but slow relative to T2 decay, so in the fast-exchange limit the compartments average toward a single apparent T1 and the information is attenuated before the estimator sees it. Three qualifications matter:

- It is governed by the ratio of exchange rate to relaxation rate difference, which varies by tissue, field strength, and pathology. The intermediate-exchange regime is not empty, and it is exactly where the problem is interesting.
- The correct response is **reparameterization, not abandonment.** Fit a Bloch–McConnell two- or three-pool model — pool fractions, exchange rates, intrinsic T1s — instead of a sum of exponentials. The question then becomes identifiability of *that* model, which is a well-posed question with a real literature and is answerable by the same CRLB machinery.
- Quantitative magnetization transfer and CEST routinely fit multi-pool exchange models and are among the few places where multi-pool parameters are reliably identified. Like diffusion, these should be **mined for transferable technique**, not treated as adjacent fields.

The instructive case study is **mcDESPOT** (Deoni), which fits a two-pool exchange model to combined SPGR/bSSFP data, and Lankford & Does's precision analysis of it (*MRM* 2013), which is a CRLB-based degeneracy critique. That pairing — an ambitious multi-pool fit and a rigorous demonstration of what it can and cannot resolve — is a template for how Phase 2 should treat every method.

**T1 probing sequences to survey (all of them, not just IR):** inversion recovery and fast/EPI variants; saturation recovery (no polarity ambiguity, shorter TR); **Look-Locker / TOMROP** (dense uniform sampling — see the sampling discussion above); MOLLI, ShMOLLI, SASHA, SAPPHIRE; variable flip angle / DESPOT1-SPGR; DESPOT1-HIFI; mcDESPOT; MP2RAGE; MR Fingerprinting with pseudorandom flip/TR trains; steady-state free precession variants; variable-TR and partial-saturation schemes; adiabatic vs. non-adiabatic inversion with inversion efficiency as a nuisance parameter; and MT-prepared/qMT variants.

Note that these differ in forward model, not merely in sampling. DESPOT1 and MRF are not sums of exponentials at all — steady-state nonlinear estimation in flip angle and dictionary matching against a simulated manifold respectively. Both belong in the survey; both need their own kernel plugin.

**T1ρ offers a free second dimension.** T1ρ dispersion — the dependence of T1ρ on spin-lock amplitude ω₁ — encodes chemical exchange through the Trott–Palmer / Chopra-type models. This converts a hopeless 1D inversion into a 2D problem with a *physically parameterized* second axis: fitting the dispersion curve yields exchange rate and population, not just an apparent decay constant. It is the cheapest available instance of the Phase 3 "add information" strategy and should be an early target.

**T1ρ variants to survey:** continuous-wave spin-lock; composite and rotary-echo spin-lock for B1/B0 compensation; adiabatic T1ρ and T2ρ; off-resonance spin-lock with variable effective field angle (which sweeps between T1ρ and T2ρ regimes and adds a *second* free axis beyond ω₁); T1ρ dispersion with Trott–Palmer, Chopra, and Bloch–McConnell-derived models; RAFF; and spin-lock preparation combined with different readouts (FSE, GRE, bSSFP), which changes the confound structure without changing the kernel.

**Diffusion is the most mathematically developed instance and should be mined, not appended.** Three reasons:

- *Multidimensional diffusion encoding* (b-tensor shape variation, Topgaard and colleagues) is the field's best existence proof that redesigning the encoding operator resolves degeneracies that no estimator could resolve. It directly validates the Phase 3 kernel-design direction.
- The *diffusion tensor distribution* lifts the problem to a Laplace transform over the cone of positive semidefinite matrices — a genuinely richer object with its own theory (Wishart priors, Jian et al.; de Almeida Martins & Topgaard).
- The *degeneracy of the white-matter standard model* (Novikov, Veraart, Jelescu, Fieremans) is the most rigorously characterized bimodal-landscape pathology anywhere in MR parameter estimation. It is the same disease this project studies, diagnosed more carefully than the T2 literature has managed.

**Diffusion encodings and models to survey:** single-diffusion-encoding PGSE with variable b; multi-shell schemes; oscillating gradient spin echo for diffusion-time dependence; double diffusion encoding; b-tensor shape variation (linear/planar/spherical); q-space and ensemble average propagator methods; DTI, DKI, and higher-order cumulant expansions; IVIM as the canonical two-compartment case; spectral/NNLS diffusion-spectrum inversion; diffusion tensor distributions with Wishart and maximum-entropy priors; the standard model and its constrained variants (NODDI, SMT, WMTI); Kärger exchange models and FEXI; anomalous-diffusion and fractional-order formulations; and joint T2–diffusion and T1–diffusion correlation acquisitions.

**Net assessment:** the estimation *machinery* transfers across all five modalities with minor adaptation. The *strategy* does not — it is set by which extra dimensions are available and which physics confounds dominate. Treat modality as a first-class axis of the Phase 1 taxonomy rather than a footnote.

---

## 3. The Noise Problem

Noise is not a nuisance term bolted onto the signal model. It is a co-equal estimation problem, and in the magnitude case it is **structurally entangled** with the parameter of greatest interest. This section is a full track, not a caveat.

### 3.1 The central structural fact

The noise distribution in an MR image is a property of **the reconstruction pipeline**, not of MRI. In raw k-space, thermal noise is circularly symmetric complex Gaussian, white, with a per-channel covariance Ψ. Every pathology below is manufactured downstream by magnitude operations, coil combination, acceleration, and regularized reconstruction.

This has a direct and important consequence: **fitting parameters directly from k-space sidesteps the distributional problem entirely.** Model-based estimation of θ from raw data under the known Gaussian likelihood never encounters Rician bias, non-central χ, spatially varying σ, or the intractable output distribution of a nonlinear reconstruction. It also eliminates Gibbs ringing bias structurally, since k-space truncation is part of the forward model rather than an artifact to be corrected afterward.

But raw access is not reliably available, so this does not retire the downstream problem. Both pathways are in scope as co-equal arms (§3.6), and the relationship between them is more useful than either alone.

### 3.2 The degeneracy that matters most

In magnitude data, the Rician noise floor contributes an approximately constant offset at long decay times. A constant offset is indistinguishable from a component with T → ∞.

**There is therefore a structural degeneracy between σ and the longest decay component.** This is not a small bias correction. It means:

- Misestimating σ directly biases long-T2 fraction, myelin water fraction, and any functional weighted toward slow components.
- The Fisher information must be computed for the **joint** parameter vector (θ, σ), not for θ with σ assumed known. The Schur complement of the joint FIM quantifies exactly how much precision is lost by not knowing σ.
- Common practice — fitting a free constant offset term — is an *implicit* σ estimate, and an inefficient one that discards known distributional structure.

This yields a third named sub-study alongside sampling design and value-of-phase: **value-of-noise-knowledge**, the CRLB gap between σ known exactly, σ estimated jointly, and σ estimated from a separate procedure with its own error. It is well-posed and cheap to compute.

**What is and is not new here.** *(Narrowed in v0.7 after the Phase 1 pass-1 sweep; v0.1–v0.6 claimed the joint (θ, σ) analysis "has not been done systematically for multi-exponential relaxometry", which was too broad.)* Joint estimation of a signal amplitude and σ from Rician magnitude data is old: Benedict & Soong (*IEEE Trans. Inf. Theory*, 1967) solved it for the sum envelope in radar, and Sijbers & den Dekker (*MRM*, 2004) gave the joint ML estimator and the joint CRLB for the single-amplitude MR case. Rician-correct CRLBs for decay models exist: Karlsen, Verhagen & Bovée (*MRM*, 1999) for T1 and perfusion, and Bouhrara, Reiter, Celik, Bonny, Lukas, Fishbein & Spencer (*MRM* 73:352–366, online 2014) for biexponential T2 under Rician noise. And the free-offset practice is documented rather than merely folklore: Milford, Rosbach, Bendszus & Heiland (*PLoS ONE*, 2015) characterize the effect of a free offset term in T2 fitting, which is exactly an *uncharacterized* handling of the degeneracy above — they measure what the offset does to the fit without deriving what it costs in information. What the sweep did **not** find, and what this sub-study therefore claims, is narrower: the joint Fisher information for the **multi-exponential** parameter vector with σ as a nuisance parameter, its **block inverse** — the Schur complement of σ against (a_k, T_k) for K ≥ 2 — and an **analytic description of the σ / long-T degeneracy manifold** with identifiability conditions. The novelty claim is confined to that. (Gaps register A3, status PARTIAL.)

*Phase 0 bound-level probe (2026-09-07, `mexp/crlb.py`; see §10 step 6).* Under the correct single-coil Rician likelihood with 32 echoes, the joint CRLB with σ as a nuisance parameter lies within 2% of the σ-known CRLB for the decay constants at first-echo SNR 100 and 30, both for a 20/80 two-component truth and for a three-component truth carrying a 2000 ms component (which is itself unrecoverable, at 450–1500% relative SD): the data pin σ to ≈ 1/√(2N) = 12.5% on their own, and the amplitude–σ cross-information is small wherever the signal is well above the floor. This does not touch the misspecification cost of a Gaussian or free-offset fit to Rician data, χ or non-stationary pipelines, or an externally estimated σ — which is where the value-of-noise-knowledge ladder's cost must live if it is large, and where the analytic work should look first.

### 3.3 Noise statistics through the pipeline

Every stage is a harness configuration, and each changes the distribution family, its stationarity, or both.

| Stage | Complex | Magnitude | Stationary? |
|---|---|---|---|
| Single coil, raw | Gaussian, white | **Rician** | Yes |
| Multi-coil, sum-of-squares | — | **Non-central χ**, 2L DOF | Yes |
| Multi-coil, correlated channels | Gaussian, covariance Ψ | Non-central χ, **non-integer effective DOF** | Yes |
| Roemer / adaptive combine | Gaussian | **Rician** (not χ) | Approximately |
| SENSE | Gaussian | Rician, **σ·g·√R** | **No** — g-factor map |
| GRAPPA | Correlated Gaussian | χ-like, **spatially varying σ *and* effective DOF** | **No** |
| Partial Fourier / homodyne | Correlated, real/imag imbalance | Modified | No |
| Compressed sensing / iterative | **No closed form** | **No closed form** | **No** |
| Deep-learning reconstruction | **No closed form**, error is structured and signal-correlated | Same | **No** |

Two points deserve emphasis. First, the coil-combination method determines the distribution *family* — Roemer gives Rician, sum-of-squares gives non-central χ — so "multi-coil means chi" is wrong as often as it is right. Second, prewhitening by Ψ^(−1/2) from a noise-only prescan restores the idealized model and is the cheapest available intervention; it should be a baseline, not an advanced option.

**Compressed sensing and DL reconstruction break closed-form analysis entirely.** Soft-thresholding introduces signal-dependent shrinkage bias; TV produces structured, spatially correlated residuals; the regularization weight itself determines how much "noise" remains. There is no distribution to write down. This is not a gap in the literature to be filled by more careful algebra — it is a genuine boundary, and it is where the interesting work is.

### 3.4 Noise estimation methods to survey

Family 7 of the Phase 1 taxonomy (§4), scored on the harness like every other family.

1. **Noise-only prescan** — direct Ψ estimation with RF off. Gold standard for thermal noise; blind to physiological noise; requires scanner access.
2. **Background/air region** — Rayleigh or χ fit to signal-free regions. Fails under parallel imaging (background statistics differ from tissue), and fails outright when the scanner masks or filters background, which many do.
3. **Histogram and mode-based** — fit the low-intensity mode of the intensity distribution.
4. **Local moment estimators** — local mean/variance relationships in homogeneous regions; Aja-Fernández's local σ and effective-DOF estimators, which handle spatial non-stationarity directly and are the natural fit for SENSE/GRAPPA.
5. **Robust/wavelet** — median absolute deviation of finest-scale wavelet coefficients (Donoho–Johnstone); resistant to outliers and spike noise.
6. **Maximum likelihood on the correct family** — joint ML over (θ, σ) under Rician or non-central χ; Koay–Basser correction; EM formulations.
7. **Repeated-acquisition differencing** — subtract two identical acquisitions. Clean in principle, defeated by motion and drift.
8. **Random matrix theory / MP-PCA** — Marchenko–Pastur analysis of the eigenvalue spectrum (Veraart et al. 2016), NORDIC (Moeller et al.). **This family deserves special attention**, for a reason given in §3.5.
9. **Variance-stabilizing transforms** — Anscombe-type transforms for Rician and χ (Foi 2011), converting to approximately homoscedastic Gaussian so standard machinery applies.
10. **Monte Carlo / pseudo-replica** — Robson et al. 2008. Re-reconstruct many synthetic noise realizations and measure empirical variance. The only method that survives nonlinear reconstruction; expensive but general.
11. **SURE-based** — Stein's unbiased risk estimate and Monte-Carlo SURE (Ramani, Blu & Unser), both for regularization tuning and residual error characterization.
12. **AMP state evolution** — for CS with suitable measurement operators, approximate message passing predicts the effective noise at each iteration is Gaussian with a tracked variance. A genuine theoretical handle where none otherwise exists, and largely unexploited in MR.
13. **Bootstrap/jackknife over k-space subsets** — distribution-free, expensive, assumption-light.
14. **Conformal prediction** — distribution-free finite-sample intervals that remain valid when the noise model is wrong. The natural answer to DL reconstruction.

**Non-thermal error sources that get lumped into "noise" and shouldn't be:** physiological fluctuation (scales with signal, not additive), B0 drift, ADC quantization, RF spikes and interference (outliers, motivating robust loss), motion, and **Gibbs ringing** — a deterministic error that masquerades as noise and measurably biases relaxometry and diffusion estimates. Each needs to be separated, not absorbed.

### 3.5 The connection worth exploiting

MP-PCA estimates the noise level *and* the number of signal components simultaneously, by separating eigenvalues that follow the Marchenko–Pastur law from those that do not.

Estimating the number of components is the same problem as estimating K in multi-exponential fitting.

That is not an analogy. A voxels × echoes decay matrix has low rank plus noise, and random matrix theory provides an asymptotically principled rank estimator together with a σ estimate — addressing model-order selection and noise estimation in one stroke, from data that is already being acquired. The gap is that the relaxometry decay matrix is not an unstructured low-rank matrix: its columns are constrained to a Vandermonde-like manifold. RMT for structured random matrices is a live area, and pushing it onto this structure is a concrete, well-posed Phase 3 target.

### 3.6 Data access levels and the two-arm architecture

Both pathways are developed fully and neither is subordinate. The raw-data arm is pursued as though raw access were guaranteed; the image-domain arm is pursued as the deployment reality. They are not separate projects, and three relationships between them do real work.

**The k-space arm is the reference standard for the image arm.** Where raw data exists, both arms run on the *same acquisition*, and the gap between them is the **cost of reconstruction** measured in parameter precision. Nobody currently measures this. Acceleration and reconstruction choices are justified on image appearance, not on downstream parameter variance, so the field has no answer to "what did that R=4 acquisition cost my myelin water fraction estimate?" The k-space arm answers it — which makes it valuable during development even for methods that will only ever deploy on magnitude images, because it establishes what was lost rather than merely what was achieved.

**Consequence for Phase 0: the simulator must be k-space-first.** This is a binding design constraint, not a preference. Generating images and adding Rician noise assumes the answer — it bakes in a stationary closed-form distribution that the real pipeline does not produce. The simulator must instead generate k-space, apply coil sensitivities, add complex Gaussian noise with a realistic channel covariance, and then *actually run* SENSE, GRAPPA, partial Fourier, and CS reconstructions to produce image-domain data. Only then is the non-stationary, correlated, signal-dependent noise in §3.3 real rather than assumed, and only then are both arms consuming the same ground truth. Retrofitting this later would invalidate every image-domain result produced before it.

**Access is a ladder, not a binary.** Each method in the taxonomy is tagged with the minimum level it requires, and under G5 each must also have a characterized degraded variant at L5–L6.

| Level | Available | Enables |
|---|---|---|
| **L0** | Raw k-space + noise prescan + sensitivity maps | Exact Gaussian likelihood, prewhitening, full model-based estimation |
| **L1** | Raw k-space only | As L0, with Ψ and sensitivities estimated from the data |
| **L2** | Per-coil complex images | Post-FT, pre-combination; Ψ still estimable; distribution tractable |
| **L3** | Coil-combined complex images | Gaussian, but reconstruction-induced correlation unknown |
| **L4** | Magnitude + pipeline metadata (R, algorithm, g-factor map) | Parametric noise model with known structure |
| **L5** | Magnitude + protocol knowledge only | Noise family assumed, parameters estimated from data |
| **L6** | Magnitude, pipeline unknown (DICOM only) | Blind identification or distribution-free methods only |

L6 is where most retrospective and multi-site data actually lives, which makes it the level with the highest practical stakes and the least theoretical support.

**The bridging problem: blind pipeline identification.** Given magnitude images and no metadata, how much of the reconstruction pipeline can be recovered from the data itself — effective degrees of freedom, the spatial σ map, the correlation structure, the acceleration factor? Components exist (Aja-Fernández's effective-DOF and local σ estimators), but framed as *"recover enough of the forward pipeline to write down a usable likelihood"* this is a coherent and unclaimed research target. It is the bridge that lets L6 data borrow the machinery built for L0, and it belongs in Phase 3.

A related and cheaper move: **calibration transfer.** Where a protocol yields both raw and magnitude data for some scans, characterize the pipeline's noise transformation once and transfer it to magnitude-only scans from the same protocol. Practical, testable, and under-explored.

**Honest limits of the k-space arm.** It dissolves the distributional pathology *manufactured by reconstruction* — not all error. Physiological fluctuation, B0 drift, motion, and RF spikes are not Gaussian in k-space either, so §3.4's non-thermal sources survive the move and still need separate treatment. And the arm carries its own costs: joint reconstruction-and-estimation is a large nonlinear inverse problem with its own local minima, substantial computational expense, and a dependence on accurate coil sensitivities and trajectory knowledge. It is the cleaner formulation, not the free one.

### 3.7 Phase 3 directions specific to noise

- **Joint (θ, σ) identifiability, characterized analytically.** Map the degeneracy manifold between σ and long-T decay components for the multi-exponential model, K ≥ 2 — building on the single-amplitude joint estimators (Benedict & Soong 1967; Sijbers & den Dekker 2004) and the Rician-correct decay CRLBs (Karlsen 1999; Bouhrara et al. 2014) rather than duplicating them. Determine the conditions under which the joint problem is identifiable, and prove them.
- **Structured random matrix theory** for simultaneous K and σ estimation, per §3.5.
- **End-to-end uncertainty propagation through CS reconstruction** via AMP state evolution, carrying a calibrated effective noise from k-space through reconstruction into parameter estimation. Currently nobody propagates reconstruction uncertainty into relaxometry uncertainty at all; parameter maps from accelerated acquisitions are reported with error bars that assume the reconstruction was noiseless.
- **Distribution-free and semiparametric estimation** — M-estimation with robust loss, empirical likelihood, Huberized likelihoods. Protects against the CS/DL case where no closed-form noise model exists, at a quantifiable efficiency cost that should be measured rather than assumed.
- **Noise-aware and minimax experimental design** — sampling that maximizes information about θ under *uncertainty* in σ, rather than assuming σ known.
- **Model-based estimation directly from k-space**, per §3.1 — the structural solution rather than a correction, pursued fully under the two-arm decision (§3.6).
- **Blind pipeline identification** — recover effective DOF, spatial σ, and correlation structure from magnitude images alone, sufficient to write down a usable likelihood at access level L6. The bridge between the two arms.
- **Cost-of-reconstruction quantification** — the paired k-space/image comparison that measures acceleration and reconstruction choices in units of parameter variance rather than image appearance.

---

## 4. Phases

### Phase 0 — Foundations and instrumentation

Build the apparatus to judge methods before surveying them.

- Derive and numerically confirm the conditioning story: SVD of the discretized kernel vs. SNR, echo count, acquisition window, and T-range — checked against the closed-form Mellin-space singular values (Epstein & Schotland 2008; McWhirter & Pike 1978) — as a check on the count and the decay rate, not index by index: with a covering window the numerical count agrees with (ln Γ/π²)·arccosh(SNR²) to about ±2, but σ₁/σ₀ is ≈ 0.33 for every Γ ≥ 100 against 0.48–0.78 from uniform Mellin quantization, and the weighting chosen for f (L²(dT) versus L²(d ln T)) moves the count by 1–3, so the closed form is asymptotic in index just as the BBP counting argument is (v0.9) — and producing the (SNR, window, T-range) → informative-direction map that §1.2 now rests on, together with the falsifiable threshold stated there. **Done for the T2 kernel, 2026-09-07** (`claude/phase0-findings.md` §3; `scripts/phase0_conditioning.py` reproduces every number). The Picard plot with Hansen smoothing is the operational diagnostic, and it doubles as a grid-coverage check: a truth component outside the T-grid shows up as Picard coefficients that stop decaying with the singular values.
- **Reproduce Lanczos's degeneracy example (*Applied Analysis*, 1956, ch. IV) as the harness's first correctness test.** A three-exponential function, f(t) = 0.0951·e^(−t) + 0.8607·e^(−3t) + 1.5576·e^(−5t), whose 24 samples on t = 0, 0.05, …, 1.15, tabulated to two decimals, are reproduced by a two-exponential sum: Lanczos's own 2.202·e^(−4.45t) + 0.305·e^(−1.58t) matches the two-decimal table at 23 of 24 points; the optimal two-exponential approximant 2.0688·e^(−4.6396t) + 0.4440·e^(−1.8725t) agrees with f to 8.8 × 10⁻⁴ (three decimal places); and separating the two models needs peak-to-σ SNR above ~3.6 × 10³ even for an oracle detector. The test (restructured in v0.9 to the (a)/(b) criteria v0.7 set) checks: that the T2 kernel reproduces the NIST Lanczos1 table (to 4.8 × 10⁻¹³); (a) that the harness's *own* best two-exponential fit on the grid — computed inside the test with `scipy.optimize.least_squares` driven by the kernel's forward model and analytic Jacobian, so that `mexp/` itself still contains no estimator — agrees with f to better than 0.001 (8.8 × 10⁻⁴) and coincides with the frozen approximant, which is separately verified as a stationary point; that the quoted coefficients deviate by 0.0064 at t = 0 and by at most one two-decimal rounding from the table; and (b) that the two- and three-component models are indistinguishable at any noise level above that residual — for every σ ≥ 8.8 × 10⁻⁴ the expected excess χ² of the two-component model, ‖Δ‖²/σ², is ≤ 5.5 < χ²₂(0.95) = 5.99, and the K = 3 CRLB puts two of the three decay constants above 100% relative SD while the two-exponential description is determined to < 3%. **Correctness test #1 passes, 2026-09-07 — provisional pending the book check (pytest marker `provisional_pending_primary`).** *(v0.1–v0.6 described this as "two very different 3-exponential sums agreeing to 3 decimal places"; corrected in v0.7; precision and provenance made exact in v0.8.)*

  **Provenance flag (narrowed in v0.8).** The three-exponential coefficients and the 24-point grid are locked from a primary-quality source: NIST StRD Lanczos1–3 cite Lanczos (1956) pp. 272–280 for the generating function, and the certified Lanczos1 fit returns the six constants to 10⁻¹⁰. The 0.0064 discrepancy that v0.7 flagged as an inconsistency is explained by the two-decimal tabulation — Lanczos's coefficients reproduce his table, and the 0.001 figure belongs to the optimal approximant. What is *still* recalled rather than fetched is Lanczos's own two-term coefficients (2.202, 4.45; 0.305, 1.58) and the two-decimal statement, attributed to p. 276: the book check remains open (`claude/phase0-harness-status.md`, item 2) and is marked in `mexp/datasets/lanczos.py`. The test does not depend on those coefficients — it locks on NIST and on the harness's own optimal approximant — so the book check can be closed without re-running anything. The flip side, from NIST Lanczos3 (five significant digits, SNR ≈ 9 × 10⁴): the certified three-exponential fit moves the slow component to 0.0868·e^(−0.955t) with certified standard deviations of 0.017 and 0.097, and that wrong answer fits the rounded data *better* than the truth does. That is the same lesson at the other end of the SNR axis.

  *Narrowed further in v0.9.* The 0.0064 deviation is at t = 0, which is on every candidate grid, so no choice of grid rescues a 0.001 reading of the quoted coefficients — the two-decimal reading is the only one consistent with them. And the quoted pair is closer to the least-squares optimum on a Δt = 0.1 grid over [0, 2.3] (2.1885, 4.5035; 0.3236, 1.5963) or over Varah's [0, 3.2] (2.2156, 4.4682; 0.2961, 1.5247) than to the NIST-grid optimum, so Lanczos's own table may be Δt = 0.1 over a longer window, as v0.7 suspected. The book check should therefore record four things: Δt, the number of points, the decimals in the table, and whether Lanczos states a number or "within the accuracy of the data". One caveat on v0.7's provenance: the 1982 technical-report version of Varah's paper does not quote the two-term coefficients (it says Lanczos's example decays too fast and generates its own Δt = 0.1, n = 33 data), so the 1985 journal version should be checked before Varah is cited for them.
- Compute Cramér–Rao lower bounds for K=2,3 as a function of separation ratio and SNR. This is the floor no algorithm can beat, and it immediately identifies impossible published claims. **Module built 2026-09-07** (`mexp/crlb.py`): Gaussian real and complex, and Rician with σ known or jointly estimated — per-sample Fisher blocks computed from the exact Rician likelihood (Gaussian and Rayleigh limits tested) and pushed through the kernel Jacobian, which is the numerical K ≥ 2 joint (θ, σ) block that §3.2 names. Not an estimator; nothing fits data. The §1.2 threshold has been evaluated with it (outcome there and in §8); the K = 2, 3 sweep over separation ratio and SNR is one script call away and is run per kernel as each is registered.
- Synthetic data generator with ground truth: discrete and continuous spectra, plus a physically realistic path (Bloch/EPG with flip-angle error and stimulated echoes).

**Standing rule — the generator is k-space-first (§3.6).** It synthesizes k-space, applies coil sensitivities, adds complex Gaussian noise with realistic channel covariance, and runs *actual* reconstruction algorithms to produce image-domain data. Generating a synthetic image and adding noise to it by formula is **not permitted**, at any stage, for any purpose that feeds the taxonomy. *(Enforced mechanically in the harness since 2026-09-07: `mexp.sim.add_kspace_noise` is the sole noise entry point, and `tests/test_kspace_first_rule.py` fails the suite if an RNG or image-domain noise model appears outside `mexp/sim`. The Phase 0 conditioning study drew no noise realization at all — SNR entered only as a threshold.)*

  *Why this is a rule and not a preference.* The shortcut is faster to code and will look correct. It assumes a stationary closed-form noise distribution — precisely the thing §3.3 shows real pipelines do not produce — which makes any result touching the noise, reconstruction, or data-access axes circular. The failure is silent: contaminated results are indistinguishable from sound ones until the first comparison against real reconstruction noise, at which point the contaminated subset cannot be identified and everything must be re-run. The rule exists because the temptation arrives later than the decision does.
- Fix evaluation metrics (§6) before running anything.

**Foundational results the harness must encode.** *(Added in v0.7. The Phase 1 pass-1 sweep found these absent from the charter entirely; each is a classical result that a later phase would otherwise rediscover or, worse, contradict.)*

| Result | What it establishes | Where it plugs in |
|---|---|---|
| **McWhirter & Pike (1978); Bertero, Boccacci & Pike (1982); Istratov & Vyvenko (1999)** | Mellin-domain diagonalization of the Laplace kernel; recoverable count grows as ln SNR and improves with restricted support; closed form for the minimum resolvable ratio of adjacent time constants | §1.2 directly. The Phase 0 SVD map is checked against these before anything else is trusted |
| **Epstein & Schotland (2008), *The bad truth about Laplace's transform*** | Closed-form singular values and singular functions of the Laplace transform, with the decay rate made explicit | The analytic reference for the Phase 0 numerical SVD; the object any Phase 3 sharp-constant result (gaps register B1) is stated in terms of |
| **Ostrowsky, Sornette, Parker & Pike (1981), exponential sampling** | The dilation-invariance of the Laplace transform gives a sampling theorem in the *solution* domain: f(T) band-limited in Mellin frequency is determined by samples on a geometric grid in T with spacing set by ω_max | The principled basis for log-spaced T grids in the regularized-inversion family (NNLS/CONTIN grids are not arbitrary); connects to the harness "log-spaced" sampling level and to the resolution limit in §1.2 |
| **Transtrum, Machta & Sethna — sloppy models (2010, 2011, 2015)** | The sum of exponentials as the canonical sloppy model: Jacobian singular values spread evenly in log across many decades; model-manifold boundaries where components merge or vanish; geodesic-acceleration and manifold-boundary methods for fitting | §1.3. Explains why multistart and LM struggle on this landscape, predicts where the VARPRO objective's critical points lie (gaps register B5), and supplies the geometry that "estimate functionals, not spectra" (Phase 3) exploits |
| **Bates & Watts (1980; 1988) — curvature decomposition** | Splits nonlinearity into *intrinsic* curvature (of the model manifold) and *parameter-effects* curvature (of the parameterization); gives the relative-curvature measures that predict when linearized (Hessian) confidence regions fail | §6.2 uncertainty calibration. The classical diagnostic of the "standard-error-from-the-Hessian fiction" that Phase 3's certified-uncertainty direction and gaps register B6 aim to replace — a result there must be positioned against it |
| **Rife & Boorstyn (1974) — single-tone CRLB** | For a sinusoid in white Gaussian noise, the frequency CRLB scales as 1/(SNR · N³): resolution improves *polynomially* with record length | The contrasting case. Fourier-side super-resolution (Candès–Fernandez-Granda, Prony-family guarantees) inherits this benign scaling; the Laplace CRLB has no N³ gain and its resolution improves only as ln SNR. Every "this works for sinusoids" transfer claim in Phase 1 family 2 and Phase 3 family 4 is checked against this contrast before it is believed |

*Phase 0 status (v0.9).* Encoded: McWhirter–Pike / BBP / Istratov–Vyvenko (count, and both R_min conventions side by side in `conditioning.r_min`); Epstein–Schotland (count-and-decay-rate check, with the per-index caveat in the first bullet above); Ostrowsky et al. (`conditioning.ostrowsky_spacing`, the geometric solution-grid ratio ln δ below which grid points carry no independent information at a given SNR); Transtrum–Machta–Sethna (FIM-spectrum diagnostic — the K = 3 spectrum at SNR 100 spans more than six decades roughly evenly in log); Rife–Boorstyn (test: the single-tone frequency CRLB falls by 8.0 from N = 32 to 64 while the T2 CRLB improves by under 10% once the window exceeds ~6 T2). Not yet: Bates & Watts, which waits on the §6.2 calibration metric and hence on estimators.

**Deliverable:** benchmark harness with pluggable kernels. Everything in Phases 1–3 is scored on it. The pass-1 sweep upheld that **no open, ground-truth benchmark for multi-exponential MR parameter estimation exists** (gaps register E1, with the nearest neighbours and why each falls short cited there), so the harness is also a resource contribution independent of any result obtained with it.

### Phase 1 — Systematic survey

Seven families *(the seventh, noise, added in v0.3)*. Anchor read: Istratov & Vyvenko, *Exponential analysis in physical phenomena*, Rev. Sci. Instrum. 1999 — read after the Phase 0 foundations table above, not instead of it.

1. **Nonlinear least squares** — Levenberg–Marquardt, trust-region, multistart. **Variable projection** (Golub & Pereyra 1973) eliminates the linear amplitudes and reduces the search to the T_k. Almost always the right baseline.
2. **Prony-type / linear-algebraic** — Prony (1795) → Kumaresan–Tufts (1982) → LPSVD/HSVD → matrix pencil (Hua & Sarkar) → ESPRIT, MUSIC. Hankel structured low-rank approximation, Cadzow denoising, Filter Diagonalization (Mandelshtam & Taylor 1997). Underused in MR: **AAA rational approximation** (Nakatsukasa–Sète–Trefethen) — poles of the rational fit are the decay rates.
3. **Regularized inversion** — NNLS (Lawson–Hanson), regularized NNLS (Whittall & MacKay 1989), CONTIN (Provencher 1982), Tikhonov, TSVD, iterative regularization with early stopping. Parameter selection: L-curve, GCV, discrepancy principle, χ².
4. **Sparse / off-the-grid** — ℓ₁ and non-negative sparse coding; then BLASSO / TV-of-measures, atomic norm, SDP relaxations, sliding Frank–Wolfe. Candès–Fernandez-Granda super-resolution is the Fourier case; the Laplace case is materially harder and less settled. **This gap is revisited in Phase 3.**
5. **Bayesian** — Bretthorst, *Bayesian Spectrum Analysis and Parameter Estimation*. MCMC/HMC, nested sampling for evidence-based K selection, reversible-jump MCMC, variational Bayes, hierarchical cross-voxel pooling, simulation-based inference.
6. **Learning-based** — direct regression, dictionary matching (MR Fingerprinting), unrolled optimization, physics-informed and score-based priors. Surveyed with one standing question: how much apparent performance is prior-injection that fails silently out-of-distribution?

7. **Noise and error modeling** — the fourteen approaches enumerated in §3.4, plus separation of non-thermal error sources. Scored on the same harness, and additionally on joint (θ, σ) estimation quality rather than σ accuracy alone.

**Cross-cutting — where most real-world error originates:**

- *Model misspecification:* stimulated echoes and B1 (EPG fitting, Prasloski et al. 2012 MRM); Rician noise-floor bias; inter-compartment exchange (Bloch–McConnell), which makes the model **wrong**, not merely hard; non-exponential relaxation (stretched exponential, fractional-order Bloch, Mittag-Leffler).
- *Extra dimensions:* 2D T1–T2 and T2–diffusion inversion (Venkataramanan, Song & Hürlimann 2002). A second encoding dimension breaks degeneracies no 1D algorithm can break. Probably the most important practical lever in the field.
- *Spatial/joint estimation:* subspace methods (T2 shuffling, Tamir et al.), locally low-rank, joint sparsity, model-based reconstruction from k-space rather than voxel-wise post-fitting.
- *Experimental design:* CRLB- or Bayesian-optimal choice of sampling points.

**Deliverable:** structured taxonomy. Per method: assumptions, sampling requirements, noise model, failure mode, modality applicability, benchmark score.

### Phase 2 — Honest comparison

Everything on the same harness. Expected finding: most methods cluster near the CRLB in the easy regime and all fail in the hard one; the spread between methods is smaller than the spread between acquisition designs. Document which published performance claims survive a fair benchmark.

### Phase 3 — Frontier

Ordered by current assessment of promise:

- **Estimate functionals, not spectra.** Backus–Gilbert theory (1968) finds the best-resolved linear functional of an unknowable model. Myelin water fraction *is* a functional. It may be well-posed where f(T) is hopeless. Startlingly under-exploited in MR; first place to look for a real result.
- **Exploit positivity properly.** Non-negativity dramatically improves super-resolution limits for sparse measures. The theory (Denoyelle, Duval, Peyré and related) has not been pushed to the Laplace kernel with sharp constants. Genuine open theory, tractable.
- **Moment-problem reformulation.** Under x = e^(−Δt/T), samples are moments of a positive measure — opening Hausdorff/Stieltjes machinery, Christoffel–Darboux kernels, and Lasserre's moment-SOS hierarchy, including **global-optimality certificates** for the nonlinear fit, which nobody currently has.
- **Certified uncertainty.** Optimal-recovery/minimax framing for rigorous confidence sets over model classes, replacing the standard-error-from-the-Hessian fiction.
- **Kernel design.** Co-optimize sequence and estimator so the forward operator is better conditioned. Highest practical payoff, lowest mathematical elegance. Diffusion's multidimensional encoding is the proof of concept.
- **Numerical algebraic geometry.** Homotopy continuation to find all critical points of the VARPRO objective and certify the global optimum.

---

## 5. Guardrails

Solo project with no deadline: the risk is drift, not schedule slip. These are binding.

**G1 — One bibliography.** A single running annotated bibliography. Every source read gets an entry with: claim made, method family, modality, evidence quality, and whether it survives Phase 2 benchmarking. No parallel or ad-hoc reading lists.

**G2 — Implementation gate.** No method counts as "surveyed" until it is implemented in the harness and scored. Reading a paper is not surveying. The Phase 1 taxonomy admits only implemented entries.

**G3 — Decision log.** Every Phase 3 branch point is logged (§8) with date, options considered, choice, reasoning, and the evidence that would reverse it. Nothing is abandoned or adopted silently.

**G4 — Baseline gate.** A Phase 3 idea is pursued only after it beats the Phase 2 baseline on synthetic data with known ground truth. Elegance is not evidence. Promising-in-principle is not evidence.

**G5 — No family is excluded a priori.** No method family may be dropped for a modality, sampling regime, or data representation on structural grounds alone. When a textbook form does not fit, the obligation is to locate or construct the adapted variant, implement it, and score it. An exclusion is admissible only as one of two logged outcomes: (a) a benchmarked score showing it is dominated, or (b) a stated impossibility argument with its assumptions made explicit and falsifiable. "Doesn't apply" is not a finding. Adaptations must be realizable on a scanner — a variant requiring physically unobtainable data is not a rescue.

**Enforcement:** these are checked at every phase transition and referenced whenever new work is proposed. A proposal that violates a guardrail is flagged before work begins, not after. G5 in particular is checked against the Phase 1 taxonomy: every cell of the method × modality × representation × sampling grid must contain a score or a logged impossibility argument, never a blank.

---

## 6. Evaluation Design

### 6.1 Harness axes

The benchmark is a grid, not a list. Every method is scored across the full product where physically meaningful, and G5 forbids leaving cells blank.

| Axis | Levels |
|---|---|
| **Method family** | The seven families of §4, Phase 1, plus adapted variants |
| **Modality / kernel** | T2, T1 (multiple sequences), T2*, T1ρ, diffusion — each a kernel plugin |
| **Data representation** | Complex · phase-corrected real · magnitude (Rician) |
| **Reconstruction pipeline** | Raw k-space · single coil · SoS multi-coil · Roemer/adaptive · SENSE (range of R) · GRAPPA · partial Fourier · compressed sensing (range of regularization) · DL reconstruction |
| **Data access level** | L0 raw + prescan · L1 raw · L2 per-coil complex · L3 combined complex · L4 magnitude + metadata · L5 magnitude + protocol · L6 magnitude only |
| **Noise knowledge** | σ known exactly · σ estimated jointly · σ from prescan · σ from background · σ misspecified (family and magnitude) |
| **Noise character** | Stationary · g-factor modulated · non-stationary χ with varying DOF · plus contamination (spikes, physiological, Gibbs) |
| **Sampling grid** | Uniform · subset-of-grid (with completion) · sparse-ruler/co-array · log-spaced · CRLB-optimal · genuinely scattered |
| **Sample budget** | Dense (32–64) · moderate (12–16) · austere (5–8) |
| **Ground truth** | Discrete K=2,3 · continuous spectrum · exchange-coupled (Bloch–McConnell) · non-exponential |
| **SNR** | Spanning clinical to high-field research conditions |

Three sub-studies fall directly out of this grid and are worth treating as named deliverables:

- **Sampling design study** — does co-array/sparse-ruler placement of a small sample budget beat conventional and CRLB-optimal placement? Directly testable, clinically realizable, and apparently untried in MR.
- **Value-of-phase study** — the CRLB comparison across the three data representations (§2.3), which quantifies what sequence modifications to retain complex data would actually buy.
- **Value-of-noise-knowledge study** — the CRLB gap across noise-knowledge levels (§3.2), quantifying the precision cost of the σ / long-T degeneracy and the return on better noise characterization.

A fourth question cuts across all three: **how much does each acceleration factor cost in parameter precision?** Acceleration is currently justified on image quality, not on downstream parameter variance. The harness answers that directly.

### 6.2 Metrics

Fixed in Phase 0, applied unchanged thereafter.

- **Parameter RMSE** — per-component amplitude and decay constant, where K is known.
- **Functional recovery** — e.g. mass below a threshold. Often well-posed where the full spectrum is not; this is the metric that matters clinically and the one Phase 3 targets.
- **Uncertainty calibration** — empirical coverage of nominal confidence/credible intervals. A method with good RMSE and 40% coverage on nominal 95% intervals is not a good method.
- **Stability under resampling** — variability across noise realizations and bootstrap resamples.
- **CRLB efficiency** — ratio of achieved variance to the theoretical floor. The primary cross-method comparator.
- **Robustness to misspecification** — degradation under exchange, stimulated echoes, and non-exponential ground truth that violate the fitted model.
- **Noise estimation accuracy** — σ (and effective DOF where applicable) against known truth, including under spatial non-stationarity.
- **Joint (θ, σ) efficiency** — achieved variance against the joint CRLB, which is the honest comparator whenever σ is not independently known.
- **Robustness to noise-model misspecification** — degradation when a Rician fit meets non-central χ data, when stationary σ meets a g-factor map, or when any closed-form model meets CS-reconstructed data. This is the realistic deployment condition and deserves equal standing with the clean case.

---

## 7. Working Practices

- Charter is a living document; substantive changes are versioned and dated.
- **`gaps-register.md` is a background companion document**, not a second work plan. It captures publishable questions that surface while doing charter work, and its entries are expected to resolve as byproducts. Every entry begins as an unverified hypothesis; the Phase 1 sweep assigns real status as a side effect of reading. No register entry is worked past exploratory scoping while unverified, and a dedicated effort on one that charter work does not require needs justification against G4.
- Bibliography maintained continuously, not reconstructed at phase end.
- Every method implementation lives in the harness with a reproducible test.
- Assumptions register (§9) reviewed at each phase transition.
- **Provenance discipline for numbers the harness will lock on.** Any coefficient, constant, or closed form that becomes a harness correctness test or a threshold in this charter is traced to its primary source before the test locks. Secondary confirmation (reference datasets, review articles) is sufficient to *write it down*, with a provenance flag; it is not sufficient to *lock on it*. *(Added in v0.7. Open flags as of v0.8: Lanczos's own two-term coefficients and two-decimal statement, p. 276 — a book check that no test depends on; and Istratov & Vyvenko's printed SNR convention for the resolvable ratio, against the harness's arccosh form.)*
- **Living documents are written back in place.** A revision of this charter or of `gaps-register.md` replaces the project copy the same session it is produced, with the version bumped and the change recorded in `claude/changelog.md` (newest entry first). Phase findings and harness status live in `claude/phase0-*.md`-style companion docs; when they contradict the charter, the charter is reconciled and the reconciliation logged in §8, rather than the two being left to disagree. Delivering a file to the conversation is not saving it. *(Added in v0.8, after v0.7 was delivered as a file but not written back, which left the harness session reading v0.6.)*

---

## 8. Decision Log

| Date | Decision | Options considered | Reasoning | What would reverse it |
|---|---|---|---|---|
| 2026-08-07 | T2 as primary testbed, pluggable kernels for T1/T2*/T1ρ/diffusion | T2-only; equal weight across modalities | T2 gives densest/cheapest data and the cleanest instance of the pure problem; abstraction makes cross-modality contrast nearly free | Evidence that T2-specific structure is not representative, or that a target application is fixed to another modality |
| 2026-08-07 | Working implementations, not paper-only study | Literature review only | Guardrail G2 requires implementation to claim survey coverage | — |
| 2026-08-07 | **Reversed:** sampling irregularity does not exclude the linear-algebraic family | Excluding family 2 for T1/T1ρ/diffusion (v0.1 position) | v0.1 conflated few samples (a conditioning limit) with irregular samples (a structural one). Look-Locker restores uniform T1 sampling outright; Hankel completion and generalized Prony handle the rest | A benchmarked demonstration that adapted variants are dominated in every cell |
| 2026-08-07 | Data representation is a three-arm harness axis, not a preference | Complex-preferred (v0.1 position); magnitude-only | Phase advantage is theoretical and offset by phase-specific corruption; magnitude is the realistic clinical target. The question is empirical | Value-of-phase CRLB study showing a negligible or overwhelming gap |
| 2026-08-07 | **Reframed:** multi-component T1 is regime-limited, not impossible | Deprioritizing T1 (v0.1 position) | Fast-exchange averaging is a claim about a parameter regime; reparameterizing to Bloch–McConnell makes it a well-posed identifiability question. qMT/CEST demonstrate multi-pool fits are achievable | Identifiability analysis showing the exchange parameterization is degenerate across all realizable acquisitions |
| 2026-08-07 | Added guardrail G5 (no a priori exclusion) | Relying on G2 alone | G2 gates what counts as surveyed; it did not prevent excluding a family before implementation. G5 closes that gap | — |
| 2026-08-07 | Noise elevated to a full track (§3) with its own survey family, harness axes, and Phase 3 directions | Treating noise as a per-method implementation detail | Noise distribution is set by the reconstruction pipeline, not the modality, and σ is structurally degenerate with the longest decay component — so it cannot be handled inside individual methods | Demonstration that the σ / long-T degeneracy is negligible at realistic SNR across all representations |
| 2026-08-07 | **A6 resolved:** two co-equal arms — k-space model-based estimation developed as if raw access were guaranteed, image-domain estimation developed as the deployment reality | k-space-primary with image-domain as fallback; image-domain only | Raw access is real but not reliable. The arms also serve each other: the k-space result is the reference standard that measures the cost of reconstruction | — (both arms are required regardless of findings) |
| 2026-08-07 | Phase 0 simulator must be k-space-first and run real reconstructions | Adding closed-form noise to synthetic images | Assumed noise distributions would make the §3.3 harness axes circular. Retrofitting later invalidates all prior image-domain results | Demonstration that real and modeled recon noise are indistinguishable for estimation purposes |
| 2026-08-07 | Separate gaps register created for candidate original contributions, with mandatory unverified-until-swept status | Tracking gaps inline in the charter; tracking them informally | Claims of absence in the literature are high-risk and need explicit status tracking, especially across four weakly-cross-citing disciplines. Separating them keeps the charter descriptive and the register speculative | — |
| 2026-08-07 | Gaps register designated a background side project, harvested from charter work rather than driving it | Running it as a parallel work stream with its own priorities | Gaps found from the armchair are unreliable; gaps hit mid-investigation are real by construction. Also keeps a single work front, which matters more than usual for a solo project with no deadline | Charter work stalling for reasons a register entry would unblock |
| 2026-09-06 | **Corrected:** Lanczos (1956) example restated as a 3-exponential sum matched by a 2-exponential sum to better than 0.001 over 24 points (§1.2, §4 Phase 0, §10 step 3); coefficients carry a provenance flag, strengthened by a numerical inconsistency found during revision | Leaving the v0.1–v0.6 wording ("two very different 3-exponential sums"); correcting silently; withholding the two-exponential coefficients until the primary is checked | The v0.1–v0.6 description was wrong in kind, not degree — the example's point is that *the number of components* is not identifiable, which a same-K comparison cannot show. As the harness's first correctness test, a mis-stated example would have locked in a test that checks the wrong property. Three-exponential coefficients and point count verified via NIST StRD Lanczos1–3; two-exponential coefficients via Istratov & Vyvenko (1999) and Varah (1985) only. A least-squares check shows the 0.001 claim holds for the optimal two-exponential on the NIST grid but not for the quoted coefficients, which fit a Δt = 0.1 grid instead — so the quoted numbers are kept, flagged, and gated on the primary rather than dropped | The primary reporting different coefficients, grid, or precision — in which case the harness test follows the primary and this row is amended |
| 2026-09-06 | **Restated:** effective numerical rank is an SNR- and T-range-dependent quantity (Istratov & Vyvenko closed form for R_min; Bertero et al. ln-SNR growth and restricted-support improvement), with ~2–3 at clinical SNR retained as a consequence and a falsifiable threshold attached (§1.2) | Keeping the constant "2–3" as a premise; dropping the number entirely | A constant rank is the wrong shape for the claim and would have made the Phase 0 conditioning map a confirmation exercise rather than a measurement. Retaining the practical figure keeps downstream calibration intact; stating the threshold makes the figure revisable on evidence rather than by argument | The threshold in §1.2 firing in either direction at the reference clinical configuration; or the primary's constant convention differing materially from the form written here |
| 2026-09-06 | **Narrowed:** joint (θ, σ) Fisher-information novelty claim confined to the multi-exponential block inverse (K ≥ 2 Schur complement) and the analytic σ / long-T degeneracy manifold (§3.2, §3.7, §10 step 4); gaps register A3 → PARTIAL | Keeping the broad "not done systematically" claim; dropping the sub-study | Adjacent prior art exists and was not cited: Benedict & Soong (1967) and Sijbers & den Dekker (2004) on joint single-amplitude/σ estimation; Karlsen et al. (1999) and Bouhrara et al. (2014) on Rician-correct CRLBs for decay models; Milford et al. (2015) documenting the free-offset practice. None covers the K ≥ 2 joint block inverse or the degeneracy manifold, so the sub-study survives with a smaller, defensible claim | A later sweep pass finding the K ≥ 2 joint FIM with σ nuisance already derived — A3 then goes to OCCUPIED and step 4 becomes a reproduction, not a result |
| 2026-09-06 | **Added** to Phase 0 foundational scope: Transtrum/Machta/Sethna sloppy models; Bates–Watts curvature decomposition; Ostrowsky et al. exponential sampling; Epstein–Schotland closed-form singular values; Rife–Boorstyn single-tone CRLB as the contrasting case; McWhirter–Pike / Bertero et al. as the source of §1.2 | Citing them in the bibliography only; deferring to Phase 1 | Each is a classical result the charter was reasoning without. Encoding them in Phase 0 makes the harness's conditioning map, uncertainty metrics, log-spaced grids, and Fourier-vs-Laplace transfer checks rest on stated theorems instead of folklore. Rife–Boorstyn in particular guards against importing sinusoid-case intuition into the Laplace case | — (these are foundations; they would be removed only if shown inapplicable, which none of them is) |
| 2026-09-06 | **Upheld:** no open, ground-truth benchmark for multi-exponential MR parameter estimation exists; gaps register E1 stays UNVERIFIED, leaning CONFIRMED | Upgrading E1 to CONFIRMED on the pass-1 result | Pass 1 covered foundations, not the method-family literature or the four originating disciplines' benchmark practices; the nearest neighbours (NIST StRD Lanczos sets; ISMRM/NIST system phantom; single-T1 reproducibility challenge; diffusion-specific challenges; per-group simulators) each fall short on a stated axis, but a later pass could still surface one. The register's rule is that status is assigned by the sweep that actually checks the entry | A later pass finding an open multi-component ground-truth benchmark with an SNR axis — E1 then goes to OCCUPIED and the harness is positioned as an extension |
| 2026-09-07 | **Reconciled §1.2 and §4 Phase 0 with the harness's Phase 0 findings** (`claude/phase0-findings.md`): informative-direction count is set by the acquisition window, γ_eff = min(T-range, window); "2–3" restated in units of *components* via the 2K rule, with measured rank 3–6 at SNR 30–1000 for 32 × 10 ms; resolvable ratio written in the exact arccosh form the harness implements; falsifiable threshold moved from the (now measured) SVD count to the CRLB; Lanczos discrepancy resolved by the two-decimal tabulation | Leaving v0.7 as delivered and letting the findings doc carry the correction; deferring until the CRLB module exists | v0.7's closed form carried T-range only and would overstate the rank by 2–5 for realistic echo trains; its threshold conflated numerical rank with component count and would already have fired at the measured count of 4. Measured numerics supersede the armchair asymptotic; the charter is the authoritative document and must not disagree with the project's own findings | The CRLB module contradicting the 2K rule at the reference configuration (the threshold in §1.2); or a kernel for which the window rule fails — the T1ρ and diffusion kernels, with few encoding points, are the first places to look |
| 2026-09-07 | **SNR definition adopted for the harness:** SNR = S_ref / σ₁, with S_ref the kernel's reference signal (unattenuated magnetization sum) and σ₁ the per-pixel real-part noise standard deviation of the *same* k-space noise in a fully sampled, single-coil, R = 1 reconstruction. Conditioning additionally reports per-sample and energy (‖s‖/σ) conventions | First-echo SNR; per-sample SNR; energy SNR as the single convention | Defining SNR at the R = 1 single-coil reconstruction of the same noise makes every pipeline penalty (g-factor, χ DOF, CS shrinkage) a *measured* quantity relative to a fixed reference rather than an assumed one, which is the whole point of §3.6. Per-sample and energy conventions are kept as reported alternates because the continuum resolution results are stated in the former and the √N gain of dense sampling shows only in the latter | A modality whose kernel has no natural unattenuated reference signal (steady-state sequences such as DESPOT1/bSSFP), which would need its own convention logged here |
| 2026-09-07 | **Threshold evaluated (v0.9):** none of the §1.2 clauses fires at the reference configuration once the amplitude vector is named; "K = 2 comfortably, K = 3 marginal" retained with measured precision behind it (K = 3 at ratio 3: 60–155% RSD on the decay constants; K = 2 at ratio 4: 5–14% at equal amplitudes, 28–41% on the short constant at 20/80); window-rule clause holds (≤ 1 change in count across six spacings at N = 8–32). Amplitude vectors written into the clauses | Leaving the amplitude vector unspecified (under which the downward clause fired for 4 of 12 cases and not for the other 8); replacing the CRLB clauses with a Picard count | The CRLB outcome depends on the amplitude split more than on placement, on Rician vs Gaussian, or on σ known vs joint (all < 2%), so a clause that does not name the vector is not falsifiable. Naming two vectors keeps the clinically relevant minor-component case visible without letting it alone decide | A CRLB result at either named vector crossing the stated bounds; or a Phase 2 estimator demonstrably beating the bound, which would mean the bound, not the figure, is wrong |
| 2026-09-07 | **Recorded (v0.9):** the Epstein–Schotland / McWhirter–Pike closed form is a check on the count and decay rate of the numerical SVD, not on individual singular values; the Lanczos grid question narrowed to a book check with four named fields; Varah's tech-report version does not carry the two-term coefficients | Treating the per-index disagreement as a harness bug; dropping the closed-form check | Covering-window numerics agree with the continuum count to ±2, but σ₁/σ₀ ≈ 0.33 for every Γ ≥ 100 against 0.48–0.78 from uniform Mellin quantization, and the f-weighting moves the count by 1–3: the closed form is asymptotic in index, as BBP's own counting argument is. The Lanczos t = 0 deviation is grid-independent, which is what makes the two-decimal reading the only consistent one | A per-index closed form (a finite-interval prolate-type result) that the numerics do match — then the check tightens; or the book giving a grid or precision the numerics did not anticipate |

---

## 9. Assumptions Register

Open assumptions that would change the plan if wrong. Reviewed at each phase transition.

- **A1** — Working implementations are wanted, not a pure paper study. *(Confirmed.)*
- **A2** — T2 relaxometry is the primary application context. *(Confirmed as starting point; other modalities in scope via pluggable kernels.)*
- **A3** — No fixed target application or scanner platform constrains the acquisition designs considered. *(Unconfirmed.)*
- **A4** — Computational budget permits MCMC/nested sampling and homotopy continuation at realistic problem sizes. *(Unconfirmed.)*
- **A5** — Publication is a possible but not required outcome. *(Unconfirmed.)*
- **A6** — ~~Reconstructed images are the primary input.~~ **Resolved 2026-08-07:** raw access is available sometimes but cannot be assumed. Both arms are in scope and co-equal (§3.6); neither is a fallback. *(Confirmed.)*
- **A7** — Accelerated and CS-reconstructed data are in scope as realistic inputs, not excluded as too poorly characterized. *(Confirmed.)*

---

## 10. Immediate Next Steps

1. Broad multi-source literature sweep to seed the Phase 1 bibliography across all seven method families (including noise, §3.4) and all four originating disciplines (NMR/MR physics, geophysics/well-logging, chemical relaxation spectroscopy, array signal processing). **Pass 1 (foundations) complete and integrated 2026-09-06 (v0.7).** Remaining passes: the seven method families, and the four disciplines' own benchmark and test-problem practices (which is what E1 still waits on).
2. Stand up the Phase 0 harness skeleton with the pluggable-kernel interface. **Done 2026-09-07** (`claude/phase0-harness-status.md`): §6.1 axes as enums, design generators including verified sparse rulers, the kernel ABC with a single abstract method, `t2_cpmg` as the only *registered* kernel (IR, Look-Locker, complex T2\*, T1ρ-dispersion, and b-tensor kernels are exercised against the base class in tests but deliberately not registered, per G2), the k-space-first rule enforced by test, 55 tests passing (v0.9). **Open:** the code (`mexp-harness.zip`) has no home yet — put it in a connected folder or a remote before anything else is built on it.
3. Reproduce the Lanczos degeneracy example as the harness's first correctness test. **Done 2026-09-07** — passes as specified in §4 Phase 0, locked on NIST StRD Lanczos1/3 and the harness's own optimal approximant. **Open:** the book check of Lanczos p. 276 for his own two-term coefficients and the two-decimal statement; no test depends on it. *v0.9:* test restructured to the (a)/(b) criteria of §4 with the quoted coefficients checked separately; the book check now has four named fields to fill (Δt, number of points, decimals, whether a number or "within the accuracy of the data" is claimed).
4. Build the Phase 0 conditioning map — SVD, Picard, and TSVD resolution kernels over (SNR, echo count, window, T-range), checked against the arccosh continuum expression. **Done for T2, 2026-09-07** (`claude/phase0-findings.md` §3); §1.2 reconciled to it in v0.8. **Open:** repeat for each kernel as it is registered — the window rule is the thing to test on the few-point kernels (T1ρ, diffusion).
5. The CRLB module. **Done 2026-09-07** — `mexp/crlb.py` (Gaussian real and complex; Rician with σ known or jointly estimated; tests for the Gaussian/Rayleigh limits, the Rife–Boorstyn contrast and the sloppy FIM spectrum). The §1.2 threshold was evaluated at the reference configuration and none of its clauses fires once the amplitude vector is named (§1.2 outcome; §8). **Open:** `design.crlb_optimal` stays an explicit `NotImplementedError` — it needs a design-optimisation loop on top of the module, which is Phase 1 experimental-design work; and the K = 2, 3 sweep should be re-run per kernel as each is registered.
6. Then the joint (θ, σ) Fisher information for the multi-exponential model and the σ / long-T degeneracy manifold — cheap, self-contained, and it calibrates how much of §3 is load-bearing. *Scope narrowed in v0.7:* the single-amplitude joint estimators (Benedict & Soong 1967; Sijbers & den Dekker 2004) and the Rician-correct decay CRLBs (Karlsen et al. 1999; Bouhrara et al. 2014) are the starting point, not the result; the contribution is the K ≥ 2 block inverse and the degeneracy manifold. (Gaps register A3, PARTIAL.) *Phase 0 probe (v0.9, §3.2):* the numerical K ≥ 2 joint block now exists in `mexp/crlb.py`, and under the correct single-coil Rician likelihood at 32 echoes the joint-σ cost is < 2% — so the analytic work should target the misspecification, free-offset, χ-pipeline and external-σ rungs of the ladder, where the cost can still be large.
7. Then, in order: the k-space-first simulator implementation (§3.6; gaps register E2), the EPG physical-truth path, and `crlb_optimal` design.
8. As a side effect of the sweep, assign verified status to entries in `gaps-register.md` — killing the ones already occupied before any effort is spent rediscovering them. This is a byproduct of reading, not a separate task. *Pass 1 outcome:* A3 → PARTIAL; E1 upheld, leaning CONFIRMED; no other entry touched.
