# Changelog — charter and gaps register

Running log, newest first. Each entry says what changed in the living documents and why. Companion docs: `charter.md`, `gaps-register.md`, `claude/phase0-findings.md`, `claude/phase0-harness-status.md`.

---

## 2026-09-07 (later still) — charter v0.9 → v0.10 · gaps register v0.5 → v0.6 · bibliography v0.1 opened

**Trigger:** Eric's review of the session output — the threshold's amplitude vector must not be "myelin or nothing"; the code needs a home; the living documents need to be in one place with history. Housekeeping: v0.9's header still read "Version: 0.8" (only the summary had been bumped); fixed here.

**§1.2 — tissue-level threshold.** A tissue and organ dictionary (`mexp/tissues.py`) is now a harness component: per (tissue, modality, field) the component fractions and time constants with literature ranges, the clinical functional and its threshold, a typical acquisition, sources, and a provenance status. Thirteen entries seeded, all `RECALLED` (from memory of the named sources; the verification pass is §10 step 8). The §1.2 clauses are evaluated over every entry (`scripts/phase0_threshold_tissues.py`, `results/threshold_tissues.md`). First reading: under a free K = 3 model no myelin-type entry is estimable at first-echo SNR 100 — the unpinned 2000 ms component roughly doubles the MWF bound; with it fixed or dropped the white-matter MWF bound is ±0.030 at SNR 100 and ±0.010 at SNR 300, myelin T2 itself at 57 % relative SD (functional better determined than parameters); minor components under ~5 % fail; well-separated two-component tissues (prostate) are estimable. The "K = 2 comfortably, K = 3 marginal" sentence is restated per tissue class. The kernel-level two-vector clauses of v0.9 are kept as the tissue-agnostic statement.

**§4 Phase 0** — dictionary bullet added; the synthetic generator's truth set now includes every dictionary entry with its functional. **§6.1** — ground-truth axis gains the "literature-derived tissue composition" level. **§7** — `bibliography.md` opened as the one G1 list (v0.1: every source cited so far, each with a `CHECKED-PRIMARY` / `CHECKED-ABSTRACT` / `BIBLIO-ONLY` / `RECALLED` status — most are `RECALLED`, which is the honest state); new practice: the git repository in the connected folder is the code's home and mirrors the living documents under `docs/project/`, with the higher version number authoritative on disagreement. **§8** — rows for the dictionary and the repository. **§10** — step 2's "no home" resolved; step 8 added (dictionary verification pass); old step 8 → 9.

**Gaps register v0.6** — E3 added (open, cited, machine-readable tissue-composition table; `UNVERIFIED`, 0.6).

**Harness** — `mexp/tissues.py`, `mexp.crlb.mass_below_gradient` / `functional_sd` (delta-method bound on a functional such as MWF), `tests/test_tissues.py`, `scripts/phase0_threshold_tissues.py`; 60 tests. Repository created at `ExponentialParameterEstimation/` with `mexp-harness/` and `docs/project/`.

**Still open (for Eric):** Lanczos book check (four fields); Istratov & Vyvenko convention; whether the v0.9/v0.10 threshold wording is accepted; the v0.7 changelog's items #4 (E1 list vs the sweep's bibliography — now checkable against `bibliography.md`) and #5 (keep the register's adjacency notes — kept). The Bouhrara citation (#3) is confirmed by title and PMC ID.

---

## 2026-09-07 (later) — charter v0.8 → v0.9 · gaps register v0.4 → v0.5

**Trigger:** the harness session re-ran its Phase 0 work against charter v0.7/v0.8 (it had worked from v0.6 the first time), built the CRLB module that v0.8 §10 named as the next item, and evaluated the §1.2 falsifiable threshold. Findings in `claude/phase0-findings.md` (revision 2); harness in `mexp-harness.zip` (55 tests); `results/threshold_evaluation.md` inside it carries every number below.

