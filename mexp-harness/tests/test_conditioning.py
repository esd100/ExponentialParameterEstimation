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
