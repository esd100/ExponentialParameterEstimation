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

Schema 2.3 (pathology axis, charter section 10 step 8c/8e) adds two fields to every entry:

    condition      {"name": "normal" | <disease state>, "kind": "normal" | "pathology" | "physiological",
                    "base": <key of the normal entry this row varies>, "operating_point": <text>}
    clinical_delta {"functional": <name>, "normal_value", "disease_value", "delta" (= disease - normal),
                    "kind", "status", "source", "note"}  or None when no change is on record.

`clinical_delta` is what the third estimability label of results/threshold_tissues.md uses:
a row is 'clinically estimable' when the CRLB SD of its functional is <= |delta| / 3, i.e. the
normal-to-disease change is a 3-sigma event in a single measurement (charter section 1.2, v0.14).
Pathology rows are built with `variant()` and inherit the bulk properties of their base entry
except where overridden; their component sets and theory blocks are their own.

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


def D(functional, normal_value, disease_value, status, source, kind="pathology", note=""):
    """clinical_delta record: the normal-to-disease change of the entry's functional."""
    return {"functional": functional, "normal_value": normal_value, "disease_value": disease_value,
            "delta": round(disease_value - normal_value, 6), "kind": kind, "status": status, "source": source,
            "note": note}


NORMAL = {"name": "normal", "kind": "normal", "base": None, "operating_point": ""}


CPMG_REF = {"n_echoes": 32, "dTE_ms": 10.0, "first_echo_snr": 100.0}

# Short source keys -> full citations are in docs/project/bibliography.md
SRC = {
    "St05": "Stanisz et al. 2005 MRM 54:507 (Table 1 read from the publisher PDF 2026-09-09: in vitro 37 C, n = 3 samples; CPMG TE 1 ms, 6000 echoes, <T2> = arithmetic mean of the NNLS spectrum; IR 35 TIs; mouse liver/muscle/heart, rat cord/kidney, bovine optic nerve/cartilage/WM/GM, human blood)",
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
    "Whi97": "Whittall et al. 1997 MRM 37:34 (Tables 1-3 read 2026-09-09: 1.5 T, single-slice 32 echoes x 10 ms, TR 3 s, n = 12; NNLS 15 ms-2 s; water content WM 0.708 / GM 0.832 g/ml; myelin water 10-50 ms window, WM 11.3 % (8.4-15.0 by structure), GM 3.1 %; main-peak gmT2 WM 77.4 (70-83) / GM 79.9 (74-87) ms; T1 one volunteer WM 756 / GM 1200 ms; CSF peak > 1 s)",
    "MacK94": "MacKay et al. 1994 MRM 31:673 (full text read 2026-09-09: 1.5 T, 32 echoes x 15 ms, TR 3 s, n = 5; myelin water 10-55 ms window: WM 15.6 +/- 8.1 % (498 small volumes), GM 3.8 +/- 6.4 %; IE 70-95 ms; CSF >= 1 s; MS lesions 4.1-6.4 %)",
    "Lau07": "Laule et al. 2007 Neurotherapeutics 4:460 (review; full text)",
    "MacM07": "MacMillan et al. ISMRM 2007 #2331 (3 T cord MWF 0.226; precursor of MacM11)",
    "MacM11": "MacMillan et al. 2011 NeuroImage 54:1083 (Tables 1, 3, 4 read 2026-09-09: 3 T, 3D 32 echoes x 10 ms, TR 1.3 s, n = 12 aged 21-30; NNLS 15 ms-2 s, MWF window 15-35 ms; MWF dorsal column 0.306 (0.284-0.329), lateral column 0.284 (0.262-0.307), grey matter 0.049 (0.030-0.067); IE gmT2 (35-200 ms) 105.5 / 96.5 / 79.9 ms; global gmT2 65.1 / 69.9 / 79.0 ms; SNR_NNLS 111-120; older adults (51-75) MWF 0.274 / 0.257)",
    "Saab99": "Saab, Thompson & Marsh 1999 MRM 42:150 (Table 1 read 2026-09-09: 1.89 T, PP-CPMG, TE 1.2 ms effective, 1000 echoes, SNR 3243 +/- 854, flexor digitorum profundus, n = 13: < 5 ms 10.9 +/- 2.0 %; 20.8 +/- 4.2 ms 27.8 +/- 15.4 %; 38.9 +/- 5.7 ms 45.5 +/- 11.9 %; 114.3 +/- 30.9 ms 11.3 +/- 4.8 %; a fifth 283 +/- 72 ms 5.0 +/- 2.8 % in 6 of 13; imaging T2 (6 echoes x 18 ms, SNR 300) 31.1 +/- 2.6 ms)",
    "Ara14": "Araujo, Fromes & Carlier 2014 Biophys J 106:2267 (Tables 1, 3 read 2026-09-09: 3 T, ISIS-CPMG, 1000 echoes x 1 ms (even echoes used), fat-saturated, soleus, n = 8; free perfusion: biexponential 92.0 +/- 2.4 % at 32.1 +/- 0.4 ms + 8.0 +/- 2.4 % at 159 +/- 25 ms (regularised NNLS 92.8 / 7.2 % at 32.8 / 132 ms); mono-exponential 38.1 +/- 2.4 ms; vascular draining 94.6 / 5.4 % at 31.7 / 139 ms; vascular filling 85.8 / 14.2 % at 32.6 / 181 ms; no short component seen (ISIS pulses filter it); 3S2X model: vascular 7.3 %, intra/interstitial 6.7:1, T2 31.5 / 37.4 ms)",
    "Rei09": "Reiter, Lin, Fishbein & Spencer 2009 MRM 61:803 (full text, PMC2711212; bovine nasal cartilage 9.4 T)",
    "Bou15": "Bouhrara et al. 2015 MRM 73:352 (author manuscript read 2026-09-09: Rician-correct biexponential T2* fitting vs CRLB, 3D MGE 32 echoes at 3 T (TE 2.6-77 ms) and 7 T (0.97-54.6 ms); ex vivo bovine nasal cartilage: biexponential in 20-26 % of voxels, short fraction ~ 0.07-0.08 at ~ 4-5 ms, long ~ 60-67 ms; SNR = S(TE1)/sigma)",
    "Sab17": "Sabouri et al. 2017 Radiology 284:451 (Table 2 read 2026-09-09) and JMRI 46:861 (Table 3 read 2026-09-09): 3 T, 3D multi-echo spin echo, 64 echoes x 25 ms (TE 25-1600 ms), TR 3073 ms, SNR ~ 103 (81-125), regularised NNLS 20-2000 ms with a 200 ms short/long cut-off; nonmalignant PZ: T2short 90 +/- 26 (52-150), T2long 545 +/- 115 (300-887) ms, LWF 0.24 +/- 0.09 (0.09-0.45), Ncomp 2.09; JMRI medians PZ 75 / 503 ms, LWF 0.20 (0.03-0.50); malignant PZ: 81 +/- 21 / 548 +/- 188 ms, LWF 0.10 +/- 0.05; LWF vs Gleason score rho -0.78, vs histological luminal area rho 0.75 (slope 0.45)",
    "Hor10": "Horch et al. 2010 MRM 64:680 (full text, PMC2933073; human cortical bone 4.7 T)",
    "Du12": "Du et al. 2012 MRM 67:645 (Table 1 read 2026-09-09: 3 T 2D UTE, 10-34 TEs from 8 us to 40 ms, in vitro, n = 5 each, noise-corrected bicomponent fit: bovine Achilles tendon 1.28 +/- 0.08 ms 71.4 +/- 5.4 % + 17.65 +/- 4.91 ms 28.6 %; goat ACL 1.53 ms 80.9 % + 14.8 ms; human meniscus 2.10 ms 48.7 % + 18.8 ms; human patellar cartilage 0.48 ms 18.5 % + 35.0 ms 81.5 %; bovine cortical bone 0.29 ms 78.2 % + 2.93 ms 21.8 %)",
    "Lab14": "Labadie et al. 2014 MRM 71:375 (Table 2 read 2026-09-09: Look-Locker IR (PURR) with ~ 64 geometrically spaced TIs, 5 deg readouts, spatially regularised ILT (CONTIN kernel, 80 ms-7 s); 3 T WM: short-T1 fraction 0.083 +/- 0.016 at 225 +/- 13 ms with TIn = 17 s (0.050 +/- 0.011 at 113 +/- 9 ms with TIn = 8 s), T1,long 1.06 +/- 0.04 s, SNR 34; GM 0.026; 4 T 0.113 at 224 ms; 7 T 0.150 at 225 ms; T2* of the short-T1 peak 27.9 +/- 13.0 vs 51.3 +/- 5.6 ms)",
    "Pra12": "Prasloski et al. 2012 MRM 67:1803 (read 2026-09-09: EPG stimulated-echo correction for multicomponent T2; 3 T 3D 32 echoes x 10 ms, SNR ~ 300; MWF window 15-40 ms; simulated WM truth 20 / 100 / 2000 ms at 15 / 75 / 10 %; exponential analysis fails below ~ 161-167 deg refocusing; frontal WM MWF 0 -> 0.075 after correction)",
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
    "Szc05": "Szczepaniak et al. 2005 Am J Physiol Endocrinol Metab 288:E462 (read 2026-09-10: Dallas Heart Study, 2,349 participants, 1.5 T PRESS TR 3 s / TE 25 ms, 27 cm3 voxel, HTGC = methylene / (methylene + water) with fixed T2 correction (water 50, fat 60 ms); low-risk subgroup n = 345: median 1.9 %, 90th percentile 4.3 %, 95th percentile 5.56 % = the steatosis cut-off; whole cohort median 4.69 % (5th/25th/75th/95th 0.99 / 2.74 / 8.56 / 22.86 %, range 0-47.5 %); CV 8.5 % on repeat)",
    "Tang13": "Tang, Tan, Sun et al. 2013 Radiology 267:422 (NASH CRN ancillary study; the ORIGIN of the >= 90 %-specificity MRI-PDFF thresholds 6.4 / 17.4 / 22.1 % for steatosis grades >= 1 / >= 2 / 3; not opened - quoted from Tang15's introduction and Table 3, which cite it as reference 46)",
    "Tang15": "Tang, Desai, Hamilton et al. 2015 Radiology 274:416 (read 2026-09-10: independent VALIDATION cohort, 89 adults with known or suspected NAFLD, 3 T magnitude-based low-flip-angle multiecho GRE with T2* correction and multipeak modelling; mean PDFF 15.2 +/- 8.4 % (1.2-37.5), grades 0/1/2/3 = 6/39/30/14; Table 3: the Tang13 thresholds 6.4 / 17.4 / 22.1 % give sensitivity 86 / 64 / 71 % and specificity 83 / 96 / 92 %; Table 4: cohort-derived thresholds 6.9 / 16.4 / 23.5 %, AUC 0.961 / 0.947 / 0.921; r = 0.87 against the near-continuous steatosis score)",
    "Sch15": "Schwimmer et al. 2015 Hepatology 61:1887 (read 2026-09-10: 174 children, 3 T magnitude-based PDFF vs histology; Table 1 mean PDFF by grade 2.6 +/- 2.2 / 9.2 +/- 5.8 / 15.1 +/- 6.8 / 26.8 +/- 8.2 % for grades 0-3 (n = 24 / 50 / 50 / 50); correlation 0.725; Table 2: published grade-0-vs-1 thresholds 1.8 / 5.5 / 6.4 / 9.0 % give sensitivity 98 / 74 / 68 / 42 %, specificity 54 / 88 / 96 / 96 %, AUROC 0.76 / 0.81 / 0.82 / 0.69; the paper proposes NO grade cut-offs of its own)",
    "Yok11": "Yokoo et al. 2011 Radiology 258:749 (read 2026-09-10: 163 subjects at 3 T; STEAM MRS TR 3.5 s, TE 10-30 ms as the reference; 2D SPGR 10 deg, TR 125-270 ms, six echoes 1.15-6.90 ms; spectroscopic FF 0.004-0.445 (mean 0.097); six-echo T2*-corrected multifrequency method: slope 0.9821, intercept -0.0007 against MRS, classification accuracy 94.5-96.3 % at FF thresholds 0.04-0.10; five-peak weights 0.09 / 0.70 / 0.12 / 0.04 / 0.05 at 0.9 / 1.3 / 2.1 / 4.2 / 5.3 ppm)",
    "Ham11": "Hamilton et al. 2011 NMR Biomed 24:784 (read 2026-09-10: 3 T STEAM TR 3.5 s, TE 10 / 15 / 20 / 25 / 30 ms, 121 subjects with known or suspected NAFLD, 20 mm voxel; Table 3, the liver fat spectrum as percent of total fat signal: 5.3 ppm 4.7 (5.29: 3.7, 5.19: 1.0), 4.2 ppm 3.9, 2.75 ppm 0.6, 2.1 ppm 12.0 (2.24: 5.8, 2.02: 6.2), 1.3 ppm 70.0 (1.60: 5.8, 1.30: 64.2), 0.9 ppm 8.8; 8.6 % of the fat signal lies under the water peak; in vivo T2 at 3 T: water 23 ms, 2.75 ppm 51, 2.1 ppm 52, 1.3 ppm 62, 0.9 ppm 83 ms; mean liver triglyceride CL 17.45, ndb 1.92, nmidb 0.32; mean FF 0.107 (0.004-0.443))",
    "Byd08": "Bydder et al. 2008 Magn Reson Imaging 26:347 (read 2026-09-10: 1.5 T; STEAM 10 mm voxel, TR 3 s, TE 20-70 ms in 10 ms steps; 21 subjects with fatty liver aged 8-66; Table II, T2-corrected peak areas relative to CH2 and peak T2: water (4.7-4.9 ppm) area 10.6 +/- 8.0, T2 36.2 +/- 4.9 ms; CH2 1.2-1.3 ppm 74.8 +/- 19.2 ms; 2.1-2.2 ppm area 0.18 +/- 0.14, T2 45.8 +/- 29.8 ms; 0.8-0.9 ppm area 0.29 +/- 0.12, T2 62 +/- 163 ms; Intralipid phantom: water 802.9, CH2 51.7 ms; expected liver T1 water 490 / fat 260 ms and T2* ~ 30 / ~ 10 ms; multi-echo GRE TE 2.3-36.8 ms, TR 122 ms, flip 10-90 deg; model (v) (independent water/fat T2*) most accurate, error 2.4 %; fat's short apparent T2* (~ 12 ms) at short TE is spectral broadening, not relaxation)",
    "Ree11": "Reeder, Cruite, Hamilton & Sirlin 2011 JMRI 34:729 (read 2026-09-10: review; Table 1 reproduces Ham11's spectrum; Table 2 taxonomy of MRS and MRI fat-quantification techniques by the confounders addressed - T1 bias, T2 / T2* decay, spectral complexity, noise bias, eddy currents - only methods addressing all of them yield PDFF; magnitude-based methods have a 0-50 % dynamic range; histologic grades 0-3 = < 5 / 5-33 / 34-66 / >= 67 % of hepatocytes; the 5.56 % cut-off attributed to Szc05)",
    "Yu08": "Yu et al. 2008 MRM 60:1122 (read 2026-09-10: multipeak IDEAL with simultaneous R2*; Table 1 precalibrated six-peak relative amplitudes (peanut oil, 16-echo) 0.62 / 0.15 / 0.10 / 0.06 / 0.03 / 0.04 at 420 / 318 / -94 / 472 / 234 / 46 Hz from water at 3 T, self-calibrated liver three-peak 0.72-0.76 / 0.16-0.20 / 0.08; a single-peak fat model overestimates R2* in fat (subcutaneous T2* 10 -> 26 ms with the multipeak model) and in fatty liver (patient with 30 %+ fat: T2* 15 -> 22 ms))",
    "Liu07": "Liu et al. 2007 MRM 58:354 (read 2026-09-10: IDEAL-SPGR fat quantification; T1 bias with T1 water 586 / fat 343 ms at 1.5 T (from dB04): 4 % error at 5 deg, 29-45 % rise over 5-30 deg at TR 10 ms; fat-fraction noise minimised at 12 deg; dual-flip-angle (5 / 29 deg) removes the T1 bias; magnitude discrimination or phase-constrained reconstruction reduces the noise-floor bias of the fat-only magnitude image at low fat fractions from 4-15 % to < 1 %)",
    "Her12": "Hernando, Hines, Yu & Reeder 2012 MRM 67:638 (read 2026-09-10: 1.5 T six-echo SPGR; eddy-current phase errors on the first echo of single-shot monopolar readouts bias complex fitting by ~ 5 % absolute at low fat fractions; mixed magnitude/complex fitting discards the first echo's phase and keeps the rest - unbiased against MRS (slope not different from 1, intercept from 0) without the SNR penalty of magnitude fitting; 104 liver data sets from 52 patients; six-peak model at 1.5 T: 217.2 / 166.1 / 242.7 / -38.3 / 25.6 / 124.6 Hz)",
    "Idi15": "Idilman et al. 2015 Abdom Imaging 40:1512 (read 2026-09-10: 41 biopsy-proven NAFLD patients, median age 47, 1.5 T IDEAL-IQ; mean MRI-PDFF liver 18.7 +/- 10 % (median 16.6, 3.3-42.8), pancreas 5.7 +/- 5.6 % (median 4.0, 0.3-32.8; head / body / tail 4.6 / 5.7 / 6.6; diabetics 12.2 +/- 12 vs 4.8 +/- 3.5), renal cortex 1.7 +/- 1.4 % (median 1.3, 0.1-7.6), renal sinus 51 +/- 15.5 %, T12 / L1 vertebral body 43.2 +/- 9.5 / 43.5 +/- 10.2 %; liver PDFF vs histological steatosis rs 0.874)",
    "Kuhn15": "Kuehn et al. 2015 Radiology 276:129 (read 2026-09-10: SHIP population study, 1,367 volunteers (1,241 analysed), median age 50, 1.5 T three-echo 3D GRE (TE 2.4 / 4.8 / 9.6 ms, TR 11 ms) confounder-corrected PDFF; mean pancreatic PDFF 4.4 % unadjusted (head 4.6, body 4.9, tail 3.9 %; 95 % CI 4.2-5.0 / 4.5-5.3 / 3.5-4.3), adjusted 4.46 % (4.16-4.76); no difference between normal glucose tolerance 4.44, prediabetes 4.48 and type 2 diabetes 4.62 %; rises with BMI and age)",
    "Gug23": "Guglielmo et al. 2023 RadioGraphics 43:e220181 (read 2026-09-10: multi-society practical guide; Table 4 PDFF grades < 6 / 6-17 / 17-22 / > 22 % = normal / mild / moderate / severe, adapted from Tang15 (their ref. 43); PDFF reported to the nearest integer, field-independent; subcutaneous fat PDFF 80-100 %, typically 93-96 %; Table 6 liver R2* by iron grade: normal < 75 s-1 at 1.5 T, < 136 s-1 at 3 T (LIC < 1.8 mg/g); LIC = 0.02603 R2* - 0.16 at 1.5 T, 0.01349 R2* - 0.03 at 3 T)",
    "Arm18": "Armstrong et al. 2018 MRM 79:370 (read 2026-09-10: free-breathing 3D stack-of-radial PDFF / R2* at 3 T, 11 healthy subjects; six echoes 1.23-7.38 ms, TR 8.85 ms, flip 5 deg; 3D gridding with linear density compensation and adaptive coil combination, seven-peak fat model at 0.97 / 1.37 / 1.66 / 2.10 / 2.32 / 2.84 / 5.38 ppm, single effective R2*, magnitude discrimination; Table 2 liver PDFF vs breath-hold Cartesian: mean difference 0.6-0.8 %, limits of agreement +/- 5-5.7 %, vs MRS 0.75-0.97 % and +/- 9.7-10.5 %, rho 0.987-0.997; radial R = 1-3)",
    "Hu11": "Hu, Goran & Nayak 2011 InTech ch. 11 (read 2026-09-10: review of abdominal adiposity and organ-fat MRI methods; Table 1 is a methods summary and Table 2 a segmentation-reproducibility table - it carries NO multi-organ table of baseline fat fractions; two pancreas examples at 11 % and 5.1 % FF; muscle, myocardium and spleen PDFF cannot be moved from it)",
    "Hen92": "Henkelman, Hardy, Bishop, Poon & Plewes 1992 JMRI 2:533 ('Why fat is bright in RARE and fast spin-echo imaging': J-coupling makes fat T2 echo-spacing dependent; not opened)",
    "PDFF-lit": "PDFF ranges for lean organs from the water-fat imaging literature, not opened: after the 2026-09-10 water-fat pass this covers only muscle, myocardium, spleen and breast - Hu11 carries no organ table, so Grimm 2018 (thigh-muscle PDFF) and Szczepaniak 2003 (myocardial triglyceride) are re-requested in literature-requests.md; the liver, pancreas, kidney and adipose PDFFs now rest on Szc05, Kuhn15 / Idi15, Idi15 and Gug23",
}

