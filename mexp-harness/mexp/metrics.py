"""
Evaluation metrics (charter §6.2) — names and signatures fixed in Phase 0,
applied unchanged thereafter.

Only the metric *vocabulary* and call signatures are fixed here.  The
functions that need an estimator's output (coverage, CRLB efficiency,
resampling stability) cannot be exercised until Phase 1 and are declared
with their contract; parameter RMSE and functional recovery are simple
enough to implement now and are used by nothing yet.
"""
from __future__ import annotations

from enum import Enum

import numpy as np


class Metric(Enum):
    PARAMETER_RMSE = "parameter_rmse"                     # per amplitude and decay constant, K known
    FUNCTIONAL_RECOVERY = "functional_recovery"           # e.g. mass below threshold
    UNCERTAINTY_CALIBRATION = "uncertainty_calibration"   # empirical coverage of nominal intervals
    RESAMPLING_STABILITY = "resampling_stability"         # variance across noise realisations / bootstrap
    CRLB_EFFICIENCY = "crlb_efficiency"                   # achieved var / CRLB (primary comparator)
    MISSPECIFICATION_ROBUSTNESS = "misspecification_robustness"   # exchange, stimulated echoes, non-exp
    NOISE_ESTIMATION_ACCURACY = "noise_estimation_accuracy"       # sigma, effective DOF vs truth
    JOINT_THETA_SIGMA_EFFICIENCY = "joint_theta_sigma_efficiency" # vs joint CRLB
    NOISE_MODEL_ROBUSTNESS = "noise_model_robustness"             # Rician fit on chi data, etc.


def parameter_rmse(theta_hat_flat: np.ndarray, theta_true_flat: np.ndarray) -> np.ndarray:
    """Per-parameter RMSE over the leading (replicate) axis. Components must
    already be matched (by sorting on the decay constant) by the caller."""
    err = np.asarray(theta_hat_flat) - np.asarray(theta_true_flat)
    return np.sqrt(np.mean(err**2, axis=0))


def functional_recovery(f_hat: np.ndarray, f_true: float) -> dict:
    f_hat = np.asarray(f_hat, dtype=float)
    return {"bias": float(np.mean(f_hat) - f_true), "rmse": float(np.sqrt(np.mean((f_hat - f_true) ** 2)))}


def coverage(intervals: np.ndarray, truth: np.ndarray) -> np.ndarray:
    """intervals: (replicates, n_params, 2); truth: (n_params,). Empirical coverage per parameter."""
    lo, hi = intervals[..., 0], intervals[..., 1]
    return np.mean((lo <= truth) & (truth <= hi), axis=0)


def crlb_efficiency(achieved_var: np.ndarray, crlb_var: np.ndarray) -> np.ndarray:
    """>= 1 for an unbiased estimator; < 1 flags bias or an over-informative prior (charter Phase 2)."""
    return np.asarray(achieved_var) / np.asarray(crlb_var)
