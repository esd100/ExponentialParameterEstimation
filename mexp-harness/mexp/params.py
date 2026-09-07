"""
Parameter vocabulary shared by every kernel.

The invariant across all five modalities (charter §2.1) is that, for fixed
non-linear parameters, the noiseless signal is *linear in the component
amplitudes*:

    S(design) = Phi(xi_1..xi_K, nu; design) @ a          (+ fixed atoms)

where xi_k are the per-component non-linear parameters (T2; T1; (T2*, df);
T1rho or a dispersion parameterisation; D or a diffusion tensor), nu are
global nuisance parameters (inversion efficiency, flip angle, global phase,
...), and a are amplitudes that may be positive, real, or complex.  This
module fixes how those three blocks are declared, packed and unpacked, so
that CRLB, VARPRO-type and Bayesian machinery downstream see one layout.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Literal, Sequence

import numpy as np


class AmplitudeField(Enum):
    POSITIVE = "positive"   # a_k > 0 (T2, T1rho, scalar diffusion, IR after polarity fix)
    REAL = "real"           # sign free (IR with unresolved polarity, phase-corrected real)
    COMPLEX = "complex"     # a_k e^{i phi_k} (T2* with retained phase)


class SignalField(Enum):
    REAL = "real"
    COMPLEX = "complex"


@dataclass(frozen=True)
class ParamSpec:
    """One scalar parameter. `scale` says how it should be gridded /
    reparameterised (decay times are log-scale; a frequency offset is linear)."""
    name: str
    unit: str = ""
    scale: Literal["log", "linear"] = "log"
    lower: float = 0.0
    upper: float = np.inf
    description: str = ""

    def validate(self, x) -> None:
        x = np.asarray(x)
        if np.any(x < self.lower) or np.any(x > self.upper):
            raise ValueError(f"{self.name} out of bounds [{self.lower}, {self.upper}]: {x}")


@dataclass
class Theta:
    """Parameters of a discrete K-component model for one kernel.

    amplitudes : (K,) real or complex
    nonlinear  : (K, p) per-component non-linear parameters, p = len(kernel.component_params)
    nuisance   : (q,)   global nuisance parameters, q = len(kernel.nuisance_params)
    fixed      : (r,)   amplitudes of the kernel's fixed atoms (e.g. constant offset)
    """
    amplitudes: np.ndarray
    nonlinear: np.ndarray
    nuisance: np.ndarray = field(default_factory=lambda: np.zeros(0))
    fixed: np.ndarray = field(default_factory=lambda: np.zeros(0))

    def __post_init__(self):
        self.amplitudes = np.atleast_1d(np.asarray(self.amplitudes))
        self.nonlinear = np.asarray(self.nonlinear, dtype=float)
        if self.nonlinear.ndim == 1:
            self.nonlinear = self.nonlinear[:, None]
        self.nuisance = np.atleast_1d(np.asarray(self.nuisance, dtype=float))
        self.fixed = np.atleast_1d(np.asarray(self.fixed))
        if self.nonlinear.shape[0] != self.amplitudes.shape[0]:
            raise ValueError("amplitudes and nonlinear must have the same K")

    @property
    def K(self) -> int:
        return int(self.amplitudes.shape[0])

    @property
    def p(self) -> int:
        return int(self.nonlinear.shape[1])

    # --- packing: the canonical flat layout used by Jacobians and CRLB ------
    # [Re a (K)] [Im a (K) if complex] [xi (K*p, row-major)] [nu (q)] [fixed (r)]
    def pack(self) -> np.ndarray:
        parts = [np.real(self.amplitudes)]
        if np.iscomplexobj(self.amplitudes):
            parts.append(np.imag(self.amplitudes))
        parts += [self.nonlinear.ravel(), self.nuisance, np.real(self.fixed)]
        return np.concatenate([np.asarray(x, dtype=float) for x in parts])

    def unpack(self, flat: np.ndarray) -> "Theta":
        flat = np.asarray(flat, dtype=float)
        K, p = self.K, self.p
        i = 0
        re = flat[i:i + K]; i += K
        if np.iscomplexobj(self.amplitudes):
            im = flat[i:i + K]; i += K
            amps = re + 1j * im
        else:
            amps = re
        xi = flat[i:i + K * p].reshape(K, p); i += K * p
        nu = flat[i:i + self.nuisance.size]; i += self.nuisance.size
        fx = flat[i:i + self.fixed.size]
        return Theta(amps, xi, nu, fx)

    def labels(self, component_params: Sequence[ParamSpec], nuisance_params: Sequence[ParamSpec],
               fixed_names: Sequence[str] = ()) -> list[str]:
        K = self.K
        out = [f"Re a{k}" if np.iscomplexobj(self.amplitudes) else f"a{k}" for k in range(K)]
        if np.iscomplexobj(self.amplitudes):
            out += [f"Im a{k}" for k in range(K)]
        for k in range(K):
            out += [f"{ps.name}{k}" for ps in component_params]
        out += [ps.name for ps in nuisance_params]
        out += list(fixed_names)
        return out
