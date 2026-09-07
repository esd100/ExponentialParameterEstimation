"""
Pluggable kernel interface (charter §2, §4 Phase 0 deliverable).

A kernel plugin declares *what a modality's forward model is* and nothing
else.  It does not know about noise, reconstruction pipelines, data
representation, access level, or estimators; those are separate layers that
consume the kernel through this interface.  The contract is:

    atoms(xi, nu, design) -> Phi           (N, M) real or complex
        Phi[n, m] = phi(design_n ; xi_m, nu)

    forward(theta, design) = atoms(theta.nonlinear, theta.nuisance, design) @ theta.amplitudes
                             + fixed_atoms(design) @ theta.fixed

Everything else (Jacobian, discretised operator, default grids) has a
generic implementation in terms of `atoms`, and kernels override only when
an analytic form is available.

How the five modalities map onto this (see docs/kernel-interface.md):

  T2 CPMG        coords (TE,)         xi = (T2,)          nu = ()            real, positive
  T2 CPMG + EPG  coords (TE,)         xi = (T2,)          nu = (B1, T1)      real, positive
  T1 IR          coords (TI,)         xi = (T1,)          nu = (eta,)        real, real/positive
  T1 Look-Locker coords (TI,)         xi = (T1,)          nu = (alpha, TR)   real, positive
  T1 SR / VFA    coords (TS,)/(FA,)   xi = (T1,)          nu = (TR,)         real, positive
  T2* mGRE       coords (TE,)         xi = (T2*, df)      nu = (phi0,)       COMPLEX, complex
  T1rho          coords (TSL,)        xi = (T1rho,)       nu = ()            real, positive
  T1rho disp.    coords (TSL, w1)     xi = (R0, Rex, kex) nu = ()            real, positive
  Diffusion      coords (b,)          xi = (D,)           nu = ()            real, positive
  Diff. tensor   coords (b_xx..b_yz)  xi = (D_xx..D_yz)   nu = ()            real, positive

The last row shows why xi is (K, p) and not (K,): a matrix-variate Laplace
kernel on the PSD cone needs p = 6 per component, and the grid used by
`discretize` is then any (M, 6) table of PSD tensors.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import ClassVar, Sequence

import numpy as np

from ..axes import Modality
from ..design import Design
from ..params import AmplitudeField, ParamSpec, SignalField, Theta


class Kernel(ABC):
    # ---- declaration (class attributes on every plugin) -------------------
    name: ClassVar[str]
    modality: ClassVar[Modality]
    coords: ClassVar[tuple[str, ...]]
    component_params: ClassVar[tuple[ParamSpec, ...]]
    nuisance_params: ClassVar[tuple[ParamSpec, ...]] = ()
    fixed_atom_names: ClassVar[tuple[str, ...]] = ()
    signal_field: ClassVar[SignalField] = SignalField.REAL
    amplitude_field: ClassVar[AmplitudeField] = AmplitudeField.POSITIVE
    citation: ClassVar[str] = ""

    # ---- the one abstract method ------------------------------------------
    @abstractmethod
    def atoms(self, xi: np.ndarray, nu: np.ndarray, design: Design) -> np.ndarray:
        """Phi (N, M): column m is the unit-amplitude signal of a component with
        non-linear parameters xi[m] (shape (M, p)) under nuisance nu (q,)."""

    # ---- generic machinery --------------------------------------------------
    @property
    def p(self) -> int:
        return len(self.component_params)

    @property
    def q(self) -> int:
        return len(self.nuisance_params)

    def fixed_atoms(self, design: Design) -> np.ndarray:
        """(N, r) columns with fixed shape and free amplitude (e.g. a constant
        offset, charter §3.2). Default: none."""
        return np.zeros((design.N, 0))

    def nuisance_defaults(self) -> np.ndarray:
        return np.zeros(self.q)

    def validate_design(self, design: Design) -> None:
        missing = [c for c in self.coords if c not in design.coords]
        if missing:
            raise ValueError(f"{self.name} needs design coords {self.coords}; missing {missing}")

    def validate_theta(self, theta: Theta) -> None:
        if theta.p != self.p:
            raise ValueError(f"{self.name}: theta.nonlinear has p={theta.p}, kernel has p={self.p}")
        if theta.nuisance.size != self.q:
            raise ValueError(f"{self.name}: theta.nuisance has q={theta.nuisance.size}, kernel has q={self.q}")
        if theta.fixed.size != len(self.fixed_atom_names):
            raise ValueError(f"{self.name}: theta.fixed has r={theta.fixed.size}, kernel has r={len(self.fixed_atom_names)}")
        for j, ps in enumerate(self.component_params):
            ps.validate(theta.nonlinear[:, j])
        for j, ps in enumerate(self.nuisance_params):
            ps.validate(theta.nuisance[j])
        if self.amplitude_field is AmplitudeField.POSITIVE and np.any(np.real(theta.amplitudes) < 0):
            raise ValueError(f"{self.name}: amplitudes must be positive")
        if self.amplitude_field is not AmplitudeField.COMPLEX and np.iscomplexobj(theta.amplitudes):
            raise ValueError(f"{self.name}: amplitudes must be real")

    def forward(self, theta: Theta, design: Design) -> np.ndarray:
        """Noiseless signal (N,), real or complex per `signal_field`."""
        self.validate_design(design)
        self.validate_theta(theta)
        Phi = self.atoms(theta.nonlinear, theta.nuisance, design)
        s = Phi @ theta.amplitudes
        if theta.fixed.size:
            s = s + self.fixed_atoms(design) @ theta.fixed
        return s

    def discretize(self, design: Design, grid: np.ndarray, nu: np.ndarray | None = None) -> np.ndarray:
        """The discretised operator A (N, M) of the continuum form (charter §1.2):
        atoms evaluated on a grid (M, p) of non-linear parameter values."""
        self.validate_design(design)
        grid = np.asarray(grid, dtype=float)
        if grid.ndim == 1:
            grid = grid[:, None]
        nu = self.nuisance_defaults() if nu is None else np.asarray(nu, dtype=float)
        return self.atoms(grid, nu, design)

    def default_grid(self, M: int, lo: Sequence[float] | None = None,
                     hi: Sequence[float] | None = None) -> np.ndarray:
        """(M, p) grid over the kernel's physical range: geometric for
        log-scale params, linear otherwise. For p > 1 it is the product of
        per-parameter 1-D grids with ~M^(1/p) points each (M total)."""
        lo = list(self.physical_range()[0] if lo is None else lo)
        hi = list(self.physical_range()[1] if hi is None else hi)
        if not (np.all(np.isfinite(lo)) and np.all(np.isfinite(hi))):
            raise ValueError(f"{self.name}: physical_range() must be finite to build a grid; got {lo}..{hi}")
        if self.p == 1:
            ps = self.component_params[0]
            g = np.geomspace(lo[0], hi[0], M) if ps.scale == "log" else np.linspace(lo[0], hi[0], M)
            return g[:, None]
        per_axis = max(2, int(round(M ** (1.0 / self.p))))
        axes = []
        for j, ps in enumerate(self.component_params):
            axes.append(np.geomspace(lo[j], hi[j], per_axis) if ps.scale == "log"
                        else np.linspace(lo[j], hi[j], per_axis))
        mesh = np.meshgrid(*axes, indexing="ij")
        return np.stack([m.ravel() for m in mesh], axis=1)

    def physical_range(self) -> tuple[tuple[float, ...], tuple[float, ...]]:
        """Default (lo, hi) per component parameter for the modality; used by
        the T-range / dynamic-range axis of the conditioning study."""
        return (tuple(ps.lower for ps in self.component_params),
                tuple(ps.upper for ps in self.component_params))

    def reference_signal(self, theta: Theta) -> float:
        """S_ref for the harness SNR definition (axes.SNRDefinition): the
        unattenuated magnetisation sum |a|_1. Kernels whose atoms are not
        unit at the reference point override this."""
        return float(np.sum(np.abs(theta.amplitudes)))

    # ---- derivatives ----------------------------------------------------------
    def jacobian(self, theta: Theta, design: Design, rel_step: float = 1e-6) -> np.ndarray:
        """d forward / d theta.pack()  ->  (N, n_params), complex if the signal is.
        Generic central finite differences; override with an analytic form."""
        self.validate_design(design)
        flat0 = theta.pack()
        n = flat0.size
        s0 = self.forward(theta, design)
        J = np.zeros((design.N, n), dtype=s0.dtype)
        for i in range(n):
            h = rel_step * max(1.0, abs(flat0[i]))
            fp, fm = flat0.copy(), flat0.copy()
            fp[i] += h
            fm[i] -= h
            J[:, i] = (self._forward_unchecked(theta.unpack(fp), design)
                       - self._forward_unchecked(theta.unpack(fm), design)) / (2 * h)
        return J

    def _forward_unchecked(self, theta: Theta, design: Design) -> np.ndarray:
        Phi = self.atoms(theta.nonlinear, theta.nuisance, design)
        s = Phi @ theta.amplitudes
        if theta.fixed.size:
            s = s + self.fixed_atoms(design) @ theta.fixed
        return s

    @staticmethod
    def as_real_rows(J: np.ndarray) -> np.ndarray:
        """Stack Re/Im rows of a complex Jacobian (for Gaussian-complex CRLB)."""
        return np.vstack([np.real(J), np.imag(J)]) if np.iscomplexobj(J) else J

    # ---- introspection ----------------------------------------------------------
    def describe(self) -> dict:
        return {
            "name": self.name, "modality": self.modality.value, "coords": self.coords,
            "component_params": [ps.name for ps in self.component_params],
            "nuisance_params": [ps.name for ps in self.nuisance_params],
            "fixed_atoms": self.fixed_atom_names,
            "signal_field": self.signal_field.value, "amplitude_field": self.amplitude_field.value,
        }

    def __repr__(self) -> str:
        return f"<Kernel {self.name}: {self.modality.value}, coords={self.coords}, p={self.p}, q={self.q}>"


class OffsetAugmented(Kernel):
    """Wrap any kernel with a free constant-offset atom (charter §3.2: the
    'free constant offset' is an implicit sigma estimate). Kept as a wrapper so
    the base kernel stays a pure decay model."""

    def __init__(self, inner: Kernel):
        self.inner = inner
        self.name = f"{inner.name}+offset"
        self.modality = inner.modality
        self.coords = inner.coords
        self.component_params = inner.component_params
        self.nuisance_params = inner.nuisance_params
        self.fixed_atom_names = (*inner.fixed_atom_names, "offset")
        self.signal_field = inner.signal_field
        self.amplitude_field = inner.amplitude_field

    def atoms(self, xi, nu, design):
        return self.inner.atoms(xi, nu, design)

    def fixed_atoms(self, design):
        base = self.inner.fixed_atoms(design)
        return np.hstack([base, np.ones((design.N, 1))])

    def physical_range(self):
        return self.inner.physical_range()