**§1.2 — Threshold evaluated; amplitude vectors written into the clauses.** At the reference configuration (32 × 10 ms, T2 support 10–300 ms, first-echo SNR 100, Rician) none of the three v0.8 clauses fires: K = 3 at adjacent ratio 3 has 60–155% relative SD on the decay constants (best all-three case 70 / 103 / 30%), so the upward clause misses by ×3–15; K = 2 at ratio 4 has 5–14% at equal amplitudes, so the downward clause does not fire — but at a 20/80 split the short constant reaches 28–41% and it would have, for 4 of 12 placement × amplitude cases. Since the outcome depends on the amplitude vector more than on placement, on Rician vs Gaussian, or on σ known vs jointly estimated (all < 2%), the clauses now name two vectors (equal; 20/80 with the minor component shortest) and the downward clause fires on the equal-amplitude case only. The window-rule clause holds: six spacings at N = 8–32 over a fixed window move the count by at most one. Outcome paragraph added under the clauses; "CRLB module (next Phase 0 item)" → "built".

**§3.2 — Bound-level probe recorded.** Under the correct single-coil Rician likelihood at 32 echoes, the joint-σ CRLB is within 2% of the σ-known CRLB for the decay constants (SNR 100 and 30; with and without a 2000 ms component). The cost of the σ / long-T degeneracy, if it is large, lives on the misspecification, free-offset, χ-pipeline and external-σ rungs — which is where §10 step 6 should aim. One paragraph; the novelty claim is unchanged.

**§4 Phase 0.** Conditioning bullet: the Epstein–Schotland / McWhirter–Pike check qualified as a check on count and decay rate, not index by index (σ₁/σ₀ ≈ 0.33 numerically for every covering-window Γ ≥ 100 against 0.48–0.78 from uniform Mellin quantization; f-weighting moves the count by 1–3). Lanczos bullet restated for the restructured test — (a) applied to the harness's own least-squares fit computed inside the test through the kernel (so `mexp/` still has no estimator), quoted coefficients checked separately, (b) indistinguishability stated via the expected excess χ² (≤ 5.5 < 5.99 for σ ≥ 8.8 × 10⁻⁴) and the K = 3 CRLB — and marked provisional with a pytest marker. Provenance flag narrowed further: the t = 0 deviation is grid-independent, so only the two-decimal reading is consistent with the quoted pair; the pair sits closer to the Δt = 0.1 long-window optima (2.1885, 4.5035; 0.3236, 1.5963 on [0, 2.3]; 2.2156, 4.4682; 0.2961, 1.5247 on [0, 3.2]) than to the NIST-grid optimum; Varah's 1982 tech report does not quote the coefficients, so the 1985 journal version needs checking before Varah is cited for them. CRLB bullet marked built. Foundations table given a Phase 0 status line (encoded: M–P/BBP/I–V, E&S, Ostrowsky, Transtrum, Rife–Boorstyn; not yet: Bates–Watts).

**§8** — two rows: the threshold outcome with the amplitude-vector decision and its reversal condition; the closed-form-is-asymptotic-in-index record with the Lanczos grid and Varah notes.

**§10** — step 2: 55 tests; step 3: test restructured, book check given four named fields (Δt, points, decimals, claimed agreement); step 5 marked done with `crlb_optimal` still open; step 6 carries the §3.2 probe as its aiming note.

