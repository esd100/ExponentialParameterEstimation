"""
Provenance for the constant BEST_TWO_EXP_LS in mexp/datasets/lanczos.py.

This script is NOT part of the harness and is not imported by it.  It uses
scipy's least_squares (an estimator, charter G2) once, offline, to find the
best two-exponential approximant to Lanczos's three-exponential function on
the 24-point grid, so that the harness test can carry the result as a frozen
constant and verify it with the kernel's Jacobian alone.

Run:  python scripts/provenance/lanczos_two_exp_approximant.py
"""
import numpy as np
from scipy.optimize import least_squares

x = 0.05 * np.arange(24)
f3 = 0.0951 * np.exp(-x) + 0.8607 * np.exp(-3 * x) + 1.5576 * np.exp(-5 * x)


def resid(p):
    return p[0] * np.exp(-p[1] * x) + p[2] * np.exp(-p[3] * x) - f3


best = None
for start in [(2.2, 4.45, 0.3, 1.58), (1.5, 5, 1, 2), (2, 4, 0.5, 1), (1, 3, 1, 1), (2.5, 6, 0.1, 0.5)]:
    sol = least_squares(resid, start, xtol=1e-15, ftol=1e-15, gtol=1e-15, max_nfev=50000)
    if best is None or sol.cost < best.cost:
        best = sol

a1, r1, a2, r2 = best.x
print(f"best 2-exp: {a1:.8f} e^(-{r1:.8f} x) + {a2:.8f} e^(-{r2:.8f} x)")
print(f"max |f3 - f2| = {np.max(np.abs(best.fun)):.3e}, rms = {np.sqrt(np.mean(best.fun**2)):.3e}")
print("frozen constant in mexp/datasets/lanczos.py: BEST_TWO_EXP_LS = [[2.06878068, 4.63964313], [0.44401299, 1.87246563]]")
