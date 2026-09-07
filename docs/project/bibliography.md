# Annotated bibliography (charter G1 — the one running list)

**Version:** 0.2 — opened 2026-09-07 (v0.1); revised the same day (v0.2: DOIs added and confirmed against Crossref/OpenAlex or publisher pages for every foundations and noise-track row; Lanczos moved to CHECKED-PRIMARY from Eric's page images; three citation corrections — Bertero 1984 Part II authors, Sabouri's second paper, Vaidyanathan & Pal author order; tissue-dictionary sources expanded with the relaxation/PD/diffusion literature actually opened). Nothing in this project may cite a source that is not on this list; every source read gets a row. Where to download each paper: `literature-requests.md`.

**Fields.** *Claim / use* — what the project takes from it. *Evidence* — primary (original result), review, dataset/standard, textbook, tertiary (website/textbook table). *Status* — `CHECKED-PRIMARY` (the text/table was read), `CHECKED-ABSTRACT` (abstract, same-author conference abstract, review table or mirrored PDF read), `BIBLIO-ONLY` (record and DOI confirmed; content not opened), `RECALLED` (from memory; not opened). *Checked* — session date the status was earned.

## Foundations (charter §1.2, §4 Phase 0 table)

| Source | DOI | Claim / use | Evidence | Status | Checked |
|---|---|---|---|---|---|
| Lanczos C. *Applied Analysis*. Prentice-Hall 1956 (Dover 1988, ISBN 0-486-65656-X), ch. IV §23 pp. 272–279 | archive.org/details/appliedanalysis00lanc_0 | 24 observations at Δx = 0.05 from 0, two decimals "accurate to ½ unit"; Prony separation; two-exponential fit 2.202e^{−4.45x} + 0.305e^{−1.58x} matching to 0.006 (k = 5), RMS 0.0026; generating law 0.0951e^{−x} + 0.8607e^{−3x} + 1.5576e^{−5x}; "numerically equivalent" | textbook | `CHECKED-PRIMARY` (page images pp. 272–279) | 2026-09-07 |
| NIST StRD Lanczos1/2/3 | itl.nist.gov/div898/strd/nls | Generating function, grid, certified fits at 14/6/5 digits | dataset | `CHECKED-PRIMARY` | 2026-09-06 |
| Varah JM. *On fitting exponentials by nonlinear least squares*. SIAM J. Sci. Stat. Comput. 6(1):30–44 (1985); UBC TR 82-02 (1982) | 10.1137/0906003 | Uses Lanczos's 3-exp data (cites p. 273) and credits Lanczos (p. 279) for the ill-conditioning; the TR does **not** quote the 2-exp coefficients | primary | TR `CHECKED-PRIMARY`; journal `BIBLIO-ONLY` | 2026-09-06/07 |
| Istratov AA & Vyvenko OF. *Exponential analysis in physical phenomena*. Rev. Sci. Instrum. 70(2):1233–1257 (1999) | 10.1063/1.1149581 | Anchor review; minimum resolvable ratio vs SNR. Secondary restatement: Steinbeck & Chmelka, JACS 127:11624 (2005), doi 10.1021/ja0439064 — "SNR 10³: two components need ratio ≥ 2; three components ≥ 3.5" | review | `BIBLIO-ONLY` (constant convention still to be read) | 2026-09-07 |
| McWhirter JG & Pike ER. J. Phys. A 11(9):1729–1745 (1978) | 10.1088/0305-4470/11/9/007 | Mellin diagonalisation; singular value √(π/cosh πω); resolution limit | primary | `BIBLIO-ONLY` | 2026-09-07 |
| Bertero M, Boccacci P & Pike ER. Proc. R. Soc. Lond. A 383(1784):15–29 (1982) | 10.1098/rspa.1982.0117 | Recoverable count grows as ln SNR; finite support raises it | primary | `BIBLIO-ONLY` | 2026-09-07 |
| Bertero M, **Boccacci P** & Pike ER. Part II: optimum sampling points. Proc. R. Soc. Lond. A 393(1804):51–65 (1984) — *authors corrected from "Brianzi"* | 10.1098/rspa.1984.0045 | Geometric sampling in t as the optimum design | primary | `BIBLIO-ONLY` | 2026-09-07 |
| Bertero M, Brianzi P & Pike ER. Part III: sampling and truncation of data. Proc. R. Soc. Lond. A 398(1814):23–44 (1985) | 10.1098/rspa.1985.0024 | Finite-window effects (the paper the window rule should be positioned against) | primary | `BIBLIO-ONLY` | 2026-09-07 |
| Epstein CL & Schotland JC. *The bad truth about Laplace's transform*. SIAM Rev. 50(3):504–520 (2008) | 10.1137/060657273 | Closed-form spectrum; decay rate explicit. Phase 0: per-index form is asymptotic, the count check holds | primary | `BIBLIO-ONLY` (author preprint open) | 2026-09-07 |
| Ostrowsky N, Sornette D, Parker P & Pike ER. Optica Acta 28(8):1059–1070 (1981) | 10.1080/713820704 | Exponential-sampling theorem; geometric T grids | primary | `BIBLIO-ONLY` | 2026-09-07 |
| Transtrum MK, Machta BB & Sethna JP. PRL 104:060201 (2010); PRE 83:036701 (2011); Transtrum, Machta, Brown, Daniels, Myers & Sethna, J. Chem. Phys. 143:010901 (2015) | 10.1103/PhysRevLett.104.060201; 10.1103/PhysRevE.83.036701; 10.1063/1.4923066 | Sloppy models; sum of exponentials as the canonical case | primary | `BIBLIO-ONLY` | 2026-09-07 |
| Bates DM & Watts DG. J. R. Stat. Soc. B 42(1):1–25 (1980, with discussion); *Nonlinear Regression Analysis and Its Applications* (Wiley 1988) | 10.1111/j.2517-6161.1980.tb01094.x | Intrinsic vs parameter-effects curvature | primary / textbook | `BIBLIO-ONLY` | 2026-09-07 |
| Rife DC & Boorstyn RR. IEEE Trans. Inf. Theory 20(5):591–598 (1974) | 10.1109/TIT.1974.1055282 | Frequency CRLB ∝ 1/(SNR·N³); reproduced by `tests/test_crlb.py` | primary | `BIBLIO-ONLY` | 2026-09-07 |
| Hansen PC. BIT 30(4):658–672 (1990) | 10.1007/BF01933214 | Discrete Picard condition and smoothing | primary | `BIBLIO-ONLY` | 2026-09-07 |

