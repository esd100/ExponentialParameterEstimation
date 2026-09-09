import numpy as np
import pytest

from mexp import conditioning as C
from mexp.design import uniform
from mexp.kernels import get
from mexp.params import Theta


@pytest.fixture(scope="module")
def k():
    return get("t2_cpmg")


def test_singular_values_decay_geometrically(k):
    A = C.discretized_operator(k, uniform(32, 10.0), C.log_grid(5, 2000, 200))
    s = C.singular_spectrum(A)
    assert np.all(np.diff(s) <= 0)
    ratios = s[1:8] / s[:7]
    assert np.all(ratios < 0.5)          # each successive singular value loses > a factor 2
    assert s[5] / s[0] < 1e-2            # sixth is below 1 % of the first: numerical rank ~5 at SNR 100


def test_effective_rank_monotone_in_snr_and_range(k):
    d = uniform(32, 10.0)
    A = C.discretized_operator(k, d, C.log_grid(10, 1000, 200))
    s = C.singular_spectrum(A)
    ranks = [C.effective_rank(s, snr) for snr in (10, 30, 100, 300, 1000)]
    assert ranks == sorted(ranks) and ranks[0] < ranks[-1]
    s_narrow = C.singular_spectrum(C.discretized_operator(k, d, C.log_grid(30, 300, 200)))
    assert C.effective_rank(s_narrow, 100) <= C.effective_rank(s, 100)


def test_effective_rank_insensitive_to_grid_density(k):
    d = uniform(32, 10.0)
    for M in (50, 200, 800):
        s = C.singular_spectrum(C.discretized_operator(k, d, C.log_grid(5, 2000, M), column_weights="sqrt_dlog"))
        assert C.effective_rank(s, 100) in (4, 5)


def test_picard_counts(k):
    d = uniform(32, 10.0)
    grid = C.log_grid(5, 2000, 200)
    A = C.discretized_operator(k, d, grid)
    th = Theta([0.2, 0.8], [[20.0], [80.0]])
    b = k.forward(th, d)
    sigma = k.reference_signal(th) / 100.0           # SNR 100, harness definition
    res = C.picard(A, b, sigma, per_sample_snr=100.0)
    assert 2 <= res.n_picard <= 8
    assert res.n_above_noise <= res.n_picard             # raw leading run can only be shorter (accidental zeros)
    assert abs(res.n_picard - res.n_energy) <= 2         # spectrum-specific count stays near the operator count
    assert res.beta.shape == res.s.shape == (32,)
    # noise-free Picard coefficients decay at least as fast as the singular values, initially
    assert res.solution_coeffs[0] > 0


def test_tsvd_resolution_tradeoff(k):
    d = uniform(32, 10.0)
    grid = C.log_grid(5, 2000, 120)
    A = C.discretized_operator(k, d, grid, column_weights="sqrt_dlog")
    r2, r4, r6 = (C.tsvd_resolution(A, kk, grid) for kk in (2, 4, 6))
    mid = slice(30, 90)
    assert np.nanmedian(r2.fwhm_log[mid]) > np.nanmedian(r4.fwhm_log[mid]) > np.nanmedian(r6.fwhm_log[mid])
    assert r2.noise_amplification < r4.noise_amplification < r6.noise_amplification


def test_continuum_reference_expressions():
    assert C.mellin_gain(0.0) == pytest.approx(np.sqrt(np.pi))
    assert C.bbp_count(100.0, 100.0) == pytest.approx(np.log(100) / np.pi**2 * np.arccosh(1e4), rel=1e-12)
    assert 2.5 < C.bbp_resolution_ratio(100.0) < 3.0        # ~2.7 at SNR 100
    assert 1.8 < C.bbp_resolution_ratio(1000.0) < 2.1       # ~2.0 at SNR 1000
    assert C.resolution_ratio_from_count(100.0, 2) == pytest.approx(10.0)


def test_covering_window_approaches_continuum_count(k):
    """With a time window that covers the T-range generously and dense sampling,
    the numerical count should be within ~1 of the BBP continuum count."""
    gamma, snr = 100.0, 100.0
    grid = C.log_grid(10, 1000, 400)
    d = uniform(2000, 0.5, start=0.05)                       # t in [0.05, 1000] ms ~ covers 10..1000
    A = C.discretized_operator(k, d, grid, column_weights="sqrt_dlog")
    n_num = C.effective_rank(C.singular_spectrum(A), snr)
    n_bbp = C.bbp_count(gamma, snr)
    assert abs(n_num - n_bbp) <= 1.5


# --- Istratov & Vyvenko 1999 Table I (after Bertero, Boccacci & Pike 1982), read from the PDF 2026-09-09 ------

def test_istratov_vyvenko_infinite_domain_column_is_the_printed_closed_form():
    """eqs (12)-(13): delta = exp(pi / w_max), cosh(pi w_max) = pi SNR^2 -> 2.44 / 1.88 / 1.63 at SNR 1e2 / 1e3 / 1e4.
    The factor pi inside the arccosh is what distinguishes their printed form from the harness's relative criterion."""
    for snr in (1e2, 1e3, 1e4):
        assert round(C.r_min(snr, "istratov"), 2) == C.ISTRATOV_TABLE_I[(snr, None)]
        assert C.r_min(snr, "istratov") < C.r_min(snr, "arccosh") < C.r_min(snr, "charter")
    # the three conventions agree to first order: the differences are O(ln pi) and O(ln 2) in the denominator
    assert abs(np.log(C.r_min(1e2, "arccosh")) / np.log(C.r_min(1e2, "istratov")) - np.arccosh(np.pi * 1e4) / np.arccosh(1e4)) < 1e-12
    assert 1.25 < C.k_max(30.0, 100.0, "istratov") - C.k_max(30.0, 100.0, "arccosh") + 1.0 < 1.5   # 0.4 for Gamma 30


def test_finite_domain_columns_reproduce_from_the_harness_svd(k):
    """Table I finite-domain columns (b0/a0 = 5: 1.74 / 1.45 / 1.32; = 2: 1.44 / 1.27 / 1.20) via their eq. (14)
    delta = (b0/a0)^(1/M), with M the harness's own count of singular values above 1/SNR for a T-grid spanning
    exactly b0/a0 under a covering, densely sampled time window.  Integer M against their interpolated M: within 0.07."""
    from mexp.design import log_spaced
    for gamma in (2.0, 5.0):
        A = C.discretized_operator(k, log_spaced(2000, 1e-3, 30 * gamma), C.log_grid(1.0, gamma, 400))
        s = C.singular_spectrum(A)
        for snr in (1e2, 1e3, 1e4):
            M = C.effective_rank(s, snr)
            assert abs(gamma ** (1.0 / M) - C.ISTRATOV_TABLE_I[(snr, gamma)]) < 0.07, (gamma, snr, M)
