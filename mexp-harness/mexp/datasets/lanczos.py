"""
Lanczos degeneracy example — reference data and provenance.

Primary: C. Lanczos, *Applied Analysis* (Prentice-Hall, 1956), ch. IV,
pp. 272-280 (Prony's method).  NIST StRD cites these pages for the
generating function below.

Generating function (NIST StRD, all three Lanczos datasets; certified for
Lanczos1 to ~1e-10):

    f(x) = 0.0951 e^{-x} + 0.8607 e^{-3x} + 1.5576 e^{-5x},   x = 0, 0.05, ..., 1.15 (24 points)

NIST StRD variants (https://www.itl.nist.gov/div898/strd/nls/nls_main.shtml):
    Lanczos1 : data generated to 14 digits  -> certified fit recovers the truth (b1 = 9.5100000027E-02 ...)
    Lanczos2 : data generated to  6 digits
    Lanczos3 : data generated to  5 digits  -> certified fit b1 = 0.0868 (truth 0.0951), b2 = 0.955 (truth 1)
               with certified SDs 0.017 and 0.097: 5 significant digits already lose the slow component.

Lanczos's own two-exponential representation of the *two-decimal* table
(as recalled from the 1956 text, p. 276; the page could not be reached
online during this session and this attribution must be checked against the
book before it is quoted):

    f(x) ~ 2.202 e^{-4.45 x} + 0.305 e^{-1.58 x}

Numerically (this module's tests): it agrees with the three-exponential
function to 0.0064 max-abs on the grid, i.e. within the two-decimal
tabulation, with a single rounding disagreement at x = 0.2 (1.12 vs 1.13).

The *best* two-exponential approximant in least squares on the same grid,
computed once offline (scripts/provenance/lanczos_two_exp_approximant.py)
and frozen here as a constant so that the harness carries no estimator:

    f(x) ~ 2.06878068 e^{-4.63964313 x} + 0.44401299 e^{-1.87246563 x}
    max |f3 - f2| = 8.8e-4,  RMS = 4.2e-4   (relative to f(0) = 2.5134: 3.5e-4 and 1.7e-4)

So the honest statement of the degeneracy is: a two-exponential sum
reproduces this three-exponential function to about three decimal places
(8.8e-4 max) over 24 samples; Lanczos's own two-term fit reproduces a
two-decimal table. ||f3 - f2_best||_2 = 2.07e-3, so an oracle detector that
knows both candidate models needs peak-to-sigma SNR above ~3.6e3 for d' = 3,
and for every sigma >= 8.8e-4 the expected excess chi-square of the wrong
model (<= 5.5) stays below the chi-square(2) 95 % critical value 5.99
(tests/test_lanczos_degeneracy.py, criterion (b)).

Status (charter v0.7 §7 provenance discipline): the three-exponential
constants and the NIST grid are LOCKED; the two-exponential coefficients,
Lanczos's own grid (dt = 0.05 on [0, 1.15] per NIST, or dt = 0.1 on a longer
window, which the quoted coefficients fit slightly better) and the
two-decimal statement are PROVISIONAL pending the book check. The test's
pass criteria do not depend on the provisional items.
"""
from __future__ import annotations

import numpy as np

X = 0.05 * np.arange(24)

# (amplitude, rate) pairs; T = 1 / rate
THREE_EXP = np.array([[0.0951, 1.0], [0.8607, 3.0], [1.5576, 5.0]])
LANCZOS_TWO_EXP = np.array([[2.202, 4.45], [0.305, 1.58]])              # recalled; see docstring
BEST_TWO_EXP_LS = np.array([[2.06878068, 4.63964313], [0.44401299, 1.87246563]])  # frozen offline

# NIST StRD Lanczos1: generated to 14 digits
NIST_LANCZOS1_Y = np.array([
    2.513400000000E+00, 2.044333373291E+00, 1.668404436564E+00, 1.366418021208E+00,
    1.123232487372E+00, 9.268897180037E-01, 7.679338563728E-01, 6.388775523106E-01,
    5.337835317402E-01, 4.479363617347E-01, 3.775847884350E-01, 3.197393199326E-01,
    2.720130773746E-01, 2.324965529032E-01, 1.996589546065E-01, 1.722704126914E-01,
    1.493405660168E-01, 1.300700206922E-01, 1.138119324644E-01, 1.000415587559E-01,
    8.833209084540E-02, 7.833544019350E-02, 6.976693743449E-02, 6.239312536719E-02,
])
NIST_LANCZOS1_CERTIFIED = np.array([9.5100000027E-02, 1.0000000001E+00, 8.6070000013E-01,
                                    3.0000000002E+00, 1.5575999998E+00, 5.0000000001E+00])

# NIST StRD Lanczos3: generated to 5 digits
NIST_LANCZOS3_Y = np.array([
    2.5134, 2.0443, 1.6684, 1.3664, 1.1232, 0.9269, 0.7679, 0.6389, 0.5338, 0.4479, 0.3776, 0.3197,
    0.2720, 0.2325, 0.1997, 0.1723, 0.1493, 0.1301, 0.1138, 0.1000, 0.0883, 0.0783, 0.0698, 0.0624,
])
NIST_LANCZOS3_CERTIFIED = np.array([8.6816414977E-02, 9.5498101505E-01, 8.4400777463E-01,
                                    2.9515951832E+00, 1.5825685901E+00, 4.9863565084E+00])
NIST_LANCZOS3_CERTIFIED_SD = np.array([1.7197908859E-02, 9.7041624475E-02, 4.1488663282E-02,
                                       1.0766312506E-01, 5.8371576281E-02, 3.4436403035E-02])
NIST_LANCZOS3_RSS = 1.6117193594E-08


def evaluate(pairs: np.ndarray, x: np.ndarray = X) -> np.ndarray:
    """Plain-numpy evaluation of sum a_k exp(-r_k x): the *independent* oracle
    the kernel forward model is tested against."""
    pairs = np.asarray(pairs, dtype=float)
    return (pairs[:, 0][None, :] * np.exp(-np.outer(x, pairs[:, 1]))).sum(axis=1)