ENTRIES = []

def add(**e):
    e.setdefault("condition", dict(NORMAL))
    e.setdefault("clinical_delta", None)
    ENTRIES.append(e)


def variant(base_key, key, tissue, condition, clinical_delta, components, theory, sources, property_overrides=None):
    """A pathology row: bulk properties inherited from `base_key` (deep-copied) except `property_overrides`;
    its own component sets, theory block and sources. `condition["base"]` is set to `base_key`."""
    import copy
    base = next(x for x in ENTRIES if x["key"] == base_key)
    props = copy.deepcopy(base["properties"])
    for k, v in (property_overrides or {}).items():
        props[k] = v
    cond = dict(condition)
    cond.setdefault("kind", "pathology")
    cond["base"] = base_key
    ENTRIES.append({"key": key, "organ": base["organ"], "tissue": tissue, "properties": props, "components": components,
                    "theory": theory, "sources": list(sources), "condition": cond, "clinical_delta": clinical_delta})

# ==============================================================================================
# BRAIN
# ==============================================================================================
add(key="brain_wm", organ="brain", tissue="white matter",
    properties={
        "water_content": V(0.69, "PRIMARY", "Woo86 Table I WM 68.5 %; Whi97 Table 2 0.708 g/ml (0.698-0.717 by structure; 0.68 g/g after specific gravity); OP19 in vivo 68.7-71.6 %", "g/g", (0.68, 0.716)),
        "pd_relative_csf": V(0.70, "TERTIARY", "RK (WM 60-70 of CSF 100); consistent with water content 0.69/1.0", None, (0.60, 0.72)),
        "T1_ms": {"1.5T": V(884, "PRIMARY", "St05 Table 1 (bovine in vitro, 884+/-50); Whi97 Table 1 in vivo WM average 756 (718-793, one volunteer, SR); Wri08 MPRAGE in vivo 646+/-32; Roo07 fit 681", None, (646, 884)),
                  "3T": V(1084, "PRIMARY", "St05 Table 1 (bovine 1084+/-45); Lab14 T1,long in vivo 1.06+/-0.04 s; Wan99 832; Wri08 838+/-50; Roo07 fit 887", None, (832, 1084))},
        "T2_ms": {"1.5T": V(72, "PRIMARY", "St05 Table 1 (72+/-4, CPMG TE 1 ms); Whi97 Table 3 main-peak gmT2 WM average 77.4 (70.3-82.5 by structure, 32 x 10 ms in vivo)", None, (65, 83)),
                  "3T": V(69, "PRIMARY", "St05 Table 1 (69+/-3); Lu05 via Boj17 75+/-3", None, (65, 80))},
        "ADC": V(0.75, "TERTIARY", "MRM-web (0.70-0.80)", "um2/ms", (0.70, 0.80)),
    },
    components={
        "T2": {"kernel": "t2_cpmg", "field_T": 1.5, "status": "PRIMARY",
               "list": [C("myelin water", 0.113, 15.0, "PRIMARY", "Whi97 Table 2: myelin water (10-50 ms) 11.3 % average of five WM structures (8.4 minor forceps - 15.0 internal capsules), n = 12, 32 x 10 ms; MacK94 15.6 +/- 8.1 % over 498 small volumes (10-55 ms window, 32 x 15 ms); T2 sits at the 15 ms grid minimum (Whi97), in vitro 10-20 ms (MacK94)", (10, 20), "fraction range 0.084-0.156 across the two primaries"),
                        C("intra/extracellular water", 0.867, 77.0, "PRIMARY", "Whi97 Table 3: main-peak gmT2 (50-150 ms) 77.4 ms WM average, 70.3-82.5 by structure; MacK94 70-95 ms", (70, 95)),
                        C("free/CSF-like water", 0.02, 2000.0, "THEORY", "MacK94 and Whi97 both see a > 1 s peak (CSF) and exclude it from the tissue water; its voxel fraction is a partial-volume working configuration, not a tabulated number", (1000, 2500))],
               "functional": "myelin water fraction (mass below 40 ms)", "functional_threshold": 40.0,
               "typical_acquisition": CPMG_REF,
               "note": "Pra12 simulates the UBC 3 T protocol with 15 / 75 / 10 % at 20 / 100 / 2000 ms, i.e. a larger CSF-like share than carried here; the MWF window is 10-50 ms (Whi97), 10-55 (MacK94) or 15-40 ms (Pra12) depending on the group"},
        "T1": {"kernel": "t1_ir", "field_T": 3.0, "status": "PRIMARY",
               "list": [C("myelin-associated (short T1)", 0.083, 225.0, "PRIMARY", "Lab14 Table 2, 3 T, TIn = 17 s: 0.083 +/- 0.016 at 225 +/- 13 ms; 0.050 +/- 0.011 at 113 +/- 9 ms with TIn = 8 s (the peak position and fraction depend on the TI range); 0.113 at 4 T, 0.150 at 7 T", (106, 225), "fraction rises with B0 and with TIn"),
                        C("intra/extracellular (long T1)", 0.917, 1060.0, "PRIMARY", "Lab14: T1,long 1.06 +/- 0.04 s in WM at 3 T (1.25 s at 4 T, 1.52 s at 7 T); St05 bovine 1084", (1000, 1150))],
               "functional": "short-T1 fraction (mass below 500 ms)", "functional_threshold": 500.0,
               "typical_acquisition": {"n_points": 64, "TI_min_ms": 38.0, "TI_max_ms": 17000.0, "spacing": "geometric (Look-Locker, 5 deg readouts)", "first_echo_snr": 34.0}},
        "diffusion": {"kernel": "diffusion_standard_model", "field_T": 3.0, "status": "SECONDARY",
               "list": [C("intra-axonal (stick)", 0.5, 2.2, "SECONDARY", "SM25: f 0.35-0.70, Da 2.03-2.41", (2.0, 2.4), "Da along the axon"),
                        C("extra-axonal", 0.5, 0.6, "SECONDARY", "SM25: De_perp 0.51-0.72, De_par 1.87-2.27", (0.5, 0.72), "value = De_perp")],
               "functional": "intra-axonal signal fraction", "functional_threshold": None,
               "typical_acquisition": {"b_values_ms_per_um2": [1, 2, 3, 5], "directions": 60, "first_echo_snr": 30.0}},
    },
    theory={
        "pools": ["myelin water (between bilayers, ~11-16 % of WM water)", "intra-axonal water", "extra-axonal / interstitial water",
                  "glial intracellular water", "blood (CBV ~ 2-3 %)", "CSF partial volume at voxel scale",
                  "non-aqueous protons (lipid, protein; T2 < 100 us)"],
        "n_pools": 7,
        "exchange": "Myelin water exchanges with intra/extra-axonal water on ~100-300 ms (intermediate on the T2 scale, fast on the T1 scale -> multi-component T1 is exchange-attenuated); intra- and extra-axonal water exchange slowly (~0.5-2 s) but have nearly equal T2 and coalesce; glial water is unresolved.",
        "n_apparent_T2": 3, "n_resolvable_clinical_T2": 2,
        "rationale": "Seven physical pools reduce to three apparent T2 components (myelin, IE, CSF) because IE-scale pools share T2 within the exchange-averaged tolerance; at clinical SNR two are resolvable, and the third (CSF) is unpinned by a 320 ms window. On the T1 axis exchange leaves only a weak short component (8 % at 3 T, rising with field). Whi97 also finds the IE peak split into two broad peaks near 80 and 150-600 ms in the most myelinated structures (posterior internal capsules 88 / 12 %, splenium 93 / 7 %) and notes that components differing by less than a factor of three cannot be separated - the resolution limit of charter section 1.2 in the primary's own words."},
    sources=["MacK94", "Whi97", "Lau07", "St05", "Wri08", "Roo07", "OP19", "Lab14", "Pra12", "SM25"],
    clinical_delta=D("myelin water fraction (mass below 40 ms)", 0.113, 0.0525, "PRIMARY",
                     "MacK94: MWF in 34 lesions of four MS patients 6.4 / 5.8 / 4.7 / 4.1 % (SE 0.6-1.1 %; 95 % CI 0-13 %), mean 5.25 %, against the dictionary's normal WM 0.113 (Whi97 structure average); within MacK94's own protocol the change is 15.6 % -> ~ 5 %, i.e. -0.10",
                     note="delta = -0.061 on the dictionary values (-0.10 within MacK94); the MS-lesion row `brain_wm_ms_lesion` is the disease operating point"))

