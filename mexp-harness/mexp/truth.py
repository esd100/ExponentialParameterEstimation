"""
Ground truth (charter §6.1 'Ground truth' axis; §6.2 'functional recovery').

Every ground truth answers two questions: what is the noiseless signal on a
design, and what is the value of a functional of the underlying spectrum.
The second is what the Phase 3 'estimate functionals, not spectra' direction
scores against, so it is part of the truth object from day one.

Kinds:
  DiscreteSpectrum      K components of a kernel                (GroundTruthKind.DISCRETE)
  ContinuousSpectrum    density on a grid of the kernel's xi     (GroundTruthKind.CONTINUOUS)
  PhysicalTruth         any object producing a signal from physics that is
                        *not* a sum of the kernel's atoms (EPG with stimulated
                        echoes, Bloch-McConnell exchange, stretched exponential).
                        Declared as a Protocol; implementations arrive with the
                        simulator, not here.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, runtime_checkable

import numpy as np

from .axes import GroundTruthKind
from .design import Design
from .kernels.base import Kernel
from .params import Theta


@runtime_checkable
class GroundTruth(Protocol):
    kind: GroundTruthKind

    def signal(self, design: Design) -> np.ndarray: ...
    def mass_below(self, threshold: float, param_index: int = 0) -> float: ...


@dataclass
class DiscreteSpectrum:
    kernel: Kernel
    theta: Theta
    kind: GroundTruthKind = GroundTruthKind.DISCRETE

    def signal(self, design: Design) -> np.ndarray:
        return self.kernel.forward(self.theta, design)

    def mass_below(self, threshold: float, param_index: int = 0) -> float:
        """Fraction of amplitude with xi[param_index] < threshold (e.g. myelin
        water fraction = mass below T2 = 40 ms)."""
        a = np.abs(self.theta.amplitudes)
        sel = self.theta.nonlinear[:, param_index] < threshold
        return float(a[sel].sum() / a.sum())

    @property
    def K(self) -> int:
        return self.theta.K


@dataclass
class ContinuousSpectrum:
    """density[m] >= 0 on grid (M, p); signal = discretize(design, grid) @ (density * weights)."""
    kernel: Kernel
    grid: np.ndarray
    density: np.ndarray
    weights: np.ndarray | None = None       # quadrature weights; default log-uniform trapezoid for p = 1
    nu: np.ndarray | None = None
    kind: GroundTruthKind = GroundTruthKind.CONTINUOUS

    def __post_init__(self):
        self.grid = np.asarray(self.grid, dtype=float)
        if self.grid.ndim == 1:
            self.grid = self.grid[:, None]
        self.density = np.asarray(self.density, dtype=float)
        if np.any(self.density < 0):
            raise ValueError("spectrum density must be non-negative (charter §1.2, f >= 0)")
        if self.weights is None:
            if self.grid.shape[1] != 1:
                raise ValueError("weights required for p > 1 grids")
            u = np.log(self.grid[:, 0])
            w = np.gradient(u)
            self.weights = w
        self.weights = np.asarray(self.weights, dtype=float)

    def signal(self, design: Design) -> np.ndarray:
        A = self.kernel.discretize(design, self.grid, self.nu)
        return A @ (self.density * self.weights)

    def mass_below(self, threshold: float, param_index: int = 0) -> float:
        m = self.density * self.weights
        sel = self.grid[:, param_index] < threshold
        return float(m[sel].sum() / m.sum())


@runtime_checkable
class PhysicalTruth(Protocol):
    """Signal from a physics simulator that violates the fitted kernel
    (EXCHANGE_COUPLED or NON_EXPONENTIAL). Must expose the *kernel-language*
    quantities a method would be judged against (e.g. pool fractions ->
    mass_below), because RMSE on parameters the model does not have is
    meaningless; functional recovery is the comparator (charter §6.2)."""
    kind: GroundTruthKind

    def signal(self, design: Design) -> np.ndarray: ...
    def mass_below(self, threshold: float, param_index: int = 0) -> float: ...
    def nominal_theta(self) -> Theta: ...
