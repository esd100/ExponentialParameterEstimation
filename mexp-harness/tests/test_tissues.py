import json
import numpy as np
import pytest

from mexp import crlb as CR, tissues as TS
from mexp.design import uniform
from mexp.kernels import get


def test_registry_loads_and_is_consistent():
    assert len(TS.keys()) >= 24 and len(TS.normal_entries()) == 19 and len(TS.pathology_entries()) == 5
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


def test_fat_content_is_carried_as_two_distinct_quantities():
    """v2.1: chemical lipid by mass (Woodard & White) and MR PDFF are different numbers; both on every entry."""
    for e in TS.all_entries():
        lm, pdff = e.properties["lipid_mass_fraction"], e.properties["pdff"]
        assert 0 <= lm["value"] <= 1 and 0 <= pdff["value"] <= 1, e.key
    assert TS.get("brain_wm").properties["lipid_mass_fraction"]["value"] > 0.15   # membrane lipid ...
    assert TS.get("brain_wm").properties["pdff"]["value"] == 0.0                  # ... is MR-invisible
    assert TS.get("adipose_tissue").properties["pdff"]["value"] > 0.8
    assert TS.get("bone_marrow_vertebral").properties["pdff"]["status"] == "PRIMARY"   # Le Ster 2016 Table 1


def test_adipose_entry_is_the_misspecification_row():
    e = TS.get("adipose_tissue")
    assert e.T2.K == 2 and e.T2.components[-1].fraction > 0.8
    assert "J-coupling" in e.T2.note and e.theory["n_resolvable_clinical_T2"] == 1
    assert e.property("T2_ms", "3T")["range"][0] < 60 < e.property("T2_ms", "3T")["value"]   # sequence dependence recorded


def test_status_summary_matches_expected_shape():
    s = TS.status_summary()
    assert s["PRIMARY"] >= 30 and s["SECONDARY"] >= 10      # v2.2 moved 16 values to PRIMARY; v2.3's five pathology rows add nine
    assert s["THEORY"] >= 8            # the abdominal T2 splits are declared, not measured
    assert s["RECALLED"] <= 1          # v2.2: no RECALLED *component* set remains (kidney-medulla D* is the one value)


def test_no_recalled_component_set_remains():
    """v2.2 (charter §10 step 8a): prostate luminal water was the last RECALLED set; it now rests on Sabouri 2017."""
    for cs in TS.entries():
        assert cs.status != TS.Provenance.RECALLED, cs.tissue_key
    p = TS.get("prostate_pz").T2
    assert p.status == TS.Provenance.PRIMARY and abs(p.components[-1].fraction - 0.24) < 1e-9
    assert p.typical_acquisition["dTE_ms"] == 25.0 and p.typical_acquisition["n_echoes"] == 64    # Sabouri's 64 x 25 ms train


def test_theta_drops_invisible_components_and_renormalises():
    cs = TS.get("skeletal_muscle").T2
    th = cs.theta(min_value=10.0)
    assert cs.K == 4 and th.K == 3 and abs(th.amplitudes.sum() - 1) < 1e-12
    assert np.allclose(th.nonlinear[:, 0], [20.8, 38.9, 114.3])        # Saab 1999 Table 1, in vivo row


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
    assert back["schema_version"] == "2.3" and len(back["entries"]) == len(TS.keys())
    assert all("condition" in e and "clinical_delta" in e for e in back["entries"])


# ---- schema 2.3: the pathology axis (charter §10 step 8c/8e) ---------------------------------------------------

def test_every_entry_carries_condition_and_pathology_rows_name_a_base():
    for e in TS.all_entries():
        assert e.condition["kind"] in {"normal", "pathology", "physiological"}, e.key
        if e.is_pathology:
            base = TS.base_of(e.key)
            assert not base.is_pathology and base.organ == e.organ, e.key
            # bulk properties are inherited (deep copy) except explicit overrides: T1 at 3 T is never overridden here
            assert e.properties["T1_ms"]["3T"] == base.properties["T1_ms"]["3T"], e.key
        else:
            assert e.base_key is None
    assert {e.key for e in TS.pathology_entries()} == {"liver_steatosis_pdff10", "liver_steatosis_pdff25", "prostate_pz_cancer",
                                                       "skeletal_muscle_venous_filling", "brain_wm_ms_lesion"}


