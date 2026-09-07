# Pluggable-kernel interface — design note

Charter references: §2 (modality scope), §2.2 (five axes), §6.1 (harness axes), §4 Phase 0 deliverable.

## What a kernel is, and is not

A kernel plugin declares one modality's **noiseless forward model** and nothing else. It answers exactly one
question — *given non-linear parameters, nuisance parameters and a design, what is the unit-amplitude signal
of one component?* — through `atoms(xi, nu, design) -> Phi (N, M)`. Everything the harness does with a kernel
is built on that one method:

| Need | Built from `atoms` | Override only if |
|---|---|---|
| `forward(theta, design)` | `Phi @ a (+ fixed_atoms @ theta.fixed)` | never |
| `jacobian(theta, design)` | central finite differences over `theta.pack()` | an analytic form exists (T2 does) |
| `discretize(design, grid)` | `atoms` on an `(M, p)` grid of xi | never |
| `default_grid(M)` | geometric / linear per `ParamSpec.scale` over `physical_range()` | never |
| `reference_signal(theta)` | `sum |a|` (unattenuated magnetisation) | atoms are not unit at the reference point |

A kernel does **not** know about noise, reconstruction, data representation, access level, sampling grid
type, or estimators. Those are separate layers (`sim`, `representation`, `axes`, `design`, `estimators`) that
*consume* kernels. This separation is what makes the §6.1 axes real: the same kernel object is scored under
every representation × pipeline × access × noise × grid × budget × truth × SNR cell without modification.

## The invariant that makes one interface suffice

Charter §2.1: all five modalities are Laplace-type transforms of a positive measure. Operationally the
invariant is weaker and more useful — **for fixed non-linear parameters the signal is linear in the
component amplitudes.** That holds for every modality and sequence in §2.2, including the ones that are not
literally sums of exponentials (IR with an asymptote, Look-Locker with a steady-state term, T1rho dispersion,
b-tensor encoding). So the parameter layout is fixed once in `params.Theta`:

```
amplitudes (K,)  real | positive | complex     <- AmplitudeField
nonlinear  (K,p) per-component xi              <- kernel.component_params
nuisance   (q,)  global nu                     <- kernel.nuisance_params
fixed      (r,)  amplitudes of fixed atoms     <- kernel.fixed_atom_names (e.g. constant offset)
```

and `pack()/unpack()` give one flat ordering that CRLB, VARPRO-type and Bayesian code will all share.

## How each modality maps (verified by `tests/test_kernel_interface.py` Part B)

| Modality / sequence | `coords` | `xi` (p) | `nu` (q) | field / amplitude | The requirement it exercises |
|---|---|---|---|---|---|
| T2 CPMG (registered) | TE | T2 (1) | — | real / positive | baseline |
| T2 CPMG + EPG (future) | TE | T2 (1) | B1, T1 | real / positive | non-exponential *atom shape* from physics; misspecification vs the pure kernel is then measurable |
| T1 IR (classic, irregular TIs) | TI | T1 (1) | eta | real / **real** | affine atom `1 − 2η e^{−TI/T1}`; polarity ambiguity handled by AmplitudeField.REAL + the magnitude arm |
| T1 Look-Locker | TI | T1 (1) | alpha, TR | real / positive | apparent T1* computed *inside the atom* from nuisance, so the component parameter stays physical and the dense uniform TI grid is Prony-ready (§2.3 route 1) |
| T1 SR / VFA / MRF | TS or FA | T1 (1) | TR, … | real / positive | steady-state, not a decay — still linear in amplitude for fixed xi; MRF dictionary = `discretize` on a fingerprint grid |
| T2* mGRE, complex | TE | T2*, Δf (2) | φ0 | **complex** / **complex** | complex field; p = 2 so `discretize` grids are 2-D; Jacobian complex, `as_real_rows` for the Gaussian-complex CRLB |
| T1rho, single ω1 | TSL | T1rho (1) | — | real / positive | baseline with a different coordinate name |
| T1rho dispersion | TSL, ω1 | R0, Rex, kex (3) | — | real / positive | **2-D design** via `product_design`; the second axis is physically parameterised (Trott–Palmer / Chopra) |
| Diffusion, scalar | b | D (1) | — | real / positive | baseline |
| Diffusion tensor distribution | b_xx…b_yz (6) | D_xx…D_yz (6) | — | real / positive | **matrix-variate Laplace kernel**: p = 6, design rows are b-tensors, `discretize` takes any (M, 6) table of PSD tensors |

