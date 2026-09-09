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

Lanczos's own treatment (PRIMARY — read from the 1956 text, ch. IV §23
"Separation of exponentials", pp. 272-279, via page images supplied by
E. Diaz on 2026-09-07; Dover reprint ISBN 0-486-65656-X has the same pages):

  p. 276  "The following set of 24 decay observations were obtained in time
          intervals of 3 minutes, i.e., 0.05 hour ... hence dx = 0.05, starting
          with the time moment x = 0"  -> the grid IS the NIST grid.
          Table y_k to two decimals: 2.51 2.04 1.67 1.37 1.12 0.93 0.77 0.64 0.53
          0.45 0.38 0.32 0.27 0.23 0.20 0.17 0.15 0.13 0.11 0.10 0.09 0.08 0.07 0.06
          "The observations are considered as accurate to 1/2 unit of the second decimal."
          A three-exponential Prony separation is attempted first (groups of 4);
          the resulting equations are "redundant within the errors of our
          observations", so only TWO exponentials are determinable.
  p. 277  Two-exponential Prony on groups of 6 (sums 964, 309, 115, 51):
          xi^2 - 0.8839 xi + 0.1640 = 0, roots 0.619 and 0.265, h = 0.3,
          lambda_1 = 4.45, lambda_2 = 1.58.
  p. 278  Amplitudes by isolating each exponential and averaging: A_1 = 2.202,
          A_2 = 0.305.  Eq. (4-23.16):  f(x) = 2.202 e^{-4.45x} + 0.305 e^{-1.58x}.
          His hand-computed table of this fit to three decimals is LANCZOS_FIT_TABLE below.
  p. 279  "the deviation is never larger than 0.005, except in the single instance
          of k = 5, where the error reaches the magnitude 0.006 ... 'average
          deviation' ... 0.0026, which is well within the error limits of our data."
          Then the reveal, eq. (4-23.17): the data were constructed from
          f(x) = 0.0951 e^{-x} + 0.8607 e^{-3x} + 1.5576 e^{-5x};  "the exponent 3
          [reduced] to 1.58 and the exponent 5 to 4.45 ... the approximate ratio 1:2
          of the amplitudes was distorted to 1:7 ... our solution is 'numerically
          equivalent' to the true solution".

Harness cross-checks (tests/test_lanczos_degeneracy.py): the two-decimal
rounding of the NIST function equals his table at all 24 points; his grouped
sums reproduce; his fitted table agrees with exact evaluation of (4-23.16) to
0.002 (hand arithmetic); his 0.006-at-k=5 and 0.0026 RMS claims reproduce from
his table; exact evaluation gives a maximum deviation of 0.0066 at k = 5.

The *best* two-exponential approximant in least squares on the same grid,
computed once offline (scripts/provenance/lanczos_two_exp_approximant.py)
and frozen here as a constant so that the harness carries no estimator:

    f(x) ~ 2.06878068 e^{-4.63964313 x} + 0.44401299 e^{-1.87246563 x}
    max |f3 - f2| = 8.8e-4,  RMS = 4.2e-4   (relative to f(0) = 2.5134: 3.5e-4 and 1.7e-4)

So the honest statement of the degeneracy is: a two-exponential sum
reproduces this three-exponential function to about three decimal places
(8.8e-4 max) over 24 samples; Lanczos's own two-term fit reproduces his
two-decimal table to within its stated accuracy (0.006 max, 0.0026 RMS).
||f3 - f2_best||_2 = 2.07e-3, so an oracle detector that knows both candidate
models needs peak-to-sigma SNR above ~3.6e3 for d' = 3, and for every
sigma >= 8.8e-4 the expected excess chi-square of the wrong model (<= 5.5)
stays below the chi-square(2) 95 % critical value 5.99 (criterion (b)).