def test_clinical_delta_is_consistent_and_sourced():
    for e in TS.all_entries():
        cd = e.clinical_delta
        if cd is None:
            continue
        assert abs(cd["disease_value"] - cd["normal_value"] - cd["delta"]) < 1e-9, e.key
        assert cd["status"] in {p.value for p in TS.Provenance} and cd["source"], e.key
        assert cd["functional"] == e.T2.functional, e.key          # Δ is stated for the T2 set's own functional
    # the four measured changes the primaries give
    assert abs(TS.get("prostate_pz").delta() + 0.14) < 1e-9           # Sabouri 2017 Table 2: LWF 0.24 -> 0.10
    assert abs(TS.get("skeletal_muscle").delta() - 0.062) < 1e-9      # Araujo 2014 Table 1: 8.0 -> 14.2 %
    assert abs(TS.get("brain_wm").delta() + 0.0605) < 1e-9            # Whittall 0.113 -> MacKay lesions 0.0525
    assert TS.get("liver").delta() is None                            # the normal row's T2 functional is the THEORY vascular tail
    # the disease rows carry the same Δ as their base rows where both exist
    for e in TS.pathology_entries():
        b = TS.base_of(e.key)
        if b.delta() is not None and e.T2.functional == b.T2.functional:
            assert abs(e.delta() - b.delta()) < 1e-9, e.key


def test_steatotic_liver_rows_are_a_fraction_sweep_at_fixed_ratio():
    """charter §10 step 8e: PDFF 10 and 25 % with the water / fat T2 pair of Bydder 2008 Table II (1.5 T STEAM)."""
    r10, r25 = TS.get("liver_steatosis_pdff10").T2, TS.get("liver_steatosis_pdff25").T2
    for r, f in ((r10, 0.10), (r25, 0.25)):
        assert r.status == TS.Provenance.PRIMARY and r.K == 2
        assert abs(r.components[1].fraction - f) < 1e-9 and abs(r.components[0].fraction - (1 - f)) < 1e-9
        assert np.allclose([c.value for c in r.components], [36.2, 74.8])
    assert TS.get("liver_steatosis_pdff10").properties["pdff"]["value"] == 0.10
    assert TS.get("liver").properties["pdff"]["status"] == "PRIMARY"                  # Szczepaniak 2005 read
    assert TS.get("pancreas").properties["pdff"]["status"] == "PRIMARY"               # Kühn 2015 read
    assert TS.get("kidney_cortex").properties["pdff"]["status"] == "PRIMARY"          # Idilman 2015 read
    assert TS.get("skeletal_muscle").properties["pdff"]["status"] == "RECALLED"       # Hu 2011 carries no organ table


def test_disease_rows_change_the_amplitude_vector_not_the_ratio():
    """prostate cancer and venous-filled muscle are amplitude-vector changes at (nearly) fixed T2 ratio."""
    n, c = TS.get("prostate_pz").T2, TS.get("prostate_pz_cancer").T2
    assert abs(c.components[1].fraction - 0.10) < 1e-9 and np.allclose([x.value for x in c.components], [81.0, 548.0])
    assert 0.8 < (c.components[1].value / c.components[0].value) / (n.components[1].value / n.components[0].value) < 1.2
    v = TS.get("skeletal_muscle_venous_filling").T2
    assert v.K == 2 and abs(v.components[1].fraction - 0.142) < 1e-9 and v.components[1].value == 181.0
    ms = TS.get("brain_wm_ms_lesion").T2
    assert abs(ms.components[0].fraction - 0.0525) < 1e-9 and ms.components[0].status == TS.Provenance.PRIMARY
    assert ms.components[1].status == TS.Provenance.THEORY                             # lesion IE T2 not tabulated by MacKay 1994
