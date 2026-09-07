import numpy as np
import pytest

from mexp import crlb as CR, tissues as TS
from mexp.design import uniform
from mexp.kernels import get


def test_registry_entries_are_consistent():
    assert len(TS.keys()) >= 10
    for e in TS.entries():
        assert abs(sum(c.fraction for c in e.components) - 1) < 1e-9
        assert all(c.value > 0 for c in e.components)
        assert e.sources and e.functional
        assert e.status is TS.Provenance.RECALLED     # nothing verified yet: flip this test when entries are checked


def test_every_entry_is_flagged_unverified_in_docstring():
    assert "RECALLED" in TS.__doc__ and "2026-09-07 every entry is RECALLED" in TS.__doc__


def test_theta_drops_invisible_components_and_renormalises():
    e = TS.get("skeletal_muscle")
    th = e.theta(min_value=10.0)
    assert th.K == 2 and abs(th.amplitudes.sum() - 1) < 1e-12
    assert np.allclose(th.nonlinear[:, 0], [33.0, 130.0])


def test_t2_entries_run_through_the_crlb_and_functional():
    k = get("t2_cpmg")
    d = uniform(32, 10.0)
    for e in TS.entries(kernel="t2_cpmg"):
        th = e.theta(min_value=10.0)
        sigma = CR.sigma_from_first_echo_snr(k, th, d, 100.0)
        r = CR.crlb(k, th, d, sigma, "rician")
        assert np.all(np.isfinite(r.relative_sd))
        if e.functional_threshold is not None and th.K > 1:
            g = CR.mass_below_gradient(th, e.functional_threshold)
            sd = CR.functional_sd(r, g)
            assert 0 <= sd < 1


def test_functional_gradient_is_correct_by_finite_differences():
    e = TS.get("brain_wm")
    th = e.theta()
    tau = 40.0
    def mwf(flat):
        t2 = th.unpack(flat)
        a = np.abs(t2.amplitudes)
        return (a * (t2.nonlinear[:, 0] < tau)).sum() / a.sum()
    g = CR.mass_below_gradient(th, tau)
    flat = th.pack()
    num = np.zeros_like(flat)
    for i in range(flat.size):
        h = 1e-6
        fp, fm = flat.copy(), flat.copy(); fp[i] += h; fm[i] -= h
        num[i] = (mwf(fp) - mwf(fm)) / (2 * h)
    assert np.allclose(g, num, atol=1e-6)