## Noise track (charter §3)

| Source | DOI | Claim / use | Evidence | Status | Checked |
|---|---|---|---|---|---|
| Benedict TR & Soong TT. IEEE Trans. Inf. Theory 13(3):447–454 (1967) | 10.1109/TIT.1967.1054037 | Joint (A, σ) from a Rician envelope, K = 1 | primary | `BIBLIO-ONLY` | 2026-09-07 |
| Sijbers J & den Dekker AJ. MRM 51(3):586–594 (2004) | 10.1002/mrm.10728 | Joint ML and CRLB, single-amplitude Rician; the K = 1 blocks `mexp/crlb.py` generalises | primary | `BIBLIO-ONLY` | 2026-09-07 |
| Karlsen OT, Verhagen R & Bovée WMMJ. MRM 41(3):614–623 (1999) | 10.1002/(SICI)1522-2594(199903)41:3<614::AID-MRM26>3.0.CO;2-1 | Rician ML for T1 and perfusion | primary | `BIBLIO-ONLY` | 2026-09-07 |
| Bouhrara M, Reiter DA, Celik H, Bonny J-M, Lukas V, Fishbein KW & Spencer RG. MRM 73(1):352–366 (2015; online 2014) | 10.1002/mrm.25111 | Rician-correct biexponential transverse relaxation, cartilage 3 T/7 T | primary | `BIBLIO-ONLY` (PMC4171354 exists) | 2026-09-07 |
| Milford D, Rosbach N, Bendszus M & Heiland S. PLoS ONE 10(12):e0145255 (2015) | 10.1371/journal.pone.0145255 | Free offset and first-echo effects | primary | `BIBLIO-ONLY` | 2026-09-07 |
| Veraart J et al. NeuroImage 142:394–406 (2016) | 10.1016/j.neuroimage.2016.08.016 | MP-PCA | primary | `BIBLIO-ONLY` | 2026-09-07 |
| Robson PM et al. MRM 60(4):895–907 (2008) | 10.1002/mrm.21728 | Pseudo-replica SNR/g-factor | primary | `BIBLIO-ONLY` | 2026-09-07 |
| Koay CG & Basser PJ. J. Magn. Reson. 179(2):317–322 (2006) | 10.1016/j.jmr.2006.01.016 | Rician bias correction | primary | `BIBLIO-ONLY` | 2026-09-07 |
| Moeller S et al. NORDIC, NeuroImage 226:117539 (2021); Aja-Fernández S et al. (MRI 27:1397 (2009); Med. Image Anal. 18:1029 (2014)); Foi A, ISBI 2011; Ramani S, Blu T & Unser M, IEEE TIP 17:1540 (2008) | — | Complex-domain denoising; non-stationary σ / DOF estimation; VST; Monte-Carlo SURE | primary | `RECALLED` | — |

