"""
Harness correctness test #1: the Lanczos degeneracy example.

Charter v0.7 §4 Phase 0 pass criteria:
  (a) the harness reproduces the two-exponential fit's agreement with the 24-point
      data at the 0.001 level — applied, per the provenance flag, to the harness's
      OWN best two-exponential fit on the grid, with the quoted coefficients
      (2.202 e^{-4.45t} + 0.305 e^{-1.58t}) checked separately;
  (b) the two- and three-component models are indistinguishable at any noise level
      above that residual.

Status: LOCKED (charter §7 provenance discipline), 2026-09-07. The
three-exponential constants and the grid are locked against NIST StRD Lanczos1
and against Lanczos (1956) pp. 276/279; the two-exponential coefficients, the
two-decimal precision and Lanczos's stated agreement are locked against
pp. 276-279 (page images read this session). See mexp/datasets/lanczos.py.

Estimator note (charter G2): the harness package contains no estimator. The
best two-exponential fit needed by criterion (a) is computed HERE, in the test,
with scipy.optimize.least_squares driven by the kernel's forward model and
analytic Jacobian, and is cross-checked against the frozen constant in
mexp/datasets/lanczos.py. Nothing in mexp/ imports an optimiser.
No noise is generated anywhere in this file.
"""
import numpy as np
import pytest
from scipy.optimize import least_squares
from scipy.stats import chi2

from mexp import crlb as CR
from mexp.datasets import lanczos as L
from mexp.design import scattered
from mexp.kernels import get
from mexp.params import Theta



def _theta(pairs):
    pairs = np.asarray(pairs, dtype=float)
    return Theta(amplitudes=pairs[:, 0], nonlinear=(1.0 / pairs[:, 1])[:, None])


@pytest.fixture(scope="module")
def kernel():
    return get("t2_cpmg")


@pytest.fixture(scope="module")
def design():
    # NIST grid used as echo times: t = 0, 0.05, ..., 1.15 (dimensionless; T = 1/rate)
    return scattered(L.X, coord="TE")


@pytest.fixture(scope="module")
def f3(kernel, design):
    return kernel.forward(_theta(L.THREE_EXP), design)


def _best_two_exp(kernel, design, target):
    """Least-squares best two-exponential approximant of `target` on `design`,
    multistart, through the kernel (amplitudes a, rates r = 1/T)."""
    def resid(p):
        th = Theta(p[[0, 2]], (1.0 / p[[1, 3]])[:, None])
        return kernel.forward(th, design) - target

    def jac(p):
        th = Theta(p[[0, 2]], (1.0 / p[[1, 3]])[:, None])
        J = kernel.jacobian(th, design)          # columns: a0 a1 T0 T1
        # chain rule dT/dr = -1/r²
        out = np.empty((design.N, 4))
        out[:, 0], out[:, 2] = J[:, 0], J[:, 1]
        out[:, 1] = J[:, 2] * (-1.0 / p[1] ** 2)
        out[:, 3] = J[:, 3] * (-1.0 / p[3] ** 2)
        return out

    best = None
    for start in [(2.2, 4.45, 0.3, 1.58), (1.5, 5.0, 1.0, 2.0), (2.0, 4.0, 0.5, 1.0), (2.5, 6.0, 0.1, 0.5)]:
        sol = least_squares(resid, start, jac=jac, bounds=(1e-9, np.inf),   # a > 0, r > 0 (kernel positivity)
                            xtol=1e-15, ftol=1e-15, gtol=1e-15, max_nfev=20000)
        if best is None or sol.cost < best.cost:
            best = sol
    return best.x, best.fun


# --- locked part: three-exponential constants and grid against NIST StRD ------------------

def test_forward_model_reproduces_nist_lanczos1(kernel, design, f3):
    assert np.max(np.abs(f3 - L.NIST_LANCZOS1_Y)) < 1e-12
    assert np.max(np.abs(f3 - L.evaluate(L.THREE_EXP))) < 1e-15


def test_nist_certified_values_are_the_generating_function():
    assert np.max(np.abs(L.NIST_LANCZOS1_CERTIFIED - L.THREE_EXP.ravel())) < 1e-9


# --- criterion (a): the harness's own best two-exponential fit ---------------------------------

