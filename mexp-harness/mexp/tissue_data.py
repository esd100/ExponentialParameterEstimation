"""
Tissue and organ dictionary — DATA (charter §1.2 tissue-level threshold, §4 Phase 0, §6.1).

This module is the single source of truth for the dictionary; `mexp.tissues`
loads it and `scripts/export_tissue_dictionary.py` writes the JSON release
(`data/tissue_dictionary.json`) that other tools can read.

Every number carries a provenance status (charter §7):

    PRIMARY    read from the original paper's own table/text this project has opened
    SECONDARY  read from an abstract, a review's table, a conference abstract by the same
               authors, or a publisher-mirrored PDF of the paper (opened, but not the primary
               table itself — or the primary read through a mirror)
    TERTIARY   read from a textbook/website tabulation that cites the literature generically
    RECALLED   written from memory of the named sources; not opened by this project
    THEORY     not a measured number: derived from physiology/physics as a working
               configuration (typically a compartment split that no paper reports)

Units: times in ms; diffusivities in um^2/ms (= 1e-3 mm^2/s); water content and
lipid content as mass fractions; PDFF (proton-density fat fraction) as a fraction of
MR-visible protons; relative proton density with CSF = 1.  Fields: "1.5T" / "3T"
(other fields noted in `note`).  Component fractions are signal fractions at the
reference point and sum to 1 within each component list.

Sources are cited by short key; the full records live in docs/project/bibliography.md
and the per-tissue discussion in docs/project/tissue-dictionary.md.  Verification
history is in the per-value `status` and the module CHANGELOG at the bottom.
"""
from __future__ import annotations

# ---- helpers to keep the literals short -------------------------------------------------------

def V(value, status, source, unit=None, range=None, note=""):
    d = {"value": value, "status": status, "source": source}
    if unit is not None: d["unit"] = unit
    if range is not None: d["range"] = list(range)
    if note: d["note"] = note
    return d


def C(name, fraction, value, status, source, range=None, note=""):
    d = {"name": name, "fraction": fraction, "value": value, "status": status, "source": source}
    if range is not None: d["range"] = list(range)
    if note: d["note"] = note
    return d


CPMG_REF = {"n_echoes": 32, "dTE_ms": 10.0, "first_echo_snr": 100.0}

# Short source keys -> full citations are in docs/project/bibliography.md
SRC = {
    "St05": "Stanisz et al. 2005 MRM 54:507 (Table 1; in vitro 37 C, mixed species; read via publisher PDF mirror)",
    "dB04": "de Bazelaire et al. 2004 Radiology 230:652 (Tables 1-2 read 2026-09-09: T1/T2 at 1.5 and 3 T in vivo, n = 6; SSFSE-IR / SSFSE multi-TE)",
    "Han03": "Han/Gold et al. ISMRM 2003 #450 (conference abstract table; superseded by Gold04 where the AJR table was read)",
    "Gold04": "Gold et al. 2004 AJR 183:343 (Tables read 2026-09-09: T1 by IR-FSE, T2 by T2-prep spiral, 1.5 and 3 T in vivo, n = 5)",
    "Woo86": "Woodard & White 1986 Br J Radiol 59:1209 (Table I read 2026-09-09: water / lipid / protein / ash, % by mass; three compositions where the literature spread is large)",
    "Wan99": "Wansapura et al. 1999 JMRI 9:531 (3 T; abstract)",
    "Wri08": "Wright et al. 2008 MAGMA 21:121 (MPRAGE T1; abstract)",
    "Roo07": "Rooney et al. 2007 MRM 57:308 (T1 field dependence; abstract)",
    "Boj17": "Bojorquez et al. 2017 MRI 35:69 (3 T review; Tables 1-2 read from the publisher PDF 2026-09-09)",
    "RP06": "Rakow-Penner et al. 2006 JMRI 23:87 as tabulated by Keenan et al. 2016 (NIST) and Bojorquez 2017",
    "vKB13": "von Knobelsdorff-Brenkenhoff et al. 2013 JCMR 15:53 (3 T myocardium; full text)",
    "Giri09": "Giri et al. 2009 JCMR 11:56 (1.5 T myocardial T2, quoted in vKB13)",
    "Qiao17": "Qiao et al. 2017 (Achilles UTE T2*; full text via Semantic Scholar PDF)",
    "AR20": "Abbasi-Rad et al. 2020 arXiv:2002.00209 (cortical bone T2*/T1; preprint)",
    "OP19": "Oros-Peusquens et al. 2019 Front Neurol 10:1333 (brain water content 3 T; full text)",
    "Whi97": "Whittall et al. 1997 MRM 37:34 (abstract: water content WM 0.71, GM 0.83 g/ml; gmT2 70-86 ms)",
    "MacK94": "MacKay et al. 1994 MRM 31:673 (full-text preview: MWF WM 15.6 +/- 8.1 %, GM 3.8 +/- 6.4 %; IE 70-95 ms)",
    "Lau07": "Laule et al. 2007 Neurotherapeutics 4:460 (review; full text)",
    "MacM07": "MacMillan et al. ISMRM 2007 #2331 (3 T cord MWF 0.226; precursor of MacMillan 2011 NeuroImage 54:1083)",
    "Saab99": "Saab, Thompson & Marsh 1999 MRM 42:150 (abstract: <5 / 21 / 39 / 114 ms, 11 / 28 / 46 / 5 %)",
    "Ara14": "Araujo, Fromes & Carlier 2014 Biophys J 106:2267 (record confirmed; values not reachable)",
    "Rei09": "Reiter, Lin, Fishbein & Spencer 2009 MRM 61:803 (full text, PMC2711212; bovine nasal cartilage 9.4 T)",
    "Bou15": "Bouhrara et al. 2015 MRM 73:352 (record confirmed)",
    "Sab17": "Sabouri et al. 2017 Radiology 284:451 and JMRI 46:861 (records confirmed; LWF values not reachable)",
    "Hor10": "Horch et al. 2010 MRM 64:680 (full text, PMC2933073; human cortical bone 4.7 T)",
    "Du12": "Du et al. 2012 MRM 67:645 (abstract; UTE bicomponent T2*)",
    "Lab14": "Labadie et al. 2014 MRM 71:375 (abstract: short-T1 106-225 ms, WM fraction 8.3 % at 3 T)",
    "LeS16": "Le Ster et al. 2016 JMRI 44:549 (Table 1 read 2026-09-09: L1-L5 marrow at 1.5 T, VIBE-Dixon two flip angles, n = 8: FF 33+/-8 %, T1w 701+/-151, T1f 334+/-113, T2*w 13.7+/-2.9, T2*f 11.4+/-2.7 ms)",
    "Luc08": "Luciani et al. 2008 Radiology 249:891 (Table 4, full PDF; liver IVIM 1.5 T)",
    "Li17": "Li et al. 2017 QIMS (27-study pooled liver IVIM; full text)",
    "Yam99": "Yamada et al. 1999 Radiology 210:617 (abstract; IVIM D liver/spleen/kidney 1.5 T)",
    "vBa17": "van Baalen et al. 2017 JMRI (full text; kidney cortex/medulla IVIM 3 T)",
    "Fil15": "Filli et al. 2015 Eur Radiol 25:2049 (abstract; renal cortex IVIM 3 T)",
    "Ser24": "Serafin et al. 2024 Diagnostics 14:571 (full text; pancreas IVIM 1.5 T, n=47)",
    "May21": "Mayer et al. 2021 Cancer Imaging 21:13 (full PDF; pancreas IVIM)",
    "McG15": "McGill et al. 2015 PLOS One 10:e0132360 (full text; myocardial DTI 3 T)",
    "Maz21": "Mazzoli et al. 2021 Front Neurol 12:608549 (full text; muscle DTI 3 T; unit flag)",
    "SM25": "bioRxiv 2025 doi 10.64898/2025.12.06.692761 and Jelescu & Budde 2017 Front Phys 5:61 (WM standard model ranges)",
    "RK": "Radiology Key 'MRI tissue parameters' Table 6-1 (relative PD, CSF = 100; tertiary, no primary cited)",
    "MRM-web": "mrimaster.com ADC table (tertiary; no b-values; no primary cited)",
    "EJR20": "Egypt J Radiol Nucl Med 2020 doi 10.1186/s43055-020-00212-3 (liver/spleen ADC controls; spleen SD anomalous)",
    "Ber83": "Bernardino et al. 1983 AJR 141:1203 (ex vivo biexponential liver T2; abstract, no values)",
    "Tas24": "Tasbihi et al. 2024 MRM 91:2532 (rat kidney biexponential T2 as tubule-volume surrogate; abstract)",
    "Szc05": "Szczepaniak et al. 2005 Am J Physiol Endocrinol Metab 288:E462 (Dallas Heart Study: hepatic triglyceride 95th percentile 5.56 % by MRS; not opened)",
    "Tang13": "Tang et al. 2013 Radiology 267:422 (MRI-PDFF vs histologic steatosis grade thresholds ~ 6.4 / 17.4 / 22.1 %; not opened)",
    "Hen92": "Henkelman, Hardy, Bishop, Poon & Plewes 1992 JMRI 2:533 ('Why fat is bright in RARE and fast spin-echo imaging': J-coupling makes fat T2 echo-spacing dependent; not opened)",
    "Ham11": "Hamilton et al. 2011 NMR Biomed 24:784 (six-peak triglyceride spectrum model for fat quantification; not opened)",
    "PDFF-lit": "PDFF ranges for lean organs from the water-fat imaging literature (Reeder/Hu/Yokoo reviews; muscle, myocardium, pancreas, kidney; not opened this session)",
}

ENTRIES = []

def add(**e):
    ENTRIES.append(e)