Nothing in `kernels/base.py` needed to change to write any row of Part B. The two design decisions that made
this true: (1) `xi` is `(K, p)` rather than `(K,)`, and (2) `Design` carries named coordinates of arbitrary
dimension rather than a time vector.

## Where the remaining §6.1 axes live

| Axis | Owner | Notes |
|---|---|---|
| Method family | `estimators.Estimator.family` | protocol only in Phase 0 (charter G2) |
| Modality / kernel | `kernels` registry | `Cell.kernel` is the registered name |
| Data representation | `representation.represent` | deterministic map on complex image data |
| Reconstruction pipeline | `sim.Simulator.reconstruct` | interface only; **the only noise entry point is `add_kspace_noise`** |
| Data access level | `axes.AccessLevel`, gating in `estimators.Observation` | fields above the level are `None` |
| Noise knowledge | `axes.NoiseKnowledge`, `Observation.sigma_hint` | |
| Noise character | `axes.NoiseCharacter` | realised only by the simulator, never synthesised by formula |
| Sampling grid | `design.*` factories | uniform, subset-of-grid, sparse-ruler / co-prime / nested, log, scattered; `crlb_optimal` is an explicit `NotImplementedError` (needs a design loop on top of `mexp.crlb`) |
| Sample budget | `Design.N`, `SampleBudget.of(N)` | |
| Ground truth | `truth.*` | discrete, continuous, and a `PhysicalTruth` protocol for exchange-coupled / non-exponential |
| SNR | `axes.SNRSpec` + `SNRDefinition` | defined at the k-space source relative to the R = 1 single-coil reconstruction, so pipeline penalties are measured, not assumed |

## SNR definition (a decision worth recording)

`SNR = S_ref / σ₁`, where `S_ref = kernel.reference_signal(theta)` (the unattenuated magnetisation sum, so it
is comparable across modalities — TE = 0 for T2, M0 for T1, b = 0 for diffusion) and `σ₁` is the per-pixel
real-part noise std that the *same* k-space noise produces in a fully sampled single-coil R = 1
reconstruction. Under this definition an R = 4 SENSE cell and an R = 1 cell at "SNR 100" share the same
k-space noise, and the g-factor penalty shows up in the score rather than in the axis label — which is what
the cost-of-reconstruction question (§3.6, §6.1) needs. The conditioning module also reports the
per-sample (`S(t₁)/σ`) and energy (`‖s‖/σ`) conventions because SVD counts depend on which one is meant, and
`mexp.crlb.sigma_from_first_echo_snr` / `sigma_from_reference_snr` convert between the charter's first-echo
convention (used by the §1.2 threshold) and the harness default.

## What is deliberately absent

- **Estimators.** None (G2). The Lanczos test is estimator-free.
- **Simulator implementation.** Interface and guard only. `tests/test_kspace_first_rule.py` fails the suite if
  any module outside `mexp/sim` touches a random generator or an image-domain noise model.
- **Registered kernels other than T2 CPMG.** The Part B kernels live in the test file so nothing un-scored can
  enter the taxonomy.
- **`design.crlb_optimal`.** Still `NotImplementedError`: the CRLB module now exists (`mexp/crlb.py`) but the
  design-optimisation loop on top of it is Phase 1 experimental-design work.