## Method families (Phase 1 anchors; none implemented — G2)

| Source | DOI | Family | Status |
|---|---|---|---|
| Golub GH & Pereyra V. SIAM J. Numer. Anal. 10(2):413–432 (1973) | 10.1137/0710036 | 1 VARPRO | `BIBLIO-ONLY` |
| Kumaresan R & Tufts DW. IEEE Trans. ASSP 30:833 (1982); Hua Y & Sarkar TK. IEEE Trans. ASSP 38:814 (1990); Mandelshtam VA & Taylor HS. J. Chem. Phys. 107:6756 (1997); Nakatsukasa Y, Sète O & Trefethen LN. SIAM J. Sci. Comput. 40:A1494 (2018); Peter T & Plonka G. Inverse Problems 29:025001 (2013); Vetterli M, Marziliano P & Blu T. IEEE Trans. SP 50:1417 (2002); Chen Y & Chi Y. IEEE Trans. IT 60:6576 (2014) | — | 2 Prony / algebraic / FRI / Hankel | `RECALLED` |
| Pal P & Vaidyanathan PP. IEEE Trans. SP 58(8):4167–4181 (2010) — nested arrays; **Vaidyanathan PP & Pal P.** IEEE Trans. SP 59(2):573–586 (2011) — co-prime (*author order corrected*) | 10.1109/TSP.2010.2049264; 10.1109/TSP.2010.2089682 | sampling design (A1); constructions in `mexp/design.py` | `BIBLIO-ONLY` |
| Whittall KP & MacKay AL. J. Magn. Reson. 84(1):134–152 (1989) | 10.1016/0022-2364(89)90011-5 | 3 regularised NNLS | `BIBLIO-ONLY` |
| Provencher SW. Comput. Phys. Commun. 27(3):213–227 and 229–242 (1982) | 10.1016/0010-4655(82)90173-4; 10.1016/0010-4655(82)90174-6 | 3 CONTIN | `BIBLIO-ONLY` |
| Lawson CL & Hanson RJ (1974); Candès EJ & Fernandez-Granda C (2014); Denoyelle, Duval & Peyré (2017); Bretthorst GL (1988); Backus G & Gilbert F (1968); Lasserre JB (2001); Venkataramanan L, Song Y-Q & Hürlimann MD (2002); Prasloski T et al. MRM 67:1803 (2012), doi 10.1002/mrm.23157; Tamir JI et al. MRM 77:180 (2017); Deoni SCL et al. MRM 60:1372 (2008); Lankford CL & Does MD. MRM 69:127 (2013) | — | 3/4/5, Phase 3, cross-cutting, misspecification | `RECALLED` (Prasloski `BIBLIO-ONLY`) |

## Tissue dictionary sources (`mexp/tissue_data.py`; short keys as used there)

