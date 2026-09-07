"""
Data representation arms (charter §2.3): complex, phase-corrected real,
magnitude.  These are deterministic maps applied to *reconstructed complex
image-domain data* produced by the k-space-first simulator (or to real
scanner data).  They add nothing and assume nothing about the noise; the
noise family of each arm (Gaussian / Gaussian / Rician or chi) is a
*consequence* of the pipeline that produced the complex data, which is why
the noise family is never declared here.
"""
from __future__ import annotations

import numpy as np

from .axes import Representation


def represent(z: np.ndarray, arm: Representation, phase_ref: np.ndarray | None = None) -> np.ndarray:
    """z: complex data, last axis = encoding points.
    phase_ref: per-sample phase estimate for the PHASE_CORRECTED_REAL arm
    (e.g. from the first echo or a low-pass fit); if None, the phase of z
    itself is used, which is the noise-free idealisation."""
    z = np.asarray(z)
    if arm is Representation.COMPLEX:
        return z.astype(complex)
    if arm is Representation.MAGNITUDE:
        return np.abs(z)
    if arm is Representation.PHASE_CORRECTED_REAL:
        ph = np.angle(z) if phase_ref is None else np.asarray(phase_ref)
        return np.real(z * np.exp(-1j * ph))
    raise ValueError(arm)
