"""
Cramér–Rao lower bounds (charter §4 Phase 0; §1.2 falsifiable threshold; §3.2).

Not an estimator: nothing here fits data (charter G2 untouched).  The
bounds are computed from a kernel's Jacobian at a ground truth and a noise
model, and are the floor every method in Phases 1–2 is scored against
(§6.2 'CRLB efficiency').

Noise models
  gaussian_real     y = s(θ) + e,  e ~ N(0, σ² I)                (phase-corrected real arm; k-space arm)
  gaussian_complex  y = s(θ) + e,  e ~ CN(0, 2σ² I)  (σ per channel)  (complex arm)
  rician            m_i ~ Rice(A_i = |s_i(θ)|, σ)                 (magnitude arm, single coil / Roemer)

For the Rician model the per-sample Fisher information is computed
numerically from the exact Rician likelihood, in the scaled variable
u = m/σ, ν = A/σ:

    ∂ℓ/∂A = (1/σ)(u R − ν),                    R = I₁(uν)/I₀(uν)
    ∂ℓ/∂σ = (1/σ)(u² + ν² − 2uνR − 2)

    I_AA = g(ν)/σ²,  I_Aσ = c(ν)/σ²,  I_σσ = h(ν)/σ²   with g, c, h expectations over Rice(ν, 1).

Gaussian limits: g → 1, c → 0, h → 2 as ν → ∞ (checked in tests).  These
are the K = 1 building blocks of Sijbers & den Dekker (MRM 2004); the
K ≥ 2 joint (θ, σ) block, obtained here by pushing them through the
multi-exponential Jacobian, is the object charter §3.2 / gaps A3 names —
this module computes it numerically; the analytic degeneracy-manifold
work of A3 is not attempted here.

SNR conventions: callers pass σ.  Helpers `sigma_from_first_echo_snr` and
`sigma_from_reference_snr` convert the two conventions the charter uses
(first-echo SNR in §1.2's threshold; S_ref/σ in the harness axes).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import numpy as np
from scipy.special import i0e, i1e

from .design import Design
from .kernels.base import Kernel
from .params import Theta

NoiseModel = Literal["gaussian_real", "gaussian_complex", "rician"]


# --------------------------------------------------------------------------
# SNR conventions
# --------------------------------------------------------------------------

def sigma_from_first_echo_snr(kernel: Kernel, theta: Theta, design: Design, snr: float) -> float:
    """σ such that |s(t_1)| / σ = snr (charter §1.2 'first-echo SNR')."""
    s = kernel.forward(theta, design)
    return float(np.abs(s[0]) / snr)


def sigma_from_reference_snr(kernel: Kernel, theta: Theta, snr: float) -> float:
    """σ such that S_ref / σ = snr (harness axes.SNRDefinition default; S_ref = Σ|a|)."""
    return float(kernel.reference_signal(theta) / snr)


# --------------------------------------------------------------------------
# Rician per-sample Fisher blocks (numerical, exact likelihood)
# --------------------------------------------------------------------------

def _rice_pdf_scaled(u: np.ndarray, nu: np.ndarray) -> np.ndarray:
    """Rice(ν, 1) density in u = m/σ, computed stably: u exp(-(u-ν)²/2) I0e(uν)."""
    return u * np.exp(-0.5 * (u - nu) ** 2) * i0e(u * nu)


def rician_fisher_blocks(nu: np.ndarray, n_grid: int = 4001) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """(g, c, h) for each ν = A/σ: dimensionless per-sample Fisher information
    for (A, σ) under Rice(A, σ); multiply by 1/σ² to get I_AA, I_Aσ, I_σσ."""
    nu = np.atleast_1d(np.asarray(nu, dtype=float))
    g = np.empty_like(nu)
    c = np.empty_like(nu)
    h = np.empty_like(nu)
    for k, v in enumerate(nu):
        umax = v + 12.0
        u = np.linspace(1e-9, umax, n_grid)
        p = _rice_pdf_scaled(u, v)
        R = i1e(u * v) / i0e(u * v)
        dA = u * R - v
        ds = u**2 + v**2 - 2 * u * v * R - 2.0
        w = np.gradient(u)
        Z = np.sum(p * w)
        g[k] = np.sum(p * dA**2 * w) / Z
        c[k] = np.sum(p * dA * ds * w) / Z
        h[k] = np.sum(p * ds**2 * w) / Z
    return g, c, h


# --------------------------------------------------------------------------
# Fisher information and CRLB
# --------------------------------------------------------------------------

@dataclass
class CRLBResult:
    fim: np.ndarray                 # (n, n) [+1 if joint σ]
    cov: np.ndarray                 # pseudo-inverse of fim
    labels: list[str]
    theta_flat: np.ndarray
    sigma: float
    noise_model: str
    joint_sigma: bool

    @property
    def sd(self) -> np.ndarray:
        return np.sqrt(np.maximum(np.diag(self.cov), 0.0))

    @property
    def relative_sd(self) -> np.ndarray:
        ref = np.concatenate([self.theta_flat, [self.sigma]]) if self.joint_sigma else self.theta_flat
        return self.sd / np.abs(ref)

    def relative_sd_of(self, prefix: str) -> dict[str, float]:
        return {l: float(r) for l, r in zip(self.labels, self.relative_sd) if l.startswith(prefix)}

    @property
    def fim_eigenvalues(self) -> np.ndarray:
        """Sloppy-model spectrum (Transtrum–Machta–Sethna): eigenvalues of the FIM, descending."""
        return np.sort(np.linalg.eigvalsh(self.fim))[::-1]


def fisher_information(kernel: Kernel, theta: Theta, design: Design, sigma: float,
                       noise_model: NoiseModel = "gaussian_real", joint_sigma: bool = False) -> CRLBResult:
    J = kernel.jacobian(theta, design)          # (N, n), complex if the signal is complex
    s = kernel.forward(theta, design)
    labels = theta.labels(kernel.component_params, kernel.nuisance_params, kernel.fixed_atom_names)
    flat = theta.pack()

    if noise_model == "gaussian_real":
        if np.iscomplexobj(J):
            raise ValueError("gaussian_real needs a real signal; use gaussian_complex or the phase-corrected arm")
        F = (J.T @ J) / sigma**2
        if joint_sigma:
            n = F.shape[0]
            Fj = np.zeros((n + 1, n + 1))
            Fj[:n, :n] = F
            Fj[n, n] = 2.0 * design.N / sigma**2       # σ block for Gaussian; cross terms vanish
            F = Fj
    elif noise_model == "gaussian_complex":
        F = np.real(np.conj(J).T @ J) / sigma**2
        if joint_sigma:
            n = F.shape[0]
            Fj = np.zeros((n + 1, n + 1))
            Fj[:n, :n] = F
            Fj[n, n] = 4.0 * design.N / sigma**2       # two real channels per sample
            F = Fj
    elif noise_model == "rician":
        if np.iscomplexobj(J):
            # magnitude of a complex signal: A = |s|, dA/dθ = Re(conj(s) J)/|s|
            A = np.abs(s)
            JA = np.real(np.conj(s)[:, None] * J) / np.maximum(A, 1e-300)[:, None]
        else:
            A = np.abs(s)
            JA = np.sign(s)[:, None] * J
        g, c, h = rician_fisher_blocks(A / sigma)
        F = (JA.T * g) @ JA / sigma**2
        if joint_sigma:
            n = F.shape[0]
            Fj = np.zeros((n + 1, n + 1))
            Fj[:n, :n] = F
            Fj[:n, n] = Fj[n, :n] = JA.T @ c / sigma**2
            Fj[n, n] = np.sum(h) / sigma**2
            F = Fj
    else:
        raise ValueError(noise_model)

    if joint_sigma:
        labels = labels + ["sigma"]
    cov = np.linalg.pinv(F, rcond=1e-15, hermitian=True)
    return CRLBResult(fim=F, cov=cov, labels=labels, theta_flat=flat, sigma=sigma,
                      noise_model=noise_model, joint_sigma=joint_sigma)


def crlb(kernel: Kernel, theta: Theta, design: Design, sigma: float,
         noise_model: NoiseModel = "gaussian_real", joint_sigma: bool = False) -> CRLBResult:
    """Alias for fisher_information (the result carries cov / sd / relative_sd)."""
    return fisher_information(kernel, theta, design, sigma, noise_model, joint_sigma)


def mass_below_gradient(theta: Theta, threshold: float, param_index: int = 0, joint_sigma: bool = False) -> np.ndarray:
    """Gradient (in theta.pack() layout, plus a trailing 0 for σ if joint) of the
    functional g(θ) = Σ_{k: ξ_k < threshold} |a_k| / Σ_k |a_k| — e.g. the myelin
    water fraction (charter §6.2 'functional recovery'). Real amplitudes only."""
    if np.iscomplexobj(theta.amplitudes):
        raise NotImplementedError("mass_below_gradient: complex amplitudes not supported yet")
    a = np.abs(theta.amplitudes)
    sel = (theta.nonlinear[:, param_index] < threshold).astype(float)
    S, Ss = a.sum(), (a * sel).sum()
    g = np.zeros(theta.pack().size + (1 if joint_sigma else 0))
    g[: theta.K] = np.sign(theta.amplitudes) * (sel * S - Ss) / S**2
    return g


def functional_sd(result: "CRLBResult", grad: np.ndarray) -> float:
    """Delta-method lower bound on the SD of a scalar functional with gradient `grad`."""
    grad = np.asarray(grad, dtype=float)
    return float(np.sqrt(max(grad @ result.cov @ grad, 0.0)))


def lrt_noncentrality(delta: np.ndarray, sigma: float) -> float:
    """‖Δ‖²/σ² for two fully specified nested-or-not models differing by Δ in the
    noiseless data under white Gaussian noise: the expected excess χ² of the
    wrong model, and (d′)² of the ideal both-models-known detector."""
    return float(np.sum(np.abs(np.asarray(delta)) ** 2) / sigma**2)