| Key | Citation | DOI | What was read | Status |
|---|---|---|---|---|
| St05 | Stanisz GJ, Odrobina EE, Pun J, Escaravage M, Graham SJ, Bronskill MJ, Henkelman RM. MRM 54(3):507–512 (2005) | 10.1002/mrm.20605 | Table 1 via publisher-mirrored PDF | `CHECKED-ABSTRACT`* |
| dB04 | de Bazelaire CMJ, Duhamel GD, Rofsky NM, Alsop DC. Radiology 230(3):652–659 (2004) | 10.1148/radiol.2303021331 | abstract (3 T values) | `CHECKED-ABSTRACT` |
| Han03 / Gold04 | Han E, Gold G, Stainsby J, et al. ISMRM 2003 #450; Gold GE et al. AJR 183(2):343–351 (2004) | 10.2214/ajr.183.2.1830343 | conference abstract table | `CHECKED-ABSTRACT` |
| Wan99 | Wansapura JP, Holland SK, Dunn RS, Ball WS. JMRI 9(4):531–538 (1999) | 10.1002/(SICI)1522-2586(199904)9:4<531::AID-JMRI4>3.0.CO;2-L | abstract (GM/WM T2 possibly transposed) | `CHECKED-ABSTRACT` |
| Wri08 | Wright PJ et al. MAGMA 21:121–130 (2008) | 10.1007/s10334-008-0104-8 | abstract (MPRAGE T1) | `CHECKED-ABSTRACT` |
| Roo07 | Rooney WD et al. MRM 57(2):308–318 (2007) | 10.1002/mrm.21122 | abstract (T1 ∝ B0^0.38 fits; CSF 4300) | `CHECKED-ABSTRACT` |
| Lu05 | Lu H et al. JMRI 22(1):13–22 (2005) | 10.1002/jmri.20356 | via Bojorquez table only | `BIBLIO-ONLY` |
| Boj17 | Bojorquez JZ et al. Magn. Reson. Imaging 35:69–80 (2017) | 10.1016/j.mri.2016.08.021 | review table via mirrored PDF | `CHECKED-ABSTRACT`* |
| RP06 / Kee16 | Rakow-Penner R et al. JMRI 23:87–91 (2006), as tabulated in Keenan KE et al. (NIST breast phantom paper, 2016) | — | tertiary table | `CHECKED-ABSTRACT` |
| vKB13 / Giri09 | von Knobelsdorff-Brenkenhoff F et al. JCMR 15:53 (2013); Giri S et al. JCMR 11:56 (2009) | 10.1186/1532-429X-15-53 | full text (vKB13) | `CHECKED-PRIMARY` |
| OP19 | Oros-Peusquens A-M et al. Front. Neurol. 10:1333 (2019) | 10.3389/fneur.2019.01333 | full text (WM 69.1 %, GM 83.7 % water) | `CHECKED-PRIMARY` |
| Whi97 | Whittall KP et al. MRM 37(1):34–43 (1997) | 10.1002/mrm.1910370107 | abstract | `CHECKED-ABSTRACT` |
| MacK94 | MacKay A et al. MRM 31(6):673–677 (1994) | 10.1002/mrm.1910310614 | full-text preview | `CHECKED-ABSTRACT` |
| Lau07 | Laule C et al. Neurotherapeutics 4(3):460–484 (2007) | 10.1016/j.nurt.2007.05.004 | full text | `CHECKED-PRIMARY` |
| MacM07 / MacM11 | MacMillan EL et al. ISMRM 2007 #2331; NeuroImage 54(2):1083–1090 (2011) | 10.1016/j.neuroimage.2010.08.076 | 2007 abstract | `CHECKED-ABSTRACT` / `BIBLIO-ONLY` |
| Saab99 | Saab G, Thompson RT, Marsh GD. MRM 42(1):150–157 (1999) | 10.1002/(SICI)1522-2594(199907)42:1<150::AID-MRM20>3.0.CO;2-5 | abstract (four components) | `CHECKED-ABSTRACT` |
| Ara14 | Araujo ECA, Fromes Y, Carlier PG. Biophys. J. 106(10):2267–2274 (2014) | 10.1016/j.bpj.2014.04.010 | record only | `BIBLIO-ONLY` |
| Rei09 | Reiter DA, Lin P-C, Fishbein KW, Spencer RG. MRM 61(4):803–809 (2009) | 10.1002/mrm.21926 | full text (PMC2711212) | `CHECKED-PRIMARY` |
| Sab17 | Sabouri S et al. Radiology 284(2):451–459 (2017); Sabouri S et al. JMRI 46(3):861–869 (2017) (*the "MRM 77:2038" citation was wrong*) | 10.1148/radiol.2017161687; 10.1002/jmri.25624 | abstracts | `CHECKED-ABSTRACT` |
| Hor10 | Horch RA, Nyman JS, Gochberg DF, Dortch RD, Does MD. MRM 64(3):680–687 (2010) | 10.1002/mrm.22459 | full text (PMC2933073) | `CHECKED-PRIMARY` |
| Du12 | Du J, Diaz E, Carl M, Bae W, Chung CB, Bydder GM. MRM 67(3):645–649 (2012) | 10.1002/mrm.23047 | abstract (reconstructed) | `CHECKED-ABSTRACT` |
| Lab14 | Labadie C et al. MRM 71(1):375–387 (2014) | 10.1002/mrm.24670 | abstract | `CHECKED-ABSTRACT` |
| LeS16 | Le Ster C et al. JMRI 44(3):549–555 (2016) | 10.1002/jmri.25205 | abstract | `CHECKED-ABSTRACT` |
| Luc08 | Luciani A et al. Radiology 249(3):891–899 (2008) | 10.1148/radiol.2493080080 | full PDF, Table 4 | `CHECKED-PRIMARY` |
| Li17 | Li YT et al. Quant. Imaging Med. Surg. (2017) | 10.21037/qims.2017.02.03 | full text | `CHECKED-PRIMARY` |
| Yam99 | Yamada I et al. Radiology 210(3):617–623 (1999) | 10.1148/radiology.210.3.r99fe17617 | abstract | `CHECKED-ABSTRACT` |
| vBa17 | van Baalen S et al. JMRI (2017) | 10.1002/jmri.25519 | full text | `CHECKED-PRIMARY` |
| Fil15 | Filli L et al. Eur. Radiol. 25:2049 (2015) | 10.1007/s00330-014-3577-z | abstract | `CHECKED-ABSTRACT` |
| Ser24 | Serafin Z et al. Diagnostics 14:571 (2024) | 10.3390/diagnostics14060571 | full text | `CHECKED-PRIMARY` |
| May21 | Mayer P et al. Cancer Imaging 21:13 (2021) | 10.1186/s40644-021-00380-1 | full PDF | `CHECKED-PRIMARY` |
| McG15 | McGill L-A et al. PLoS ONE 10:e0132360 (2015) | 10.1371/journal.pone.0132360 | full text | `CHECKED-PRIMARY` |
| Maz21 | Mazzoli V et al. Front. Neurol. 12:608549 (2021) | 10.3389/fneur.2021.608549 | full text (unit flag) | `CHECKED-PRIMARY` |
| SM25 | Jelescu IO & Budde MD. Front. Phys. 5:61 (2017); bioRxiv 2025 (doi 10.64898/2025.12.06.692761) | 10.3389/fphy.2017.00061 | full text | `CHECKED-PRIMARY` |
| Qiao17 / AR20 | Qiao Y et al. 2017 (Achilles UTE T2*); Abbasi-Rad S et al. arXiv:2002.00209 (2020) | — | full text / preprint | `CHECKED-PRIMARY` |
| RK / MRM-web | Radiology Key "MRI tissue parameters" Table 6-1; mrimaster.com ADC table | — | website tables | tertiary, `CHECKED` |
| Ber83 | Bernardino ME et al. AJR 141(6):1203–1208 (1983) | 10.2214/ajr.141.6.1203 | abstract (no values) | `CHECKED-ABSTRACT` |
| Tas24 | Tasbihi E et al. MRM 91(6):2532–2545 (2024) | 10.1002/mrm.30023 | abstract | `CHECKED-ABSTRACT` |
| — | Woodard HQ & White DR. Br. J. Radiol. 59(708):1209–1218 (1986); Mezer A et al. Nat. Med. 19:1667 (2013); Volz S et al. NeuroImage 63:540 (2012); Neeb H et al. NeuroImage 31:1156 (2006); Abbas Z et al. MRM 72:1735 (2014); Sigmund EE et al. Radiology 263:758 (2012); Lemke A et al. Invest. Radiol. 44:769 (2009); Le Bihan D et al. Radiology 168:497 (1988) | see `literature-requests.md` | records confirmed, content not opened | `BIBLIO-ONLY` |

\* Stanisz 2005 and Bojorquez 2017 were read in full but through mirrored PDFs, not the publisher's copy; they move to `CHECKED-PRIMARY` when the publisher PDF is in `literature/`.

## Benchmarks and infrastructure (register E1 nearest neighbours) — kept as-is with flag (Eric's decision, 2026-09-07)

| Source | Used for | Status |
|---|---|---|
| ISMRM/NIST system phantom (Stupic KF et al. MRM 86:1194 (2021)) | single-component T1/T2 physical ground truth | `RECALLED` |
| ISMRM 2020 T1 mapping reproducibility challenge (Boudreau M et al. MRM 2024) | multi-site single-component T1 | `RECALLED` |
| ISMRM 2015 white-matter modelling challenge; MEMENTO (Fick RHJ et al. 2021) | diffusion-specific challenges | `RECALLED` |
| DECAES (Doucette J et al. Z. Med. Phys. 2020); UBC MWI toolbox; qMRLab (Karakuzu A et al. JOSS 2020); MRiLab; JEMRIS; KomaMRI | per-group simulators/toolboxes | `RECALLED` |