def test_a_best_two_exp_agrees_to_better_than_0p001(kernel, design, f3):
    p, res = _best_two_exp(kernel, design, f3)
    assert np.max(np.abs(res)) < 1e-3, "criterion (a): better than 0.001 over the 24 points"
    assert np.max(np.abs(res)) == pytest.approx(8.8e-4, abs=0.1e-4)
    # agrees with the frozen offline constant (provenance script)
    frozen = L.BEST_TWO_EXP_LS.ravel()
    assert np.allclose(p, frozen, rtol=1e-5, atol=1e-7)


def test_a_frozen_constant_is_a_stationary_point(kernel, design, f3):
    """Estimator-free restatement of (a) for the harness proper: J^T r = 0 at the constant."""
    th2 = _theta(L.BEST_TWO_EXP_LS)
    r = kernel.forward(th2, design) - f3
    g = kernel.jacobian(th2, design).T @ r
    th_off = Theta(th2.amplitudes * 1.01, th2.nonlinear * 1.01)
    g_off = kernel.jacobian(th_off, design).T @ (kernel.forward(th_off, design) - f3)
    assert np.linalg.norm(g) < 1e-4 * np.linalg.norm(g_off)


# --- criterion (a), second half: Lanczos's OWN coefficients against his own text (PRIMARY) ------

def test_lanczos_data_table_is_the_nist_function_to_two_decimals():
    """p. 276: 24 observations, dx = 0.05 from x = 0, two decimals — the NIST grid."""
    assert np.array_equal(np.round(L.evaluate(L.THREE_EXP), 2), L.LANCZOS_DATA_TABLE)


def test_lanczos_prony_grouped_sums_reproduce():
    """pp. 276-277: sums over groups of 4 (759, 346, 168, 87, 49, 30) and of 6 (964, 309, 115, 51)."""
    y = L.LANCZOS_DATA_TABLE
    assert [int(round(100 * v)) for v in y.reshape(6, 4).sum(axis=1)] == [759, 346, 168, 87, 49, 30]
    assert [int(round(100 * v)) for v in y.reshape(4, 6).sum(axis=1)] == [964, 309, 115, 51]


def test_lanczos_fit_table_and_stated_agreement(kernel, design, f3):
    """p. 278 table of 2.202 e^{-4.45x} + 0.305 e^{-1.58x} (hand arithmetic, 3 decimals) and the
    p. 279 claims: max deviation 0.006 at k = 5, RMS 0.0026, data accurate to 1/2 unit."""
    f2q = kernel.forward(_theta(L.LANCZOS_TWO_EXP), design)
    assert np.max(np.abs(np.round(f2q, 3) - L.LANCZOS_FIT_TABLE)) < 0.0025     # slide-rule era arithmetic (8 of 24 differ by <= 0.002)
    dev = L.LANCZOS_FIT_TABLE - L.LANCZOS_DATA_TABLE
    assert np.argmax(np.abs(dev)) == 4 and abs(np.abs(dev).max() - L.LANCZOS_STATED_MAX_DEVIATION) < 5e-4
    assert abs(np.sqrt(np.mean(dev**2)) - L.LANCZOS_STATED_RMS_DEVIATION) < 1e-4
    assert np.sum(np.abs(dev) > L.LANCZOS_STATED_ACCURACY) == 1                   # "except in the single instance of k = 5"
    # exact evaluation of his coefficients against the exact function: 0.0064 at t = 0, within two decimals
    d = np.abs(f3 - f2q)
    assert d.max() == pytest.approx(0.0064, abs=2e-4) and d.max() > 1e-3