**Gaps register v0.5** — Phase 0 numerical notes on A1 (placement at fixed window moves the count by ≤ 1, so the design question must be posed in CRLB units), A3 (the joint block exists numerically; item 2's cost is small in the clean regime, aim items 3–4 at the misspecified/offset/pipeline rungs) and D1 (the finite-window count is measured; the linear-algebraic half of the austere-budget impossibility is on record). No status changes.

**Harness** — `mexp/crlb.py` added (Gaussian real/complex, Rician σ-known and joint; Rife–Boorstyn and sloppy-spectrum tests); `conditioning.r_min / k_max / ostrowsky_spacing / mellin_closed_form_ratios` added with both constant conventions; Lanczos test restructured; k-space-first guard refined to forbid noise *generation*, not the naming of a likelihood; `scripts/phase0_threshold.py` added. Still open: the harness has no home outside the conversation.

---

## 2026-09-07 — charter v0.7 → v0.8 · gaps register v0.3 → v0.4

**Trigger:** the harness session's `claude/phase0-findings.md` and `claude/phase0-harness-status.md` (written 2026-09-06/07) asked for §1.2 and the §4 Lanczos text to be re-checked against measured Phase 0 numbers, and found the project still holding charter v0.6 because v0.7 had been delivered as a file but not written back. Both fixed here.

**§1.1** — one sentence noting that a_k > 0 is the T2 statement and that the harness generalizes the amplitude field (positive · real · complex) for IR-magnitude and complex T2\*; the §2 reuse claims rest on that.

**§1.2 — Lanczos, made exact.** The v0.7 flag ("the grid, the 0.001 claim, and the quoted coefficients are mutually inconsistent") is resolved by the findings: Lanczos's table was given to two decimals; his own two-term coefficients reproduce that table at 23 of 24 points (max deviation 0.0064 from f); the optimal two-exponential approximant, 2.0688·e^(−4.6396t) + 0.4440·e^(−1.8725t), agrees to 8.8 × 10⁻⁴. So the "better than 0.001" in the pass-1 brief belongs to the optimal approximant, not to Lanczos's own fit. Added the oracle-detector separation figure (SNR ≳ 3.6 × 10³). Grid and three-exponential coefficients are now locked from NIST StRD (which cites Lanczos pp. 272–280); only Lanczos's own two-term coefficients remain a book check, and no test depends on them.

**§1.2 — Rank, reconciled to measurement.** Three changes. (1) The resolvable-ratio closed form is written in the exact arccosh form the harness implements, δ = exp(π²/arccosh(SNR²)) — 3.7 / 2.7 / 2.0 at SNR 30 / 100 / 1000 — which also settles the O(ln 2) convention question v0.7 flagged; the finite-window cost (factor ≈ 1.1–1.2) is stated from the harness. (2) The count expression now carries the acquisition window: N_inf ≈ (ln γ_eff/π²)·arccosh(SNR²) + 1, γ_eff = min(T_max/T_min, t_max/t_min), ±1.5. v0.7's K_max ≈ 1 + 2·ln SNR·ln Γ/π² used T-range only and would overstate the rank by 2–5 for realistic trains; the harness showed the window binds and that sampling density inside it barely matters. Measured counts for 32 × 10 ms: 3, 4, 5, 6 at SNR 30, 100, 300, 1000. (3) Units. "2–3" is a count of *components* (2K rule: K components need ≥ 2K informative directions), while the numerical rank is 3–6; v0.7 did not say which, and its falsifiable threshold ("revise upward if the SVD count is ≥ 4") conflated the two and would already have fired at the measured 4. The threshold is moved to the CRLB module (upward if K = 3 at ratio 3 is < 10% RSD at SNR 100; downward if K = 2 at ratio 4 exceeds 25%), plus a window-rule test.

**§2.3** — "few samples" bullet refined: the window binds, not the sample count within it; sparse designs spanning the same window cost mainly the √N energy gain. This strengthens the case for the sparse-ruler study.

**§4 Phase 0** — conditioning bullet re-axed (echo count and window replace "echo spacing"), marked done for T2 with the Picard diagnostic noted; Lanczos correctness test restated per the findings' recommended wording and marked passing (NIST table reproduced to 4.8 × 10⁻¹³; optimal approximant verified as a stationary point; oracle-SNR figure); provenance flag narrowed to the one open book check; the NIST Lanczos3 flip-side example added. k-space-first rule annotated as mechanically enforced by `tests/test_kspace_first_rule.py`.

**§7** — provenance flags updated to the two that remain open. New working practice: living documents are written back in place the same session, with the changelog appended, and companion findings docs that contradict the charter trigger a reconciliation rather than being left to disagree. Delivering a file is not saving it.

**§8** — two entries dated 2026-09-07: the reconciliation (with reversal conditions on the CRLB module and the few-point kernels), and the harness's SNR definition (S_ref/σ₁ at the R = 1 single-coil reconstruction of the same k-space noise; per-sample and energy conventions reported alongside), which the harness-status doc asked to have recorded.

**§10** — steps 2, 3 and the conditioning map marked done with what is open on each (harness code has no home yet; Lanczos book check); the CRLB module is now the named next item, followed by the joint (θ, σ) FIM, the simulator, the EPG path, and `crlb_optimal`.

**Gaps register v0.4** — formula in the B1 note and the D3 note aligned with §1.2's harness form. No status changes; the findings do not bear on any entry's status (A3 is next in the harness queue but not started).

**Harness-status doc** — open items 1 and 4 marked done (v0.7/v0.8 saved; cross-reference fixes landed in v0.7).

**Items still flagged for you:** the Lanczos p. 276 book check; Istratov & Vyvenko's printed SNR convention vs. the arccosh form; the identity of "the 2014 biexponential Rician work" as Bouhrara et al.; the E1 nearest-neighbour list vs. the sweep's bibliography; the register's adjacency notes. And one decision only you can make: where the harness code lives.

---

## 2026-09-06 — charter v0.6 → v0.7 · gaps register v0.2 → v0.3

**Trigger:** three corrections and one set of omissions established by the pass-1 foundations sweep; one claim upheld. *(Note added 2026-09-07: v0.7 was delivered to the conversation but not written to the project until 2026-09-07; the harness session in between worked from v0.6. Its Lanczos and §1.2 findings superseded parts of this entry — see the v0.8 entry above.)*

## Charter v0.6 → v0.7

**§1.2 — Lanczos example (correction 1).** The example is now stated correctly: a *three*-exponential sum, f(t) = 0.0951·e^(−t) + 0.8607·e^(−3t) + 1.5576·e^(−5t), matched to better than 0.001 in amplitude over 24 sampled points by the *two*-exponential sum 2.202·e^(−4.45t) + 0.305·e^(−1.58t). v0.6's §1 did not actually contain the Lanczos text (it lived only in §4 Phase 0 and §10); the correct statement was added to §1.2 as the canonical illustration of the ill-posedness, because that is where a reader first needs it. The old wording is quoted and marked as corrected. *Why:* the mis-description ("two very different 3-exponential sums") missed the example's point — that the *number* of components is not identifiable — and would have locked in a correctness test checking the wrong property.

**§1.2 — Effective numerical rank (correction 2).** The constant "roughly 2–3" is replaced by the dependence: Istratov & Vyvenko's closed form for the minimum resolvable ratio of adjacent time constants, R_min(SNR) = exp(π²/(2 ln SNR)), derived from the McWhirter–Pike / Bertero Mellin-domain cutoff ω_max ≈ (2/π)·ln SNR; Bertero, Boccacci & Pike's result that the recoverable count grows only as ln SNR and improves with restricted support; and a heuristic combined estimate K_max ≈ 1 + 2·ln SNR·ln Γ / π² over a T-range of ratio Γ. Worked numbers at SNR 30/100/1000 are given. The ~2–3 figure at clinical SNR is retained, but derived as a consequence at a stated operating point (first-echo SNR 50–200, T2 support 10–300 ms), with the separability-vs-useful-precision distinction and the finite-window effect explaining the step from the closed form's 3.5–4.5 down to 2–3. A **falsifiable threshold** is attached, tied to Phase 0's numerical SVD at a reference clinical configuration (32 echoes, 10 ms spacing, T2 support 10–300 ms, first-echo SNR 100, Rician), with explicit upward and downward revision conditions. "The single most important quantity" is now the map, not the number.

**§1.3 — Sloppy models.** One sentence added placing Transtrum, Machta & Sethna's sloppy-model geometry as the fitting-side statement of the same ill-conditioning (the sum of exponentials is their canonical sloppy model).

**§3.2 — Joint (θ, σ) novelty claim (correction 3).** The sentence "to my knowledge has not been done systematically for multi-exponential relaxometry" is replaced by a "what is and is not new" paragraph naming the adjacent prior art: Benedict & Soong (1967) and Sijbers & den Dekker (2004) on joint single-amplitude/σ estimation; Karlsen et al. (1999) and Bouhrara et al. (MRM 73:352–366, online 2014) on Rician-correct CRLBs for decay models; Milford et al. (2015) on the free-offset practice. The claim is narrowed to the multi-exponential joint FIM block inverse (K ≥ 2 Schur complement of σ) and the analytic σ / long-T degeneracy manifold. §3.7's first bullet and §10 step 4 were narrowed to match.

**§4 Phase 0 — Correctness test and foundations table.** The Lanczos correctness test is restated with explicit pass criteria and a **provenance flag**: coefficients verified via NIST StRD Lanczos1–3, Istratov & Vyvenko (1999), and Varah (1985), not the primary; Lanczos (1956) must be checked for grid, precision, and coefficients before the test locks. A new table, **"Foundational results the harness must encode"**, adds the results the sweep found missing entirely — Transtrum/Machta/Sethna sloppy models, Bates–Watts curvature decomposition, Ostrowsky et al. exponential sampling, Epstein–Schotland closed-form singular values, Rife–Boorstyn single-tone CRLB as the contrasting sinusoid case — plus McWhirter–Pike / Bertero et al. / Istratov & Vyvenko as the source of §1.2. Each row states what it establishes and where it plugs in. The Phase 0 deliverable now records that the no-open-benchmark claim was upheld, pointing to E1 for the evidence.

**§7 — Provenance discipline.** New working practice: any number that becomes a harness correctness test or a charter threshold is traced to its primary before locking; secondary confirmation suffices to write it down with a flag, not to lock on it.

**§8 — Decision log.** Five entries dated 2026-09-06: Lanczos corrected; rank restated with threshold; joint-FIM claim narrowed (A3 → PARTIAL); foundations added; no-benchmark claim upheld (E1 stays UNVERIFIED, leaning CONFIRMED). Each carries the options considered, reasoning, and reversal condition.

**§10 — Next steps.** Step 1 marks pass 1 complete and names the remaining passes. Step 3 gates the Lanczos test on the primary check. Step 4 carries the narrowed scope. Step 5 records the pass-1 register outcome. New step 6: build the Phase 0 conditioning map and evaluate the §1.2 threshold.

**Housekeeping (not decisions):** "Six families" → "Seven families" in §4 Phase 1 (family 7 was added in v0.3 but the header was never updated); §6.1 method-family axis cross-reference corrected from "six families of §3" to "seven families of §4". Nothing else in §2, §3.1, §3.3–3.6, §5, §6, or §9 was altered.

## Gaps register v0.2 → v0.3

**A3 → `PARTIAL`.** The original claim is kept verbatim for the calibration record. The prior art is listed under "what is occupied" with full citations, and the open sub-question is enumerated in four parts (K ≥ 2 joint FIM with σ nuisance; block inverse / Schur complement; analytic degeneracy manifold with identifiability conditions and the free-offset estimator located on it; the K ≥ 2 value-of-noise-knowledge ladder). Original confidence 0.8 retained as the number to be scored; a separate 0.7 stated for the narrowed sub-question. Reversal condition to `OCCUPIED` stated.

**E1 stays `UNVERIFIED (leaning CONFIRMED)`.** The upholding evidence is now cited: the nearest neighbours (NIST StRD Lanczos sets; ISMRM/NIST system phantom; the 2020 T1 reproducibility challenge; diffusion-specific challenges; per-group simulators and toolboxes) each with the axis on which it falls short. "Why not CONFIRMED" is stated — pass 1 did not cover the method families or the four disciplines' test-problem practices — along with what would move it to `OCCUPIED`.

**§0.2 — Lean annotations defined.** "UNVERIFIED (leaning CONFIRMED)" is now a defined construct: an annotation recording evidence from a nearby pass, not a status; it does not lift the exploratory-scoping restriction.

**Adjacency notes, statuses unchanged.** Short notes on A1, B1, B5, B6, C1–C3, D1, and D3 recording prior art the *foundations reading* bears on (Bertero Part II and Ostrowsky for A1; the R_min baseline and Epstein–Schotland for B1; Transtrum et al. for B5; Bates–Watts for B6; Rife–Boorstyn scaling for the Fourier-side transfers; Bertero/Istratov–Vyvenko impossibility results for D1; the §1.2 map for D3). Each is explicitly labelled as derived from the foundations reading, not from a check of the entry, and no status was changed. These are positioning constraints for future work, not verdicts.

**§7 — Calibration ledger opened**, with A3 as its first row, and the rule that a `PARTIAL` counts as a half-miss.

**§0.1, §6** — one-sentence updates noting the first instance of the process working (A3) and that pass 1 alone does not warrant re-ranking.

---

## Items flagged for you to check

1. **Lanczos primary — now more than a formality.** While verifying the example I fit the two-exponential model to the three-exponential sum numerically. On the NIST 24-point grid (t = 0, 0.05, …, 1.15) the least-squares-optimal two-exponential is 2.069·e^(−4.64t) + 0.444·e^(−1.87t), max deviation 0.00088 — so "better than 0.001 over 24 points" is achievable and the example's point stands. But the quoted coefficients 2.202·e^(−4.45t) + 0.305·e^(−1.58t) deviate by 0.0064 at t = 0 on that grid; they match the optimum on a Δt = 0.1 grid over 0–2.3 (2.189·e^(−4.50t) + 0.324·e^(−1.60t)), where the best achievable agreement is ≈ 0.0024. The grid, the 0.001 claim, and the quoted coefficients cannot all be right together as stated. I kept the quoted numbers in the charter (they are what the sweep established), recorded the inconsistency in the §4 provenance flag and the §8 row, and made the correctness test's pass criterion apply to the harness's own best fit on the primary's grid, with the quoted coefficients checked separately. *Applied Analysis* (1956), ch. IV needs to settle the grid, the stated precision, and the coefficients as Lanczos reports them.
2. **R_min constant convention.** I could not reach the Istratov & Vyvenko primary or Bertero 1982 from here (paywalled / blocked). The form exp(π²/(2 ln SNR)) follows from the Mellin cutoff ω_max ≈ (2/π) ln SNR, which I did confirm independently (it appears as y_max ≈ (2/π)·m·ln 10 for m decimal digits in a Laplace-inversion paper), but whether Istratov & Vyvenko write SNR as an amplitude or power ratio, and whether they carry the O(ln 2) normalization term, should be pinned before the resolution test locks. Flagged in §1.2 the same way as the Lanczos coefficients.
3. **"The 2014 biexponential Rician work."** I identified this as Bouhrara, Reiter, Celik, Bonny, Lukas, Fishbein & Spencer, MRM 73(1):352–366, online February 2014 (Crossref-confirmed). If the sweep meant a different paper, swap the citation in charter §3.2/§3.7/§8/§10 and register A3.
4. **E1 upholding evidence.** The nearest-neighbour list is my reconstruction of what a no-open-benchmark finding rests on; match it against the sweep's actual bibliography entries and prune anything the sweep did not look at.
5. **Adjacency notes in the register.** These were derived from the foundations list you supplied, not from sweep verdicts. If you would rather the register carry only sweep-verified annotations, delete them — no status depends on them.

Citations verified today against a bibliographic source: NIST StRD Lanczos1 (model, 24 observations, Lanczos 1956 provenance); Bouhrara et al. 2014; Milford et al. 2015; Benedict & Soong 1967. Cited from knowledge without a live check today: Sijbers & den Dekker 2004, Karlsen et al. 1999, Epstein & Schotland 2008, Ostrowsky et al. 1981, Rife & Boorstyn 1974, Bates & Watts 1980/1988, Transtrum et al. 2010/2011/2015, McWhirter & Pike 1978, Bertero et al. 1982/1984, Varah 1985.
