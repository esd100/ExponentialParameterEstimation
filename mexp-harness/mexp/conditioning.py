"""
Conditioning analysis of the discretised kernel (charter §1.2, §4 Phase 0).

This module analyses the *operator* A = discretize(kernel, design, grid) and a
noise *level*.  It never draws a noise realisation: the effective rank, the
Picard diagnostic and the truncation trade-off are all properties of (A, b,
sigma), so the k-space-first rule is not touched.

Contents
  discretized_operator   A (N, M), optionally column-weighted for a quadrature
  singular_spectrum      singular values, descending
  effective_rank         #{i : s_i / s_0 > 1/SNR}  (two SNR conventions, see below)
  picard                 |u_i^T b| against s_i and the noise level; the operational diagnostic
  tsvd_resolution        model-resolution (averaging) kernels of TSVD at truncation k
  mellin_gain, bbp_*     the continuum (Mellin-space) reference expressions

SNR conventions used by `effective_rank` (axes.SNRDefinition):
  FIRST_SAMPLE_OVER_SIGMA  S(t_1)/sigma        per-sample, the MR convention
  ENERGY                   ||s||_2 / sigma      what the SVD coordinates actually see:
                           noise has std sigma in *every* SVD coordinate, and the
                           signal energy is spread over ||s||_2; the two differ by ~sqrt(N_eff).

Continuum reference (McWhirter & Pike 1978, J. Phys. A 11:1729; Bertero,
Boccacci & Pike 1982, Proc. R. Soc. Lond. A 383:15).  In log variables the
Laplace transform is a convolution, diagonalised by the Mellin transform with
gain |Gamma(1/2 + i w)| = sqrt(pi / cosh(pi w)).  Restricting the object to a
T-range of dynamic range gamma = T_max/T_min (log-length L = ln gamma) and
sampling t densely over a range that covers it, Szego-type counting gives the
number of singular values above a fraction eps of the largest as

    N(eps) ~ (L / pi) * w_max,   cosh(pi w_max) = 1/eps^2
           = (ln gamma / pi^2) * arccosh(SNR^2)                      (eps = 1/SNR)
           ~ (ln gamma / pi^2) * ln(2 SNR^2)

and the corresponding Rayleigh-type resolution ratio in T

    delta = gamma^{1/N} = exp(pi^2 / arccosh(SNR^2)).

These assume the *time* window covers the whole T-range (t_min << T_min,
t_max >> T_max).  A finite echo train does not, and the finite-window
operator has fewer usable singular values than the formula; the sweep in
scripts/phase0_conditioning.py measures that gap.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .axes import SNRDefinition
from .design import Design
from .kernels.base import Kernel


# --------------------------------------------------------------------------
# operator
# --------------------------------------------------------------------------

def log_grid(lo: float, hi: float, M: int) -> np.ndarray:
    return np.geomspace(lo, hi, M)


def discretized_operator(kernel: Kernel, design: Design, grid: np.ndarray, nu: np.ndarray | None = None,
                         column_weights: str = "none") -> np.ndarray:
    """A (N, M).  column_weights:
        'none'      A_ij = phi(t_i; T_j)                 (the NNLS / dictionary matrix)
        'sqrt_dlog' A_ij = phi(t_i; T_j) sqrt(dlogT_j)   (L2(dlogT) quadrature; makes s_i the
                                                          singular values of the continuum operator
                                                          restricted to the grid span)"""
    grid = np.asarray(grid, dtype=float)
    A = kernel.discretize(design, grid, nu)
    if column_weights == "none":
        return A
    if column_weights == "sqrt_dlog":
        g = grid if grid.ndim == 1 else grid[:, 0]
        w = np.gradient(np.log(g))
        return A * np.sqrt(w)[None, :]
    raise ValueError(column_weights)


def singular_spectrum(A: np.ndarray) -> np.ndarray:
    return np.linalg.svd(A, compute_uv=False)


def effective_rank(s: np.ndarray, snr: float) -> int:
    """#{i : s_i / s_0 > 1 / snr}.  Which SNR to pass is the caller's decision
    (see module docstring); `energy_snr` converts the per-sample convention."""
    s = np.asarray(s)
    return int(np.sum(s / s[0] > 1.0 / snr))


def energy_snr(signal: np.ndarray, per_sample_snr: float, reference: float | None = None) -> float:
    """Convert S_ref/sigma (per sample) to ||s||/sigma for a specific noiseless
    signal. reference defaults to |s[0]|."""
    s = np.asarray(signal)
    ref = abs(float(s[0])) if reference is None else reference
    sigma = ref / per_sample_snr
    return float(np.linalg.norm(s) / sigma)


# --------------------------------------------------------------------------
# Picard
# --------------------------------------------------------------------------

@dataclass
class PicardResult:
    s: np.ndarray            # singular values, descending
    beta: np.ndarray         # |u_i^T b|, the Fourier/Picard coefficients of the noiseless data
    beta_smoothed: np.ndarray  # geometric mean over 2q+1 neighbours (Hansen's smoothing)
    sigma: float             # noise level per SVD coordinate (= per-sample sigma for white noise)
    n_picard: int            # last index (1-based) whose *smoothed* coefficient exceeds c * sigma
    n_above_noise: int       # leading run of raw coefficients with beta_i > c * sigma (brittle: accidental zeros)
    n_energy: int            # effective_rank with the ENERGY convention
    n_per_sample: int        # effective_rank with the per-sample convention
    solution_coeffs: np.ndarray  # beta_i / s_i : the TSVD solution coefficients (Picard ratio)

    @property
    def picard_ratio(self) -> np.ndarray:
        return self.beta / self.s


def _geomean_smooth(x: np.ndarray, q: int) -> np.ndarray:
    lx = np.log(np.maximum(x, np.finfo(float).tiny))
    out = np.empty_like(lx)
    n = lx.size
    for i in range(n):
        lo, hi = max(0, i - q), min(n, i + q + 1)
        out[i] = lx[lo:hi].mean()
    return np.exp(out)


def picard(A: np.ndarray, b: np.ndarray, sigma: float, c: float = 1.0,
           per_sample_snr: float | None = None, q: int = 1) -> PicardResult:
    """Discrete Picard condition (Hansen 1990, BIT 30:658).  b is the *noiseless*
    data; sigma the per-sample noise std in the arm being analysed.  For white
    noise every coefficient u_i^T e has std sigma, so beta_i above ~sigma is
    signal and below it is unrecoverable.

    The operational count `n_picard` uses Hansen's geometric-mean smoothing
    over 2q+1 neighbours, because a single raw coefficient can be small by
    accident (the truth happens to be nearly orthogonal to one singular
    vector) without the later ones being unrecoverable.  The raw leading run
    is kept as `n_above_noise` for comparison."""
    U, s, Vt = np.linalg.svd(A, full_matrices=False)
    beta = np.abs(U.T @ b)
    above = beta > c * sigma
    n = 0
    while n < above.size and above[n]:
        n += 1
    bs = _geomean_smooth(beta, q)
    idx = np.nonzero(bs > c * sigma)[0]
    n_pic = int(idx[-1] + 1) if idx.size else 0
    n_energy = effective_rank(s, np.linalg.norm(b) / sigma)
    n_ps = effective_rank(s, per_sample_snr) if per_sample_snr else effective_rank(s, abs(b[0]) / sigma)
    return PicardResult(s=s, beta=beta, beta_smoothed=bs, sigma=sigma, n_picard=n_pic, n_above_noise=n,
                        n_energy=n_energy, n_per_sample=n_ps, solution_coeffs=beta / s)


# --------------------------------------------------------------------------
# TSVD truncation: resolution vs noise amplification (operator property)
# --------------------------------------------------------------------------

@dataclass
class TruncationResult:
    k: int
    noise_amplification: float      # ||A_k^+||_2 = 1 / s_k
    fwhm_log: np.ndarray            # FWHM (in ln T) of the averaging kernel centred at each grid point
    resolution_ratio: np.ndarray    # exp(fwhm_log): T-ratio a delta function is smeared over
    R: np.ndarray                   # model resolution matrix V_k V_k^T (M, M)


def tsvd_resolution(A: np.ndarray, k: int, grid: np.ndarray) -> TruncationResult:
    """Averaging kernels of the TSVD pseudo-inverse: f_k = A_k^+ A f = R_k f with
    R_k = V_k V_k^T.  Row j of R_k is what an estimate at T_j actually averages
    over.  Its width is the resolution bought by keeping k singular values; the
    price is noise amplification 1/s_k.  Backus-Gilbert (charter Phase 3) is
    the optimisation of exactly this trade-off for a chosen functional."""
    U, s, Vt = np.linalg.svd(A, full_matrices=False)
    Vk = Vt[:k].T
    R = Vk @ Vk.T
    u = np.log(np.asarray(grid, dtype=float).reshape(-1))
    fwhm = np.full(R.shape[0], np.nan)
    for j in range(R.shape[0]):
        row = R[j]
        peak = row[j]
        if peak <= 0:
            continue
        half = 0.5 * peak
        # walk outwards from j until the kernel drops below half maximum
        lo = j
        while lo > 0 and row[lo - 1] >= half:
            lo -= 1
        hi = j
        while hi < row.size - 1 and row[hi + 1] >= half:
            hi += 1
        fwhm[j] = u[hi] - u[lo] + (u[1] - u[0])  # add one cell so a delta has non-zero width
    return TruncationResult(k=k, noise_amplification=float(1.0 / s[k - 1]), fwhm_log=fwhm,
                            resolution_ratio=np.exp(fwhm), R=R)


# --------------------------------------------------------------------------
# continuum reference expressions
# --------------------------------------------------------------------------

def mellin_gain(omega: np.ndarray) -> np.ndarray:
    """|Gamma(1/2 + i omega)| = sqrt(pi / cosh(pi omega)): the singular-value
    'curve' of the Laplace transform on log scales (McWhirter & Pike 1978)."""
    omega = np.asarray(omega, dtype=float)
    return np.sqrt(np.pi / np.cosh(np.pi * omega))


def bbp_count(dynamic_range: float, snr: float) -> float:
    """Continuum count of singular values above 1/SNR of the largest for a
    T-range of dynamic range gamma, assuming a covering time window:
        N = (ln gamma / pi^2) arccosh(SNR^2)  ~  (ln gamma / pi^2) ln(2 SNR^2)."""
    return float(np.log(dynamic_range) / np.pi**2 * np.arccosh(float(snr) ** 2))


def bbp_resolution_ratio(snr: float) -> float:
    """delta = exp(pi^2 / arccosh(SNR^2)): T-ratio below which two components
    are unresolvable in the Rayleigh sense, independent of gamma."""
    return float(np.exp(np.pi**2 / np.arccosh(float(snr) ** 2)))


def resolution_ratio_from_count(dynamic_range: float, n: float) -> float:
    """delta = gamma^{1/n}: what a measured count n implies for resolution."""
    return float(dynamic_range ** (1.0 / max(n, 1e-12)))


# --- the charter §1.2 (v0.7) closed forms, with both constant conventions ---------------

def r_min(snr: float, convention: str = "arccosh") -> float:
    """Minimum resolvable ratio of adjacent time constants.

    'charter'  exp(pi^2 / (2 ln SNR))          = exp(pi^2 / ln SNR^2)      (charter v0.7 §1.2, Istratov & Vyvenko form)
    'arccosh'  exp(pi^2 / arccosh(SNR^2))      ~ exp(pi^2 / ln(2 SNR^2))   (from the Mellin gain sqrt(pi/cosh(pi w)) directly)

    The two differ by the O(ln 2) term the charter flags: at SNR 100 they give 2.92 and 2.71.
    SNR is an amplitude ratio in both."""
    snr = float(snr)
    if convention == "charter":
        return float(np.exp(np.pi**2 / (2.0 * np.log(snr))))
    if convention == "arccosh":
        return bbp_resolution_ratio(snr)
    raise ValueError(convention)


def k_max(dynamic_range: float, snr: float, convention: str = "arccosh") -> float:
    """Recoverable count over a T-range of ratio Gamma at the separability threshold.

    'charter'  1 + ln Gamma / ln R_min = 1 + 2 ln SNR ln Gamma / pi^2   (charter v0.7 §1.2 heuristic)
    'arccosh'  (ln Gamma / pi^2) arccosh(SNR^2) + 1                      (Szego count plus the O(1) edge term measured in Phase 0)

    Gamma must be the *in-window* range: min(T_max/T_min, t_max/t_min) (Phase 0 finding)."""
    L = np.log(float(dynamic_range))
    if convention == "charter":
        return float(1.0 + 2.0 * np.log(float(snr)) * L / np.pi**2)
    if convention == "arccosh":
        return float(bbp_count(dynamic_range, snr) + 1.0)
    raise ValueError(convention)


def ostrowsky_spacing(snr: float, convention: str = "arccosh") -> float:
    """Exponential-sampling spacing in ln T (Ostrowsky, Sornette, Parker & Pike 1981):
    a solution band-limited to Mellin frequency w_max is determined by samples on a
    geometric grid with ratio exp(pi / w_max) = R_min. Solution-domain grids denser
    than this carry no independent information at that SNR; the harness's default
    grids are much denser (for quadrature), which is fine but not informative."""
    return float(np.log(r_min(snr, convention)))


def mellin_closed_form_ratios(n: np.ndarray, dynamic_range: float) -> np.ndarray:
    """sigma_n / sigma_0 = 1 / sqrt(cosh(n pi^2 / ln gamma)) — the per-index prediction
    from uniform quantisation of the Mellin frequency on a log-interval of length
    ln gamma.  Phase 0 measurement: the *count* it implies is right to about +-2 with a
    covering window, but the individual low-index ratios are not (sigma_1/sigma_0 is
    ~0.33 numerically for every gamma >= 100, against 0.48-0.78 predicted), so use it
    for the decay *rate*, not per index."""
    n = np.asarray(n, dtype=float)
    return 1.0 / np.sqrt(np.cosh(n * np.pi**2 / np.log(dynamic_range)))