Secondary restatements, checked against the PDFs on 2026-09-09:
  Istratov & Vyvenko 1999 (Rev. Sci. Instrum. 70:1233), Fig. 2 caption: 24 points,
          f2 = 2.202 exp(-4.45 t) + 0.305 exp(-1.58 t), f3 = 0.0951 e^{-t} + 0.8607 e^{-3t}
          + 1.5576 e^{-5t}, "units of time are hours" -> quotes Lanczos's coefficients
          exactly (their text says "two ... reproduced by three", the reverse direction
          of Lanczos's narrative; same content).  Their Fig. 5 extends the two functions
          to 6 h, where they separate visibly but by < 0.001 of the amplitude.
  Varah 1985 (SIAM J. Sci. Stat. Comput. 6:30), §2: generator (2.4) = f3, "dt = .05,
          24 points, truncating the values to two decimal places"; his Table 1 equals
          LANCZOS_DATA_TABLE at all 24 points.  He does NOT quote Lanczos's two-term
          coefficients (nor does his 1982 tech report); his Table 2 gives his own
          best two-term least-squares fit to the two-decimal data:
          a = (0.40, 2.11), b = (-1.81, -4.57), I = 1.0e-4 -> VARAH_TWO_EXP_LS below.
          His Table 3: with data error 0.001 the uncertainty region for (b1, b2)
          contains (-1.6, -4.4) and (-2.1, -4.7).
          The harness's own least squares on LANCZOS_DATA_TABLE gives
          (0.403, 2.105; 1.809, 4.572), SS = 1.14e-4 (tests/test_lanczos_degeneracy.py).

Status (charter §7 provenance discipline): everything in this module is
LOCKED against a primary source as of 2026-09-07 — the three-exponential
constants and grid against NIST StRD and against Lanczos p. 276/279, the
two-exponential coefficients, table precision and Lanczos's stated
agreement against pp. 276-279; the two secondaries above were read on
2026-09-09 and agree with the primary where they quote it.
"""
from __future__ import annotations

import numpy as np

X = 0.05 * np.arange(24)

# (amplitude, rate) pairs; T = 1 / rate
THREE_EXP = np.array([[0.0951, 1.0], [0.8607, 3.0], [1.5576, 5.0]])
LANCZOS_TWO_EXP = np.array([[2.202, 4.45], [0.305, 1.58]])              # Lanczos 1956 eq. (4-23.16), p. 278 (PRIMARY)
BEST_TWO_EXP_LS = np.array([[2.06878068, 4.63964313], [0.44401299, 1.87246563]])  # frozen offline
VARAH_TWO_EXP_LS = np.array([[2.11, 4.57], [0.40, 1.81]])   # Varah 1985 Table 2: his LS fit to the two-decimal data (PRIMARY)
VARAH_TWO_EXP_LS_SS = 1.0e-4                                  # Varah 1985 Table 2, I (sum of squares), one significant figure

# Lanczos 1956, p. 276: the 24 "decay observations", two decimals, dx = 0.05 h from x = 0
LANCZOS_DATA_TABLE = np.array([2.51, 2.04, 1.67, 1.37, 1.12, 0.93, 0.77, 0.64, 0.53, 0.45, 0.38, 0.32,
                               0.27, 0.23, 0.20, 0.17, 0.15, 0.13, 0.11, 0.10, 0.09, 0.08, 0.07, 0.06])
# Lanczos 1956, p. 278: his hand-computed values of 2.202 e^{-4.45x} + 0.305 e^{-1.58x} at the 24 points
LANCZOS_FIT_TABLE = np.array([2.507, 2.044, 1.672, 1.370, 1.126, 0.929, 0.769, 0.639, 0.533, 0.447, 0.376, 0.318,
                              0.270, 0.230, 0.197, 0.173, 0.148, 0.130, 0.114, 0.100, 0.088, 0.079, 0.070, 0.063])
# Lanczos 1956, p. 279: his stated agreement between fit and data
LANCZOS_STATED_MAX_DEVIATION = 0.006      # "in the single instance of k = 5"
LANCZOS_STATED_RMS_DEVIATION = 0.0026     # "square root of ... sum of squares ... divided by 24"
LANCZOS_STATED_ACCURACY = 0.005           # "accurate to 1/2 unit of the second decimal"

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