# ==============================================================================================
# BRAIN
# ==============================================================================================
add(key="brain_wm", organ="brain", tissue="white matter",
    properties={
        "water_content": V(0.69, "PRIMARY", "Woo86 Table I WM 68.5 %; OP19 in vivo 68.7-71.6 %; Whi97 0.71 g/ml", "g/g", (0.685, 0.716)),
        "pd_relative_csf": V(0.70, "TERTIARY", "RK (WM 60-70 of CSF 100); consistent with water content 0.69/1.0", None, (0.60, 0.72)),
        "T1_ms": {"1.5T": V(884, "SECONDARY", "St05 (bovine, 884+/-50); Wri08 MPRAGE in vivo 646+/-32; Roo07 fit 681", None, (646, 884)),
                  "3T": V(1084, "SECONDARY", "St05 (bovine 1084+/-45); Wan99 832; Wri08 838+/-50; Roo07 fit 887", None, (832, 1084))},
        "T2_ms": {"1.5T": V(72, "SECONDARY", "St05 (72+/-4)", None, (65, 80)),
                  "3T": V(69, "SECONDARY", "St05 (69+/-3); Lu05 via Boj17 75+/-3", None, (65, 80))},
        "ADC": V(0.75, "TERTIARY", "MRM-web (0.70-0.80)", "um2/ms", (0.70, 0.80)),
    },
    components={
        "T2": {"kernel": "t2_cpmg", "field_T": 1.5, "status": "SECONDARY",
               "list": [C("myelin water", 0.15, 15.0, "SECONDARY", "MacK94 MWF 15.6+/-8.1 %; window 10-50 ms (Whi97, Lau07)", (10, 20)),
                        C("intra/extracellular water", 0.83, 78.0, "SECONDARY", "MacK94 70-95 ms; Whi97 gmT2 70-86 ms", (70, 95)),
                        C("free/CSF-like water", 0.02, 2000.0, "RECALLED", "Lau07 (>= 1 s); partial volume", (1000, 2500))],
               "functional": "myelin water fraction (mass below 40 ms)", "functional_threshold": 40.0,
               "typical_acquisition": CPMG_REF},
        "T1": {"kernel": "t1_ir", "field_T": 3.0, "status": "SECONDARY",
               "list": [C("myelin-associated (short T1)", 0.083, 170.0, "SECONDARY", "Lab14: 106-225 ms, WM fraction 8.3 % at 3 T", (106, 225)),
                        C("intra/extracellular (long T1)", 0.917, 1000.0, "SECONDARY", "Lab14 main peak; St05/Wri08 bulk T1", (830, 1100))],
               "functional": "short-T1 fraction (mass below 500 ms)", "functional_threshold": 500.0,
               "typical_acquisition": {"n_points": 32, "TI_spacing_ms": 100.0, "first_echo_snr": 100.0}},
        "diffusion": {"kernel": "diffusion_standard_model", "field_T": 3.0, "status": "SECONDARY",
               "list": [C("intra-axonal (stick)", 0.5, 2.2, "SECONDARY", "SM25: f 0.35-0.70, Da 2.03-2.41", (2.0, 2.4), "Da along the axon"),
                        C("extra-axonal", 0.5, 0.6, "SECONDARY", "SM25: De_perp 0.51-0.72, De_par 1.87-2.27", (0.5, 0.72), "value = De_perp")],
               "functional": "intra-axonal signal fraction", "functional_threshold": None,
               "typical_acquisition": {"b_values_ms_per_um2": [1, 2, 3, 5], "directions": 60, "first_echo_snr": 30.0}},
    },
    theory={
        "pools": ["myelin water (between bilayers, ~15 % of WM water)", "intra-axonal water", "extra-axonal / interstitial water",
                  "glial intracellular water", "blood (CBV ~ 2-3 %)", "CSF partial volume at voxel scale",
                  "non-aqueous protons (lipid, protein; T2 < 100 us)"],
        "n_pools": 7,
        "exchange": "Myelin water exchanges with intra/extra-axonal water on ~100-300 ms (intermediate on the T2 scale, fast on the T1 scale -> multi-component T1 is exchange-attenuated); intra- and extra-axonal water exchange slowly (~0.5-2 s) but have nearly equal T2 and coalesce; glial water is unresolved.",
        "n_apparent_T2": 3, "n_resolvable_clinical_T2": 2,
        "rationale": "Seven physical pools reduce to three apparent T2 components (myelin, IE, CSF) because IE-scale pools share T2 within the exchange-averaged tolerance; at clinical SNR two are resolvable, and the third (CSF) is unpinned by a 320 ms window. On the T1 axis exchange leaves only a weak short component (8 % at 3 T, rising with field)."},
    sources=["MacK94", "Whi97", "Lau07", "St05", "Wri08", "Roo07", "OP19", "Lab14", "SM25"])

add(key="brain_gm", organ="brain", tissue="cortical grey matter",
    properties={
        "water_content": V(0.83, "PRIMARY", "Woo86 Table I GM 82.6 %; OP19 83.7+/-1.2 %; Whi97 0.83 g/ml", "g/g", (0.805, 0.846)),
        "pd_relative_csf": V(0.83, "TERTIARY", "RK (GM 70-85); water content 0.84", None, (0.70, 0.85)),
        "T1_ms": {"1.5T": V(1124, "SECONDARY", "St05 (bovine 1124+/-50); Wri08 MPRAGE 1197+/-134; Roo07 fit 998", None, (998, 1197)),
                  "3T": V(1607, "SECONDARY", "Wri08 (1607+/-112); St05 bovine 1820+/-114; Wan99 1331; Lu05 via Boj17 1165", None, (1165, 1820))},
        "T2_ms": {"1.5T": V(95, "SECONDARY", "St05 (95+/-8)", None, (85, 110)),
                  "3T": V(99, "SECONDARY", "St05 (99+/-7); Lu05 via Boj17 83+/-4", None, (80, 110))},
        "ADC": V(0.85, "TERTIARY", "MRM-web (0.80-0.90)", "um2/ms", (0.80, 0.90)),
    },
    components={
        "T2": {"kernel": "t2_cpmg", "field_T": 1.5, "status": "SECONDARY",
               "list": [C("myelin water", 0.04, 15.0, "SECONDARY", "MacK94 GM MWF 3.8+/-6.4 %", (10, 20)),
                        C("intra/extracellular water", 0.93, 90.0, "SECONDARY", "Whi97 gmT2 70-86 ms (GM at the upper end); St05 95", (80, 110)),
                        C("CSF partial volume", 0.03, 2000.0, "RECALLED", "cortical ribbon partial volume", (1000, 2500))],
               "functional": "myelin water fraction (mass below 40 ms)", "functional_threshold": 40.0, "typical_acquisition": CPMG_REF},
    },
    theory={"pools": ["neuronal/glial intracellular water", "extracellular water", "sparse myelin water", "blood (CBV ~ 4-6 %)", "CSF partial volume", "non-aqueous protons"],
            "n_pools": 6, "exchange": "Intra/extracellular water coalesce; myelin water is sparse; blood is a few percent at longer T2 (oxygenation dependent).",
            "n_apparent_T2": 3, "n_resolvable_clinical_T2": 1,
            "rationale": "The minor components (myelin ~4 %, blood ~5 %, CSF ~3 %) are each below the clinical detectability floor; GM is effectively mono-exponential to a CPMG train at SNR 100 and is the hard case for any short-T2 fraction."},
    sources=["MacK94", "Whi97", "St05", "Wri08", "OP19"])

add(key="csf", organ="brain", tissue="cerebrospinal fluid (ventricular)",
    properties={
        "water_content": V(0.99, "PRIMARY", "Woo86 Table I CSF 99.0 %", "g/g"),
        "pd_relative_csf": V(1.0, "TERTIARY", "definition"),
        "T1_ms": {"1.5T": V(4300, "SECONDARY", "Roo07 (4300+/-200, field independent)", None, (4000, 4500)),
                  "3T": V(4300, "SECONDARY", "Roo07; Lu05 via Boj17 3817+/-424", None, (3800, 4500))},
        "T2_ms": {"1.5T": V(2200, "TERTIARY", "Wikipedia table (2100-2300, uncited)", None, (1500, 2500)),
                  "3T": V(2000, "RECALLED", "typically 1.5-2.5 s", None, (1500, 2500))},
        "ADC": V(3.0, "TERTIARY", "MRM-web (2.0-3.0); free water at 37 C is 3.0", "um2/ms", (2.0, 3.2)),
    },
    components={"T2": {"kernel": "t2_cpmg", "field_T": 1.5, "status": "SECONDARY",
                       "list": [C("free water", 1.0, 2000.0, "TERTIARY", "single pool", (1500, 2500))],
                       "functional": "T2 (mono-exponential)", "functional_threshold": None,
                       "typical_acquisition": CPMG_REF}},
    theory={"pools": ["free water"], "n_pools": 1, "exchange": "n/a", "n_apparent_T2": 1, "n_resolvable_clinical_T2": 1,
            "rationale": "K = 1 reference and the partial-volume contaminant of every brain entry; its T2 exceeds any clinical echo train, so it appears as a near-constant offset — the charter §3.2 sigma / long-T degeneracy in physical form."},
    sources=["Roo07", "Boj17"])

