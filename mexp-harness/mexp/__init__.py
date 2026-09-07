"""
mexp — Phase 0 benchmark harness for multi-exponential MR parameter estimation.

Layers (each a charter §6.1 axis or a consumer of them):

    axes            the grid vocabulary; Cell = one benchmark address
    design          encoding points; sampling-grid factories; co-array designs
    params          ParamSpec / Theta: the shared parameter layout
    kernels         pluggable forward models (Kernel ABC; T2 CPMG registered)
    truth           ground-truth objects with signal() and functionals
    representation  complex / phase-corrected real / magnitude arms
    sim             k-space-first simulator slot (interface + noise-entry guard)
    conditioning    SVD, Picard, TSVD resolution, continuum reference expressions
    metrics         §6.2 metric vocabulary
    estimators      Estimator protocol; no implementations (charter G2)
    datasets        reference data (NIST StRD Lanczos)
"""
from . import axes, conditioning, design, kernels, metrics, params, representation, truth

__all__ = ["axes", "conditioning", "design", "kernels", "metrics", "params", "representation", "truth"]
__version__ = "0.0.1"
