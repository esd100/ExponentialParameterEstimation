"""
Estimator interface — deliberately empty of implementations.

Charter G2: no method counts as surveyed until it is implemented *in the
harness* and scored, and Phase 1 (method families) is gated on a finished
Phase 0 harness.  This module therefore fixes only the contract that every
family will implement, so the harness axes are bound before any method
exists and no method can be written against a private convention.

    class Estimator(Protocol):
        family: MethodFamily
        variant: str
        min_access: AccessLevel
        def supports(kernel, representation, grid) -> (bool, reason)
        def fit(obs: Observation) -> Estimate

`supports` returning False is *not* a permitted blank in the grid (G5): the
obligation is to locate or construct the adapted variant.  The `reason`
string is what goes into the logged impossibility argument if no variant
exists, so it must state its assumptions.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping, Protocol, runtime_checkable

import numpy as np

from ..axes import AccessLevel, Cell, MethodFamily, Representation, SamplingGrid
from ..design import Design
from ..kernels.base import Kernel
from ..params import Theta


@dataclass
class Observation:
    """What an estimator is allowed to see, gated by the access level of the
    cell. Fields above the cell's access level are None."""
    cell: Cell
    kernel: Kernel
    design: Design
    data: np.ndarray                       # image-domain data in the cell's representation, or k-space for RAW_KSPACE
    kspace: np.ndarray | None = None       # L0/L1 only
    coil_sensitivities: np.ndarray | None = None   # L0 only
    noise_covariance: np.ndarray | None = None     # L0 only (prescan Psi)
    pipeline_metadata: Mapping[str, object] | None = None  # L4 and better
    sigma_hint: float | None = None        # NoiseKnowledge.SIGMA_KNOWN / SIGMA_PRESCAN / SIGMA_MISSPECIFIED


@dataclass
class Estimate:
    theta: Theta | None                     # discrete estimate (None for spectrum-only methods)
    K: int | None
    spectrum_grid: np.ndarray | None = None # (M, p) for continuum methods
    spectrum: np.ndarray | None = None      # (M,)
    covariance: np.ndarray | None = None    # in theta.pack() layout
    intervals: np.ndarray | None = None     # (n_params, 2) nominal 95%
    sigma: float | None = None              # jointly estimated noise level, if any
    diagnostics: dict = field(default_factory=dict)


@runtime_checkable
class Estimator(Protocol):
    family: MethodFamily
    variant: str
    min_access: AccessLevel

    def supports(self, kernel: Kernel, representation: Representation, grid: SamplingGrid) -> tuple[bool, str]: ...
    def fit(self, obs: Observation) -> Estimate: ...


_REGISTRY: dict[str, type] = {}


def register(cls):
    key = f"{cls.family.value}:{cls.variant}"
    if key in _REGISTRY:
        raise ValueError(f"estimator {key} already registered")
    _REGISTRY[key] = cls
    return cls


def available() -> list[str]:
    return sorted(_REGISTRY)


# No estimators are registered in Phase 0 (charter G2). The Lanczos
# correctness test is estimator-free by construction: it compares published
# and pre-computed exponential sums through the kernel's forward model only.