add(key="spinal_cord_wm", organ="spinal cord", tissue="cervical cord white matter (lateral/dorsal columns)",
    properties={
        "water_content": V(0.70, "THEORY", "no cord-specific composition in Woo86; taken as brain WM (68.5 %) with a small GM/CSF admixture", "g/g", (0.68, 0.75)),
        "pd_relative_csf": V(0.70, "TERTIARY", "as WM", None, (0.60, 0.75)),
        "T1_ms": {"1.5T": V(745, "SECONDARY", "St05 (rat cord 745+/-37)", None, (700, 900)),
                  "3T": V(750, "SECONDARY", "Smith & van Zijl ISMRM 2007: lateral 752+/-89, dorsal 745+/-61; St05 rat 993+/-47", None, (745, 993))},
        "T2_ms": {"1.5T": V(74, "SECONDARY", "St05 (rat 74+/-6)", None, (65, 80)),
                  "3T": V(66, "SECONDARY", "Smith & van Zijl 2007: 65+/-4 / 66+/-4; St05 rat 78+/-2", None, (65, 78))},
        "ADC": V(0.9, "RECALLED", "cord MD ~0.9 (strongly anisotropic)", "um2/ms", (0.8, 1.1)),
    },
    components={"T2": {"kernel": "t2_cpmg", "field_T": 3.0, "status": "SECONDARY",
                       "list": [C("myelin water", 0.23, 20.0, "SECONDARY", "MacM07: whole-cord MWF 0.226, myelin T2 ~20 ms (window < 40 ms) at 3 T", (10, 25)),
                                C("intra/extracellular water", 0.74, 75.0, "SECONDARY", "Smith & van Zijl 2007 bulk 65-66 ms; St05", (65, 90)),
                                C("CSF partial volume", 0.03, 2000.0, "RECALLED", "severe around the cord", (1500, 2500))],
                       "functional": "myelin water fraction (mass below 40 ms)", "functional_threshold": 40.0, "typical_acquisition": CPMG_REF}},
    theory={"pools": ["myelin water (denser than brain WM)", "intra-axonal", "extra-axonal", "glial", "blood", "CSF partial volume (large: small structure)", "non-aqueous"],
            "n_pools": 7, "exchange": "as brain WM", "n_apparent_T2": 3, "n_resolvable_clinical_T2": 2,
            "rationale": "Same pool structure as brain WM with a larger myelin fraction (0.2-0.3), which is why the MWF is the easy myelin case, and a larger CSF contaminant, which is why the long component matters more."},
    sources=["MacM07", "St05"])

# ==============================================================================================
# MUSCULOSKELETAL
# ==============================================================================================
add(key="skeletal_muscle", organ="musculoskeletal", tissue="skeletal muscle (calf / forearm / paravertebral)",
    properties={
        "water_content": V(0.74, "PRIMARY", "Woo86 Table I skeletal muscle 2: 74.1 % (compositions 1-3: 70.0 / 74.1 / 78.6 %)", "g/g", (0.70, 0.786)),
        "pd_relative_csf": V(0.90, "TERTIARY", "RK"),
        "T1_ms": {"1.5T": V(1008, "SECONDARY", "St05 (mouse 1008+/-20); Han03 in vivo 1130+/-92; dB04 paravertebral 856+/-61 (PRIMARY)", None, (856, 1200)),
                  "3T": V(1412, "SECONDARY", "St05 (1412+/-13); Han03 1420+/-38; dB04 paravertebral 898+/-33 (PRIMARY)", None, (898, 1420))},
        "T2_ms": {"1.5T": V(35, "SECONDARY", "Han03 in vivo 35.3+/-3.9; dB04 paravertebral 27+/-8 (PRIMARY); St05 mouse 44+/-6; Saab99 imaging T2 31 ms", None, (27, 45)),
                  "3T": V(32, "SECONDARY", "Han03 31.7+/-1.9; dB04 paravertebral 29+/-4 (PRIMARY); St05 50+/-4 (mouse)", None, (29, 50))},
        "ADC": V(1.5, "SECONDARY", "Maz21/Schlaffke: AD 1.9-2.6, RD 1.35-1.6 (unit flag in source); MRM-web 1.0-1.5", "um2/ms", (1.3, 1.8)),
    },
    components={
        "T2": {"kernel": "t2_cpmg", "field_T": 1.5, "status": "SECONDARY",
               "list": [C("macromolecule-associated water", 0.12, 4.0, "SECONDARY", "Saab99: < 5 ms, 11+/-2 %", (2, 5), "invisible to a 10 ms first echo"),
                        C("short intracellular (myofibrillar) water", 0.31, 21.0, "SECONDARY", "Saab99: 21+/-4 ms, 28+/-15 %", (17, 25)),
                        C("main intracellular (sarcoplasmic) water", 0.51, 39.0, "SECONDARY", "Saab99: 39+/-4 ms, 46+/-12 %", (35, 43)),
                        C("extracellular / interstitial water", 0.06, 114.0, "SECONDARY", "Saab99: 114+/-6 ms, 5 %", (100, 200), "rises with oedema, exercise")],
               "functional": "extracellular fraction (1 - mass below 60 ms)", "functional_threshold": 60.0, "typical_acquisition": CPMG_REF},
        "diffusion": {"kernel": "diffusion_tensor", "field_T": 3.0, "status": "SECONDARY",
               "list": [C("tensor: axial diffusivity", 1.0, 2.0, "SECONDARY", "Maz21 PGSE TA/soleus AD 2.32/2.64; Schlaffke AD 1.89/2.14", (1.9, 2.6)),
                        C("tensor: radial diffusivity", 0.0, 1.5, "SECONDARY", "Maz21 RD 1.55/1.51; Schlaffke 1.35/1.62", (1.35, 1.6), "fraction 0 = same pool, second eigenvalue")],
               "functional": "fractional anisotropy", "functional_threshold": None,
               "typical_acquisition": {"b_values_s_per_mm2": [0, 400, 600], "directions": 12, "first_echo_snr": 30.0}},
    },
    theory={"pools": ["myofibrillar (intra-sarcomere) water", "sarcoplasmic / mitochondrial water", "interstitial (endomysial) water", "vascular water (~ 3-5 % blood volume)",
                      "macromolecule-bound water (< 5 ms)", "intramuscular fat (methylene protons; variable)"],
            "n_pools": 6, "exchange": "Intracellular sub-pools exchange on ms-tens of ms and are only separable at very high SNR (Saab99's 1000-echo, SNR 3500 data); intra/extracellular exchange ~ 100s of ms is slow enough to leave two visible components.",
            "n_apparent_T2": 4, "n_resolvable_clinical_T2": 2,
            "rationale": "Saab et al. needed SNR ~3500 and 1.2 ms echoes to see four components; a clinical 32 x 10 ms train sees the ~30 ms intracellular pool and, at best, the ~120 ms extracellular one (the oedema marker)."},
    sources=["Saab99", "Ara14", "St05", "Han03", "dB04", "Maz21"])

add(key="articular_cartilage", organ="knee", tissue="articular (hyaline) cartilage",
    properties={
        "water_content": V(0.75, "PRIMARY", "Woo86 Table I cartilage 75.0 %; depth-dependent 65-80 % (Shiguetomi-Medina 2017, SECONDARY)", "g/g", (0.65, 0.80)),
        "pd_relative_csf": V(0.60, "RECALLED", "collagen/PG matrix reduces mobile PD; not opened", None, (0.5, 0.7)),
        "T1_ms": {"1.5T": V(1024, "SECONDARY", "St05 (bovine 1024+/-70 at 0 deg); Han03 in vivo 1060+/-155", None, (1000, 1100)),
                  "3T": V(1168, "SECONDARY", "St05 (1168+/-18); Han03 1240+/-107", None, (1150, 1250))},
        "T2_ms": {"1.5T": V(37, "SECONDARY", "St05 30+/-4 (0 deg) / 44+/-5 (55 deg, magic angle); Han03 42.1+/-7.1", None, (30, 44)),
                  "3T": V(35, "SECONDARY", "St05 27+/-3 / 43+/-2; Han03 36.9+/-3.8", None, (27, 43))},
        "ADC": V(1.3, "SECONDARY", "Raya 2012: healthy-vs-OA threshold ADC 1.2 (7 T); MRM-web n/a", "um2/ms", (1.1, 1.5)),
    },
    components={"T2": {"kernel": "t2_cpmg", "field_T": 9.4, "status": "PRIMARY",
                       "list": [C("collagen-bound water", 0.062, 2.3, "PRIMARY", "Rei09 control: 2.3+/-0.6 ms, 6.2+/-2.5 %", (1.7, 2.9), "needs UTE; invisible to CPMG at 10 ms"),
                                C("proteoglycan-associated water", 0.145, 25.2, "PRIMARY", "Rei09: 25.2+/-6.2 ms, 14.5+/-3.9 %", (19, 31)),
                                C("bulk water", 0.793, 96.3, "PRIMARY", "Rei09: 96.3+/-4.7 ms, 79.3+/-6.1 %", (90, 101))],
                       "functional": "short/intermediate fraction (mass below 45 ms)", "functional_threshold": 45.0,
                       "typical_acquisition": {"n_echoes": 32, "dTE_ms": 6.0, "first_echo_snr": 100.0},
                       "note": "ex vivo bovine nasal cartilage at 9.4 T (Rei09); in vivo human articular cartilage at 3 T has shorter bulk T2 (~35-45 ms) and a magic-angle dependence; Bou15 treats it as biexponential T2* at 3/7 T"}},
    theory={"pools": ["collagen-bound water (T2 ~ 1-3 ms)", "proteoglycan-associated water", "bulk (free) water", "zonal variation superficial/transitional/deep (orientation-dependent T2)", "synovial fluid partial volume at the surface"],
            "n_pools": 5, "exchange": "Bound and PG-associated water exchange with bulk on sub-ms to ms scales; the residual three-component structure (Rei09) survives because exchange is not complete. Orientation (magic angle) modulates T2 within the bulk pool, i.e. a distribution, not a discrete component.",
            "n_apparent_T2": 3, "n_resolvable_clinical_T2": 2,
            "rationale": "At clinical TE_1 = 6-10 ms the 2 ms pool is gone; what remains is a ~25 ms / ~90 ms pair with ratio ~4 and a 15 % minor fraction — resolvable at high SNR in thick cartilage, marginal in vivo where SNR and thickness are both smaller."},
    sources=["Rei09", "Bou15", "St05", "Han03"])

