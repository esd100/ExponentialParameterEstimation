"""
Simulator slot — k-space-first by construction (charter §3.6, §4 standing rule).

Nothing here is implemented in this skeleton; what is fixed is *where noise
may enter*.  The only noise entry point in the whole package is
:meth:`Simulator.add_kspace_noise`, which acts on a :class:`KSpace` object.
There is no function anywhere that takes an image and returns a noisy image,
and tests/test_kspace_first_rule.py fails the suite if one appears outside
this sub-package.

Pipeline (each stage a harness axis level, charter §3.3):

    parameter maps + kernel + design
        -> synthesize_kspace(...)            noiseless multi-coil k-space, trajectory, sensitivities
        -> add_kspace_noise(kspace, Psi)     circular complex Gaussian, channel covariance Psi
        -> reconstruct(kspace, pipeline)     SINGLE_COIL | SOS | ROEMER | SENSE(R) | GRAPPA | PF | CS | DL
        -> complex image-domain data         consumed by mexp.representation.represent(...)

The k-space arm (ReconPipeline.RAW_KSPACE) skips `reconstruct` and hands the
noisy k-space to the estimator directly (access L0/L1).

SNR is defined at the source (axes.SNRDefinition.REFERENCE_OVER_UNACCELERATED_SIGMA):
`sigma_ref` is the per-pixel real-part noise std that the *same* k-space
noise produces in a fully sampled single-coil R=1 reconstruction.  Any
pipeline's actual noise is then a measured consequence, never an input.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping, Protocol, runtime_checkable

import numpy as np

from ..axes import ReconPipeline
from ..design import Design
from ..kernels.base import Kernel


class ImageDomainNoiseForbidden(RuntimeError):
    """Raised by any code path that would add noise to image-domain data.
    Charter §4: 'Generating a synthetic image and adding noise to it by
    formula is not permitted, at any stage, for any purpose that feeds the
    taxonomy.'"""


@dataclass
class KSpace:
    data: np.ndarray                         # (n_coils, n_encodings, *k_shape) complex
    trajectory: Mapping[str, object]         # cartesian mask / non-cartesian coordinates, R, PF fraction
    sensitivities: np.ndarray | None         # (n_coils, *img_shape) complex, None if unknown
    noise_covariance: np.ndarray | None = None  # Psi (n_coils, n_coils); None before add_kspace_noise
    sigma_ref: float | None = None           # see module docstring
    meta: dict = field(default_factory=dict)

    @property
    def is_noisy(self) -> bool:
        return self.noise_covariance is not None


@dataclass
class ComplexImages:
    data: np.ndarray                         # (n_encodings, *img_shape) complex, coil-combined
    per_coil: np.ndarray | None              # (n_coils, n_encodings, *img_shape) if pipeline exposes L2
    pipeline: ReconPipeline
    pipeline_params: Mapping[str, float]
    g_factor: np.ndarray | None = None       # SENSE/GRAPPA only; *measured* by pseudo-replica, not assumed
    meta: dict = field(default_factory=dict)


@runtime_checkable
class Simulator(Protocol):
    def synthesize_kspace(self, parameter_maps: Mapping[str, np.ndarray], kernel: Kernel, design: Design,
                          sensitivities: np.ndarray, trajectory: Mapping[str, object]) -> KSpace: ...

    def add_kspace_noise(self, kspace: KSpace, psi: np.ndarray, sigma_ref: float,
                         rng: np.random.Generator) -> KSpace: ...

    def reconstruct(self, kspace: KSpace, pipeline: ReconPipeline,
                    params: Mapping[str, float]) -> ComplexImages: ...


def add_image_noise(*args, **kwargs):
    """Intentionally present and intentionally unusable, so that a grep for
    the obvious shortcut finds this docstring instead of a working function."""
    raise ImageDomainNoiseForbidden(
        "Image-domain noise injection is forbidden by charter §4. Synthesize k-space, "
        "add complex Gaussian noise there (Simulator.add_kspace_noise), and run a real reconstruction."
    )
