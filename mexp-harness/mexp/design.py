"""
Sampling designs (charter §2.3, §6.1 'Sampling grid' x 'Sample budget').

A :class:`Design` is a set of *encoding points*.  Each point is a vector of
named coordinates, so one class covers echo times (T2, T2*), inversion times
(T1), spin-lock time x spin-lock amplitude (T1rho dispersion), and b-value or
full b-tensor plus direction and diffusion time (diffusion).  Sampling grid
type is carried as an axis tag and the exact sample count is the budget.

Factories below build one-dimensional designs; multi-dimensional designs are
built with :func:`product_design`.  Integer-lattice designs (uniform,
subset-of-grid, sparse-ruler, co-prime, nested) record their lattice so that
difference-domain / Hankel-completion methods can recover the virtual grid.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from itertools import combinations
from typing import Iterable, Mapping, Sequence

import numpy as np

from .axes import SampleBudget, SamplingGrid


@dataclass(frozen=True)
class Design:
    points: np.ndarray                  # (N, d) float
    coords: tuple[str, ...]             # names of the d coordinates
    grid: SamplingGrid
    meta: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self):
        pts = np.asarray(self.points, dtype=float)
        if pts.ndim == 1:
            pts = pts[:, None]
        if pts.ndim != 2 or pts.shape[1] != len(self.coords):
            raise ValueError(f"points must be (N, {len(self.coords)}); got {pts.shape}")
        object.__setattr__(self, "points", pts)
        object.__setattr__(self, "coords", tuple(self.coords))

    @property
    def N(self) -> int:
        return int(self.points.shape[0])

    @property
    def budget(self) -> SampleBudget:
        return SampleBudget.of(self.N)

    def coord(self, name: str) -> np.ndarray:
        try:
            j = self.coords.index(name)
        except ValueError as e:
            raise KeyError(f"design has coords {self.coords}, not {name!r}") from e
        return self.points[:, j]

    def lattice_indices(self) -> np.ndarray | None:
        """Integer lattice positions if this design lives on one (uniform,
        subset, ruler, co-array designs), else None."""
        idx = self.meta.get("lattice_indices")
        return None if idx is None else np.asarray(idx, dtype=int)

    def with_coords(self, coords: Sequence[str]) -> "Design":
        return Design(self.points, tuple(coords), self.grid, self.meta)


# --------------------------------------------------------------------------
# 1-D factories. `coord` names the encoding variable ("TE", "TI", "TSL", "b").
# --------------------------------------------------------------------------

def uniform(n: int, spacing: float, start: float | None = None, coord: str = "TE") -> Design:
    """n points start, start+spacing, ...  Default start = spacing (CPMG: TE_1 = ESP)."""
    if start is None:
        start = spacing
    idx = np.arange(n)
    pts = start + spacing * idx
    return Design(pts, (coord,), SamplingGrid.UNIFORM,
                  {"lattice_spacing": spacing, "lattice_origin": start, "lattice_indices": idx})


def subset_of_grid(base: Design, keep: Iterable[int]) -> Design:
    """Keep a subset of a lattice design's points; retains the virtual full grid."""
    base_idx = base.lattice_indices()
    if base_idx is None:
        raise ValueError("subset_of_grid needs a lattice design")
    keep = np.asarray(sorted(set(int(k) for k in keep)))
    meta = dict(base.meta)
    meta.update({"lattice_indices": base_idx[keep], "virtual_grid_size": base.N})
    return Design(base.points[keep], base.coords, SamplingGrid.SUBSET_OF_GRID, meta)


def log_spaced(n: int, lo: float, hi: float, coord: str = "TE") -> Design:
    return Design(np.geomspace(lo, hi, n), (coord,), SamplingGrid.LOG_SPACED, {"lo": lo, "hi": hi})


def scattered(points: Sequence[float], coord: str = "TE") -> Design:
    """Genuinely non-lattice points (classic IR TIs, clinical b-value sets)."""
    pts = np.sort(np.asarray(points, dtype=float))
    return Design(pts, (coord,), SamplingGrid.SCATTERED)


def crlb_optimal(*args, **kwargs) -> Design:
    """Placeholder for the CRLB-/Bayesian-optimal design (charter Phase 1
    cross-cutting 'experimental design'). Requires the Phase 0 CRLB module,
    which is the next Phase 0 deliverable after conditioning; not built here."""
    raise NotImplementedError("crlb_optimal design requires the Phase 0 CRLB module (not yet built)")


# --------------------------------------------------------------------------
# Difference-set (co-array) designs, charter §2.3 / gaps A1.
# Positions are integers on a unit lattice; `from_lattice` maps to time.
# --------------------------------------------------------------------------

def difference_coarray(positions: Sequence[int]) -> tuple[np.ndarray, int]:
    """Return (sorted non-negative differences, largest L such that every lag
    0..L is present). L is the aperture of the virtual uniform grid that
    difference-domain methods see."""
    p = np.asarray(sorted(set(int(x) for x in positions)))
    diffs = np.unique(np.abs(p[:, None] - p[None, :]).ravel())
    L = 0
    while L + 1 in set(diffs.tolist()):
        L += 1
    return diffs, L


def is_complete_ruler(positions: Sequence[int]) -> bool:
    p = sorted(set(int(x) for x in positions))
    _, L = difference_coarray(p)
    return L == p[-1] - p[0]