add(key="achilles_tendon", organ="musculoskeletal", tissue="Achilles tendon",
    properties={
        "water_content": V(0.60, "PRIMARY", "Woo86 Table I connective tissue 60.4 % (composition based on cattle tendon, Oser 1965)", "g/g", (0.55, 0.70)),
        "pd_relative_csf": V(0.3, "RECALLED", "most water is collagen-bound with sub-ms T2 (invisible at conventional TE)", None, (0.1, 0.5)),
        "T1_ms": {"3T": V(700, "RECALLED", "UTE-T1 of tendon ~ 600-800 ms; not opened", None, (500, 900))},
        "T2_ms": {"3T": V(11, "SECONDARY", "Qiao17: mono-exponential UTE T2* 11.1+/-0.3 ms (T2*, not CPMG T2)", None, (8, 15))},
        "ADC": V(1.0, "RECALLED", "tendon diffusion rarely measured; anisotropic", "um2/ms", (0.8, 1.4)),
    },
    components={"T2": {"kernel": "t2star_ute", "field_T": 3.0, "status": "SECONDARY",
                       "list": [C("short T2* (collagen-bound)", 0.8, 1.0, "SECONDARY", "Du12: short-T2* fraction up to 80.9 % (ligament); short T2* 0.3-2.9 ms across tissues", (0.5, 2.0)),
                                C("long T2* (free water)", 0.2, 15.0, "SECONDARY", "Du12; Qiao17 mono 11.1 ms", (8, 25))],
                       "functional": "short fraction (mass below 5 ms)", "functional_threshold": 5.0,
                       "typical_acquisition": {"n_echoes": 12, "dTE_ms": 0.5, "first_echo_snr": 40.0}}},
    theory={"pools": ["collagen-bound water (sub-ms)", "free/interfibrillar water", "peritendinous fluid partial volume", "collagen protons (T2 ~ 10s of us)"],
            "n_pools": 4, "exchange": "Bound/free exchange is fast relative to T1 but slow relative to the sub-ms/ms T2 split; magic-angle orientation dependence dominates the free pool's T2.",
            "n_apparent_T2": 2, "n_resolvable_clinical_T2": 2,
            "rationale": "A two-component UTE T2* case with ratio ~10 and a dominant short pool: the mirror image of the myelin problem (major short component), estimable when TE_1 < 0.5 ms."},
    sources=["Du12", "Qiao17"])

add(key="cortical_bone", organ="bone", tissue="cortical bone (femur / tibia)",
    properties={
        "water_content": V(0.12, "PRIMARY", "Woo86 Table I cortical bone 12.2 % by mass; Hor10 bound + pore water ~ 31-34 mol 1H/L (~ 15-20 % by volume)", "g/g", (0.10, 0.25)),
        "pd_relative_csf": V(0.05, "TERTIARY", "RK cortical bone 1-10", None, (0.01, 0.10)),
        "T1_ms": {"3T": V(306, "SECONDARY", "AR20 quoting prior work: free (pore) water T1 306 ms; bound water T1 ~ 100-150 ms", None, (100, 400))},
        "T2_ms": {"1.5T": V(0.45, "SECONDARY", "AR20: bound-water T2* 0.45 ms (quoted), free-water T2* 2.81+/-0.31 ms (T2*, not CPMG T2)", None, (0.3, 3.0))},
        "ADC": V(None, "RECALLED", "not measurable with conventional DWI", "um2/ms"),
    },
    components={"T2": {"kernel": "t2star_ute", "field_T": 4.7, "status": "PRIMARY",
                       "list": [C("collagen-bound water", 0.68, 0.42, "PRIMARY", "Hor10 CPMG: 416+/-35 us, 60.8+/-5.3 % (plus 57 us pool 16.1 %); FID T2* 736 us 57.7 %", (0.3, 0.75)),
                                C("pore water (and lipid)", 0.32, 5.0, "PRIMARY", "Hor10: 1-1000 ms long-lived, 23.0+/-6.5 % (~60 % pore water / 40 % lipid); AR20 free T2* 2.8 ms at 1.5 T", (1.0, 20.0))],
                       "functional": "bound-water fraction (mass below 1 ms)", "functional_threshold": 1.0,
                       "typical_acquisition": {"n_echoes": 12, "dTE_ms": 0.3, "first_echo_snr": 40.0},
                       "note": "fractions renormalised over the two water pools visible to UTE; Hor10 also sees a 57 us pool (16 %) and a collagen 12 us pool (34 % of FID) that only solid-state methods reach"}},
    theory={"pools": ["collagen-bound water (~0.4 ms)", "pore water in Haversian/lacunar-canalicular space (1-1000 ms, itself distributed by pore size)", "lipid in pores", "collagen backbone protons (~12 us)", "a 57 us pool (Hor10; assignment debated)"],
            "n_pools": 5, "exchange": "Pore and bound water do not exchange on the T2 scale; pore water T2 is a size distribution, not one value.",
            "n_apparent_T2": 3, "n_resolvable_clinical_T2": 2,
            "rationale": "Well-separated (ratio > 10) but both pools are sub-10 ms and need UTE/ZTE; the continuous pore-size distribution makes the pore component a spectrum, the charter's continuum form in miniature."},
    sources=["Hor10", "AR20", "Du12"])

add(key="bone_marrow_vertebral", organ="bone", tissue="vertebral (red / haematopoietic) bone marrow",
    properties={
        "water_content": V(0.35, "SECONDARY", "Woo86 Table I red marrow 39.7 %, yellow marrow 15.3 %; lumbar marrow of young adults is ~ 2/3 water-signal (LeS16 FF 33 %), i.e. between the two compositions", "g/g", (0.28, 0.40)),
        "pd_relative_csf": V(0.85, "RECALLED", "water + fat protons both visible", None, (0.7, 0.95)),
        "T1_ms": {"1.5T": V(701, "PRIMARY", "LeS16 Table 1: T1 water 701+/-151, T1 fat 334+/-113 (1.5 T, Dixon two flip angles); dB04 bulk 549+/-52", None, (334, 850)),
                  "3T": V(586, "PRIMARY", "dB04 Table 1 L4 vertebra 586+/-73 at 3 T (549+/-52 at 1.5 T); bulk, fat-dominated", None, (500, 700))},
        "T2_ms": {"1.5T": V(49, "PRIMARY", "dB04 Table 2 L4 vertebra 49+/-8 at 1.5 T; LeS16 T2* water 13.7+/-2.9, fat 11.4+/-2.7 (T2*, 1.5 T)", None, (40, 60)),
                  "3T": V(49, "PRIMARY", "dB04 Table 2 L4 vertebra 49+/-4 at 3 T", None, (40, 60))},
        "ADC": V(0.4, "TERTIARY", "MRM-web marrow 0.20-0.60", "um2/ms", (0.2, 0.6)),
    },
    components={"T2": {"kernel": "t2_cpmg", "field_T": 1.5, "status": "SECONDARY",
                       "list": [C("haematopoietic/water", 0.67, 45.0, "SECONDARY", "LeS16 Table 1 water fraction 67 % (PRIMARY); T2 of marrow water ~ 40-60 ms is inferred from bulk 49 (dB04) and T2* 13.7", (35, 60)),
                                C("fat (methylene)", 0.33, 130.0, "SECONDARY", "LeS16 Table 1 FF 33+/-8 % (PRIMARY); fat T2 sequence-dependent: Gold04 T2-prep marrow fat 165 (1.5 T) / 133 (3 T), dB04 SSFSE subcutaneous fat 58 / 68", (58, 165))],
                       "functional": "fat fraction (1 - mass below 75 ms)", "functional_threshold": 75.0,
                       "typical_acquisition": CPMG_REF,
                       "note": "fat and water are chemically shifted; Dixon separates them far better than T2 — this entry is a T2-only stress test"}},
    theory={"pools": ["haematopoietic cell water", "adipocyte lipid (multiple resonances: methylene, methyl, olefinic)", "trabecular-bone-adjacent water (susceptibility broadened)", "sinusoidal blood (~5-10 %)"],
            "n_pools": 4, "exchange": "Fat and water do not exchange; the fat pool is itself multi-resonance (chemical shift, not relaxation).",
            "n_apparent_T2": 2, "n_resolvable_clinical_T2": 1,
            "rationale": "A ratio ~2 two-component case at the resolvability floor (delta ~ 2.7 at SNR 100): T2 alone should fail and chemical shift should be used — a deliberate 'wrong tool' row for the harness."},
    sources=["LeS16", "dB04", "Han03"])

# ==============================================================================================
# THORAX / VASCULAR
# ==============================================================================================
add(key="myocardium", organ="heart", tissue="left-ventricular myocardium",
    properties={
        "water_content": V(0.76, "PRIMARY", "Woo86 Table I heart 2: 75.9 % (compositions 1-3: 71.0 / 75.9 / 80.9 %; blood-filled 77.7 %)", "g/g", (0.71, 0.81)),
        "pd_relative_csf": V(0.85, "RECALLED", "", None, (0.8, 0.9)),
        "T1_ms": {"1.5T": V(1030, "SECONDARY", "St05 (mouse heart 1030+/-34); in vivo MOLLI ~950-1000 (RECALLED)", None, (950, 1050)),
                  "3T": V(1170, "SECONDARY", "vKB13 MOLLI 1157-1181 base->apex; St05 1471+/-31 (mouse); Boj17 1116-1341", None, (1116, 1341))},
        "T2_ms": {"1.5T": V(52, "SECONDARY", "Giri09 52.2 (quoted in vKB13); St05 mouse 40+/-6", None, (40, 55)),
                  "3T": V(45, "SECONDARY", "vKB13 44.1-46.9; St05 47+/-11; Boj17 39-67", None, (39, 67))},
        "ADC": V(0.89, "SECONDARY", "McG15 MD 0.89+/-0.06, FA 0.42+/-0.03 (3 T DW-STEAM)", "um2/ms", (0.8, 1.0)),
    },
    components={"T2": {"kernel": "t2_cpmg", "field_T": 1.5, "status": "SECONDARY",
                       "list": [C("myocardial water", 1.0, 48.0, "SECONDARY", "Giri09/vKB13 mono-exponential 44-52 ms", (42, 55))],
                       "functional": "T2 (mono-exponential)", "functional_threshold": None,
                       "typical_acquisition": {"n_echoes": 8, "dTE_ms": 12.0, "first_echo_snr": 60.0}},
                "diffusion": {"kernel": "diffusion_tensor", "field_T": 3.0, "status": "SECONDARY",
                       "list": [C("tensor: mean diffusivity", 1.0, 0.89, "SECONDARY", "McG15 MD 0.89 (epi 0.87, meso 0.89, endo 0.91)", (0.85, 0.95))],
                       "functional": "fractional anisotropy (0.42)", "functional_threshold": None,
                       "typical_acquisition": {"b_values_s_per_mm2": [150, 750], "directions": 6, "first_echo_snr": 20.0}}},
    theory={"pools": ["myocyte intracellular water", "interstitial water", "capillary/vascular blood (~10 % of myocardial volume)", "blood-pool partial volume at endocardium", "epicardial fat partial volume"],
            "n_pools": 5, "exchange": "Intra/extracellular exchange is fast enough at clinical TE that myocardium fits as mono-exponential; the vascular pool (~10 %, T2 ~ 100-250 ms depending on oxygenation) is the candidate second component that oedema/haemorrhage/iron perturb.",
            "n_apparent_T2": 2, "n_resolvable_clinical_T2": 1,
            "rationale": "K = 1 null case at clinical echo counts (8 x 12 ms): any method reporting two components here is fitting noise unless SNR and echo count are raised substantially."},
    sources=["vKB13", "Giri09", "St05", "McG15", "Boj17"])