add(key="brain_gm", organ="brain", tissue="cortical grey matter",
    properties={
        "water_content": V(0.83, "PRIMARY", "Woo86 Table I GM 82.6 %; Whi97 Table 2 GM average 0.832 g/ml (cortical grey 0.792, caudate 0.874); OP19 83.7+/-1.2 %", "g/g", (0.79, 0.874)),
        "pd_relative_csf": V(0.83, "TERTIARY", "RK (GM 70-85); water content 0.84", None, (0.70, 0.85)),
        "T1_ms": {"1.5T": V(1124, "PRIMARY", "St05 Table 1 (bovine 1124+/-50); Whi97 Table 1 in vivo GM average 1200 (cortical grey 1260, one volunteer); Wri08 MPRAGE 1197+/-134; Roo07 fit 998", None, (998, 1260)),
                  "3T": V(1607, "SECONDARY", "Wri08 (1607+/-112); St05 Table 1 bovine 1820+/-114 (PRIMARY); Wan99 1331; Lu05 via Boj17 1165", None, (1165, 1820))},
        "T2_ms": {"1.5T": V(95, "PRIMARY", "St05 Table 1 (95+/-8, CPMG TE 1 ms, bovine cortex); Whi97 Table 3 main-peak gmT2 GM average 79.9 (73.9-86.5; cortical grey 77.9) in vivo", None, (74, 103)),
                  "3T": V(99, "PRIMARY", "St05 Table 1 (99+/-7); Lu05 via Boj17 83+/-4", None, (80, 110))},
        "ADC": V(0.85, "TERTIARY", "MRM-web (0.80-0.90)", "um2/ms", (0.80, 0.90)),
    },
    components={
        "T2": {"kernel": "t2_cpmg", "field_T": 1.5, "status": "PRIMARY",
               "list": [C("myelin water", 0.031, 15.0, "PRIMARY", "Whi97 Table 2: myelin water (10-50 ms) 3.1 % average of six GM structures (2.0 cingulate - 5.8 thalamus; cortical grey 2.2 %); MacK94 3.8 +/- 6.4 % over 493 small volumes", (10, 20), "fraction range 0.020-0.058 across structures"),
                        C("intra/extracellular water", 0.939, 80.0, "PRIMARY", "Whi97 Table 3: main-peak gmT2 GM average 79.9 ms (73.9-86.5; cortical grey 77.9); St05 bulk 95 in vitro", (74, 95)),
                        C("CSF partial volume", 0.03, 2000.0, "THEORY", "cortical ribbon partial volume; Whi97 excludes the > 1 s peak from the tissue water and does not tabulate its fraction", (1000, 2500))],
               "functional": "myelin water fraction (mass below 40 ms)", "functional_threshold": 40.0, "typical_acquisition": CPMG_REF},
    },
    theory={"pools": ["neuronal/glial intracellular water", "extracellular water", "sparse myelin water", "blood (CBV ~ 4-6 %)", "CSF partial volume", "non-aqueous protons"],
            "n_pools": 6, "exchange": "Intra/extracellular water coalesce; myelin water is sparse; blood is a few percent at longer T2 (oxygenation dependent).",
            "n_apparent_T2": 3, "n_resolvable_clinical_T2": 1,
            "rationale": "The minor components (myelin ~3 %, blood ~5 %, CSF ~3 %) are each below the clinical detectability floor; GM is effectively mono-exponential to a CPMG train at SNR 100 and is the hard case for any short-T2 fraction."},
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
    components={"T2": {"kernel": "t2_cpmg", "field_T": 1.5, "status": "TERTIARY",
                       "list": [C("free water", 1.0, 2000.0, "TERTIARY", "single pool; MacK94 / Whi97 / MacM11 place the CSF peak at >= 1 s at the top of their 2 s NNLS grid, so the in vivo value is not pinned by the multi-echo literature read", (1500, 2500))],
                       "functional": "T2 (mono-exponential)", "functional_threshold": None,
                       "typical_acquisition": CPMG_REF}},
    theory={"pools": ["free water"], "n_pools": 1, "exchange": "n/a", "n_apparent_T2": 1, "n_resolvable_clinical_T2": 1,
            "rationale": "K = 1 reference and the partial-volume contaminant of every brain entry; its T2 exceeds any clinical echo train, so it appears as a near-constant offset — the charter §3.2 sigma / long-T degeneracy in physical form."},
    sources=["Roo07", "Boj17"])

