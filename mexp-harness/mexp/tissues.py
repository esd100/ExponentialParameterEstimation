"""
Tissue and organ dictionary — reference multi-component compositions.

Why this exists (charter §1.2, v0.10): the falsifiable threshold on the
"K = 2 comfortably, K = 3 marginal" figure turned out to depend on the
amplitude vector more than on anything else, and a single myelin-like
20/80 split is not the body.  Each entry here is a literature-derived
composition (component fractions and time constants) for one tissue, one
modality and, where it matters, one field strength, together with the
clinically meaningful functional of that composition (e.g. the myelin water
fraction, the luminal water fraction) and a typical acquisition.  The
harness evaluates the CRLB clauses at every entry
(scripts/phase0_threshold_tissues.py), so "what K does clinical data
support" is answered per tissue rather than for one synthetic vector.

PROVENANCE (charter §7).  Every entry carries a status:

    RECALLED   values written from memory of the named sources; NOT checked
               against the paper in this session.  Usable to *shape* a
               harness configuration; not citable as a number until checked.
    SECONDARY  matched to a review, dataset or abstract that was read.
    PRIMARY    matched to the table/figure of the original paper.

As of 2026-09-07 every entry is RECALLED.  The verification pass is an open
item in claude/phase0-harness-status.md; the sources named are the ones the
verification should start from.  Values are representative central values
with the range noted; real tissue varies with field strength, sequence
(refocusing flip angle, TE_1), age and pathology, and several components
(< 5 ms) are invisible to a CPMG train starting at 10 ms.

Kernels: entries whose kernel is not yet registered ("t2star_ute", "t1_ir",
"diffusion_ivim") are carried for completeness and skipped by the T2 scripts.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Mapping

import numpy as np

from .axes import Modality
from .params import Theta


class Provenance(Enum):
    RECALLED = "recalled"
    SECONDARY = "secondary"
    PRIMARY = "primary"


@dataclass(frozen=True)
class Component:
    name: str
    fraction: float          # signal fraction at the reference point (sums to 1 over the entry)
    value: float             # T2 / T2* / T1 in ms, or D in um^2/ms (= 1e-3 mm^2/s)
    range: tuple[float, float] | None = None   # literature range for `value`
    note: str = ""


@dataclass(frozen=True)
class TissueEntry:
    key: str
    organ: str
    tissue: str
    modality: Modality
    kernel: str                                  # registered kernel name, or a future one
    field_T: float | None
    components: tuple[Component, ...]
    functional: str                              # human name of the clinical functional
    functional_threshold: float | None           # mass below this value (same unit as Component.value); None if n/a
    typical_acquisition: Mapping[str, float]     # e.g. n_echoes, dTE_ms, first_echo_snr
    sources: tuple[str, ...]
    status: Provenance = Provenance.RECALLED
    notes: str = ""

    def __post_init__(self):
        s = sum(c.fraction for c in self.components)
        if abs(s - 1.0) > 1e-6:
            raise ValueError(f"{self.key}: fractions sum to {s}, not 1")
        vals = [c.value for c in self.components]
        if vals != sorted(vals):
            raise ValueError(f"{self.key}: components must be ordered by increasing value")

    @property
    def K(self) -> int:
        return len(self.components)

    def theta(self, min_value: float | None = None) -> Theta:
        """Theta for the entry's kernel; components with value < min_value are
        dropped and the remaining fractions renormalised (a CPMG train starting
        at 10 ms cannot see a 3 ms component; the harness should not pretend)."""
        comps = [c for c in self.components if min_value is None or c.value >= min_value]
        a = np.array([c.fraction for c in comps], dtype=float)
        a = a / a.sum()
        return Theta(a, np.array([[c.value] for c in comps], dtype=float))

    def visible_components(self, min_value: float) -> tuple[Component, ...]:
        return tuple(c for c in self.components if c.value >= min_value)


_REG: dict[str, TissueEntry] = {}


def register(e: TissueEntry) -> TissueEntry:
    if e.key in _REG:
        raise ValueError(f"duplicate tissue key {e.key}")
    _REG[e.key] = e
    return e


def get(key: str) -> TissueEntry:
    return _REG[key]


def entries(kernel: str | None = None, modality: Modality | None = None) -> list[TissueEntry]:
    out = list(_REG.values())
    if kernel is not None:
        out = [e for e in out if e.kernel == kernel]
    if modality is not None:
        out = [e for e in out if e.modality is modality]
    return out


def keys() -> list[str]:
    return list(_REG)


R = Provenance.RECALLED
CPMG_REF = {"n_echoes": 32, "dTE_ms": 10.0, "first_echo_snr": 100.0}

# ----------------------------------------------------------------------------------------------
# T2 (CPMG) entries
# ----------------------------------------------------------------------------------------------

register(TissueEntry(
    key="brain_wm", organ="brain", tissue="white matter", modality=Modality.T2, kernel="t2_cpmg", field_T=1.5,
    components=(
        Component("myelin water", 0.12, 15.0, (10.0, 20.0), "MWF ~0.08-0.15 across WM structures"),
        Component("intra/extracellular water", 0.86, 75.0, (65.0, 90.0)),
        Component("free/CSF-like water", 0.02, 2000.0, (1000.0, 2500.0), "partial volume; often absent in pure WM"),
    ),
    functional="myelin water fraction (mass below 40 ms)", functional_threshold=40.0,
    typical_acquisition=CPMG_REF,
    sources=("MacKay et al. 1994 MRM 31:673", "Whittall et al. 1997 MRM 37:34", "Laule et al. 2007 Neurotherapeutics 4:460",
             "Prasloski et al. 2012 MRM 67:1803 (3 T, EPG)"),
    notes="The canonical case. At 3 T with EPG-corrected fitting MWF is similar; myelin water T2 shifts shorter with field."))

register(TissueEntry(
    key="brain_gm", organ="brain", tissue="cortical grey matter", modality=Modality.T2, kernel="t2_cpmg", field_T=1.5,
    components=(
        Component("myelin water", 0.03, 15.0, (10.0, 20.0)),
        Component("intra/extracellular water", 0.94, 90.0, (80.0, 110.0)),
        Component("free/CSF-like water", 0.03, 2000.0, (1000.0, 2500.0), "cortical partial volume with CSF"),
    ),
    functional="myelin water fraction (mass below 40 ms)", functional_threshold=40.0,
    typical_acquisition=CPMG_REF,
    sources=("Whittall et al. 1997 MRM 37:34", "Laule et al. 2007"),
    notes="Small minor component: the hard case for the short-T2 fraction."))

register(TissueEntry(
    key="spinal_cord_wm", organ="spinal cord", tissue="white matter (dorsal/lateral columns)", modality=Modality.T2,
    kernel="t2_cpmg", field_T=3.0,
    components=(
        Component("myelin water", 0.25, 15.0, (10.0, 20.0), "MWF 0.2-0.3 in cord WM"),
        Component("intra/extracellular water", 0.72, 80.0, (70.0, 100.0)),
        Component("free/CSF-like water", 0.03, 2000.0, (1500.0, 2500.0), "CSF partial volume is severe in cord"),
    ),
    functional="myelin water fraction (mass below 40 ms)", functional_threshold=40.0,
    typical_acquisition=CPMG_REF,
    sources=("MacMillan et al. 2011 NeuroImage 54:1083", "Laule et al. 2010"),
    notes="Higher MWF than brain; the easy myelin case."))

register(TissueEntry(
    key="skeletal_muscle", organ="musculoskeletal", tissue="skeletal muscle (calf/thigh)", modality=Modality.T2,
    kernel="t2_cpmg", field_T=1.5,
    components=(
        Component("macromolecule-associated water", 0.05, 4.0, (2.0, 8.0), "invisible to a 10 ms first echo"),
        Component("intracellular water", 0.85, 33.0, (28.0, 40.0)),
        Component("extracellular/interstitial water", 0.10, 130.0, (100.0, 200.0), "rises with oedema, exercise"),
    ),
    functional="extracellular fraction (mass above 60 ms, i.e. 1 - mass below 60 ms)", functional_threshold=60.0,
    typical_acquisition=CPMG_REF,
    sources=("Saab, Thompson & Marsh 1999 MRM 42:150", "Araujo et al. 2014 Biophys J 106:2267 (3 T)"),
    notes="Saab et al. report four components at 1.5 T; the shortest is below any clinical first echo."))

register(TissueEntry(
    key="articular_cartilage", organ="knee", tissue="articular cartilage", modality=Modality.T2, kernel="t2_cpmg", field_T=3.0,
    components=(
        Component("collagen-bound water", 0.05, 3.0, (1.0, 5.0), "needs UTE; invisible to CPMG at 10 ms"),
        Component("intermediate (proteoglycan-associated) water", 0.20, 25.0, (15.0, 35.0)),
        Component("bulk water", 0.75, 90.0, (60.0, 150.0)),
    ),
    functional="short/intermediate fraction (mass below 45 ms)", functional_threshold=45.0,
    typical_acquisition={"n_echoes": 32, "dTE_ms": 6.0, "first_echo_snr": 100.0},
    sources=("Reiter, Lin, Fishbein & Spencer 2009 MRM 61:803 (bovine nasal cartilage, ex vivo)",
             "Bouhrara et al. 2015 MRM 73:352 (biexponential T2*, 3 T / 7 T)"),
    notes="Ex vivo values; in vivo human cartilage is thinner and lower SNR. Fractions depend strongly on depth zone."))

register(TissueEntry(
    key="prostate_pz", organ="prostate", tissue="peripheral zone, normal", modality=Modality.T2, kernel="t2_cpmg", field_T=3.0,
    components=(
        Component("epithelial/stromal water", 0.65, 60.0, (40.0, 80.0)),
        Component("luminal water", 0.35, 500.0, (300.0, 800.0), "long-T2 glandular lumen"),
    ),
    functional="luminal water fraction (1 - mass below 200 ms)", functional_threshold=200.0,
    typical_acquisition={"n_echoes": 64, "dTE_ms": 8.0, "first_echo_snr": 80.0},
    sources=("Sabouri et al. 2017 MRM 77:2038 (luminal water imaging)", "Sabouri et al. 2017 Radiology"),
    notes="Two well-separated components (ratio ~8); LWF falls in tumour. Long echo train needed for the 500 ms component."))

register(TissueEntry(
    key="breast_fibroglandular", organ="breast", tissue="fibroglandular tissue with fat partial volume", modality=Modality.T2,
    kernel="t2_cpmg", field_T=1.5,
    components=(
        Component("fibroglandular water", 0.6, 50.0, (40.0, 70.0)),
        Component("fat (methylene)", 0.4, 100.0, (70.0, 140.0), "chemically shifted; better separated by Dixon than by T2"),
    ),
    functional="fat fraction (1 - mass below 75 ms)", functional_threshold=75.0,
    typical_acquisition=CPMG_REF,
    sources=("Edden et al. 2009 JMRI (breast T2)", "general fat/water relaxometry literature"),
    notes="Illustrates a two-component case with ratio ~2: at the resolvability limit at clinical SNR."))

register(TissueEntry(
    key="myocardium", organ="heart", tissue="left-ventricular myocardium", modality=Modality.T2, kernel="t2_cpmg", field_T=1.5,
    components=(
        Component("myocardial water", 1.0, 48.0, (42.0, 55.0)),
    ),
    functional="T2 (mono-exponential)", functional_threshold=None,
    typical_acquisition={"n_echoes": 8, "dTE_ms": 12.0, "first_echo_snr": 60.0},
    sources=("Giri et al. 2009 JCMR (T2 mapping)", "Baessler et al. 2015"),
    notes="K = 1 null case: a method that finds two components here is fitting noise. Austere budget."))

register(TissueEntry(
    key="liver_parenchyma_t2", organ="liver", tissue="parenchyma (normal iron)", modality=Modality.T2, kernel="t2_cpmg", field_T=1.5,
    components=(
        Component("hepatocellular water", 0.9, 45.0, (35.0, 55.0)),
        Component("blood/bile/vascular partial volume", 0.1, 200.0, (120.0, 300.0)),
    ),
    functional="long-T2 fraction (1 - mass below 100 ms)", functional_threshold=100.0,
    typical_acquisition={"n_echoes": 16, "dTE_ms": 8.0, "first_echo_snr": 60.0},
    sources=("general hepatic T2 relaxometry literature; iron-overload T2/T2* work (St Pierre 2005, Wood 2005)"),
    notes="Iron shortens T2 drastically; this entry is the normal-iron case. Weak literature support for the second component."))

# ----------------------------------------------------------------------------------------------
# Entries for kernels not yet registered (carried for the dictionary's completeness)
# ----------------------------------------------------------------------------------------------

register(TissueEntry(
    key="cortical_bone_ute", organ="bone", tissue="cortical bone", modality=Modality.T2STAR, kernel="t2star_ute", field_T=3.0,
    components=(
        Component("collagen-bound water", 0.7, 0.35, (0.25, 0.5), "T2* in ms"),
        Component("pore water", 0.3, 3.0, (1.0, 10.0), "broad; multi-exponential in itself"),
    ),
    functional="bound-water fraction (mass below 1 ms)", functional_threshold=1.0,
    typical_acquisition={"n_echoes": 12, "dTE_ms": 0.3, "first_echo_snr": 40.0},
    sources=("Horch, Nyman, Gochberg, Dortch & Does 2010 MRM 64:680", "Du et al. 2010 JMR / Bydder UTE literature"),
    notes="Needs a UTE T2* kernel; ratio ~10 but both components are sub-10 ms."))

register(TissueEntry(
    key="achilles_tendon_ute", organ="musculoskeletal", tissue="Achilles tendon", modality=Modality.T2STAR, kernel="t2star_ute", field_T=3.0,
    components=(
        Component("short T2* (bound)", 0.8, 1.0, (0.5, 2.0)),
        Component("long T2* (free)", 0.2, 15.0, (10.0, 25.0)),
    ),
    functional="short fraction (mass below 5 ms)", functional_threshold=5.0,
    typical_acquisition={"n_echoes": 12, "dTE_ms": 0.5, "first_echo_snr": 40.0},
    sources=("Du et al. 2010 MRI 28:178 (UTE bicomponent T2*)", "Juras et al. 2013"),
    notes="Magic-angle dependent; the fractions swing with fibre orientation."))

register(TissueEntry(
    key="brain_wm_t1", organ="brain", tissue="white matter", modality=Modality.T1, kernel="t1_ir", field_T=3.0,
    components=(
        Component("myelin-associated (short T1)", 0.15, 300.0, (150.0, 450.0), "exchange-attenuated; see charter §2.3"),
        Component("intra/extracellular (long T1)", 0.85, 950.0, (800.0, 1100.0)),
    ),
    functional="short-T1 fraction (mass below 600 ms)", functional_threshold=600.0,
    typical_acquisition={"n_points": 32, "TI_spacing_ms": 100.0, "first_echo_snr": 100.0},
    sources=("Labadie et al. 2014 MRM 71:375", "Deoni et al. 2008 (mcDESPOT)", "Lankford & Does 2013 MRM 69:127 (precision critique)"),
    notes="The exchange-limited case (charter §2.3); needs the IR kernel and a Bloch-McConnell truth to score honestly."))

register(TissueEntry(
    key="liver_ivim", organ="liver", tissue="parenchyma", modality=Modality.DIFFUSION, kernel="diffusion_ivim", field_T=1.5,
    components=(
        Component("tissue diffusion D", 0.75, 1.1, (0.9, 1.3), "um^2/ms"),
        Component("pseudo-diffusion D*", 0.25, 50.0, (20.0, 100.0), "um^2/ms; perfusion fraction f ~0.2-0.3"),
    ),
    functional="perfusion fraction f (1 - mass below 10 um^2/ms)", functional_threshold=10.0,
    typical_acquisition={"n_b": 10, "b_max_s_per_mm2": 800.0, "first_echo_snr": 50.0},
    sources=("Le Bihan et al. 1988 Radiology 168:497", "Luciani et al. 2008 Radiology 249:891"),
    notes="The canonical two-compartment diffusion case; ratio ~45 in D but the fast component lives in b < 100."))