add(key="blood_arterial", organ="vascular", tissue="arterial blood (Hct ~ 0.42, Y ~ 0.98)",
    properties={
        "water_content": V(0.79, "PRIMARY", "Woo86 Table I whole blood 79.0 % (plasma 91.9 %, erythrocytes 64.0 %)", "g/g", (0.77, 0.83)),
        "pd_relative_csf": V(0.85, "TERTIARY", "RK blood 85", None, (0.8, 0.9)),
        "T1_ms": {"1.5T": V(1441, "SECONDARY", "St05 (human in vitro 1441+/-120); Roo07 fit 1550", None, (1350, 1600)),
                  "3T": V(1932, "SECONDARY", "St05 (1932+/-85); Roo07 fit 1961", None, (1650, 2000))},
        "T2_ms": {"1.5T": V(290, "SECONDARY", "St05 (oxygenated in vitro 290+/-30); venous 50-200 depending on Y (Wikipedia tertiary)", None, (150, 300)),
                  "3T": V(275, "SECONDARY", "St05 (275+/-50); venous much shorter", None, (100, 275))},
        "ADC": V(3.0, "RECALLED", "free-water-like plus flow; Funck 2018 not opened", "um2/ms", (2.5, 3.5)),
    },
    components={"T2": {"kernel": "t2_cpmg", "field_T": 1.5, "status": "SECONDARY",
                       "list": [C("blood water (plasma + RBC, fast exchange)", 1.0, 250.0, "SECONDARY", "St05 290 in vitro; in vivo arterial ~ 200-250 (RECALLED)", (150, 300))],
                       "functional": "T2 (mono-exponential; oxygenation via Luz-Meiboom)", "functional_threshold": None,
                       "typical_acquisition": {"n_echoes": 32, "dTE_ms": 10.0, "first_echo_snr": 60.0}}},
    theory={"pools": ["plasma water", "erythrocyte intracellular water"],
            "n_pools": 2, "exchange": "Plasma-RBC water exchange ~ 10 ms is fast relative to the T2 difference: one apparent component whose T2 depends on oxygenation and echo spacing (Luz-Meiboom), i.e. a CPMG-spacing-dependent 'T2' — a model-misspecification case rather than a K > 1 case.",
            "n_apparent_T2": 1, "n_resolvable_clinical_T2": 1,
            "rationale": "K = 1 physically but with echo-spacing dependence; the partial-volume contaminant for kidney, spleen, liver and myocardium entries."},
    sources=["St05", "Roo07"])

# ==============================================================================================
# ABDOMEN
# ==============================================================================================
add(key="liver", organ="liver", tissue="parenchyma (normal iron, no steatosis)",
    properties={
        "water_content": V(0.745, "PRIMARY", "Woo86 Table I liver 2: 74.5 % (compositions 1-3: 72.8 / 74.5 / 75.6 %)", "g/g", (0.728, 0.756)),
        "pd_relative_csf": V(0.90, "TERTIARY", "RK"),
        "T1_ms": {"1.5T": V(586, "PRIMARY", "dB04 Table 1 586+/-39 (human in vivo); St05 mouse 576+/-30", None, (550, 620)),
                  "3T": V(809, "PRIMARY", "dB04 Table 1 809+/-71; St05 812+/-64", None, (750, 870))},
        "T2_ms": {"1.5T": V(46, "PRIMARY", "dB04 Table 2 46+/-6 (human in vivo); St05 46+/-6", None, (40, 55)),
                  "3T": V(34, "PRIMARY", "dB04 Table 2 34+/-4; St05 42+/-3", None, (30, 45))},
        "ADC": V(1.39, "PRIMARY", "Luc08 Table 4: 1.39+/-0.2 (b up to 800); EJR20 1.65+/-0.44; MRM-web 0.6-1.1", "um2/ms", (1.0, 1.7)),
    },
    components={
        "T2": {"kernel": "t2_cpmg", "field_T": 1.5, "status": "THEORY",
               "list": [C("hepatocellular water", 0.78, 42.0, "THEORY", "bulk T2 (St05/dB04); fraction = 1 - IVIM perfusion fraction (Luc08 f 0.27; Li17 0.22)", (35, 50)),
                        C("sinusoidal blood / bile", 0.22, 150.0, "THEORY", "vascular fraction from IVIM f (0.22-0.27); T2 of partially deoxygenated blood 100-200 ms", (100, 250))],
               "functional": "vascular/long-T2 fraction (1 - mass below 90 ms)", "functional_threshold": 90.0,
               "typical_acquisition": {"n_echoes": 16, "dTE_ms": 8.0, "first_echo_snr": 60.0},
               "note": "no in vivo multi-component liver T2 study reached (Ber83 ex vivo biexponential, no values); the split is a working configuration from IVIM and bulk T2"},
        "diffusion": {"kernel": "diffusion_ivim", "field_T": 1.5, "status": "PRIMARY",
               "list": [C("tissue diffusion D", 0.73, 1.10, "PRIMARY", "Luc08 Table 4: D 1.10+/-0.7, f 27.0+/-5.3 %; Li17 pooled D 1.09, f 22.4 %; Yam99 D 0.72", (0.9, 1.3)),
                        C("pseudo-diffusion D*", 0.27, 79.1, "PRIMARY", "Luc08: D* 79.1+/-18.1; Li17 pooled 70.6", (50, 100))],
               "functional": "perfusion fraction f", "functional_threshold": 10.0,
               "typical_acquisition": {"b_values_s_per_mm2": [0, 10, 20, 30, 50, 80, 100, 200, 400, 800], "first_echo_snr": 50.0}},
    },
    theory={"pools": ["hepatocyte cytoplasmic water", "sinusoidal blood (large: ~ 25 % of volume, hence IVIM f 0.2-0.3)", "bile canalicular/ductal fluid (~ 1-2 %)", "Kupffer/endothelial cell water", "lipid droplets in steatosis (0-30 %)", "iron-loaded cells (shorten T2 drastically)"],
            "n_pools": 6, "exchange": "Hepatocyte-sinusoid water exchange across fenestrated endothelium is fast (tens of ms), so the blood pool is partially averaged into the parenchymal T2; steatosis adds a chemically shifted fat pool; iron collapses T2 (T2* especially).",
            "n_apparent_T2": 2, "n_resolvable_clinical_T2": 1,
            "rationale": "The large vascular fraction is the physical reason liver ADC is IVIM-biexponential; on the T2 axis the same pool is partially exchange-averaged and only a long tail survives — a good test of whether T2 and diffusion compartment fractions agree (they need not)."},
    sources=["St05", "dB04", "Luc08", "Li17", "Yam99", "Ber83"])

add(key="spleen", organ="spleen", tissue="splenic parenchyma",
    properties={
        "water_content": V(0.787, "PRIMARY", "Woo86 Table I spleen 78.7 %", "g/g", (0.76, 0.80)),
        "pd_relative_csf": V(0.90, "TERTIARY", "RK"),
        "T1_ms": {"1.5T": V(1057, "PRIMARY", "dB04 Table 1 1057+/-42", None, (1000, 1100)),
                  "3T": V(1328, "PRIMARY", "dB04 Table 1 1328+/-31", None, (1250, 1400))},
        "T2_ms": {"1.5T": V(79, "PRIMARY", "dB04 Table 2 79+/-15", None, (65, 95)),
                  "3T": V(61, "PRIMARY", "dB04 Table 2 61+/-9", None, (52, 70))},
        "ADC": V(0.85, "SECONDARY", "EJR20 0.85 (SD anomalous); Yam99 IVIM D 0.80; MRM-web n/a", "um2/ms", (0.7, 1.0)),
    },
    components={"T2": {"kernel": "t2_cpmg", "field_T": 1.5, "status": "THEORY",
                       "list": [C("red-pulp / cellular water", 0.65, 65.0, "THEORY", "bulk T2 (dB04 61 at 3 T)", (55, 80)),
                                C("sinusoidal / venous blood", 0.35, 130.0, "THEORY", "spleen is ~ 30-40 % blood by volume; venous T2 100-150 ms at 1.5 T", (90, 180))],
                       "functional": "blood/long-T2 fraction (1 - mass below 95 ms)", "functional_threshold": 95.0,
                       "typical_acquisition": {"n_echoes": 16, "dTE_ms": 8.0, "first_echo_snr": 60.0},
                       "note": "no multi-component spleen relaxometry reached in the literature search; working configuration"}},
    theory={"pools": ["red-pulp cord cells and macrophages", "sinusoidal blood (very high blood volume)", "white-pulp lymphoid tissue", "fibrous trabeculae"],
            "n_pools": 4, "exchange": "Open circulation: cell water and blood exchange freely; splenic T2 is strongly oxygenation- and blood-volume-dependent (splenic contraction). Likely close to mono-exponential with a long blood tail.",
            "n_apparent_T2": 2, "n_resolvable_clinical_T2": 1,
            "rationale": "Ratio ~2 between the working components: at the resolvability floor, so the T2 axis will report K = 1; the IVIM axis is where the blood pool shows."},
    sources=["dB04", "Yam99", "EJR20"])

