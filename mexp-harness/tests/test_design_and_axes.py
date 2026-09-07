import numpy as np
import pytest

from mexp import design as D
from mexp.axes import (AccessLevel, Cell, GroundTruthKind, MethodFamily, NoiseCharacter, NoiseKnowledge,
                       ReconPipeline, Representation, SampleBudget, SamplingGrid, SNRSpec, enumerate_cells)


# ---- sampling-grid factories -------------------------------------------------------

def test_uniform_and_subset_keep_lattice():
    u = D.uniform(32, 10.0)
    assert u.N == 32 and u.grid is SamplingGrid.UNIFORM and u.budget is SampleBudget.DENSE
    assert np.allclose(u.coord("TE")[:3], [10, 20, 30])
    s = D.subset_of_grid(u, [0, 1, 2, 5, 8, 13, 21])
    assert s.grid is SamplingGrid.SUBSET_OF_GRID and s.N == 7 and s.budget is SampleBudget.AUSTERE
    assert s.meta["virtual_grid_size"] == 32
    assert np.array_equal(s.lattice_indices(), [0, 1, 2, 5, 8, 13, 21])


@pytest.mark.parametrize("n", sorted(D._SPARSE_RULERS))
def test_sparse_ruler_table_is_complete(n):
    marks = D._SPARSE_RULERS[n]
    assert len(marks) == n and D.is_complete_ruler(marks)


@pytest.mark.parametrize("n,length", [(3, 3), (4, 6), (5, 9), (6, 13), (7, 17)])
def test_sparse_ruler_table_is_maximal_by_search(n, length):
    found = D.search_sparse_ruler(n)
    assert found[-1] == length == D._SPARSE_RULERS[n][-1]


def test_sparse_ruler_design_virtual_grid():
    d = D.sparse_ruler(8, spacing=10.0)
    assert d.N == 8 and d.meta["virtual_grid_size"] == 24 and d.grid is SamplingGrid.SPARSE_RULER
    _, L = D.difference_coarray(d.lattice_indices())
    assert L == 23


def test_coprime_and_nested_coarrays():
    c = D.coprime_array(2, 3, 10.0)        # {0,2,4} U {0,3,6,9}
    assert c.N == 2 * 2 + 3 - 1
    _, L = D.difference_coarray(c.lattice_indices())
    assert L >= 2 * 3 + 2 - 1
    n = D.nested_array(3, 3, 10.0)         # {1,2,3} U {4,8,12} -> lags 0..11
    _, L = D.difference_coarray(n.lattice_indices())
    assert L == 3 * (3 + 1) - 1


def test_log_spaced_scattered_product():
    g = D.log_spaced(8, 5.0, 320.0)
    assert g.grid is SamplingGrid.LOG_SPACED and np.isclose(g.points[-1, 0], 320.0)
    s = D.scattered([50, 100, 400, 1600], coord="TI")
    assert s.grid is SamplingGrid.SCATTERED and s.coords == ("TI",)
    p = D.product_design(D.uniform(4, 1.0, coord="TSL"), s.with_coords(("w1",)))
    assert p.N == 16 and p.coords == ("TSL", "w1")


def test_crlb_optimal_is_an_explicit_placeholder():
    with pytest.raises(NotImplementedError):
        D.crlb_optimal()


# ---- axes ----------------------------------------------------------------------------

def _cell(**over):
    base = dict(method=MethodFamily.NLS, kernel="t2_cpmg", representation=Representation.MAGNITUDE,
                pipeline=ReconPipeline.SINGLE_COIL, access=AccessLevel.L6, noise_knowledge=NoiseKnowledge.SIGMA_JOINT,
                noise_character=NoiseCharacter.STATIONARY, grid=SamplingGrid.UNIFORM, budget=SampleBudget.DENSE,
                truth=GroundTruthKind.DISCRETE, snr=SNRSpec(100.0))
    base.update(over)
    return Cell(**base)


def test_physically_meaningful_rules():
    assert _cell().is_physically_meaningful()[0]
    ok, why = _cell(representation=Representation.COMPLEX).is_physically_meaningful()
    assert not ok and "L4-L6" in why
    ok, _ = _cell(representation=Representation.COMPLEX, access=AccessLevel.L3).is_physically_meaningful()
    assert ok
    ok, _ = _cell(pipeline=ReconPipeline.RAW_KSPACE, access=AccessLevel.L1).is_physically_meaningful()
    assert ok
    ok, _ = _cell(noise_character=NoiseCharacter.G_FACTOR_MODULATED).is_physically_meaningful()
    assert not ok


def test_enumerate_cells_filters_and_counts():
    cells = list(enumerate_cells(
        method=[MethodFamily.NLS], kernel=["t2_cpmg"],
        representation=list(Representation), pipeline=[ReconPipeline.SINGLE_COIL],
        access=[AccessLevel.L3, AccessLevel.L6], noise_knowledge=[NoiseKnowledge.SIGMA_KNOWN],
        noise_character=[NoiseCharacter.STATIONARY], grid=[SamplingGrid.UNIFORM, SamplingGrid.SPARSE_RULER],
        budget=[SampleBudget.DENSE, SampleBudget.AUSTERE], truth=[GroundTruthKind.DISCRETE],
        snr=[SNRSpec(50.0), SNRSpec(200.0)],
    ))
    # 3 reps x 2 access x 2 grid x 2 budget x 2 snr = 48, minus complex/phase-corrected at L6 (2 x 8 = 16)
    assert len(cells) == 32


def test_snr_must_be_positive():
    with pytest.raises(ValueError):
        SNRSpec(0.0)