def test_varah_1985_table_2_reproduces(kernel, design):
    """Varah 1985 §2 (read 2026-09-09): his Table 1 is Lanczos's two-decimal table; his Table 2 gives the best
    two-term least-squares fit to it, a = (0.40, 2.11), b = (-1.81, -4.57), I = 1.0e-4.  He does not quote
    Lanczos's own coefficients — the v0.7 provenance note that attributed them to Varah is corrected here."""
    p, r = _best_two_exp(kernel, design, L.LANCZOS_DATA_TABLE)
    a = np.array([p[0], p[2]]); rate = np.array([p[1], p[3]])
    order = np.argsort(-rate)                                     # fast component first, as Varah's Table 2 lists a2, b2
    a_ref, r_ref = L.VARAH_TWO_EXP_LS[:, 0], L.VARAH_TWO_EXP_LS[:, 1]
    assert np.allclose(a[order], a_ref, atol=0.006) and np.allclose(rate[order], r_ref, atol=0.006)   # his 2-3 sig. figs
    assert (r**2).sum() == pytest.approx(L.VARAH_TWO_EXP_LS_SS, rel=0.2)                          # I = 1.0e-4 (1 sig. fig.)
    # Varah Table 3: (b1, b2) = (-1.6, -4.4) and (-2.1, -4.7) lie inside his data-error uncertainty region.  Checked in the
    # form the data support directly: with those rates fixed, the linear LS fit's RMS residual (0.0034, 0.0028) stays below
    # the table's stated accuracy of 0.005 — rate pairs 30 % apart fit the two-decimal data within its own precision.
    for b in [(1.6, 4.4), (2.1, 4.7)]:
        A = np.exp(-np.outer(L.X, b))
        coef, res, *_ = np.linalg.lstsq(A, L.LANCZOS_DATA_TABLE, rcond=None)
        assert np.all(coef > 0) and np.sqrt(float(res[0]) / 24) < L.LANCZOS_STATED_ACCURACY


def test_istratov_vyvenko_fig2_quotes_lanczos_exactly():
    """I&V 1999 Fig. 2 caption (read 2026-09-09): f2 = 2.202 exp(-4.45 t) + 0.305 exp(-1.58 t), 24 points, hours."""
    assert np.array_equal(L.LANCZOS_TWO_EXP, np.array([[2.202, 4.45], [0.305, 1.58]]))
    assert np.array_equal(L.THREE_EXP, np.array([[0.0951, 1.0], [0.8607, 3.0], [1.5576, 5.0]])) and L.X.size == 24


# --- criterion (b): indistinguishable at any noise level above the residual --------------------

def test_b_models_indistinguishable_above_residual_noise(kernel, design, f3):
    f2 = kernel.forward(_theta(L.BEST_TWO_EXP_LS), design)
    delta = f3 - f2
    resid = np.max(np.abs(delta))
    crit = chi2.ppf(0.95, df=2)                              # K=3 has two more parameters than K=2
    for sigma in (resid, 1e-3, 2e-3, 5e-3):
        # expected excess chi-square of the wrong (K=2) model = (d')² of the ideal detector
        assert CR.lrt_noncentrality(delta, sigma) < crit
        # and the K=3 decay constants are not estimable: CRLB relative SD > 100 % on two of them
        r3 = CR.crlb(kernel, _theta(L.THREE_EXP), design, sigma, "gaussian_real")
        rel = np.array(list(r3.relative_sd_of("T2").values()))
        assert np.sum(rel > 1.0) >= 2 and rel.min() > 0.2
    # whereas the two-exponential description is well determined at the residual level
    r2 = CR.crlb(kernel, _theta(L.BEST_TWO_EXP_LS), design, resid, "gaussian_real")
    assert max(r2.relative_sd_of("T2").values()) < 0.03


def test_snr_needed_to_separate_the_models(kernel, design, f3):
    """Record the operating point: d' = 3 needs SNR (peak / σ) ≈ 3.6e3 on this grid."""
    f2 = kernel.forward(_theta(L.BEST_TWO_EXP_LS), design)
    sep = np.linalg.norm(f3 - f2)
    snr_needed = f3[0] / (sep / 3.0)
    assert 3.3e3 < snr_needed < 4.0e3


# --- NIST Lanczos3: five significant digits already move the slow component ------------------

def test_five_digit_rounding_moves_the_certified_fit_off_the_truth(kernel, design, f3):
    truth, cert = L.THREE_EXP.ravel(), L.NIST_LANCZOS3_CERTIFIED
    assert abs(cert[0] - truth[0]) / truth[0] > 0.05
    assert abs(cert[1] - truth[1]) / truth[1] > 0.03
    rss_truth = np.sum((f3 - L.NIST_LANCZOS3_Y) ** 2)
    assert L.NIST_LANCZOS3_RSS < rss_truth                  # the wrong parameters fit the rounded data better