add(key="kidney_cortex", organ="kidney", tissue="renal cortex",
    properties={
        "water_content": V(0.77, "PRIMARY", "Woo86 Table I kidney 2: 76.6 % (whole kidney; compositions 1-3: 72.3 / 76.6 / 80.5 %)", "g/g", (0.723, 0.805)),
        "pd_relative_csf": V(0.95, "TERTIARY", "RK"),
        "T1_ms": {"1.5T": V(966, "PRIMARY", "dB04 Table 1 cortex 966+/-58 (human in vivo); St05 rat whole kidney 690+/-30", None, (690, 1000)),
                  "3T": V(1142, "PRIMARY", "dB04 Table 1 cortex 1142+/-154; St05 rat whole 1194+/-27", None, (1000, 1250))},
        "T2_ms": {"1.5T": V(87, "PRIMARY", "dB04 Table 2 cortex 87+/-4 (human in vivo); St05 rat whole kidney 55+/-3", None, (55, 95)),
                  "3T": V(76, "PRIMARY", "dB04 Table 2 cortex 76+/-7", None, (65, 85))},
        "ADC": V(2.0, "SECONDARY", "vBa17 cortex D 2.04+/-0.08 (bi-exp); Fil15 D 1.7, ADC MRM-web 1.5-2.5", "um2/ms", (1.7, 2.3)),
    },
    components={
        "T2": {"kernel": "t2_cpmg", "field_T": 3.0, "status": "THEORY",
               "list": [C("tubular epithelium + interstitium", 0.75, 70.0, "THEORY", "bulk T2 (dB04 76)", (60, 85)),
                        C("tubular lumen fluid + glomerular capillary blood", 0.25, 200.0, "THEORY", "IVIM f 0.10-0.21 (vBa17, Fil15) plus tubular fluid; Tas24 uses the long-T2 amplitude as a tubule-volume surrogate", (150, 300))],
               "functional": "tubular/vascular long-T2 fraction (1 - mass below 120 ms)", "functional_threshold": 120.0,
               "typical_acquisition": {"n_echoes": 16, "dTE_ms": 8.0, "first_echo_snr": 60.0},
               "note": "in vivo human multi-component renal T2 not reached; Tas24 (rat, 9.4 T) supports a biexponential structure; working configuration"},
        "diffusion": {"kernel": "diffusion_ivim", "field_T": 3.0, "status": "SECONDARY",
               "list": [C("tissue diffusion D", 0.85, 2.04, "SECONDARY", "vBa17 cortex D 2.04+/-0.08, f 9.7+/-1.7 %; Fil15 D 1.7, f 20.9 %", (1.7, 2.1)),
                        C("pseudo-diffusion D*", 0.15, 15.6, "SECONDARY", "Fil15 D* 15.6+/-6.5", (10, 40))],
               "functional": "perfusion fraction f", "functional_threshold": 8.0,
               "typical_acquisition": {"b_values_s_per_mm2": [0, 10, 25, 40, 75, 100, 200, 300, 500, 700], "first_echo_snr": 40.0}},
    },
    theory={"pools": ["proximal/distal tubular epithelial cell water", "tubular lumen filtrate (fast-flowing free fluid)", "peritubular interstitium", "glomerular and peritubular capillary blood (high renal blood flow; f ~ 0.1-0.2)", "Bowman's space filtrate"],
            "n_pools": 5, "exchange": "Aquaporin-rich epithelium makes lumen-cell water exchange fast (ms), so tubular fluid is largely averaged into the parenchymal T2; blood and free fluid contribute a long tail; directional tubular flow gives the medulla its diffusion anisotropy.",
            "n_apparent_T2": 2, "n_resolvable_clinical_T2": 1,
            "rationale": "Physiologically the most compartmentalised abdominal organ, yet fast water exchange hides it on T2; the documented multi-exponential signal is in diffusion (IVIM, with the fluid/flow component) and in rat T2 at 9.4 T. A strong test case for 'exchange-coupled' ground truth (charter §6.1)."},
    sources=["dB04", "St05", "vBa17", "Fil15", "Tas24"])

add(key="kidney_medulla", organ="kidney", tissue="renal medulla",
    properties={
        "water_content": V(0.80, "THEORY", "Woo86 gives whole kidney only (72.3-80.5 %); medulla placed at the wet end", "g/g", (0.77, 0.83)),
        "pd_relative_csf": V(0.95, "TERTIARY", "RK (kidney)"),
        "T1_ms": {"1.5T": V(1412, "PRIMARY", "dB04 Table 1 medulla 1412+/-58", None, (1300, 1500)),
                  "3T": V(1545, "PRIMARY", "dB04 Table 1 medulla 1545+/-142", None, (1400, 1700))},
        "T2_ms": {"1.5T": V(85, "PRIMARY", "dB04 Table 2 medulla 85+/-11", None, (75, 100)),
                  "3T": V(81, "PRIMARY", "dB04 Table 2 medulla 81+/-8", None, (70, 90))},
        "ADC": V(1.93, "SECONDARY", "vBa17 medulla D 1.93+/-0.08; MRM-web 1.8-2.2", "um2/ms", (1.8, 2.2)),
    },
    components={"T2": {"kernel": "t2_cpmg", "field_T": 3.0, "status": "THEORY",
                       "list": [C("tubular epithelium (loops, collecting ducts) + interstitium", 0.70, 75.0, "THEORY", "bulk T2 (dB04 81)", (65, 90)),
                                C("luminal fluid (loops of Henle, collecting ducts) + vasa recta blood", 0.30, 220.0, "THEORY", "vBa17 medullary f 15.8 %; larger luminal fraction than cortex", (150, 300))],
                       "functional": "luminal/vascular long-T2 fraction (1 - mass below 120 ms)", "functional_threshold": 120.0,
                       "typical_acquisition": {"n_echoes": 16, "dTE_ms": 8.0, "first_echo_snr": 50.0}},
                "diffusion": {"kernel": "diffusion_ivim", "field_T": 3.0, "status": "SECONDARY",
                       "list": [C("tissue diffusion D", 0.84, 1.93, "SECONDARY", "vBa17 medulla D 1.93+/-0.08, f 15.8+/-2.8 %", (1.8, 2.1)),
                                C("pseudo-diffusion D*", 0.16, 20.0, "RECALLED", "medullary D* not on an opened page; cortex 15.6 (Fil15)", (10, 40))],
                       "functional": "perfusion fraction f", "functional_threshold": 8.0,
                       "typical_acquisition": {"b_values_s_per_mm2": [0, 10, 25, 40, 75, 100, 200, 300, 500, 700], "first_echo_snr": 40.0}}},
    theory={"pools": ["loop-of-Henle and collecting-duct epithelium", "luminal fluid in radially oriented tubules (directional flow)", "vasa recta blood (countercurrent)", "hypertonic interstitium"],
            "n_pools": 4, "exchange": "As cortex, with a larger luminal fraction and radial orientation: diffusion is anisotropic, T2 slightly longer, T1 longer (higher water content, hypertonicity).",
            "n_apparent_T2": 2, "n_resolvable_clinical_T2": 1,
            "rationale": "Companion row to the cortex; the medulla/cortex difference is the clinically used contrast (corticomedullary differentiation), so the dictionary must carry both."},
    sources=["dB04", "vBa17"])

add(key="pancreas", organ="pancreas", tissue="pancreatic parenchyma",
    properties={
        "water_content": V(0.733, "PRIMARY", "Woo86 Table I pancreas 73.3 % (lipid 12.8 %); fat infiltration increases with age", "g/g", (0.65, 0.78)),
        "pd_relative_csf": V(0.85, "RECALLED", "", None, (0.8, 0.9)),
        "T1_ms": {"1.5T": V(584, "PRIMARY", "dB04 Table 1 584+/-14", None, (550, 650)),
                  "3T": V(725, "PRIMARY", "dB04 Table 1 725+/-71", None, (650, 800))},
        "T2_ms": {"1.5T": V(46, "PRIMARY", "dB04 Table 2 46+/-6", None, (40, 55)),
                  "3T": V(43, "PRIMARY", "dB04 Table 2 43+/-7", None, (36, 50))},
        "ADC": V(1.86, "SECONDARY", "Ser24 ADC 1.86 (1.66-2.06); Mayer 2021 D 1.5", "um2/ms", (1.5, 2.1)),
    },
    components={"T2": {"kernel": "t2_cpmg", "field_T": 3.0, "status": "THEORY",
                       "list": [C("acinar/ductal cell water", 0.78, 45.0, "THEORY", "bulk T2 (dB04 43)", (38, 55)),
                                C("capillary blood + ductal fluid", 0.22, 160.0, "THEORY", "IVIM f 0.21-0.40 (May21, Ser24, Klauss 2016 20.7 %)", (100, 250))],
                       "functional": "vascular/long-T2 fraction (1 - mass below 90 ms)", "functional_threshold": 90.0,
                       "typical_acquisition": {"n_echoes": 16, "dTE_ms": 8.0, "first_echo_snr": 50.0},
                       "note": "no multi-component pancreatic T2 study reached; working configuration"},
                "diffusion": {"kernel": "diffusion_ivim", "field_T": 1.5, "status": "SECONDARY",
                       "list": [C("tissue diffusion D", 0.70, 1.19, "SECONDARY", "Ser24 D 1.19 (1.08-1.30), f 0.40; May21 D 1.5, f 0.211; Klauss 2016 f 0.207", (1.1, 1.5)),
                                C("pseudo-diffusion D*", 0.30, 20.0, "SECONDARY", "Ser24 D* 18.5; May21 21.9", (15, 25))],
                       "functional": "perfusion fraction f", "functional_threshold": 8.0,
                       "typical_acquisition": {"b_values_s_per_mm2": [0, 10, 20, 50, 100, 200, 400, 600, 1000], "first_echo_snr": 40.0}}},
    theory={"pools": ["acinar cell water (protein-rich, short T1)", "ductal fluid", "capillary blood (high perfusion: f 0.2-0.4)", "interlobular fat (increases with age/obesity)"],
            "n_pools": 4, "exchange": "Cell-capillary exchange fast; fat is a chemically shifted non-exchanging pool; perfusion dominates the IVIM signal.",
            "n_apparent_T2": 2, "n_resolvable_clinical_T2": 1,
            "rationale": "Perfusion-rich organ with a short bulk T2: the IVIM axis carries the compartment information; on T2 the organ is near mono-exponential unless fat infiltration is present."},
    sources=["dB04", "Ser24", "May21"])