add(key="spinal_cord_wm", organ="spinal cord", tissue="cervical cord white matter (lateral/dorsal columns)",
    properties={
        "water_content": V(0.70, "THEORY", "no cord-specific composition in Woo86; taken as brain WM (68.5 %) with a small GM/CSF admixture", "g/g", (0.68, 0.75)),
        "pd_relative_csf": V(0.70, "TERTIARY", "as WM", None, (0.60, 0.75)),
        "T1_ms": {"1.5T": V(745, "PRIMARY", "St05 Table 1 (rat cord 745+/-37)", None, (700, 900)),
                  "3T": V(750, "SECONDARY", "Smith & van Zijl ISMRM 2007: lateral 752+/-89, dorsal 745+/-61; St05 Table 1 rat 993+/-47 (PRIMARY)", None, (745, 993))},
        "T2_ms": {"1.5T": V(74, "PRIMARY", "St05 Table 1 (rat 74+/-6)", None, (65, 80)),
                  "3T": V(66, "PRIMARY", "MacM11 Table 1 global gmT2 (15 ms-2 s) dorsal column 65.1 (61.4-68.8), lateral column 69.9 (65.9-73.9), grey matter 79.0; Smith & van Zijl 2007 mono-exponential 65+/-4 / 66+/-4; St05 rat 78+/-2", None, (61, 78))},
        "ADC": V(0.9, "RECALLED", "cord MD ~0.9 (strongly anisotropic)", "um2/ms", (0.8, 1.1)),
    },
    components={"T2": {"kernel": "t2_cpmg", "field_T": 3.0, "status": "PRIMARY",
                       "list": [C("myelin water", 0.296, 20.0, "PRIMARY", "MacM11 Table 1 / 4: MWF (15-35 ms window) 0.306 dorsal column, 0.284 lateral column, WM 0.296 (SD 0.039), n = 12 aged 21-30, 3 T 32 x 10 ms; older adults 0.274 / 0.257; grey matter 0.049; the myelin peak sits at the 15 ms grid edge with the window cut at 35 ms", (15, 25), "fraction range 0.257-0.329 across columns and age groups"),
                                C("intra/extracellular water", 0.674, 100.0, "PRIMARY", "MacM11 Table 1: IE gmT2 (35-200 ms) 105.5 dorsal (102.6-108.4), 96.5 lateral (93.6-99.5); 99.5 / 93.6 in older adults; grey matter 79.9", (94, 108)),
                                C("CSF partial volume", 0.03, 2000.0, "THEORY", "severe around the cord in a voxel; MacM11's ROIs sit well inside the columns and do not tabulate a CSF fraction", (1500, 2500))],
                       "functional": "myelin water fraction (mass below 40 ms)", "functional_threshold": 40.0, "typical_acquisition": CPMG_REF,
                       "note": "MacM11's SNR_NNLS (TE = 0 amplitude / residual SD) was 111-120, close to the reference first-echo SNR 100; the myelin water fraction is ~ 2.5x brain WM's and the IE T2 ~ 25 ms longer, so the ratio between the two visible components is ~ 5 (brain WM ~ 5 as well, but with a 3x smaller minor fraction)"}},
    theory={"pools": ["myelin water (denser than brain WM)", "intra-axonal", "extra-axonal", "glial", "blood", "CSF partial volume (large: small structure)", "non-aqueous"],
            "n_pools": 7, "exchange": "as brain WM", "n_apparent_T2": 3, "n_resolvable_clinical_T2": 2,
            "rationale": "Same pool structure as brain WM with a larger myelin fraction (0.26-0.33, MacM11), which is why the MWF is the easy myelin case, and a larger CSF contaminant, which is why the long component matters more."},
    sources=["MacM11", "MacM07", "St05"],
    clinical_delta=D("myelin water fraction (mass below 40 ms)", 0.296, 0.2655, "PRIMARY",
                     "MacM11 Table 3: older adults (51-75 y) MWF 0.274 dorsal / 0.257 lateral (mean 0.2655) against 0.306 / 0.284 (0.296) at 21-30 y",
                     kind="physiological", note="an age effect, not a disease: no cord-lesion MWF primary is on hand; delta = -0.031"))

# ==============================================================================================
# MUSCULOSKELETAL
# ==============================================================================================
add(key="skeletal_muscle", organ="musculoskeletal", tissue="skeletal muscle (calf / forearm / paravertebral)",
    properties={
        "water_content": V(0.74, "PRIMARY", "Woo86 Table I skeletal muscle 2: 74.1 % (compositions 1-3: 70.0 / 74.1 / 78.6 %)", "g/g", (0.70, 0.786)),
        "pd_relative_csf": V(0.90, "TERTIARY", "RK"),
        "T1_ms": {"1.5T": V(1008, "PRIMARY", "St05 Table 1 (mouse 1008+/-20); Gold04 in vivo 1130+/-92; dB04 paravertebral 856+/-61", None, (856, 1200)),
                  "3T": V(1412, "PRIMARY", "St05 Table 1 (1412+/-13); Gold04 1420+/-38; dB04 paravertebral 898+/-33", None, (898, 1420))},
        "T2_ms": {"1.5T": V(35, "PRIMARY", "Gold04 in vivo 35.3+/-3.9; dB04 paravertebral 27+/-8; St05 Table 1 mouse 44+/-6 (CPMG TE 1 ms); Saab99 imaging T2 31.1+/-2.6 (1.89 T, 6 x 18 ms)", None, (27, 45)),
                  "3T": V(32, "PRIMARY", "Gold04 31.7+/-1.9; dB04 paravertebral 29+/-4; Ara14 mono-exponential ISIS-CPMG 38.1+/-2.4 (soleus); St05 Table 1 50+/-4 (mouse, TE 1 ms)", None, (29, 50))},
        "ADC": V(1.5, "SECONDARY", "Maz21/Schlaffke: AD 1.9-2.6, RD 1.35-1.6 (unit flag in source); MRM-web 1.0-1.5", "um2/ms", (1.3, 1.8)),
    },
    components={
        "T2": {"kernel": "t2_cpmg", "field_T": 1.89, "status": "PRIMARY",
               "list": [C("macromolecule-associated water", 0.114, 4.0, "PRIMARY", "Saab99 Table 1 in vivo: < 5 ms, 10.9 +/- 2.0 % (reported as '< 5 ms' because the 1.2 ms echo spacing cannot pin it)", (2, 5), "invisible to a 10 ms first echo"),
                        C("short intracellular (myofibrillar) water", 0.291, 20.8, "PRIMARY", "Saab99 Table 1: 20.8 +/- 4.2 ms, 27.8 +/- 15.4 %", (16.6, 25.0)),
                        C("main intracellular (sarcoplasmic) water", 0.477, 38.9, "PRIMARY", "Saab99 Table 1: 38.9 +/- 5.7 ms, 45.5 +/- 11.9 %", (33.2, 44.6)),
                        C("extracellular / interstitial water", 0.118, 114.3, "PRIMARY", "Saab99 Table 1: 114.3 +/- 30.9 ms, 11.3 +/- 4.8 % (the abstract's 11 +/- 5 %; the v2 value 5 % was the fifth component's share, mis-assigned); Ara14 at 3 T: 8.0 +/- 2.4 % at 159 +/- 25 ms, rising to 14.2 % at 181 ms with venous filling", (83, 181), "rises with oedema, exercise and vascular filling (Ara14)")],
               "functional": "extracellular fraction (1 - mass below 60 ms)", "functional_threshold": 60.0, "typical_acquisition": CPMG_REF,
               "note": "fractions are Saab99's four all-subject components renormalised from 95.5 %; Saab99 also sees a fifth component at 283 +/- 72 ms (5.0 +/- 2.8 %) in 6 of 13 subjects, attributed to free or vascular water, not carried. At 3 T with a 2 ms effective spacing and fat saturation Ara14 sees exactly two components (92 % at 32 ms, 8 % at 159 ms) and shows with a three-site exchange model that the 32 ms peak is intracellular plus interstitial water and the long peak is vascular water - the clinically visible K = 2 description"},
        "diffusion": {"kernel": "diffusion_tensor", "field_T": 3.0, "status": "SECONDARY",
               "list": [C("tensor: axial diffusivity", 1.0, 2.0, "SECONDARY", "Maz21 PGSE TA/soleus AD 2.32/2.64; Schlaffke AD 1.89/2.14", (1.9, 2.6)),
                        C("tensor: radial diffusivity", 0.0, 1.5, "SECONDARY", "Maz21 RD 1.55/1.51; Schlaffke 1.35/1.62", (1.35, 1.6), "fraction 0 = same pool, second eigenvalue")],
               "functional": "fractional anisotropy", "functional_threshold": None,
               "typical_acquisition": {"b_values_s_per_mm2": [0, 400, 600], "directions": 12, "first_echo_snr": 30.0}},
    },
    theory={"pools": ["myofibrillar (intra-sarcomere) water", "sarcoplasmic / mitochondrial water", "interstitial (endomysial) water", "vascular water (~ 3-5 % blood volume)",
                      "macromolecule-bound water (< 5 ms)", "intramuscular fat (methylene protons; variable)"],
            "n_pools": 6, "exchange": "Intracellular sub-pools exchange on ms-tens of ms and are only separable at very high SNR (Saab99's 1000-echo, SNR 3500 data); Ara14's exchange modelling puts the intracellular residence time near 1 s and the intravascular one at 0.3-3 s, i.e. slow on the T2 scale, so the long component is vascular (not interstitial) water and the interstitial T2 (~ 37 ms) is close to the intracellular one.",
            "n_apparent_T2": 4, "n_resolvable_clinical_T2": 2,
            "rationale": "Saab et al. needed SNR ~3500 and 1.2 ms echoes to see four components; Araujo et al. at 3 T with 2 ms spacing see two (92 / 8 % at 32 / 159 ms); a clinical 32 x 10 ms train sees the ~30 ms intracellular pool and, at best, the ~120-160 ms vascular/extracellular one (the oedema marker). St05 Fig. 1 shows three peaks in mouse muscle at 3 T without tabulating them."},
    sources=["Saab99", "Ara14", "St05", "Gold04", "dB04", "Maz21"],
    clinical_delta=D("extracellular fraction (1 - mass below 60 ms)", 0.080, 0.142, "PRIMARY",
                     "Ara14 Table 1: the long (vascular) fraction rises from 8.0 +/- 2.4 % (free perfusion) to 14.2 % under venous filling in the same subjects and protocol (3 T, ISIS-CPMG); Saab99's extracellular 11.3 % at 1.89 T is this row's own value",
                     kind="physiological", note="venous filling is the measured surrogate for the oedema / extracellular-expansion pathologies; delta = +0.062 is a paired within-protocol change, the row's own functional value is Saab99's 0.118"))

add(key="articular_cartilage", organ="knee", tissue="articular (hyaline) cartilage",
    properties={
        "water_content": V(0.75, "PRIMARY", "Woo86 Table I cartilage 75.0 %; depth-dependent 65-80 % (Shiguetomi-Medina 2017, SECONDARY)", "g/g", (0.65, 0.80)),
        "pd_relative_csf": V(0.60, "RECALLED", "collagen/PG matrix reduces mobile PD; not opened", None, (0.5, 0.7)),
        "T1_ms": {"1.5T": V(1024, "PRIMARY", "St05 Table 1 (bovine 1024+/-70 at 0 deg, 1038+/-67 at 55 deg); Gold04 in vivo 1060+/-155", None, (1000, 1100)),
                  "3T": V(1168, "PRIMARY", "St05 Table 1 (1168+/-18 at 0 deg, 1156+/-10 at 55 deg); Gold04 1240+/-107", None, (1150, 1250))},
        "T2_ms": {"1.5T": V(37, "PRIMARY", "St05 Table 1 30+/-4 (0 deg) / 44+/-5 (55 deg, magic angle); Gold04 in vivo 42.1+/-7.1", None, (30, 44)),
                  "3T": V(35, "PRIMARY", "St05 Table 1 27+/-3 / 43+/-2; Gold04 36.9+/-3.8", None, (27, 43))},
        "ADC": V(1.3, "SECONDARY", "Raya 2012: healthy-vs-OA threshold ADC 1.2 (7 T); MRM-web n/a", "um2/ms", (1.1, 1.5)),
    },
    components={"T2": {"kernel": "t2_cpmg", "field_T": 9.4, "status": "PRIMARY",
                       "list": [C("collagen-bound water", 0.062, 2.3, "PRIMARY", "Rei09 control: 2.3+/-0.6 ms, 6.2+/-2.5 %", (1.7, 2.9), "needs UTE; invisible to CPMG at 10 ms"),
                                C("proteoglycan-associated water", 0.145, 25.2, "PRIMARY", "Rei09: 25.2+/-6.2 ms, 14.5+/-3.9 %", (19, 31)),
                                C("bulk water", 0.793, 96.3, "PRIMARY", "Rei09: 96.3+/-4.7 ms, 79.3+/-6.1 %", (90, 101))],
                       "functional": "short/intermediate fraction (mass below 45 ms)", "functional_threshold": 45.0,
                       "typical_acquisition": {"n_echoes": 32, "dTE_ms": 6.0, "first_echo_snr": 100.0},
                       "note": "ex vivo bovine nasal cartilage at 9.4 T (Rei09); in vivo human articular cartilage at 3 T has shorter bulk T2 (~35-45 ms) and a magic-angle dependence. Two T2* primaries at 3 T give a different split: Bou15 (bovine nasal cartilage, MGE, Rician-correct fit) finds biexponential decay in only 20-26 % of voxels, with a short fraction ~ 0.07-0.08 at ~ 4-5 ms and a long component at ~ 60-67 ms; Du12 Table 1 (human patellar cartilage, UTE from 8 us) finds 18.5 +/- 5.1 % at 0.48 +/- 0.09 ms and 81.5 % at 35.0 +/- 9.6 ms, i.e. the collagen-bound and proteoglycan pools merge into one sub-ms UTE component"}},
    theory={"pools": ["collagen-bound water (T2 ~ 1-3 ms)", "proteoglycan-associated water", "bulk (free) water", "zonal variation superficial/transitional/deep (orientation-dependent T2)", "synovial fluid partial volume at the surface"],
            "n_pools": 5, "exchange": "Bound and PG-associated water exchange with bulk on sub-ms to ms scales; the residual three-component structure (Rei09) survives because exchange is not complete. Orientation (magic angle) modulates T2 within the bulk pool, i.e. a distribution, not a discrete component.",
            "n_apparent_T2": 3, "n_resolvable_clinical_T2": 2,
            "rationale": "At clinical TE_1 = 6-10 ms the 2 ms pool is gone; what remains is a ~25 ms / ~90 ms pair with ratio ~4 and a 15 % minor fraction — resolvable at high SNR in thick cartilage, marginal in vivo where SNR and thickness are both smaller."},
    sources=["Rei09", "Bou15", "Du12", "St05", "Gold04"])

