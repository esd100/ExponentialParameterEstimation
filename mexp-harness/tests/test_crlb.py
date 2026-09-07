"""
CRLB machinery tests, plus two of the charter v0.7 'foundational results the
harness must encode': the Rife–Boorstyn contrast (sinusoid frequency CRLB
improves as 1/N^3; the Laplace decay-constant CRLB does not) and the
sloppy-model FIM spectrum (Transtrum–Machta–Sethna).
"""
import numpy as np
import pytest

from mexp import crlb as CR
from mexp.axes import Modality
from mexp.design import uniform
from mexp.kernels import get
from mexp.kernels.base import Kernel
from mexp.params import AmplitudeField, ParamSpec, SignalField, Theta


def test_rician_blocks_have_gaussian_and_rayleigh_limits():
    g, c, h = CR.rician_fisher_blocks(np.array([0.0, 200.0]))
    assert abs(h[0] - 4.0) < 1e-3 and abs(g[0]) < 1e-6          # Rayleigh: I_σσ = 4/σ², no amplitude information
    assert abs(g[1] - 1.0) < 1e-3 and abs(h[1] - 2.0) < 1e-3 and abs(c[1]) < 1e-2   # Gaussian limit


def test_single_exponential_amplitude_crlb_matches_closed_form():
    k = get("t2_cpmg")
    d = uniform(16, 10.0)
    th = Theta([1.0], [[50.0]])
    sigma = 0.01
    r = CR.crlb(k, th, d, sigma, "gaussian_real")
    # FIM = J^T J / σ² with J = [e, a t/T² e]; check the (a, a) element directly
    e = np.exp(-d.coord("TE") / 50.0)
    assert r.fim[0, 0] == pytest.approx(np.sum(e**2) / sigma**2)
    assert r.labels == ["a0", "T20"]


def test_rician_matches_gaussian_at_high_snr_and_departs_at_low():
    k = get("t2_cpmg")
    d = uniform(32, 10.0)
    th = Theta([0.5, 0.5], [[20.0], [80.0]])
    hi = CR.sigma_from_first_echo_snr(k, th, d, 1000.0)
    lo = CR.sigma_from_first_echo_snr(k, th, d, 5.0)
    g_hi, r_hi = CR.crlb(k, th, d, hi, "gaussian_real"), CR.crlb(k, th, d, hi, "rician")
    g_lo, r_lo = CR.crlb(k, th, d, lo, "gaussian_real"), CR.crlb(k, th, d, lo, "rician")
    assert np.allclose(r_hi.relative_sd, g_hi.relative_sd, rtol=2e-2)
    assert np.all(r_lo.relative_sd > g_lo.relative_sd)            # magnitude data carries less information


def test_joint_sigma_block_is_psd_and_costs_little_at_snr_100():
    k = get("t2_cpmg")
    d = uniform(32, 10.0)
    th = Theta([0.2, 0.8], [[20.0], [80.0]])
    sigma = CR.sigma_from_first_echo_snr(k, th, d, 100.0)
    known = CR.crlb(k, th, d, sigma, "rician", joint_sigma=False)
    joint = CR.crlb(k, th, d, sigma, "rician", joint_sigma=True)
    assert np.all(np.linalg.eigvalsh(joint.fim) > 0)
    assert joint.labels[-1] == "sigma"
    # σ is pinned to ~1/sqrt(2N) = 12.5 % by 32 samples on its own
    assert 0.10 < joint.relative_sd[-1] < 0.15
    # and not knowing it costs < 2 % in decay-constant precision here (Phase 0 measurement)
    assert np.all(joint.relative_sd[:-1] <= known.relative_sd * 1.02 + 1e-12)


class _Tone(Kernel):
    """Single complex sinusoid — the Rife–Boorstyn case, as a throw-away kernel."""
    name = "_test_tone"
    modality = Modality.T2STAR
    coords = ("t",)
    component_params = (ParamSpec("f", "cycles/sample", "linear", -0.5, 0.5),)
    signal_field = SignalField.COMPLEX
    amplitude_field = AmplitudeField.COMPLEX

    def physical_range(self):
        return ((-0.5,), (0.5,))

    def atoms(self, xi, nu, design):
        t = design.coord("t")[:, None]
        f = np.asarray(xi).reshape(-1, 1)[:, 0][None, :]
        return np.exp(2j * np.pi * f * t)


def test_rife_boorstyn_contrast():
    """Sinusoid: var(f) ∝ 1/N³ at fixed SNR per sample (Rife & Boorstyn 1974).
    Laplace: var(T2) stops improving once the window exceeds a few T2."""
    tone = _Tone()
    v = []
    for N in (32, 64):
        d = uniform(N, 1.0, start=0.0, coord="t")
        th = Theta(np.array([1.0 + 0j]), [[0.1]])
        r = CR.crlb(tone, th, d, 0.1, "gaussian_complex")
        v.append(r.cov[r.labels.index("f0"), r.labels.index("f0")])
    ratio_tone = v[1] / v[0]
    assert abs(ratio_tone * 8 - 1) < 0.12                  # within ~12 % of 1/8 (finite-N corrections)

    k = get("t2_cpmg")
    w = []
    for N in (32, 64):
        d = uniform(N, 10.0)
        th = Theta([1.0], [[50.0]])
        r = CR.crlb(k, th, d, 0.01, "gaussian_real")
        w.append(r.cov[1, 1])
    ratio_decay = w[1] / w[0]
    assert ratio_decay > 0.9                                # the extra 32 echoes at t > 6.4 T2 buy almost nothing
    assert ratio_tone < 0.2 < ratio_decay


def test_sloppy_fim_spectrum_spans_decades():
    """Transtrum–Machta–Sethna: sum-of-exponentials FIM eigenvalues spread ~uniformly in log."""
    k = get("t2_cpmg")
    d = uniform(32, 10.0)
    th = Theta([1 / 3, 1 / 3, 1 / 3], [[20.0], [60.0], [180.0]])
    r = CR.crlb(k, th, d, CR.sigma_from_first_echo_snr(k, th, d, 100.0), "gaussian_real")
    ev = r.fim_eigenvalues
    decades = np.log10(ev[0] / ev[-1])
    assert decades > 6                                     # six parameters, > 6 decades of stiffness
    gaps = np.diff(np.log10(ev))
    assert np.std(gaps) < 1.5 * abs(np.mean(gaps))         # roughly even spacing in log (no single cliff)
