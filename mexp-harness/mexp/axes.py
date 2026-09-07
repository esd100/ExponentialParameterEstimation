"""
Harness axes (charter §6.1).

Every axis of the benchmark grid is a first-class enumeration here, so that a
benchmark result is always addressed by a full :class:`Cell` and never by an
implicit default.  Nothing in this module computes anything; it fixes the
vocabulary that every kernel, design, ground truth, simulator stage and (later)
estimator must speak.

Design rule: an axis that is "not applicable yet" still exists as an enum with
an explicit level, so that adding a level later is a data change, not an API
change.  The one continuous axis (SNR) is carried as a value plus a definition
tag, because "SNR" is ambiguous across modalities and pipelines (see
:class:`SNRDefinition`).
"""
from __future__ import annotations

from dataclasses import dataclass, field, fields
from enum import Enum
from itertools import product
from typing import Iterable, Iterator, Mapping


class MethodFamily(Enum):
    """Charter §4, Phase 1 families (seven, incl. noise/error modelling)."""
    NLS = "nonlinear_least_squares"           # 1. LM, trust-region, VARPRO, multistart
    LINEAR_ALGEBRAIC = "prony_linear_algebraic" # 2. Prony, matrix pencil, ESPRIT, HSVD, AAA ...
    REGULARIZED = "regularized_inversion"       # 3. NNLS, rNNLS, CONTIN, Tikhonov, TSVD
    SPARSE = "sparse_off_grid"                  # 4. l1, BLASSO, atomic norm, SDP
    BAYESIAN = "bayesian"                       # 5. MCMC/HMC, nested sampling, RJMCMC, VB, SBI
    LEARNING = "learning_based"                 # 6. regression, dictionary matching, unrolled
    NOISE = "noise_error_modelling"             # 7. the §3.4 approaches
    REFERENCE = "reference"                     # CRLB / oracle rows in a results table (not a method)


class Modality(Enum):
    """Charter §2.2 headline modalities. Kernel *plugins* are finer than this
    (e.g. T1 has IR, SR, Look-Locker, VFA, MRF ...); each plugin declares one."""
    T2 = "T2"
    T1 = "T1"
    T2STAR = "T2star"
    T1RHO = "T1rho"
    DIFFUSION = "diffusion"


class Representation(Enum):
    """Charter §2.3 three data arms. Applied to complex image-domain data by
    :mod:`mexp.representation`; never inside a kernel."""
    COMPLEX = "complex"
    PHASE_CORRECTED_REAL = "phase_corrected_real"
    MAGNITUDE = "magnitude"


class ReconPipeline(Enum):
    """Charter §3.3 / §6.1. RAW_KSPACE is the k-space arm (no reconstruction)."""
    RAW_KSPACE = "raw_kspace"
    SINGLE_COIL = "single_coil"
    SOS_MULTICOIL = "sos_multicoil"
    ROEMER_ADAPTIVE = "roemer_adaptive"
    SENSE = "sense"                 # parameterised by R (see Cell.pipeline_params)
    GRAPPA = "grappa"               # parameterised by R, kernel size
    PARTIAL_FOURIER = "partial_fourier"
    COMPRESSED_SENSING = "compressed_sensing"  # parameterised by regulariser, weight
    DL_RECON = "dl_reconstruction"


class AccessLevel(Enum):
    """Charter §3.6 access ladder. Ordered: lower value = more access."""
    L0 = 0   # raw k-space + noise prescan + sensitivity maps
    L1 = 1   # raw k-space only
    L2 = 2   # per-coil complex images
    L3 = 3   # coil-combined complex images
    L4 = 4   # magnitude + pipeline metadata
    L5 = 5   # magnitude + protocol knowledge
    L6 = 6   # magnitude only (DICOM)

    def __le__(self, other: "AccessLevel") -> bool:
        return self.value <= other.value

    def __lt__(self, other: "AccessLevel") -> bool:
        return self.value < other.value


class NoiseKnowledge(Enum):
    """Charter §6.1 'Noise knowledge' axis (§3.2 value-of-noise-knowledge study)."""
    SIGMA_KNOWN = "sigma_known"
    SIGMA_JOINT = "sigma_estimated_jointly"
    SIGMA_PRESCAN = "sigma_from_prescan"
    SIGMA_BACKGROUND = "sigma_from_background"
    SIGMA_MISSPECIFIED = "sigma_misspecified"   # family and/or magnitude wrong


class NoiseCharacter(Enum):
    """Charter §6.1 'Noise character' axis. Realised only by the k-space-first
    simulator (charter §4 standing rule); never synthesised by formula."""
    STATIONARY = "stationary"
    G_FACTOR_MODULATED = "g_factor_modulated"
    NONSTATIONARY_CHI = "nonstationary_chi_varying_dof"
    CONTAMINATED_SPIKES = "contaminated_spikes"
    CONTAMINATED_PHYSIOLOGICAL = "contaminated_physiological"
    CONTAMINATED_GIBBS = "contaminated_gibbs"