add(key="achilles_tendon", organ="musculoskeletal", tissue="Achilles tendon",
    properties={
        "water_content": V(0.60, "PRIMARY", "Woo86 Table I connective tissue 60.4 % (composition based on cattle tendon, Oser 1965)", "g/g", (0.55, 0.70)),
        "pd_relative_csf": V(0.3, "RECALLED", "most water is collagen-bound with sub-ms T2 (invisible at conventional TE)", None, (0.1, 0.5)),
        "T1_ms": {"3T": V(700, "RECALLED", "UTE-T1 of tendon ~ 600-800 ms; not opened", None, (500, 900))},
        "T2_ms": {"3T": V(11, "SECONDARY", "Qiao17: mono-exponential UTE T2* 11.1+/-0.3 ms (T2*, not CPMG T2)", None, (8, 15))},
        "ADC": V(1.0, "RECALLED", "tendon diffusion rarely measured; anisotropic", "um2/ms", (0.8, 1.4)),
    },
    components={"T2": {"kernel": "t2star_ute", "field_T": 3.0, "status": "PRIMARY",
                       "list": [C("short T2* (collagen-bound)", 0.714, 1.28, "PRIMARY", "Du12 Table 1, bovine Achilles tendon in vitro, n = 5: 1.28 +/- 0.08 ms, 71.4 +/- 5.4 % (goat ACL 1.53 ms, 80.9 %)", (1.20, 1.36), "the v2 value (80 %, 1.0 ms) was the ligament row"),
                                C("long T2* (free water)", 0.286, 17.65, "PRIMARY", "Du12 Table 1: 17.65 +/- 4.91 ms, 28.6 +/- 3.8 %; Qiao17 in vivo mono-exponential UTE T2* 11.1 ms", (11, 22.6))],
                       "functional": "short fraction (mass below 5 ms)", "functional_threshold": 5.0,
                       "typical_acquisition": {"n_echoes": 16, "dTE_ms": 0.5, "first_echo_snr": 50.0},
                       "note": "Du12 acquired 10-34 TEs from 8 us to 40 ms and reports < 3 % fitting error at SNR ~ 50 with 12-16 echoes for a two-component fit with the fractions constrained to sum to one; the acquisition here is that design"}},
    theory={"pools": ["collagen-bound water (sub-ms)", "free/interfibrillar water", "peritendinous fluid partial volume", "collagen protons (T2 ~ 10s of us)"],
            "n_pools": 4, "exchange": "Bound/free exchange is fast relative to T1 but slow relative to the sub-ms/ms T2 split; magic-angle orientation dependence dominates the free pool's T2.",
            "n_apparent_T2": 2, "n_resolvable_clinical_T2": 2,
            "rationale": "A two-component UTE T2* case with ratio ~14 and a dominant short pool: the mirror image of the myelin problem (major short component), estimable when TE_1 < 0.5 ms."},
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
                       "note": "fractions renormalised over the two water pools visible to UTE; Hor10 also sees a 57 us pool (16 %) and a collagen 12 us pool (34 % of FID) that only solid-state methods reach. Du12 Table 1 (bovine cortical bone, 3 T UTE T2*, n = 5) gives the same two-pool picture: 0.29 +/- 0.02 ms 78.2 +/- 2.6 % and 2.93 +/- 0.57 ms 21.8 +/- 3.6 %"}},
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
        "T1_ms": {"1.5T": V(1030, "PRIMARY", "St05 Table 1 (mouse heart in vitro 1030+/-34); in vivo MOLLI ~950-1000 (RECALLED)", None, (950, 1050)),
                  "3T": V(1170, "SECONDARY", "vKB13 MOLLI 1157-1181 base->apex; St05 Table 1 1471+/-31 (mouse, PRIMARY); Boj17 1116-1341", None, (1116, 1341))},
        "T2_ms": {"1.5T": V(52, "SECONDARY", "Giri09 52.2 (quoted in vKB13); St05 Table 1 mouse 40+/-6 (PRIMARY)", None, (40, 55)),
                  "3T": V(45, "SECONDARY", "vKB13 44.1-46.9; St05 Table 1 47+/-11 (PRIMARY); Boj17 39-67", None, (39, 67))},
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
        "T1_ms": {"1.5T": V(1441, "PRIMARY", "St05 Table 1 (human blood in vitro at 95 % oxygenation, 1441+/-120); Roo07 fit 1550", None, (1350, 1600)),
                  "3T": V(1932, "PRIMARY", "St05 Table 1 (1932+/-85); Roo07 fit 1961", None, (1650, 2000))},
        "T2_ms": {"1.5T": V(290, "PRIMARY", "St05 Table 1 (95 % oxygenated in vitro, CPMG TE 1 ms: 290+/-30); venous 50-200 depending on Y (Wikipedia tertiary)", None, (150, 300)),
                  "3T": V(275, "PRIMARY", "St05 Table 1 (275+/-50); venous much shorter; Ara14 fixes venous blood T2 at 3 T to 186 ms (Chen & Pike 2009) in its exchange model", None, (100, 275))},
        "ADC": V(3.0, "RECALLED", "free-water-like plus flow; Funck 2018 not opened", "um2/ms", (2.5, 3.5)),
    },
    components={"T2": {"kernel": "t2_cpmg", "field_T": 1.5, "status": "SECONDARY",
                       "list": [C("blood water (plasma + RBC, fast exchange)", 1.0, 250.0, "SECONDARY", "St05 Table 1 290 in vitro at TE 1 ms (PRIMARY); in vivo arterial ~ 200-250 at clinical echo spacing (RECALLED; Luz-Meiboom spacing dependence)", (150, 300))],
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
        "T1_ms": {"1.5T": V(586, "PRIMARY", "dB04 Table 1 586+/-39 (human in vivo); St05 Table 1 mouse 576+/-30", None, (550, 620)),
                  "3T": V(809, "PRIMARY", "dB04 Table 1 809+/-71; St05 Table 1 812+/-64", None, (750, 870))},
        "T2_ms": {"1.5T": V(46, "PRIMARY", "dB04 Table 2 46+/-6 (human in vivo); St05 Table 1 46+/-6; water peak by STEAM MRS in 21 fatty livers 36.2+/-4.9 (Byd08 Table II; fat CH2 74.8+/-19.2)", None, (36, 55)),
                  "3T": V(34, "PRIMARY", "dB04 Table 2 34+/-4; St05 Table 1 42+/-3 (CPMG TE 1 ms); water peak by STEAM MRS in NAFLD 23 (Ham11 Table 3; fat CH2 62), Guiu et al. via Ham11 27 / 60", None, (23, 45))},
        "ADC": V(1.39, "PRIMARY", "Luc08 Table 4: 1.39+/-0.2 (b up to 800); EJR20 1.65+/-0.44; MRM-web 0.6-1.1", "um2/ms", (1.0, 1.7)),
    },
    components={
        "T2": {"kernel": "t2_cpmg", "field_T": 1.5, "status": "THEORY",
               "list": [C("hepatocellular water", 0.78, 42.0, "THEORY", "bulk T2 (St05/dB04); fraction = 1 - IVIM perfusion fraction (Luc08 f 0.27; Li17 0.22)", (35, 50)),
                        C("sinusoidal blood / bile", 0.22, 150.0, "THEORY", "vascular fraction from IVIM f (0.22-0.27); T2 of partially deoxygenated blood 100-200 ms", (100, 250))],
               "functional": "vascular/long-T2 fraction (1 - mass below 90 ms)", "functional_threshold": 90.0,
               "typical_acquisition": {"n_echoes": 16, "dTE_ms": 8.0, "first_echo_snr": 60.0},
               "note": "no in vivo multi-component liver T2 study reached (Ber83 ex vivo biexponential, no values); the split is a working configuration from IVIM and bulk T2. The steatotic variants (`liver_steatosis_pdff10`, `_pdff25`) carry the measured water / fat T2 pair instead (Byd08 Table II) and drop this vascular tail"},
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
        "T1_ms": {"1.5T": V(966, "PRIMARY", "dB04 Table 1 cortex 966+/-58 (human in vivo); St05 Table 1 rat whole kidney 690+/-30", None, (690, 1000)),
                  "3T": V(1142, "PRIMARY", "dB04 Table 1 cortex 1142+/-154; St05 Table 1 rat whole 1194+/-27", None, (1000, 1250))},
        "T2_ms": {"1.5T": V(87, "PRIMARY", "dB04 Table 2 cortex 87+/-4 (human in vivo); St05 Table 1 rat whole kidney 55+/-3", None, (55, 95)),
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
        "T2_ms": {"1.5T": V(88, "PRIMARY", "dB04 Table 2 whole gland 88 (SD reported as 0); PZ alone is longer (Sab17 gmT2 of the whole distribution: nonmalignant PZ 138+/-46 at 3 T)", None, (85, 140)),
                  "3T": V(74, "PRIMARY", "dB04 Table 2 whole gland 74+/-9; Sab17 Table 2 gmT2 (20-2000 ms) nonmalignant PZ 138+/-46 (68-298), TZ 138+/-49, malignant PZ 94+/-27, fibromuscular stroma 58-77", None, (70, 140))},
        "ADC": V(1.6, "TERTIARY", "MRM-web prostate 1.4-1.8", "um2/ms", (1.4, 1.9)),
    },
    components={"T2": {"kernel": "t2_cpmg", "field_T": 3.0, "status": "PRIMARY",
                       "list": [C("epithelial / stromal water", 0.76, 90.0, "PRIMARY", "Sab17 Radiology Table 2, nonmalignant PZ, 18 patients: T2short (gmT2 of the 20-200 ms peak) 90 +/- 26 ms, range 52-150; JMRI Table 3 median 75 (50-152); nonmalignant TZ 104 +/- 38", (52, 150)),
                                C("luminal water", 0.24, 545.0, "PRIMARY", "Sab17 Radiology Table 2: T2long (200-2000 ms peak) 545 +/- 115 ms, range 300-887, LWF 0.24 +/- 0.09 (0.09-0.45); JMRI Table 3 median 503 (249-904), LWF 0.20 (0.03-0.50); LWF vs histological luminal area rho 0.75 with slope 0.45, vs Gleason score rho -0.78", (300, 887), "fraction range 0.09-0.45; malignant PZ 0.10 +/- 0.05 at 548 +/- 188 ms")],
                       "functional": "luminal water fraction (1 - mass below 200 ms)", "functional_threshold": 200.0,
                       "typical_acquisition": {"n_echoes": 64, "dTE_ms": 25.0, "first_echo_snr": 100.0},
                       "note": "the strongest clinically validated two-component T2 case. Sab17's protocol is a 3D multi-echo spin echo with 64 echoes at 25 ms spacing (TE 25-1600 ms, TR 3073 ms, 1 x 1 x 4 mm, 11 min) at an average prostate SNR of 103 (95 % CI 81-125), chosen by simulation over TE 7-55 ms and NE 10-64 for T2short 25-75 / T2long 200-800 ms; the v2 acquisition (64 x 8 ms, SNR 80) was wrong in the spacing, so the v2 'own acquisition' row of the threshold table was evaluated on a 512 ms window instead of 1600 ms. Regularised NNLS (Bjarnason & Mitchell 2010) on a 20-2000 ms grid with the short/long cut at 200 ms from the histogram of 4700 two-peak pixels; Ncomp 2.09 +/- 0.22 in nonmalignant PZ, 1.81 in malignant PZ (higher-grade tumours become mono-exponential)"}},
    theory={"pools": ["glandular lumen fluid (secretions; large in normal PZ: 27 % of the section area by histology, Sab17 JMRI)", "epithelial cell water", "stromal (smooth muscle/fibrous) water", "vascular blood"],
            "n_pools": 4, "exchange": "Lumen-epithelium exchange is slow relative to the large T2 difference (ratio ~ 6), so two components persist; stroma and epithelium share T2 and coalesce. Cancer replaces lumen with cells -> LWF falls (0.24 -> 0.10 in PZ). Sab17 JMRI attributes the LWF-vs-histology slope of 0.45 partly to lumen-epithelium water exchange and partly to 2D-area vs 3D-volume and fixation shrinkage.",
            "n_apparent_T2": 2, "n_resolvable_clinical_T2": 2,
            "rationale": "Well-separated (ratio ~ 6), both fractions large: the easy case, and the positive control for every estimator; the malignant PZ variant (LWF 0.10 at 81 / 548 ms) is the pathology-axis row for this organ."},
    sources=["Sab17", "dB04", "Boj17"],
    clinical_delta=D("luminal water fraction (1 - mass below 200 ms)", 0.24, 0.10, "PRIMARY",
                     "Sab17 Radiology Table 2: LWF 0.24 +/- 0.09 in nonmalignant PZ against 0.10 +/- 0.05 in malignant PZ (same protocol, 18 patients); JMRI Table 3 medians 0.20 vs 0.07",
                     note="delta = -0.14; the disease operating point is `prostate_pz_cancer`"))

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
# Pathology axis (charter §6.1, §10 step 8e): hepatic steatosis is graded on PDFF - normal < 5.56 % (Szc05, read),
# grade thresholds 6.4 / 17.4 / 22.1 % (origin Tang13, validated by Tang15 - read - and rounded to 6 / 17 / 22 % by Gug23);
# pancreatic, muscular and myocardial fat rise with obesity and age; marrow FF rises with age and falls with infiltration.
# v2.3: the steatotic-liver rows at PDFF 10 % and 25 % are entries (below, built with variant()).
# Status after the 2026-09-10 water-fat pass: liver (Szc05), pancreas (Kuhn15, Idi15), kidney cortex (Idi15), marrow
# (LeS16) and adipose (Gug23, SECONDARY) are read; muscle, myocardium, spleen and breast stay RECALLED because Hu11
# carries no organ table (Grimm 2018 and Szczepaniak 2003 re-requested).
# ==============================================================================================
FAT = {
    "brain_wm":            (V(0.181, "PRIMARY", "Woo86 WM lipid 18.1 % (assumed 50 % sphingomyelin, 25 % cerebroside, 25 % cholesterol — membrane lipid)", "g/g"),
                            V(0.0, "THEORY", "membrane lipid is MR-invisible at TE >= 1 ms; water-fat decomposition of normal brain returns PDFF ~ 0", None, (0.0, 0.01))),
    "brain_gm":            (V(0.053, "PRIMARY", "Woo86 GM lipid 5.3 % (membrane lipid)", "g/g"),
                            V(0.0, "THEORY", "as WM: membrane lipid invisible; PDFF ~ 0", None, (0.0, 0.01))),
    "csf":                 (V(0.0, "PRIMARY", "Woo86 CSF: no lipid", "g/g"), V(0.0, "PRIMARY", "no lipid", None)),
    "spinal_cord_wm":      (V(0.18, "THEORY", "as brain WM (Woo86 18.1 %)", "g/g"), V(0.0, "THEORY", "as brain WM", None, (0.0, 0.01))),
    "skeletal_muscle":     (V(0.042, "PRIMARY", "Woo86 skeletal muscle 2: 4.2 % (compositions 1-3: 6.8 / 4.2 / 1.6 %)", "g/g", (0.016, 0.068)),
                            V(0.03, "RECALLED", "PDFF-lit: healthy thigh/calf muscle PDFF ~ 1-5 % (intra- plus extramyocellular lipid); rises to 10-50 % in dystrophy and sarcopenia. Hu11 read 2026-09-10: no organ table - Grimm 2018 re-requested", None, (0.01, 0.05))),
    "articular_cartilage": (V(0.0, "PRIMARY", "Woo86 cartilage: no lipid column (11 % chondroitin sulphate)", "g/g"), V(0.0, "THEORY", "no mobile lipid", None)),
    "achilles_tendon":     (V(0.01, "PRIMARY", "Woo86 connective tissue lipid 1.0 %", "g/g"), V(0.0, "THEORY", "no mobile lipid in tendon proper; peritendinous fat is partial volume", None, (0.0, 0.02))),
    "cortical_bone":       (V(0.0, "PRIMARY", "Woo86 cortical bone: no lipid column (58 % mineral ash)", "g/g"),
                            V(0.02, "THEORY", "Haversian/Volkmann canals carry marrow fat; UTE water-fat studies report a small fat signal fraction in cortical bone; not opened", None, (0.0, 0.10))),
    "bone_marrow_vertebral": (V(0.60, "PRIMARY", "Woo86 red marrow 39.7 %, yellow marrow 80.4 % lipid; adult lumbar marrow is a mixture", "g/g", (0.397, 0.804)),
                            V(0.33, "PRIMARY", "LeS16 Table 1: FF 33+/-8 % over L1-L5 at 1.5 T (n = 8 healthy), rising ~ 2 % per vertebra L1->L5 and with age; Idi15 T12 / L1 43.2+/-9.5 / 43.5+/-10.2 % in NAFLD patients of median age 47 (PRIMARY, a different population)", None, (0.25, 0.44))),
    "myocardium":          (V(0.062, "PRIMARY", "Woo86 heart 2: 6.2 % (compositions 1-3: 10.0 / 6.2 / 2.4 %; includes epicardial fat in the gross tissue)", "g/g", (0.024, 0.10)),
                            V(0.01, "RECALLED", "PDFF-lit / Dallas Heart Study MRS: myocardial triglyceride ~ 0.5-1.5 % in lean subjects, higher in obesity and diabetes. Hu11 read 2026-09-10: no organ table - Szczepaniak 2003 re-requested", None, (0.003, 0.03))),
    "blood_arterial":      (V(0.006, "PRIMARY", "Woo86 whole blood lipid 0.6 % (plasma 0.7 %)", "g/g"), V(0.0, "THEORY", "plasma lipoprotein lipid is not resolved as a fat signal fraction at clinical resolution", None, (0.0, 0.01))),
    "liver":               (V(0.046, "PRIMARY", "Woo86 liver 2: 4.6 % (compositions 1-3: 7.8 / 4.6 / 1.5 %; membrane plus triglyceride)", "g/g", (0.015, 0.078)),
                            V(0.019, "PRIMARY", "Szc05 (read): low-risk subgroup of the Dallas Heart Study (n = 345) median HTGC 1.9 %, 90th / 95th percentile 4.3 / 5.56 % - the 95th percentile is the steatosis cut-off; the whole cohort (n = 2,287) median 4.69 %, 5th-95th 0.99-22.86 %. HTGC is methylene / (methylene + water) with a fixed T2 correction, i.e. a signal fat fraction that the field quotes as the PDFF cut-off (Ree11). Steatosis grades on MRI-PDFF: 6.4 / 17.4 / 22.1 % (Tang13 origin; Tang15 validation; Gug23 rounds to 6 / 17 / 22 %)", None, (0.0, 0.0556))),
    "spleen":              (V(0.018, "PRIMARY", "Woo86 spleen lipid 1.8 %", "g/g"), V(0.01, "RECALLED", "PDFF-lit: splenic PDFF ~ 0-2 % (used as the in-body zero-fat reference in some PDFF pipelines). Hu11 read 2026-09-10: no organ table; no spleen-PDFF primary on hand", None, (0.0, 0.03))),
    "kidney_cortex":       (V(0.048, "PRIMARY", "Woo86 kidney 2: 4.8 % (compositions 1-3: 6.9 / 4.8 / 2.8 %; whole kidney)", "g/g", (0.028, 0.069)),
                            V(0.017, "PRIMARY", "Idi15 (read): renal cortex MRI-PDFF 1.7 +/- 1.4 % (median 1.3 %, range 0.1-7.6 %) in 41 NAFLD patients at 1.5 T IDEAL-IQ, uncorrelated with liver fat; renal sinus fat 51 +/- 15.5 % is excluded", None, (0.001, 0.076))),
    "kidney_medulla":      (V(0.048, "PRIMARY", "Woo86 whole kidney (no cortex/medulla split)", "g/g", (0.028, 0.069)),
                            V(0.017, "THEORY", "as cortex: Idi15 measured the cortex only; no medullary PDFF on hand", None, (0.001, 0.076))),
    "pancreas":            (V(0.128, "PRIMARY", "Woo86 pancreas lipid 12.8 % (interlobular fat included in the gross organ)", "g/g"),
                            V(0.044, "PRIMARY", "Kuhn15 (read): SHIP general population, n = 1,241, mean pancreatic PDFF 4.4 % (head 4.6, body 4.9, tail 3.9; adjusted 4.46 %, 95 % CI 4.16-4.76), no dependence on glucose tolerance, rising with BMI and age; Idi15 in NAFLD: 5.7 +/- 5.6 % (median 4.0, 0.3-32.8), 12.2 % in diabetics", None, (0.01, 0.12))),
    "prostate_pz":         (V(0.012, "PRIMARY", "Woo86 prostate lipid 1.2 %", "g/g"), V(0.0, "THEORY", "no mobile lipid in the gland; periprostatic fat is partial volume", None, (0.0, 0.02))),
    "breast_fibroglandular": (V(0.309, "PRIMARY", "Woo86 mammary gland 2: 30.9 % (compositions 1-3: 56.2 / 30.9 / 5.6 % — fatty / mixed / glandular)", "g/g", (0.056, 0.562)),
                            V(0.30, "RECALLED", "PDFF-lit: fibroglandular ROIs 10-40 % by partial volume; whole-breast PDFF 60-90 % depending on density category", None, (0.10, 0.60))),
    "adipose_tissue":      (V(0.741, "PRIMARY", "Woo86 adipose tissue 2: 74.1 % (compositions 1-3: 61.4 / 74.1 / 87.3 %)", "g/g", (0.614, 0.873)),
                            V(0.94, "SECONDARY", "Gug23 (practical guide, read): subcutaneous fat PDFF 80-100 %, typically 93-96 % - the in-body reference used to check ROI scaling; visceral slightly lower (RECALLED)", None, (0.80, 1.0))),
}
for _e in ENTRIES:
    _lm, _pdff = FAT[_e["key"]]
    _e["properties"]["lipid_mass_fraction"] = _lm
    _e["properties"]["pdff"] = _pdff
del _e, _lm, _pdff

# ==============================================================================================
# PATHOLOGY AXIS (v2.3, charter §10 step 8c/8e) — one disease operating point per organ where a primary supplies it.
# Rows inherit the bulk properties of their base entry (deep copy) except the overrides given; component sets are their own.
# ==============================================================================================
_STEATOSIS_T2_NOTE = ("water and fat T2 are Byd08 Table II (STEAM at 1.5 T in 21 fatty livers: water 36.2 +/- 4.9 ms, CH2 74.8 +/- 19.2 ms); the "
                      "fractions are the row's operating point (PDFF by construction: fat protons / all visible protons at TE = 0). The fat pool is "
                      "chemically shifted (Ham11 six-peak spectrum, 70 % at 1.3 ppm) and J-coupled, so under a CPMG train its apparent T2 depends on echo "
                      "spacing (Hen92) and its true signal is a multi-frequency, not a mono-exponential, decay: this row is scored under the T2 kernel it is "
                      "known to violate, like the adipose row, and its functional (fat fraction from T2 alone) is the wrong-tool functional; PDFF is what "
                      "chemical-shift-encoded imaging measures with slope ~ 1 against MRS (Yok11, Arm18). The normal row's THEORY vascular tail is not carried: "
                      "the STEAM primaries see one water T2 in fatty liver, and the question this row asks is fat against water at ratio ~ 2")

variant("liver", "liver_steatosis_pdff10", "parenchyma, hepatic steatosis at PDFF 10 % (histologic grade 1)",
    condition={"name": "hepatic steatosis, grade 1", "kind": "pathology",
               "operating_point": "PDFF 0.10: inside the grade-1 band 6.4-17.4 % (Tang13 thresholds, Tang15 validation, Gug23 6-17 %); Sch15 grade-1 mean 9.2 +/- 5.8 %"},
    clinical_delta=D("fat fraction (1 - mass below 55 ms)", 0.019, 0.10, "PRIMARY",
                     "normal: Szc05 low-risk median 1.9 % (cut-off 5.56 %); disease: the row's operating point, the grade-1 band of Tang13 / Tang15 and Sch15's grade-1 mean",
                     note="delta = +0.081 from normal; the grade steps around this point are 6.4 -> 17.4 % (0.11 wide), so grading needs SD < ~ 0.02-0.04 as well"),
    components={"T2": {"kernel": "t2_cpmg", "field_T": 1.5, "status": "PRIMARY",
                       "list": [C("liver water (hepatocellular + sinusoidal, one STEAM peak)", 0.90, 36.2, "PRIMARY", "Byd08 Table II water peak T2 36.2 +/- 4.9 ms (1.5 T STEAM, TE 20-70 ms, 21 fatty livers); dB04 bulk 46 in normal liver; the fraction is 1 - PDFF", (31, 46)),
                                C("triglyceride protons (methylene-dominated, chemically shifted, J-coupled)", 0.10, 74.8, "PRIMARY", "Byd08 Table II CH2 (1.2-1.3 ppm) T2 74.8 +/- 19.2 ms at 1.5 T; Ham11 62 ms at 3 T; fraction = PDFF 0.10 (operating point)", (56, 94))],
                       "functional": "fat fraction (1 - mass below 55 ms)", "functional_threshold": 55.0,
                       "typical_acquisition": {"n_echoes": 16, "dTE_ms": 8.0, "first_echo_snr": 60.0},
                       "note": _STEATOSIS_T2_NOTE}},
    theory={"pools": ["hepatocyte cytoplasmic water", "sinusoidal blood (partially exchange-averaged into the water peak)", "bile", "intracellular triglyceride droplets (macro- and microvesicular; 10 % of visible protons here)",
                      "non-aqueous protons"],
            "n_pools": 5, "exchange": "Water pools exchange as in the normal row; the triglyceride pool does not exchange with water and is separated by chemical shift (3.4 ppm), not by relaxation; its CPMG decay is J-modulated.",
            "n_apparent_T2": 2, "n_resolvable_clinical_T2": 1,
            "rationale": "Ratio ~ 2 between water (36 ms) and fat (75 ms) with a 10 % minor fraction: at the resolvability floor of charter section 1.2 (delta ~ 2.4-2.7 at SNR 100) and misspecified for a pure-exponential kernel - the fat axis's first pathological row, expected to fail on T2 and to be the case chemical-shift encoding solves."},
    sources=["Byd08", "Ham11", "Szc05", "Tang13", "Tang15", "Sch15", "Gug23", "Yok11", "Hen92", "dB04"],
    property_overrides={"pdff": V(0.10, "PRIMARY", "operating point: histologic grade 1 (Tang13 6.4-17.4 %, Tang15 Table 3 validation; Sch15 grade-1 mean 9.2 +/- 5.8 %; Gug23 6-17 %)", None, (0.064, 0.174)),
                        "water_content": V(0.68, "THEORY", "Woo86 liver 74.5 % water reduced by a 10 % triglyceride pool by volume (~ 0.9 g/ml): a working value", "g/g", (0.65, 0.72))})

variant("liver", "liver_steatosis_pdff25", "parenchyma, hepatic steatosis at PDFF 25 % (histologic grade 3)",
    condition={"name": "hepatic steatosis, grade 3", "kind": "pathology",
               "operating_point": "PDFF 0.25: above the grade-3 threshold 22.1 % (Tang13 / Tang15; Gug23 > 22 %); Sch15 grade-3 mean 26.8 +/- 8.2 %; Tang15 cohort maximum 37.5 %, Szc05 cohort maximum 47.5 %"},
    clinical_delta=D("fat fraction (1 - mass below 55 ms)", 0.019, 0.25, "PRIMARY",
                     "normal: Szc05 low-risk median 1.9 %; disease: the row's operating point above Tang13's 22.1 % grade-3 threshold, near Sch15's grade-3 mean 26.8 %",
                     note="delta = +0.231 from normal; the nearest grade step is 17.4 -> 22.1 % (0.047 wide), so grade-2-vs-3 classification needs SD < ~ 0.016"),
    components={"T2": {"kernel": "t2_cpmg", "field_T": 1.5, "status": "PRIMARY",
                       "list": [C("liver water (hepatocellular + sinusoidal, one STEAM peak)", 0.75, 36.2, "PRIMARY", "Byd08 Table II water peak T2 36.2 +/- 4.9 ms; the fraction is 1 - PDFF", (31, 46)),
                                C("triglyceride protons (methylene-dominated, chemically shifted, J-coupled)", 0.25, 74.8, "PRIMARY", "Byd08 Table II CH2 T2 74.8 +/- 19.2 ms; fraction = PDFF 0.25 (operating point)", (56, 94))],
                       "functional": "fat fraction (1 - mass below 55 ms)", "functional_threshold": 55.0,
                       "typical_acquisition": {"n_echoes": 16, "dTE_ms": 8.0, "first_echo_snr": 60.0},
                       "note": _STEATOSIS_T2_NOTE}},
    theory={"pools": ["hepatocyte cytoplasmic water", "sinusoidal blood (partially exchange-averaged into the water peak)", "bile", "intracellular triglyceride droplets (25 % of visible protons here)", "non-aqueous protons"],
            "n_pools": 5, "exchange": "as the grade-1 row; at this fat load the water signal is also T2*-shortened around droplets (Byd08 expected T2* ~ 30 ms water / ~ 10 ms fat at 1.5 T), which the CPMG kernel does not see but a GRE-based method must model.",
            "n_apparent_T2": 2, "n_resolvable_clinical_T2": 1,
            "rationale": "Same ratio ~ 2 as the grade-1 row with a 25 % minor fraction: the fraction is large enough for the CRLB to say something at high SNR, which makes the pair of rows a fraction sweep at fixed ratio - the fat-axis counterpart of the 20/80 vector of charter section 1.2."},
    sources=["Byd08", "Ham11", "Szc05", "Tang13", "Tang15", "Sch15", "Gug23", "Yok11", "Hen92", "dB04"],
    property_overrides={"pdff": V(0.25, "PRIMARY", "operating point: histologic grade 3 (Tang13 > 22.1 %, Tang15 Table 3 validation; Sch15 grade-3 mean 26.8 +/- 8.2 %; Gug23 > 22 %)", None, (0.221, 0.475)),
                        "water_content": V(0.58, "THEORY", "Woo86 liver 74.5 % water reduced by a 25 % triglyceride pool by volume: a working value", "g/g", (0.52, 0.65))})

variant("prostate_pz", "prostate_pz_cancer", "peripheral zone, prostate cancer (malignant PZ)",
    condition={"name": "prostate cancer, peripheral zone", "kind": "pathology",
               "operating_point": "Sab17 Radiology Table 2 malignant PZ (18 patients, 378 ROIs): LWF 0.10 +/- 0.05 at T2short 81 +/- 21 / T2long 548 +/- 188 ms, gmT2 94 +/- 27, Ncomp 1.81; JMRI Table 3 medians 72 / 507 ms, LWF 0.07 (higher Gleason grades become mono-exponential)"},
    clinical_delta=D("luminal water fraction (1 - mass below 200 ms)", 0.24, 0.10, "PRIMARY",
                     "Sab17 Radiology Table 2: 0.24 +/- 0.09 nonmalignant vs 0.10 +/- 0.05 malignant PZ, same protocol; LWF vs Gleason score rho -0.78",
                     note="delta = -0.14; histological luminal area 27.2 % -> 11.6 % (JMRI Table 2)"),
    components={"T2": {"kernel": "t2_cpmg", "field_T": 3.0, "status": "PRIMARY",
                       "list": [C("epithelial / stromal water", 0.90, 81.0, "PRIMARY", "Sab17 Radiology Table 2 malignant PZ T2short 81 +/- 21 ms; JMRI median 72", (60, 102)),
                                C("luminal water", 0.10, 548.0, "PRIMARY", "Sab17 Radiology Table 2 malignant PZ T2long 548 +/- 188 ms, LWF 0.10 +/- 0.05; JMRI median 507, LWF 0.07", (360, 736), "fraction range ~ 0.03-0.15")],
                       "functional": "luminal water fraction (1 - mass below 200 ms)", "functional_threshold": 200.0,
                       "typical_acquisition": {"n_echoes": 64, "dTE_ms": 25.0, "first_echo_snr": 100.0},
                       "note": "the disease operating point of the strongest clinically validated two-component case: the ratio (~ 6.8) is unchanged, the minor fraction falls from 0.24 to 0.10 - a pure amplitude-vector change, which is exactly what charter section 1.2 found decides estimability; Sab17's 64 x 25 ms train and SNR ~ 100 are carried"}},
    theory={"pools": ["residual glandular lumen fluid (11.6 % of section area by histology)", "tumour epithelial cell water (crowded, replaces lumen)", "stromal water", "vascular blood"],
            "n_pools": 4, "exchange": "as the normal row; cancer replaces lumen with cells, so the slowly exchanging luminal pool shrinks and the two-component structure fades toward mono-exponential (Ncomp 1.81; higher grades ~ 1).",
            "n_apparent_T2": 2, "n_resolvable_clinical_T2": 2,
            "rationale": "Well-separated but with a 10 % minor fraction: the harness's test of whether a functional (LWF) stays estimable when its value halves at fixed ratio and window - the decision the clinical test (LWF cut-off between 0.10 and 0.24) actually needs."},
    sources=["Sab17", "dB04", "Boj17"])

variant("skeletal_muscle", "skeletal_muscle_venous_filling", "skeletal muscle (soleus) under venous filling - oedema surrogate",
    condition={"name": "venous filling (vascular compartment expanded)", "kind": "physiological",
               "operating_point": "Ara14 Table 1 vascular-filling state (thigh cuff at venous pressure), 3 T ISIS-CPMG fat-saturated, n = 8: 85.8 / 14.2 % at 32.6 / 181 ms, against 92.0 / 8.0 % at 32.1 / 159 ms with free perfusion and 94.6 / 5.4 % at 31.7 / 139 ms when drained"},
    clinical_delta=D("extracellular / vascular fraction (1 - mass below 60 ms)", 0.080, 0.142, "PRIMARY",
                     "Ara14 Table 1: long fraction 8.0 +/- 2.4 % (free perfusion) -> 14.2 % (venous filling), paired within-protocol",
                     kind="physiological", note="delta = +0.062; the measured surrogate for the oedema / extracellular-expansion pathologies (inflammatory myopathy, denervation) for which no multi-component primary is on hand"),
    components={"T2": {"kernel": "t2_cpmg", "field_T": 3.0, "status": "PRIMARY",
                       "list": [C("intracellular + interstitial water", 0.858, 32.6, "PRIMARY", "Ara14 Table 1 venous filling: 85.8 % at 32.6 ms (free perfusion 92.0 % at 32.1 +/- 0.4 ms)", (30, 35)),
                                C("vascular water (expanded)", 0.142, 181.0, "PRIMARY", "Ara14 Table 1 venous filling: 14.2 % at 181 ms (free perfusion 8.0 +/- 2.4 % at 159 +/- 25 ms); three-site exchange model assigns this pool to venous blood (T2 fixed at 186 ms in the model)", (139, 206), "rises with venous filling, oedema, exercise")],
                       "functional": "extracellular / vascular fraction (1 - mass below 60 ms)", "functional_threshold": 60.0,
                       "typical_acquisition": CPMG_REF,
                       "note": "Ara14's own protocol is 1000 echoes x 1 ms (even echoes used, 2 ms effective) in a 52 cm3 ISIS voxel at 3 T with fat saturation; its SNR is not tabulated, so the reference train is carried as the typical acquisition and the 3 T two-component description is the row. The normal row (Saab99 at 1.89 T) has four components and a 10 ms first echo sees three; this variant is the K = 2 clinical picture at 3 T, which is why it is also the right comparator for the normal muscle Delta"}},
    theory={"pools": ["myofibrillar + sarcoplasmic water (one 32 ms peak at 2 ms spacing)", "interstitial water (T2 ~ 36-41 ms in the exchange model, merged)", "venous / capillary blood (expanded to ~ 14 % of the signal)", "macromolecule-bound water (filtered by the ISIS pulses)", "intramuscular fat (saturated)"],
            "n_pools": 5, "exchange": "Ara14's three-site two-exchange model: intracellular residence ~ 1 s, vascular residence 0.3-3 s - slow on the T2 scale, so the vascular pool survives as its own component and its fraction tracks blood volume.",
            "n_apparent_T2": 2, "n_resolvable_clinical_T2": 2,
            "rationale": "Ratio ~ 5.5 with the minor fraction at 14 %: the pair of muscle rows (8 % -> 14 % at fixed ratio) asks whether a 6-point change in a vascular / extracellular fraction is a 3-sigma event at clinical SNR - the oedema question in bound units."},
    sources=["Ara14", "Saab99", "St05", "Gold04"])

variant("brain_wm", "brain_wm_ms_lesion", "white matter, chronic multiple-sclerosis lesion (demyelinated)",
    condition={"name": "multiple sclerosis lesion (chronic, demyelinated)", "kind": "pathology",
               "operating_point": "MacK94: 95 volumes from 34 lesions in four MS patients, MWF 6.4 / 5.8 / 4.7 / 4.1 % per patient (SE 0.6-1.1 %), 95 % CI 0-13 %; lesions show >= 10 % more water and an elevated T2 than normal-appearing WM (Fig. 5-6); the row takes the four-patient mean 5.25 %"},
    clinical_delta=D("myelin water fraction (mass below 40 ms)", 0.113, 0.0525, "PRIMARY",
                     "MacK94 lesion MWF (mean of four patients, 5.25 %) against the dictionary's normal WM 0.113 (Whi97); within MacK94 15.6 % -> ~ 5 %",
                     note="delta = -0.061 (dictionary values), -0.10 within MacK94"),
    components={"T2": {"kernel": "t2_cpmg", "field_T": 1.5, "status": "PRIMARY",
                       "list": [C("myelin water (residual)", 0.0525, 15.0, "PRIMARY", "MacK94: lesion MWF 4.1-6.4 % by patient (10-55 ms window, 32 x 15 ms at 1.5 T); T2 taken at the normal row's 15 ms", (10, 20), "fraction range 0.0-0.13 (95 % CI)"),
                                C("intra/extracellular water (oedematous, gliotic)", 0.9275, 100.0, "THEORY", "MacK94 plots lesion T2 distributions with an elevated IE peak and >= 10 % more water but does not tabulate the lesion IE T2; placed at 100 ms (85-150) against 77 ms in normal WM (Whi97) as a working value", (85, 150)),
                                C("free/CSF-like water", 0.02, 2000.0, "THEORY", "as the normal row (partial volume; periventricular lesions have more)", (1000, 2500))],
                       "functional": "myelin water fraction (mass below 40 ms)", "functional_threshold": 40.0,
                       "typical_acquisition": CPMG_REF,
                       "note": "the MS-lesion row keeps the normal row's three-component structure so that the two are compared like for like; only the myelin fraction rests on the primary (MacK94), the lesion IE T2 is a working value (THEORY) until a primary tabulates it. With MWF ~ 5 % the row sits with grey matter (3.1 %) below the ~ 5 % floor that the normal-WM evaluation found - the question is whether 'demyelinated' is distinguishable from 'normal' at SNR 100, i.e. whether SD(MWF) <= 0.02"}},
    theory={"pools": ["residual myelin water (~ 5 % of water)", "intra-axonal water (axons partly preserved)", "expanded extracellular / oedematous water", "gliotic (astrocytic) water", "blood", "CSF partial volume", "non-aqueous protons (reduced: myelin lipid lost)"],
            "n_pools": 7, "exchange": "as normal WM; with the myelin sheath gone the residual short pool is small and the IE pool is larger and slower (more free water), so the apparent structure moves toward K = 1 with a long tail.",
            "n_apparent_T2": 3, "n_resolvable_clinical_T2": 1,
            "rationale": "The disease operating point of the myelin case: the MWF falls by a factor ~ 2-3 to the level where the normal-WM evaluation already found minor components unestimable, so the clinical question - is this lesion demyelinated - is a detection problem on the functional (SD <= |Delta| / 3 = 0.02), not a component-resolution problem."},
    sources=["MacK94", "Whi97", "Lau07", "St05"],
    property_overrides={"water_content": V(0.78, "THEORY", "MacK94: lesions show at least a 10 % increase in water content over normal WM (0.708 g/ml, Whi97): 0.71 x 1.1", "g/g", (0.75, 0.85)),
                        "lipid_mass_fraction": V(0.10, "THEORY", "myelin lipid lost with demyelination; Woo86 WM 18.1 % is the normal value; no lesion composition primary on hand", "g/g", (0.05, 0.18))})

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
    "2026-09-09 v2.2 (verification pass, charter section 10 step 8a): twelve priority-1 PDFs read from literature/ and applied. "
    "Prostate (Sabouri 2017 Radiology Table 2 / JMRI Table 3): the last RECALLED component set moves to PRIMARY - LWF 0.24 "
    "(not 0.35), T2short 90 / T2long 545 ms, and the protocol is 64 x 25 ms at SNR ~ 100 (not 64 x 8 ms). Brain WM / GM "
    "(Whittall 1997 Tables 1-3, MacKay 1994): MWF 0.113 / 0.031 with the Whittall structure averages, IE gmT2 77 / 80 ms; the "
    "CSF-like partial-volume components relabelled THEORY (seen but not tabulated by the primaries). Spinal cord (MacMillan 2011 "
    "Tables 1, 3, 4): MWF 0.296, IE 100 ms. Skeletal muscle (Saab 1999 Table 1): four components at 10.9 / 27.8 / 45.5 / 11.3 % "
    "(the v2 5 % for the 114 ms pool was the fifth component's share), field 1.89 T; Araujo 2014 (3 T, two components 92 / 8 % at "
    "32 / 159 ms, exchange model) recorded in the note. WM T1 (Labadie 2014 Table 2): 0.083 at 225 ms, T1,long 1.06 s, Look-Locker "
    "geometric TIs. Tendon (Du 2012 Table 1): 71.4 % at 1.28 ms + 28.6 % at 17.65 ms (the v2 numbers were the ligament row); Du 2012 "
    "also added to cartilage and cortical bone notes; Bouhrara 2015 (Rician-correct biexponential T2*, bovine nasal cartilage) to the "
    "cartilage note; Prasloski 2012 (EPG stimulated-echo correction, simulated WM truth 15 / 75 / 10 %) to the WM note. Stanisz 2005 "
    "Table 1 re-read from the publisher PDF: every St05 value moves to PRIMARY unchanged. PDFF ranges for the lean organs stay "
    "RECALLED: none of the 57 PDFs on hand is a water-fat paper for those organs (requests added to literature-requests.md).",
    "2026-09-10 v2.3 (water-fat pass and pathology axis, charter section 10 step 8c/8e): the fifteen water-fat papers of "
    "literature-requests.md #58-#72 read from literature/. Schema: `condition` and `clinical_delta` on every entry; pathology rows "
    "built with variant() inherit their base row's bulk properties. Five variants added (24 entries): steatotic liver at PDFF 10 % "
    "(grade 1) and 25 % (grade 3) with the water / fat T2 pair of Bydder 2008 Table II (36.2 / 74.8 ms at 1.5 T, PRIMARY) and the "
    "grade calibration of Tang 2013 (origin) / Tang 2015 (validation) / Schwimmer 2015 (per-grade means) / Guglielmo 2023 (6 / 17 / "
    "22 %); malignant prostate PZ (Sabouri 2017 Table 2: LWF 0.10 at 81 / 548 ms); venous-filled skeletal muscle (Araujo 2014 Table 1: "
    "14.2 % at 181 ms, the oedema surrogate); MS-lesion white matter (MacKay 1994: MWF 4.1-6.4 %, IE T2 a THEORY working value). "
    "clinical_delta on the normal rows where a primary gives the change: WM (MWF 0.113 -> 0.0525), cord (age, 0.296 -> 0.2655), "
    "muscle (0.080 -> 0.142, Araujo paired states), prostate (0.24 -> 0.10). PDFF column: liver -> PRIMARY (Szczepaniak 2005 read: "
    "low-risk median 1.9 %, 95th percentile 5.56 %), pancreas -> PRIMARY (Kuehn 2015 4.4 %; Idilman 2015 5.7 % in NAFLD), kidney "
    "cortex -> PRIMARY (Idilman 2015 1.7 %), medulla -> THEORY (as cortex), adipose -> SECONDARY (Guglielmo 2023 93-96 %); muscle, "
    "myocardium, spleen and breast stay RECALLED because Hu 2011 carries no organ table (Grimm 2018 and Szczepaniak 2003 "
    "re-requested). Liver bulk-T2 sources gain the STEAM water / fat T2 at both fields (Bydder 2008, Hamilton 2011). Correction to the "
    "v2.1/v2.2 note text: the 6.4 / 17.4 / 22.1 % grade thresholds originate in Tang 2013 (NASH CRN) and are validated, not proposed, "
    "in Tang 2015; Schwimmer 2015 proposes no grade cut-offs (the 5.3 / 14.5 / 22.1 % attributed to it in literature-requests v4 are "
    "not in the paper).",
]
