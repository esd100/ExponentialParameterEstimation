"""
Tissue and organ dictionary — API over `mexp.tissue_data` (charter §1.2, §4, §6.1; v2.1).

Why this exists: the §1.2 falsifiable threshold depends on the amplitude vector
more than on anything else, and one myelin-like split is not the body.  The
dictionary carries, per tissue, the measured bulk MR properties (water content /
relative PD, T1 and T2 at 1.5 T and 3 T, ADC, lipid mass fraction and PDFF), the multi-component structure per
modality (T2 components for the CPMG kernel; T1 components; diffusion
compartments), the clinical functional of that structure, a typical
acquisition, and a *theory* block: the physical water pools a voxel of the
tissue contains, their exchange regime, and hence how many components are
apparent, documented and resolvable.  Every number has a provenance status
(see `mexp.tissue_data`).

Usage:
    from mexp import tissues as TS
    for view in TS.entries(kernel="t2_cpmg"):    # one view per (tissue, T2 component set)
        theta = view.theta(min_value=10.0)       # drop components below the first echo
    TS.get("liver").properties["T1_ms"]["3T"]    # bulk property records
    TS.get("liver").theory["n_pools"]

`scripts/export_tissue_dictionary.py` writes data/tissue_dictionary.json.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Mapping

import numpy as np

from . import tissue_data
from .params import Theta


class Provenance(Enum):
    PRIMARY = "PRIMARY"
    SECONDARY = "SECONDARY"
    TERTIARY = "TERTIARY"
    RECALLED = "RECALLED"
    THEORY = "THEORY"


MODALITY_OF_KERNEL = {
    "t2_cpmg": "T2", "t2star_ute": "T2", "t1_ir": "T1",
    "diffusion_ivim": "diffusion", "diffusion_tensor": "diffusion", "diffusion_standard_model": "diffusion",
}


@dataclass(frozen=True)
class Component:
    name: str
    fraction: float
    value: float
    status: Provenance
    source: str
    range: tuple[float, float] | None = None
    note: str = ""


@dataclass(frozen=True)
class ComponentSet:
    """One tissue's components for one modality/kernel."""
    tissue_key: str
    organ: str
    tissue: str
    modality: str                       # "T2" | "T1" | "diffusion"
    kernel: str
    field_T: float | None
    components: tuple[Component, ...]
    functional: str
    functional_threshold: float | None
    typical_acquisition: Mapping[str, Any]
    status: Provenance
    note: str = ""

    @property
    def K(self) -> int:
        return len(self.components)

    def visible_components(self, min_value: float | None = None) -> tuple[Component, ...]:
        if min_value is None:
            return self.components
        return tuple(c for c in self.components if c.value >= min_value)

    def theta(self, min_value: float | None = None) -> Theta:
        """Theta for the kernel: fractions as amplitudes (renormalised after dropping
        components below `min_value`, e.g. the first echo), values as the non-linear
        parameter (T2 / T1 / D). Zero-fraction tensor rows are dropped."""
        comps = [c for c in self.visible_components(min_value) if c.fraction > 0]
        if not comps:
            raise ValueError(f"{self.tissue_key}/{self.modality}: no component visible above {min_value}")
        a = np.array([c.fraction for c in comps], dtype=float)
        return Theta(a / a.sum(), np.array([[c.value] for c in comps], dtype=float))


@dataclass(frozen=True)
class TissueEntry:
    key: str
    organ: str
    tissue: str
    properties: Mapping[str, Any]
    component_sets: Mapping[str, ComponentSet]     # keyed by modality: "T2", "T1", "diffusion"
    theory: Mapping[str, Any]
    sources: tuple[str, ...]

    def for_modality(self, modality: str) -> ComponentSet:
        return self.component_sets[modality]

    @property
    def T2(self) -> ComponentSet | None:
        return self.component_sets.get("T2")

    def property(self, name: str, field: str | None = None) -> Mapping[str, Any]:
        p = self.properties[name]
        return p[field] if field is not None else p

    def worst_status(self) -> Provenance:
        order = [Provenance.PRIMARY, Provenance.SECONDARY, Provenance.TERTIARY, Provenance.RECALLED, Provenance.THEORY]
        worst = Provenance.PRIMARY
        for cs in self.component_sets.values():
            for c in cs.components:
                if order.index(c.status) > order.index(worst):
                    worst = c.status
        return worst


def _component(d) -> Component:
    return Component(d["name"], float(d["fraction"]), float(d["value"]), Provenance(d["status"]), d["source"],
                     tuple(d["range"]) if d.get("range") else None, d.get("note", ""))


def _build() -> dict[str, TissueEntry]:
    reg: dict[str, TissueEntry] = {}
    for e in tissue_data.ENTRIES:
        sets = {}
        for modality, cs in e["components"].items():
            comps = tuple(_component(c) for c in cs["list"])
            s = sum(c.fraction for c in comps)
            if abs(s - 1.0) > 1e-6:
                raise ValueError(f"{e['key']}/{modality}: fractions sum to {s:.4f}")
            vals = [c.value for c in comps if c.fraction > 0]
            if modality in ("T2", "T1") and vals != sorted(vals):      # relaxation components: ordered by time constant
                raise ValueError(f"{e['key']}/{modality}: components must be ordered by increasing value")
            sets[modality] = ComponentSet(e["key"], e["organ"], e["tissue"], modality, cs["kernel"], cs.get("field_T"),
                                          comps, cs["functional"], cs.get("functional_threshold"), cs["typical_acquisition"],
                                          Provenance(cs["status"]), cs.get("note", ""))
        if e["key"] in reg:
            raise ValueError(f"duplicate tissue key {e['key']}")
        reg[e["key"]] = TissueEntry(e["key"], e["organ"], e["tissue"], e["properties"], sets, e["theory"], tuple(e["sources"]))
    return reg


_REG = _build()


def get(key: str) -> TissueEntry:
    return _REG[key]


def keys() -> list[str]:
    return list(_REG)


def all_entries() -> list[TissueEntry]:
    return list(_REG.values())


def entries(kernel: str | None = None, modality: str | None = None) -> list[ComponentSet]:
    """Component sets across the dictionary, filtered by kernel and/or modality."""
    out = []
    for e in _REG.values():
        for m, cs in e.component_sets.items():
            if kernel is not None and cs.kernel != kernel:
                continue
            if modality is not None and m != modality:
                continue
            out.append(cs)
    return out


def status_summary() -> dict[str, int]:
    """Count of component values by provenance status (for the docs and the changelog)."""
    counts = {p.value: 0 for p in Provenance}
    for cs in entries():
        for c in cs.components:
            counts[c.status.value] += 1
    return counts


def to_json_dict() -> dict:
    return {
        "schema_version": "2.1",
        "generated_from": "mexp.tissue_data",
        "status_legend": {
            "PRIMARY": "read from the original paper's own table/text", "SECONDARY": "abstract / review table / same-author conference abstract / mirrored PDF",
            "TERTIARY": "textbook or website tabulation without a specific primary", "RECALLED": "from memory of the named sources; not opened",
            "THEORY": "derived working configuration, not a measurement"},
        "units": {"times": "ms", "diffusivity": "um^2/ms (= 1e-3 mm^2/s)", "water_content": "mass fraction", "lipid_mass_fraction": "mass fraction (chemical lipid, Woodard & White 1986)", "pdff": "fraction of MR-visible protons (proton-density fat fraction)", "pd_relative_csf": "CSF = 1"},
        "sources": tissue_data.SRC,
        "entries": tissue_data.ENTRIES,
        "changelog": tissue_data.CHANGELOG,
    }
