import json
import numpy as np
import pytest

from mexp import crlb as CR, tissues as TS
from mexp.design import uniform
from mexp.kernels import get


def test_registry_loads_and_is_consistent():
    assert len(TS.keys()) >= 18
    for e in TS.all_entries():
        assert e.properties and e.theory["n_pools"] >= 1 and e.sources
        for m, cs in e.component_sets.items():
            assert abs(sum(c.fraction for c in cs.components) - 1) < 1e-9
            assert all(c.value > 0 for c in cs.components)
            assert cs.kernel in TS.MODALITY_OF_KERNEL and TS.MODALITY_OF_KERNEL[cs.kernel] == m


def test_every_value_carries_a_status_and_theory_counts_are_ordered():
    for e in TS.all_entries():
        for name, prop in e.properties.items():
            recs = prop.values() if "value" not in prop else [prop]
            for r in recs:
                assert r["status"] in {p.value for p in TS.Provenance}, (e.key, name)
        th = e.theory
        assert th["n_resolvable_clinical_T2"] <= th["n_apparent_T2"] <= th["n_pools"], e.key


def test_status_summary_matches_expected_shape():
    s = TS.status_summary()
    assert s["PRIMARY"] >= 5 and s["SECONDARY"] >= 20
    assert s["THEORY"] >= 8            # the abdominal T2 splits are declared, not measured


def test_theta_drops_invisible_components_and_renormalises():
    cs = TS.get("skeletal_muscle").T2
    th = cs.theta(min_value=10.0)
    assert cs.K == 4 and th.K == 3 and abs(th.amplitudes.sum() - 1) < 1e-12
    assert np.allclose(th.nonlinear[:, 0], [21.0, 39.0, 114.0])


def test_t2_sets_run_through_crlb_and_functional():
    k = get("t2_cpmg")
    d = uniform(32, 10.0)
    for cs in TS.entries(kernel="t2_cpmg"):
        th = cs.theta(min_value=10.0)
        sigma = CR.sigma_from_first_echo_snr(k, th, d, 100.0)
        r = CR.crlb(k, th, d, sigma, "rician")
        assert np.all(np.isfinite(r.relative_sd))
        if cs.functional_threshold is not None and th.K > 1:
            sd = CR.functional_sd(r, CR.mass_below_gradient(th, cs.functional_threshold))
            assert 0 <= sd < 2


def test_functional_gradient_by_finite_differences():
    th = TS.get("brain_wm").T2.theta()
    tau = 40.0
    def mwf(flat):
        t2 = th.unpack(flat); a = np.abs(t2.amplitudes)
        return (a * (t2.nonlinear[:, 0] < tau)).sum() / a.sum()
    g = CR.mass_below_gradient(th, tau)
    flat = th.pack(); num = np.zeros_like(flat)
    for i in range(flat.size):
        fp, fm = flat.copy(), flat.copy(); fp[i] += 1e-6; fm[i] -= 1e-6
        num[i] = (mwf(fp) - mwf(fm)) / 2e-6
    assert np.allclose(g, num, atol=1e-6)


def test_json_export_round_trips():
    d = TS.to_json_dict()
    s = json.dumps(d)
    back = json.loads(s)
    assert back["schema_version"] == "2.0" and len(back["entries"]) == len(TS.keys())