# Longest complete (sparse) rulers with n marks. Lengths are OEIS A004137
# (1, 3, 6, 9, 13, 17, 23, 29, 36 for n = 2..10). Every entry is checked for
# completeness in tests/test_design_and_axes.py; maximality is re-derived by
# exhaustive search there for n <= 7, and the n = 8, 9, 10 entries were found
# by `search_sparse_ruler` started at the A004137 length (0.2 s, 1.3 s, 32 s).
_SPARSE_RULERS: dict[int, tuple[int, ...]] = {
    2: (0, 1),
    3: (0, 1, 3),
    4: (0, 1, 4, 6),
    5: (0, 1, 2, 6, 9),
    6: (0, 1, 2, 6, 10, 13),
    7: (0, 1, 2, 3, 8, 13, 17),
    8: (0, 1, 2, 11, 15, 18, 21, 23),
    9: (0, 1, 2, 14, 18, 21, 24, 27, 29),
    10: (0, 1, 3, 6, 13, 20, 27, 31, 35, 36),
}


def search_sparse_ruler(n_marks: int, max_length: int | None = None) -> tuple[int, ...]:
    """Exhaustive search for the longest complete ruler with n_marks marks.
    Feasible for n_marks <= 9 in seconds; use the table for the usual budgets."""
    if n_marks < 2:
        raise ValueError("need at least two marks")
    upper = max_length if max_length is not None else n_marks * (n_marks - 1) // 2
    for L in range(upper, n_marks - 2, -1):
        for interior in combinations(range(1, L), n_marks - 2):
            marks = (0, *interior, L)
            if is_complete_ruler(marks):
                return marks
    raise RuntimeError("no complete ruler found (should not happen)")


def sparse_ruler(n_marks: int, spacing: float, start: float = 0.0, coord: str = "TE") -> Design:
    """Longest complete ruler with n_marks samples: the difference set covers
    every lag 0..L on the unit lattice, so a Hankel/difference-domain method
    sees a virtual uniform grid of L+1 points from n_marks acquisitions."""
    marks = _SPARSE_RULERS.get(n_marks) or search_sparse_ruler(n_marks)
    idx = np.asarray(marks)
    return Design(start + spacing * idx, (coord,), SamplingGrid.SPARSE_RULER,
                  {"lattice_spacing": spacing, "lattice_origin": start,
                   "lattice_indices": idx, "virtual_grid_size": int(idx[-1]) + 1,
                   "construction": "sparse_ruler"})


def coprime_array(m: int, n: int, spacing: float, start: float = 0.0, coord: str = "TE") -> Design:
    """Co-prime design (Pal & Vaidyanathan): {0, m, ..., (n-1) m} U {0, n, ..., (2m-1) n},
    m < n co-prime. 2m + n - 1 samples; contiguous co-array lags 0..(m n + m - 1)."""
    if np.gcd(m, n) != 1 or not (m < n):
        raise ValueError("need co-prime m < n")
    idx = np.unique(np.concatenate([m * np.arange(n), n * np.arange(2 * m)]))
    _, L = difference_coarray(idx)
    return Design(start + spacing * idx, (coord,), SamplingGrid.SPARSE_RULER,
                  {"lattice_spacing": spacing, "lattice_origin": start, "lattice_indices": idx,
                   "virtual_grid_size": L + 1, "construction": f"coprime({m},{n})"})


def nested_array(n1: int, n2: int, spacing: float, start: float = 0.0, coord: str = "TE") -> Design:
    """Two-level nested design (Pal & Vaidyanathan): {1..n1} U {(n1+1) k, k=1..n2}
    (shifted to start at 0). n1 + n2 samples; contiguous lags 0..(n2 (n1+1) - 1)."""
    idx = np.unique(np.concatenate([np.arange(1, n1 + 1), (n1 + 1) * np.arange(1, n2 + 1)])) - 1
    _, L = difference_coarray(idx)
    return Design(start + spacing * idx, (coord,), SamplingGrid.SPARSE_RULER,
                  {"lattice_spacing": spacing, "lattice_origin": start, "lattice_indices": idx,
                   "virtual_grid_size": L + 1, "construction": f"nested({n1},{n2})"})


# --------------------------------------------------------------------------
# Multi-dimensional designs (T1rho dispersion, diffusion b-tensor/direction,
# T2* with retained frequency axis handled in the kernel, not here).
# --------------------------------------------------------------------------

def product_design(*designs: Design, grid: SamplingGrid | None = None) -> Design:
    """Cartesian product of 1-D designs -> (prod N_i, sum d_i) design."""
    mesh = np.meshgrid(*[d.points[:, 0] for d in designs], indexing="ij")
    pts = np.stack([m.ravel() for m in mesh], axis=1)
    coords = tuple(c for d in designs for c in d.coords)
    g = grid or (designs[0].grid if len({d.grid for d in designs}) == 1 else SamplingGrid.SCATTERED)
    return Design(pts, coords, g, {"factors": [dict(d.meta) for d in designs]})


def stacked_design(points: np.ndarray, coords: Sequence[str], grid: SamplingGrid = SamplingGrid.SCATTERED,
                   meta: Mapping[str, object] | None = None) -> Design:
    """Arbitrary (N, d) encoding table, e.g. a diffusion scheme of b-tensors."""
    return Design(np.asarray(points, dtype=float), tuple(coords), grid, dict(meta or {}))