class SamplingGrid(Enum):
    """Charter §6.1 'Sampling grid' axis (see :mod:`mexp.design` factories)."""
    UNIFORM = "uniform"
    SUBSET_OF_GRID = "subset_of_grid"       # with Hankel completion downstream
    SPARSE_RULER = "sparse_ruler_coarray"   # difference-set designs
    LOG_SPACED = "log_spaced"
    CRLB_OPTIMAL = "crlb_optimal"
    SCATTERED = "scattered"


class SampleBudget(Enum):
    """Charter §6.1 bands. The exact N lives on the Design; this is the band."""
    DENSE = "dense"        # 32-64
    MODERATE = "moderate"  # 12-16
    AUSTERE = "austere"    # 5-8

    @staticmethod
    def of(n: int) -> "SampleBudget":
        if n >= 32:
            return SampleBudget.DENSE
        if n >= 12:
            return SampleBudget.MODERATE
        return SampleBudget.AUSTERE


class GroundTruthKind(Enum):
    """Charter §6.1 'Ground truth' axis."""
    DISCRETE = "discrete"                 # K = 2, 3 ...
    CONTINUOUS = "continuous_spectrum"
    EXCHANGE_COUPLED = "exchange_coupled"  # Bloch-McConnell; model is *wrong*, not hard
    NON_EXPONENTIAL = "non_exponential"    # stretched, Mittag-Leffler, ...


class SNRDefinition(Enum):
    """How the SNR number is to be read.

    The harness default is :attr:`REFERENCE_OVER_UNACCELERATED_SIGMA`:
    SNR = S_ref / sigma_1, where S_ref is the kernel's reference signal
    (:meth:`mexp.kernels.base.Kernel.reference_signal`, e.g. the unattenuated
    magnetisation sum |a| for a decay kernel) and sigma_1 is the per-pixel
    standard deviation of the real part of the noise in the *fully sampled,
    single-coil, R = 1* reconstruction of the same k-space noise.  Defining
    SNR at the k-space source means acceleration and coil-combination
    penalties are *measured* by the pipeline, not assumed (charter §3.6, §4).
    """
    REFERENCE_OVER_UNACCELERATED_SIGMA = "reference_over_unaccelerated_sigma"
    FIRST_SAMPLE_OVER_SIGMA = "first_sample_over_sigma"   # MR convention, per sample
    ENERGY = "signal_norm_over_sigma"                     # ||s||_2 / sigma (used in SVD counts)


@dataclass(frozen=True)
class SNRSpec:
    value: float
    definition: SNRDefinition = SNRDefinition.REFERENCE_OVER_UNACCELERATED_SIGMA

    def __post_init__(self):
        if not (self.value > 0):
            raise ValueError("SNR must be positive")


@dataclass(frozen=True)
class Cell:
    """One point of the §6.1 product grid. A benchmark score is always
    attached to a Cell; a blank cell is a G5 violation, not a default."""
    method: MethodFamily
    kernel: str                       # registered kernel plugin name, e.g. "t2_cpmg"
    representation: Representation
    pipeline: ReconPipeline
    access: AccessLevel
    noise_knowledge: NoiseKnowledge
    noise_character: NoiseCharacter
    grid: SamplingGrid
    budget: SampleBudget
    truth: GroundTruthKind
    snr: SNRSpec
    pipeline_params: Mapping[str, float] = field(default_factory=dict)  # R, reg weight ...
    method_variant: str = ""          # e.g. "varpro", "matrix_pencil_hankel_completed"

    def is_physically_meaningful(self) -> tuple[bool, str]:
        """Charter §6.1: 'the full product *where physically meaningful*'.
        Returns (ok, reason). These are the only admissible blanks; every
        other blank needs a G5 score or a logged impossibility argument."""
        if self.representation is not Representation.MAGNITUDE and self.access.value >= 4:
            return False, "complex / phase-corrected data unavailable at L4-L6 (magnitude only)"
        if self.pipeline is ReconPipeline.RAW_KSPACE and self.access.value >= 2:
            return False, "k-space arm requires L0/L1 access"
        if self.noise_knowledge is NoiseKnowledge.SIGMA_PRESCAN and self.access is not AccessLevel.L0:
            return False, "prescan sigma requires L0"
        if self.noise_character is NoiseCharacter.G_FACTOR_MODULATED and self.pipeline not in (
            ReconPipeline.SENSE, ReconPipeline.GRAPPA
        ):
            return False, "g-factor modulation only arises under parallel-imaging pipelines"
        return True, ""


def enumerate_cells(**levels: Iterable) -> Iterator[Cell]:
    """Cartesian product over the given axis levels; other axes must be given
    as single-element iterables. Yields only physically meaningful cells."""
    names = [f.name for f in fields(Cell) if f.name not in ("pipeline_params", "method_variant")]
    missing = [n for n in names if n not in levels]
    if missing:
        raise TypeError(f"enumerate_cells needs every axis; missing {missing}")
    extra = {k: v for k, v in levels.items() if k in ("pipeline_params", "method_variant")}
    for combo in product(*(list(levels[n]) for n in names)):
        cell = Cell(**dict(zip(names, combo)), **{k: list(v)[0] for k, v in extra.items()})
        ok, _ = cell.is_physically_meaningful()
        if ok:
            yield cell