# ==============================================================================================
# PELVIS / BREAST
# ==============================================================================================
add(key="prostate_pz", organ="prostate", tissue="peripheral zone, normal",
    properties={
        "water_content": V(0.833, "PRIMARY", "Woo86 Table I prostate 83.3 % (whole gland)", "g/g", (0.78, 0.86)),
        "pd_relative_csf": V(0.85, "RECALLED", "", None, (0.8, 0.95)),
        "T1_ms": {"1.5T": V(1317, "PRIMARY", "dB04 Table 1 whole gland 1317+/-85", None, (1200, 1450)),
                  "3T": V(1597, "PRIMARY", "dB04 Table 1 whole gland 1597+/-42; Boj17 1400-1700", None, (1400, 1700))},
        "T2_ms": {"1.5T": V(88, "PRIMARY", "dB04 Table 2 whole gland 88 (SD reported as 0); PZ alone is longer, ~ 100-130 (RECALLED)", None, (85, 140)),
                  "3T": V(74, "PRIMARY", "dB04 Table 2 whole gland 74+/-9 (PZ alone is longer, ~ 100-120 RECALLED)", None, (70, 130))},
        "ADC": V(1.6, "TERTIARY", "MRM-web prostate 1.4-1.8", "um2/ms", (1.4, 1.9)),
    },
    components={"T2": {"kernel": "t2_cpmg", "field_T": 3.0, "status": "RECALLED",
                       "list": [C("epithelial / stromal water", 0.65, 60.0, "RECALLED", "Sab17 T2short (values not reachable this session)", (40, 90)),
                                C("luminal water", 0.35, 500.0, "RECALLED", "Sab17 T2long / LWF; LWF correlates with luminal space (JMRI 46:861, rho 0.75) and falls with Gleason grade (rho -0.78)", (300, 800))],
                       "functional": "luminal water fraction (1 - mass below 200 ms)", "functional_threshold": 200.0,
                       "typical_acquisition": {"n_echoes": 64, "dTE_ms": 8.0, "first_echo_snr": 80.0},
                       "note": "the strongest clinically validated two-component T2 case; component numbers still RECALLED pending the full text"}},
    theory={"pools": ["glandular lumen fluid (secretions; large in normal PZ)", "epithelial cell water", "stromal (smooth muscle/fibrous) water", "vascular blood"],
            "n_pools": 4, "exchange": "Lumen-epithelium exchange is slow relative to the large T2 difference (ratio ~ 8), so two components persist; stroma and epithelium share T2 and coalesce. Cancer replaces lumen with cells -> LWF falls.",
            "n_apparent_T2": 2, "n_resolvable_clinical_T2": 2,
            "rationale": "Well-separated, both fractions large: the easy case, estimable to ~5 % on the LWF with a 64-echo train — the positive control for every estimator."},
    sources=["Sab17", "dB04", "Boj17"])

add(key="breast_fibroglandular", organ="breast", tissue="fibroglandular tissue (with fat partial volume)",
    properties={
        "water_content": V(0.51, "PRIMARY", "Woo86 Table I mammary gland 2: 51.4 % (compositions 1-3: 30.2 / 51.4 / 72.6 % water with 56.2 / 30.9 / 5.6 % lipid — fatty / mixed / glandular)", "g/g", (0.30, 0.73)),
        "pd_relative_csf": V(0.8, "RECALLED", "", None, (0.7, 0.95)),
        "T1_ms": {"1.5T": V(1266, "SECONDARY", "RP06 via Keenan 2016: fibroglandular 1266+/-82; fat 296+/-13", None, (1100, 1400)),
                  "3T": V(1445, "SECONDARY", "RP06 via Keenan/Boj17: 1445+/-93; fat 367+/-8", None, (1300, 1550))},
        "T2_ms": {"1.5T": V(57.5, "SECONDARY", "RP06: 57.5+/-10.2; fat 53.3+/-2.1", None, (45, 70)),
                  "3T": V(54.4, "SECONDARY", "RP06: 54.4+/-9.4; fat 53.0+/-1.5", None, (45, 65))},
        "ADC": V(1.5, "TERTIARY", "MRM-web glandular 1.2-1.8", "um2/ms", (1.2, 1.8)),
    },
    components={"T2": {"kernel": "t2_cpmg", "field_T": 1.5, "status": "SECONDARY",
                       "list": [C("fibroglandular water", 0.6, 57.0, "SECONDARY", "RP06 57.5 (1.5 T)", (45, 70)),
                                C("fat (methylene)", 0.4, 110.0, "SECONDARY", "RP06 breast fat T2 53 (short, spin-echo w/ J-coupling); Gold04 subcutaneous fat 165 (1.5 T, T2-prep); dB04 58 / 68 (SSFSE, 1.5 / 3 T) — CPMG fat T2 is sequence-dependent", (53, 165))],
                       "functional": "fat fraction (1 - mass below 80 ms)", "functional_threshold": 80.0,
                       "typical_acquisition": CPMG_REF,
                       "note": "fat T2 under CPMG depends on echo spacing (J-coupling); Dixon is the right tool — a deliberate 'wrong tool' row like marrow"}},
    theory={"pools": ["ductal/lobular epithelial water", "fibrous stroma water", "ductal fluid", "adipose lipid (multi-resonance)", "vascular"],
            "n_pools": 5, "exchange": "Water pools coalesce; fat is non-exchanging and chemically shifted; the apparent two-component T2 is a water/fat mixture, not two water pools.",
            "n_apparent_T2": 2, "n_resolvable_clinical_T2": 1,
            "rationale": "Ratio ~2 with sequence-dependent fat T2: at the resolvability floor and misspecified for a pure-exponential kernel; belongs in the harness as a failure-mode row."},
    sources=["RP06", "Han03", "dB04"])

# ==============================================================================================
# ADIPOSE TISSUE (added v2.1)
# ==============================================================================================
add(key="adipose_tissue", organ="adipose", tissue="subcutaneous white adipose tissue",
    properties={
        "water_content": V(0.21, "PRIMARY", "Woo86 Table I adipose tissue 2: 21.2 % (compositions 1-3: 30.5 / 21.2 / 11.4 % water with 61.4 / 74.1 / 87.3 % lipid)", "g/g", (0.114, 0.305)),
        "pd_relative_csf": V(0.95, "TERTIARY", "RK fat 90-100 (water + lipid protons both visible; lipid proton density per gram ~ 0.9 of water's)", None, (0.85, 1.0)),
        "T1_ms": {"1.5T": V(288, "PRIMARY", "Gold04 Table subcutaneous fat 288+/-8 (marrow fat 288+/-5); dB04 Table 1 343+/-37", None, (280, 380)),
                  "3T": V(371, "PRIMARY", "Gold04 371+/-8 (marrow fat 365+/-9); dB04 382+/-13; Boj17 review 346-450 across IR methods", None, (346, 450))},
        "T2_ms": {"1.5T": V(165, "PRIMARY", "Gold04 T2-prep 165+/-6; dB04 SSFSE multi-TE 58+/-4 — the spread is the sequence dependence of fat T2 (J-coupling, Hen92), not disagreement", None, (58, 165)),
                  "3T": V(133, "PRIMARY", "Gold04 T2-prep 133+/-4; dB04 SSFSE 68+/-4; Boj17 Table 2a: 41 (single SE) to 154 (16-echo CPMG) and 371 (hybrid SE) by sequence", None, (41, 371))},
        "ADC": V(0.15, "RECALLED", "triglyceride self-diffusion is ~ 10x slower than water; fat ADC 0.05-0.3 reported in Dixon-suppressed and fat-only DWI; not opened", "um2/ms", (0.05, 0.3)),
    },
    components={"T2": {"kernel": "t2_cpmg", "field_T": 1.5, "status": "THEORY",
                       "list": [C("adipocyte / interstitial water", 0.10, 40.0, "THEORY", "Woo86 water 11-31 % by mass -> ~ 8-25 % of visible protons; T2 of the water fraction of adipose tissue not reached; placed at 30-60 ms", (30, 60)),
                                C("triglyceride protons (methylene-dominated, J-coupled)", 0.90, 140.0, "SECONDARY", "Gold04 bulk T2-prep 165 (1.5 T) / 133 (3 T); Boj17 CPMG-type values 103-154 at 3 T; fraction from Woo86 composition 2 converted to proton fraction (~ 0.9)", (100, 165))],
                       "functional": "water fraction (mass below 75 ms)", "functional_threshold": 75.0,
                       "typical_acquisition": CPMG_REF,
                       "note": "fat is not an exponential family under CPMG: homonuclear J-coupling makes the methylene decay depend on echo spacing (41 ms single SE vs 120-165 ms short-spacing CPMG), and the six-line chemical-shift spectrum (Ham11) makes chemical-shift-encoded (Dixon/IDEAL) modelling the correct tool — a deliberate misspecification row, and the source of the fat partial-volume pool in marrow, breast, pancreas and muscle"}},
    theory={"pools": ["adipocyte triglyceride: methylene (CH2)n, ~ 70 % of lipid protons", "other triglyceride resonances (methyl, olefinic, alpha/beta-carboxyl, glycerol, diallylic) ~ 30 % — the six-peak model",
                      "adipocyte cytoplasmic water (thin rim around the lipid droplet)", "interstitial / stromal water and capillary blood", "collagenous septa (short T2, invisible at clinical TE)"],
            "n_pools": 5, "exchange": "Lipid and water protons do not exchange; the lipid resonances are separated by chemical shift (up to ~ 5 ppm), not by relaxation, and their CPMG decay is modulated by J-coupling so the apparent fat T2 depends on echo spacing and refocusing quality (Hen92).",
            "n_apparent_T2": 2, "n_resolvable_clinical_T2": 1,
            "rationale": "A ~ 90/10 lipid/water mixture whose dominant component is not a fixed exponential: the right model is chemical-shift-encoded with a single fat T2*, and any multi-exponential T2 fit is misspecified by construction. In the harness this row tests the model-misspecification axis (charter §6.1), not K; PDFF is its functional."},
    sources=["Woo86", "Gold04", "dB04", "Boj17", "Hen92", "Ham11"])

