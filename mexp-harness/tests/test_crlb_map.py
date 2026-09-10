"""The CRLB map over the dictionary (scripts/phase0_crlb_map.py): the crossing machinery and a few locked numbers."""
import importlib.util
import pathlib

import numpy as np
import pytest

from mexp import crlb as CR, tissues as TS
from mexp.design import uniform
from mexp.kernels import get

SCRIPT = pathlib.Path(__file__).resolve().parents[1] / "scripts" / "phase0_crlb_map.py"


@pytest.fixture(scope="module")
def mapmod(tmp_path_factory):
    """Import the script's functions without running its sweep (the module body writes results/): exec the definitions only."""
    src = SCRIPT.read_text().split("rows = []")[0]
    ns = {"__name__": "crlb_map_defs", "__file__": str(SCRIPT)}
    exec(compile(src, str(SCRIPT), "exec"), ns)
    return ns


def test_crossing_snr_interpolates_a_one_over_snr_law(mapmod):
    snrs = np.array([20.0, 50.0, 100.0, 300.0, 1000.0])
    vals = 3.0 / snrs                                    # SD = 3 / SNR
    assert abs(mapmod["crossing_snr"](snrs, vals, 0.01) - 300.0) < 1e-9
    assert abs(mapmod["crossing_snr"](snrs, vals, 0.02) - 150.0) < 1e-6   # between grid points, exact on a power law
    assert mapmod["crossing_snr"](snrs, vals, 1e-4) == np.inf              # never reached
    assert abs(mapmod["crossing_snr"](snrs, vals, 1.0) - 20.0) < 1e-9      # already passing at the grid's first point


def test_constrained_bound_matches_the_threshold_table(mapmod):
    """results/threshold_tissues.md: WM MWF SD 0.038 with the long T2 fixed at SNR 100, 0.074 free."""
    th = TS.get("brain_wm").T2.theta(min_value=10.0)
    _, free, _ = mapmod["bounds"](th, 32, 10.0, 100.0, 40.0)
    _, fixed, _ = mapmod["bounds"](th, 32, 10.0, 100.0, 40.0, fix_long=True)
    assert abs(free - 0.0737) < 0.002 and abs(fixed - 0.038) < 0.002
    # fixing the 2000 ms component removes it from the free parameters and nothing else
    k = get("t2_cpmg"); d = uniform(32, 10.0)
    r = CR.crlb(k, th, d, CR.sigma_from_first_echo_snr(k, th, d, 100.0), "rician")
    assert r.labels == ["a0", "a1", "a2", "T20", "T21", "T22"] and th.nonlinear[2, 0] == 2000.0


def test_bounds_scale_as_one_over_snr_above_the_floor(mapmod):
    th = TS.get("prostate_pz").T2.theta(min_value=10.0)
    _, s100, _ = mapmod["bounds"](th, 32, 10.0, 100.0, 200.0)
    _, s1000, _ = mapmod["bounds"](th, 32, 10.0, 1000.0, 200.0)
    assert 9.5 < s100 / s1000 < 10.5


def test_singular_fim_reports_infinite_not_zero(mapmod):
    """K = 3 on 8 echoes: the CSF-like direction carries no information; the map must say ∞, never 0 (the v0.11 pseudo-inverse lesson)."""
    th = TS.get("brain_wm").T2.theta(min_value=10.0)
    relT, fsd, _ = mapmod["bounds"](th, 8, 10.0, 100.0, 40.0)
    assert not np.isfinite(relT) or relT > 10
    assert fsd == np.inf or fsd > 0.5


def test_rician_and_joint_sigma_cost_is_small_above_the_floor(mapmod):
    """§3.2 bound-level probe generalised: the magnitude and joint-σ costs are < 2 % wherever the signal stays above the floor
    (prostate: T2 ≥ 90 ms on a 320 ms window) and are largest for the steatotic rows (water T2 36 ms reaches the floor)."""
    th = TS.get("prostate_pz").T2.theta(min_value=10.0)
    _, g, _ = mapmod["bounds"](th, 32, 10.0, 100.0, 200.0, noise="gaussian_real")
    _, r, _ = mapmod["bounds"](th, 32, 10.0, 100.0, 200.0, noise="rician")
    _, j, _ = mapmod["bounds"](th, 32, 10.0, 100.0, 200.0, noise="rician", joint=True)
    assert r / g < 1.02 and j / r < 1.02
    th = TS.get("liver_steatosis_pdff10").T2.theta(min_value=10.0)
    _, g, _ = mapmod["bounds"](th, 32, 10.0, 100.0, 55.0, noise="gaussian_real")
    _, r, _ = mapmod["bounds"](th, 32, 10.0, 100.0, 55.0, noise="rician")
    _, j, _ = mapmod["bounds"](th, 32, 10.0, 100.0, 55.0, noise="rician", joint=True)
    assert r / g > 1.1 and j / r > 1.03