# ==============================================================================================
# FAT CONTENT (added v2.1) — two numbers per entry, because they are not the same quantity:
#   lipid_mass_fraction : chemical lipid by mass (Woodard & White 1986 Table I, PRIMARY). Includes membrane
#                         phospholipid and cholesterol, which have T2 < 1 ms and are invisible to water-fat imaging.
#   pdff                : MR proton-density fat fraction = mobile triglyceride protons / all MR-visible protons,
#                         the quantity Dixon/IDEAL/MRS measure and the clinical steatosis biomarker.
# Pathology axis note (charter §6.1): hepatic steatosis is graded on PDFF (Szc05 normal < 5.56 %; Tang13 grade
# thresholds ~ 6.4 / 17.4 / 22.1 %); pancreatic, muscular and myocardial fat rise with obesity and age; marrow FF
# rises with age and falls with infiltration. Pathological variants are not entries yet (dictionary §6).
# ==============================================================================================
FAT = {
    "brain_wm":            (V(0.181, "PRIMARY", "Woo86 WM lipid 18.1 % (assumed 50 % sphingomyelin, 25 % cerebroside, 25 % cholesterol — membrane lipid)", "g/g"),
                            V(0.0, "THEORY", "membrane lipid is MR-invisible at TE >= 1 ms; water-fat decomposition of normal brain returns PDFF ~ 0", None, (0.0, 0.01))),
    "brain_gm":            (V(0.053, "PRIMARY", "Woo86 GM lipid 5.3 % (membrane lipid)", "g/g"),
                            V(0.0, "THEORY", "as WM: membrane lipid invisible; PDFF ~ 0", None, (0.0, 0.01))),
    "csf":                 (V(0.0, "PRIMARY", "Woo86 CSF: no lipid", "g/g"), V(0.0, "PRIMARY", "no lipid", None)),
    "spinal_cord_wm":      (V(0.18, "THEORY", "as brain WM (Woo86 18.1 %)", "g/g"), V(0.0, "THEORY", "as brain WM", None, (0.0, 0.01))),
    "skeletal_muscle":     (V(0.042, "PRIMARY", "Woo86 skeletal muscle 2: 4.2 % (compositions 1-3: 6.8 / 4.2 / 1.6 %)", "g/g", (0.016, 0.068)),
                            V(0.03, "RECALLED", "PDFF-lit: healthy thigh/calf muscle PDFF ~ 1-5 % (intra- plus extramyocellular lipid); rises to 10-50 % in dystrophy and sarcopenia", None, (0.01, 0.05))),
    "articular_cartilage": (V(0.0, "PRIMARY", "Woo86 cartilage: no lipid column (11 % chondroitin sulphate)", "g/g"), V(0.0, "THEORY", "no mobile lipid", None)),
    "achilles_tendon":     (V(0.01, "PRIMARY", "Woo86 connective tissue lipid 1.0 %", "g/g"), V(0.0, "THEORY", "no mobile lipid in tendon proper; peritendinous fat is partial volume", None, (0.0, 0.02))),
    "cortical_bone":       (V(0.0, "PRIMARY", "Woo86 cortical bone: no lipid column (58 % mineral ash)", "g/g"),
                            V(0.02, "THEORY", "Haversian/Volkmann canals carry marrow fat; UTE water-fat studies report a small fat signal fraction in cortical bone; not opened", None, (0.0, 0.10))),
    "bone_marrow_vertebral": (V(0.60, "PRIMARY", "Woo86 red marrow 39.7 %, yellow marrow 80.4 % lipid; adult lumbar marrow is a mixture", "g/g", (0.397, 0.804)),
                            V(0.33, "PRIMARY", "LeS16 Table 1: FF 33+/-8 % over L1-L5 at 1.5 T, rising ~ 2 % per vertebra L1->L5 and with age", None, (0.25, 0.41))),
    "myocardium":          (V(0.062, "PRIMARY", "Woo86 heart 2: 6.2 % (compositions 1-3: 10.0 / 6.2 / 2.4 %; includes epicardial fat in the gross tissue)", "g/g", (0.024, 0.10)),
                            V(0.01, "RECALLED", "PDFF-lit / Dallas Heart Study MRS: myocardial triglyceride ~ 0.5-1.5 % in lean subjects, higher in obesity and diabetes", None, (0.003, 0.03))),
    "blood_arterial":      (V(0.006, "PRIMARY", "Woo86 whole blood lipid 0.6 % (plasma 0.7 %)", "g/g"), V(0.0, "THEORY", "plasma lipoprotein lipid is not resolved as a fat signal fraction at clinical resolution", None, (0.0, 0.01))),
    "liver":               (V(0.046, "PRIMARY", "Woo86 liver 2: 4.6 % (compositions 1-3: 7.8 / 4.6 / 1.5 %; membrane plus triglyceride)", "g/g", (0.015, 0.078)),
                            V(0.03, "RECALLED", "Szc05: hepatic triglyceride by MRS, 95th percentile of the low-risk population 5.56 % (the steatosis cut-off); typical healthy PDFF 1-5 %; Tang13 grades 1-3 above ~ 6.4 / 17.4 / 22.1 %", None, (0.01, 0.056))),
    "spleen":              (V(0.018, "PRIMARY", "Woo86 spleen lipid 1.8 %", "g/g"), V(0.01, "RECALLED", "PDFF-lit: splenic PDFF ~ 0-2 % (used as the in-body zero-fat reference in some PDFF pipelines)", None, (0.0, 0.03))),
    "kidney_cortex":       (V(0.048, "PRIMARY", "Woo86 kidney 2: 4.8 % (compositions 1-3: 6.9 / 4.8 / 2.8 %; whole kidney)", "g/g", (0.028, 0.069)),
                            V(0.02, "RECALLED", "PDFF-lit: renal parenchymal PDFF ~ 1-3 % excluding sinus fat; rises in diabetic nephropathy", None, (0.0, 0.05))),
    "kidney_medulla":      (V(0.048, "PRIMARY", "Woo86 whole kidney (no cortex/medulla split)", "g/g", (0.028, 0.069)),
                            V(0.02, "RECALLED", "as cortex (PDFF-lit)", None, (0.0, 0.05))),
    "pancreas":            (V(0.128, "PRIMARY", "Woo86 pancreas lipid 12.8 % (interlobular fat included in the gross organ)", "g/g"),
                            V(0.05, "RECALLED", "PDFF-lit: pancreatic PDFF ~ 2-10 % in healthy adults, strongly age- and BMI-dependent; > 10 % often taken as fatty pancreas", None, (0.02, 0.15))),
    "prostate_pz":         (V(0.012, "PRIMARY", "Woo86 prostate lipid 1.2 %", "g/g"), V(0.0, "THEORY", "no mobile lipid in the gland; periprostatic fat is partial volume", None, (0.0, 0.02))),
    "breast_fibroglandular": (V(0.309, "PRIMARY", "Woo86 mammary gland 2: 30.9 % (compositions 1-3: 56.2 / 30.9 / 5.6 % — fatty / mixed / glandular)", "g/g", (0.056, 0.562)),
                            V(0.30, "RECALLED", "PDFF-lit: fibroglandular ROIs 10-40 % by partial volume; whole-breast PDFF 60-90 % depending on density category", None, (0.10, 0.60))),
    "adipose_tissue":      (V(0.741, "PRIMARY", "Woo86 adipose tissue 2: 74.1 % (compositions 1-3: 61.4 / 74.1 / 87.3 %)", "g/g", (0.614, 0.873)),
                            V(0.90, "RECALLED", "PDFF-lit: subcutaneous adipose PDFF ~ 85-95 % (the in-body ~ 100 % reference); visceral slightly lower", None, (0.80, 0.97))),
}
for _e in ENTRIES:
    _lm, _pdff = FAT[_e["key"]]
    _e["properties"]["lipid_mass_fraction"] = _lm
    _e["properties"]["pdff"] = _pdff
del _e, _lm, _pdff

# ==============================================================================================
CHANGELOG = [
    "2026-09-07 v1: 13 entries, all RECALLED (first draft).",
    "2026-09-07 v2: restructured (properties: water/PD, T1, T2 at 1.5 and 3 T, ADC; components per modality; theory block); "
    "20 entries; verified values from Stanisz 2005 (SECONDARY, table via mirror), de Bazelaire 2004 (abstract), Han/Gold 2003, "
    "Reiter 2009 (PRIMARY), Horch 2010 (PRIMARY), Saab 1999 (abstract), MacKay 1994 / Whittall 1997 (abstract/preview), "
    "Labadie 2014 (abstract), Luciani 2008 (PRIMARY table), van Baalen 2017, Filli 2015, Serafin 2024, Mayer 2021, McGill 2015, "
    "Mazzoli 2021, Oros-Peusquens 2019; liver, spleen, kidney cortex/medulla, pancreas, marrow, blood, CSF added; "
    "abdominal T2 splits are THEORY (no multi-component study reached) and say so.",
    "2026-09-09 v2.1: adipose tissue added (19 entries); lipid mass fraction (Woodard & White 1986 Table I, PRIMARY) and "
    "PDFF added to every entry as two distinct quantities; Woodard & White 1986, de Bazelaire 2004 (Tables 1-2), Gold 2004 "
    "(Tables) and Le Ster 2016 (Table 1) read from the PDFs in literature/ — water contents and the abdominal/pelvic T1/T2 "
    "columns moved to PRIMARY, 1.5 T columns filled for spleen, kidney, pancreas, prostate and liver; fat T2 recorded as "
    "sequence-dependent (J-coupling) with both the T2-prep and the SSFSE values; hepatic steatosis and the other fat "
    "pathologies noted under the pathology axis (not entries yet). The abdominal multi-component T2 splits remain THEORY: "
    "measuring them is recorded as a potential future research project (register E3), not current focus.",
]
