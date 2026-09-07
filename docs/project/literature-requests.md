# Literature to fetch — full citations and DOI links

**Purpose.** Papers the project needs to *open* (not merely cite) to move dictionary values, charter constants and
bibliography rows from `RECALLED` / `SECONDARY` to `PRIMARY`. Download the PDF and drop it into the repository's
`literature/` folder (git-ignored; copyrighted material is never committed) under the file name in the last column; the next
session reads them from there. DOI links resolve to the publisher page (institutional access may be needed); an open copy is
noted where one is known. Every DOI below was confirmed against a Crossref/OpenAlex record or the publisher page on
2026-09-07 unless marked *unconfirmed*.

## Priority 1 — settles an open charter item

| # | Citation | DOI / link | Open copy | Why | file name |
|---|---|---|---|---|---|
| 1 | Istratov AA, Vyvenko OF. Exponential analysis in physical phenomena. *Rev. Sci. Instrum.* 1999;70(2):1233–1257. | https://doi.org/10.1063/1.1149581 | — | Their printed resolution formula and definition of SNR (charter §1.2 constant convention; §7 open flag). Look for the section on resolution / Mellin transform. | `Istratov1999_RSI.pdf` |
| 2 | Varah JM. On fitting exponentials by nonlinear least squares. *SIAM J. Sci. Stat. Comput.* 1985;6(1):30–44. | https://doi.org/10.1137/0906003 | 1982 preprint: https://www.cs.ubc.ca/sites/default/files/tr/1982/TR-82-02.pdf (does **not** quote the coefficients) | Does the journal version quote Lanczos's two-exponential coefficients? (v0.7 provenance claim). | `Varah1985_SISSC.pdf` |
| 3 | Sabouri S, Chang SD, Savdie R, et al. Luminal water imaging: a new MR imaging T2 mapping technique for prostate cancer diagnosis. *Radiology* 2017;284(2):451–459. | https://doi.org/10.1148/radiol.2017161687 | PMC (green OA) | Component T2s and luminal water fraction — the dictionary's prostate row is still RECALLED. | `Sabouri2017_Radiology.pdf` |
| 4 | Sabouri S, Fazli L, Chang SD, et al. MR measurement of luminal water in prostate gland: quantitative correlation between MRI and histology. *JMRI* 2017;46(3):861–869. | https://doi.org/10.1002/jmri.25624 | — | Same; note: the "MRM 77:2038" citation in earlier documents was wrong — this is the paper. | `Sabouri2017_JMRI.pdf` |
| 5 | Whittall KP, MacKay AL, Graeb DA, Nugent RA, Li DKB, Paty DW. In vivo measurement of T2 distributions and water contents in normal human brain. *MRM* 1997;37(1):34–43. | https://doi.org/10.1002/mrm.1910370107 | — | Per-structure MWF and geometric-mean T2 table (brain WM/GM rows). | `Whittall1997_MRM.pdf` |
| 6 | MacKay A, Whittall K, Adler J, Li D, Paty D, Graeb D. In vivo visualization of myelin water in brain by magnetic resonance. *MRM* 1994;31(6):673–677. | https://doi.org/10.1002/mrm.1910310614 | — | Myelin-water window (10–50 vs 10–55 ms) and fractions. | `MacKay1994_MRM.pdf` |
| 7 | Stanisz GJ, Odrobina EE, Pun J, Escaravage M, Graham SJ, Bronskill MJ, Henkelman RM. T1, T2 relaxation and magnetization transfer in tissue at 3T. *MRM* 2005;54(3):507–512. | https://doi.org/10.1002/mrm.20605 | mirrored PDF exists (mriquestions.com) — read this session | Table 1 is the backbone of the T1/T2 columns; a publisher copy moves those rows to PRIMARY. | `Stanisz2005_MRM.pdf` |
| 8 | de Bazelaire CMJ, Duhamel GD, Rofsky NM, Alsop DC. MR imaging relaxation times of abdominal and pelvic tissues measured in vivo at 3.0 T: preliminary results. *Radiology* 2004;230(3):652–659. | https://doi.org/10.1148/radiol.2303021331 | Harvard DASH deposit exists | 1.5 T table and per-tissue SDs (abdominal rows). | `deBazelaire2004_Radiology.pdf` |
| 9 | Gold GE, Han E, Stainsby J, Wright G, Brittain J, Beaulieu C. Musculoskeletal MRI at 3.0 T: relaxation times and image contrast. *AJR* 2004;183(2):343–351. | https://doi.org/10.2214/ajr.183.2.1830343 | ISMRM 2003 #450 abstract is open (read) | MSK rows at 1.5 and 3 T. | `Gold2004_AJR.pdf` |
| 10 | Saab G, Thompson RT, Marsh GD. Multicomponent T2 relaxation of in vivo skeletal muscle. *MRM* 1999;42(1):150–157. | https://doi.org/10.1002/(SICI)1522-2594(199907)42:1%3C150::AID-MRM20%3E3.0.CO;2-5 | — | Field strength and the full component table (muscle row is from the abstract). | `Saab1999_MRM.pdf` |
| 11 | Araujo ECA, Fromes Y, Carlier PG. New insights on human skeletal muscle tissue compartments revealed by in vivo T2 NMR relaxometry. *Biophys. J.* 2014;106(10):2267–2274. | https://doi.org/10.1016/j.bpj.2014.04.010 | PMC4052352 (free) | 3 T muscle compartments. | `Araujo2014_BiophysJ.pdf` |
| 12 | MacMillan EL, Mädler B, Fichtner N, et al. Myelin water and T2 relaxation measurements in the healthy cervical spinal cord at 3T: repeatability and changes with age. *NeuroImage* 2011;54(2):1083–1090. | https://doi.org/10.1016/j.neuroimage.2010.08.076 | — | Cord row (currently from the authors' 2007 ISMRM abstract). | `MacMillan2011_NeuroImage.pdf` |
| 13 | Labadie C, Lee J-H, Rooney WD, et al. Myelin water mapping by spatially regularized longitudinal relaxographic imaging at high magnetic fields. *MRM* 2014;71(1):375–387. | https://doi.org/10.1002/mrm.24670 | — | Multi-component T1 row. | `Labadie2014_MRM.pdf` |
| 14 | Prasloski T, Mädler B, Xiang Q-S, MacKay A, Jones C. Applications of stimulated echo correction to multicomponent T2 analysis. *MRM* 2012;67(6):1803–1814. | https://doi.org/10.1002/mrm.23157 | — | EPG-corrected MWF values at 3 T; the stimulated-echo misspecification path. | `Prasloski2012_MRM.pdf` |
| 15 | Du J, Diaz E, Carl M, Bae W, Chung CB, Bydder GM. Ultrashort echo time imaging with bicomponent analysis. *MRM* 2012;67(3):645–649. | https://doi.org/10.1002/mrm.23047 | — | Tendon/ligament/bone short-T2* fractions (abstract only so far). | `Du2012_MRM.pdf` |
| 16 | Bouhrara M, Reiter DA, Celik H, et al. Incorporation of Rician noise in the analysis of biexponential transverse relaxation in cartilage using a multiple gradient echo sequence at 3 and 7 Tesla. *MRM* 2015;73(1):352–366. | https://doi.org/10.1002/mrm.25111 | PMC4171354 (author manuscript) | Cartilage row at 3 T/7 T; noise-track prior art (§3.2). | `Bouhrara2015_MRM.pdf` |
| 17 | Le Ster C, Gambarota G, Lasbleiz J, Guillin R, Decaux O, Saint-Jalmes H. Breath-hold MR measurements of fat fraction, T1, and T2* of water and fat in vertebral bone marrow. *JMRI* 2016;44(3):549–555. | https://doi.org/10.1002/jmri.25205 | — | Marrow row. | `LeSter2016_JMRI.pdf` |

## Priority 2 — bulk-property and diffusion sources (dictionary columns)

| # | Citation | DOI / link | Open copy | file name |
|---|---|---|---|---|
| 18 | Bojorquez JZ, Bricq S, Acquitter C, Brunotte F, Walker PM, Lalande A. What are normal relaxation times of tissues at 3 T? *Magn. Reson. Imaging* 2017;35:69–80. | https://doi.org/10.1016/j.mri.2016.08.021 | mirrored PDF exists (read) | `Bojorquez2017_MRI.pdf` |
| 19 | Wansapura JP, Holland SK, Dunn RS, Ball WS. NMR relaxation times in the human brain at 3.0 tesla. *JMRI* 1999;9(4):531–538. | https://doi.org/10.1002/(SICI)1522-2586(199904)9:4%3C531::AID-JMRI4%3E3.0.CO;2-L | — | `Wansapura1999_JMRI.pdf` |
| 20 | Lu H, Nagae-Poetscher LM, Golay X, Lin D, Pomper M, van Zijl PCM. Routine clinical brain MRI sequences for use at 3.0 Tesla. *JMRI* 2005;22(1):13–22. | https://doi.org/10.1002/jmri.20356 | — | `Lu2005_JMRI.pdf` |
| 21 | Wright PJ, Mougin OE, Totman JJ, et al. Water proton T1 measurements in brain tissue at 7, 3, and 1.5 T using IR-EPI, IR-TSE, and MPRAGE. *MAGMA* 2008;21(1–2):121–130. | https://doi.org/10.1007/s10334-008-0104-8 | — | `Wright2008_MAGMA.pdf` |
| 22 | Rooney WD, Johnson G, Li X, et al. Magnetic field and tissue dependencies of human brain longitudinal 1H2O relaxation in vivo. *MRM* 2007;57(2):308–318. | https://doi.org/10.1002/mrm.21122 | — | `Rooney2007_MRM.pdf` |
| 23 | Woodard HQ, White DR. The composition of body tissues. *Br. J. Radiol.* 1986;59(708):1209–1218. | https://doi.org/10.1259/0007-1285-59-708-1209 | — | `Woodard1986_BJR.pdf` (per-organ water content) |
| 24 | Mezer A, Yeatman JD, Stikov N, et al. Quantifying the local tissue volume and composition in individual brains with magnetic resonance imaging. *Nat. Med.* 2013;19(12):1667–1672. | https://doi.org/10.1038/nm.3390 | PMC3855886 | `Mezer2013_NatMed.pdf` |
| 25 | Volz S, Nöth U, Jurcoane A, Ziemann U, Hattingen E, Deichmann R. Quantitative proton density mapping: correcting the receiver sensitivity bias via pseudo proton densities. *NeuroImage* 2012;63(1):540–552. | https://doi.org/10.1016/j.neuroimage.2012.06.076 (*DOI unconfirmed*) | — | `Volz2012_NeuroImage.pdf` |
| 26 | Neeb H, Zilles K, Shah NJ. A new method for fast quantitative mapping of absolute water content in vivo. *NeuroImage* 2006;31(3):1156–1168. | https://doi.org/10.1016/j.neuroimage.2005.12.063 | — | `Neeb2006_NeuroImage.pdf` |
| 27 | Abbas Z, Gras V, Möllenhoff K, Keil F, Oros-Peusquens A-M, Shah NJ. Analysis of proton-density bias corrections based on T1 measurement for robust quantification of water content in the brain at 3 Tesla. *MRM* 2014;72(6):1735–1745. | https://doi.org/10.1002/mrm.25086 | — | `Abbas2014_MRM.pdf` |
| 28 | Sigmund EE, Vivier P-H, Sui D, et al. Intravoxel incoherent motion and diffusion-tensor imaging in renal tissue under hydration and furosemide flow challenges. *Radiology* 2012;263(3):758–769. | https://doi.org/10.1148/radiol.12111327 | — | `Sigmund2012_Radiology.pdf` (kidney IVIM numbers) |
| 29 | Lemke A, Laun FB, Klauss M, et al. Differentiation of pancreas carcinoma from healthy pancreatic tissue using multiple b-values: comparison of apparent diffusion coefficient and intravoxel incoherent motion derived parameters. *Invest. Radiol.* 2009;44(12):769–775. | https://doi.org/10.1097/RLI.0b013e3181b62271 | — | `Lemke2009_InvestRadiol.pdf` |
| 30 | Le Bihan D, Breton E, Lallemand D, Aubin M-L, Vignaud J, Laval-Jeantet M. Separation of diffusion and perfusion in intravoxel incoherent motion MR imaging. *Radiology* 1988;168(2):497–505. | https://doi.org/10.1148/radiology.168.2.3393671 | — | `LeBihan1988_Radiology.pdf` |
| 31 | Bernardino ME, Small W, Goldstein J, et al. Multiple NMR T2 relaxation values in human liver tissue. *AJR* 1983;141(6):1203–1208. | https://doi.org/10.2214/ajr.141.6.1203 | — | `Bernardino1983_AJR.pdf` (the only multi-exponential liver T2 study found; ex vivo) |
| 32 | Tasbihi E, Gladytz T, Millward JM, et al. In vivo monitoring of renal tubule volume fraction using dynamic parametric MRI. *MRM* 2024;91(6):2532–2545. | https://doi.org/10.1002/mrm.30023 | CC-BY | `Tasbihi2024_MRM.pdf` (rat kidney biexponential T2) |

## Priority 3 — foundations (charter §1.2 / §4 table; cite-level today, read-level before Phase 3 theory work)

| # | Citation | DOI / link | Open copy |
|---|---|---|---|
| 33 | Lanczos C. *Applied Analysis*. Prentice-Hall, 1956; Dover reprint 1988, ISBN 0-486-65656-X. | https://archive.org/details/appliedanalysis00lanc_0 | **pp. 272–279 on hand** (`appliedanalysisLanczos/`) — book check closed |
| 34 | McWhirter JG, Pike ER. On the numerical inversion of the Laplace transform and similar Fredholm integral equations of the first kind. *J. Phys. A* 1978;11(9):1729–1745. | https://doi.org/10.1088/0305-4470/11/9/007 | IOP PDF (bronze) |
| 35 | Bertero M, Boccacci P, Pike ER. On the recovery and resolution of exponential relaxation rates from experimental data: a singular-value analysis of the Laplace transform inversion in the presence of noise. *Proc. R. Soc. Lond. A* 1982;383(1784):15–29. | https://doi.org/10.1098/rspa.1982.0117 | — |
| 36 | Bertero M, Boccacci P, Pike ER. …II. The optimum choice of experimental sampling points for Laplace transform inversion. *Proc. R. Soc. Lond. A* 1984;393(1804):51–65. (**authors corrected**: Boccacci, not Brianzi) | https://doi.org/10.1098/rspa.1984.0045 | — |
| 37 | Bertero M, Brianzi P, Pike ER. …III. The effect of sampling and truncation of data on the Laplace transform inversion. *Proc. R. Soc. Lond. A* 1985;398(1814):23–44. | https://doi.org/10.1098/rspa.1985.0024 | — |
| 38 | Epstein CL, Schotland JC. The bad truth about Laplace's transform. *SIAM Rev.* 2008;50(3):504–520. | https://doi.org/10.1137/060657273 | author preprint: https://www2.math.upenn.edu/~cle/papers/laplce_rev2.pdf |
| 39 | Ostrowsky N, Sornette D, Parker P, Pike ER. Exponential sampling method for light scattering polydispersity analysis. *Optica Acta* 1981;28(8):1059–1070. | https://doi.org/10.1080/713820704 | — |
| 40 | Hansen PC. The discrete Picard condition for discrete ill-posed problems. *BIT* 1990;30(4):658–672. | https://doi.org/10.1007/BF01933214 | — |
| 41 | Sijbers J, den Dekker AJ. Maximum likelihood estimation of signal amplitude and noise variance from MR data. *MRM* 2004;51(3):586–594. | https://doi.org/10.1002/mrm.10728 | — |
| 42 | Benedict TR, Soong TT. The joint estimation of signal and noise from the sum envelope. *IEEE Trans. Inf. Theory* 1967;13(3):447–454. | https://doi.org/10.1109/TIT.1967.1054037 | — |
| 43 | Karlsen OT, Verhagen R, Bovée WMMJ. Parameter estimation from Rician-distributed data sets using a maximum likelihood estimator: application to T1 and perfusion measurements. *MRM* 1999;41(3):614–623. | https://doi.org/10.1002/(SICI)1522-2594(199903)41:3%3C614::AID-MRM26%3E3.0.CO;2-1 | — |
| 44 | Milford D, Rosbach N, Bendszus M, Heiland S. Mono-exponential fitting in T2-relaxometry: relevance of offset and first echo. *PLoS ONE* 2015;10(12):e0145255. | https://doi.org/10.1371/journal.pone.0145255 | gold OA |
| 45 | Rife DC, Boorstyn RR. Single-tone parameter estimation from discrete-time observations. *IEEE Trans. Inf. Theory* 1974;20(5):591–598. | https://doi.org/10.1109/TIT.1974.1055282 | — |
| 46 | Transtrum MK, Machta BB, Sethna JP. Why are nonlinear fits to data so challenging? *Phys. Rev. Lett.* 2010;104:060201. | https://doi.org/10.1103/PhysRevLett.104.060201 | arXiv:0909.3884 |
| 47 | Transtrum MK, Machta BB, Sethna JP. Geometry of nonlinear least squares with applications to sloppy models and optimization. *Phys. Rev. E* 2011;83:036701. | https://doi.org/10.1103/PhysRevE.83.036701 | arXiv:1010.1449 |
| 48 | Transtrum MK, Machta BB, Brown KS, Daniels BC, Myers CR, Sethna JP. Perspective: Sloppiness and emergent theories in physics, biology, and beyond. *J. Chem. Phys.* 2015;143:010901. | https://doi.org/10.1063/1.4923066 | arXiv:1501.07668 |
| 49 | Bates DM, Watts DG. Relative curvature measures of nonlinearity. *J. R. Stat. Soc. B* 1980;42(1):1–25 (with discussion). | https://doi.org/10.1111/j.2517-6161.1980.tb01094.x | — |
| 50 | Whittall KP, MacKay AL. Quantitative interpretation of NMR relaxation data. *J. Magn. Reson.* 1989;84(1):134–152. | https://doi.org/10.1016/0022-2364(89)90011-5 | — |
| 51 | Provencher SW. A constrained regularization method for inverting data represented by linear algebraic or integral equations. *Comput. Phys. Commun.* 1982;27(3):213–227; and CONTIN, *ibid.* 229–242. | https://doi.org/10.1016/0010-4655(82)90173-4 ; https://doi.org/10.1016/0010-4655(82)90174-6 | — |
| 52 | Golub GH, Pereyra V. The differentiation of pseudo-inverses and nonlinear least squares problems whose variables separate. *SIAM J. Numer. Anal.* 1973;10(2):413–432. | https://doi.org/10.1137/0710036 | — |
| 53 | Pal P, Vaidyanathan PP. Nested arrays: a novel approach to array processing with enhanced degrees of freedom. *IEEE Trans. Signal Process.* 2010;58(8):4167–4181. | https://doi.org/10.1109/TSP.2010.2049264 | — |
| 54 | Vaidyanathan PP, Pal P. Sparse sensing with co-prime samplers and arrays. *IEEE Trans. Signal Process.* 2011;59(2):573–586. (**author order corrected**) | https://doi.org/10.1109/TSP.2010.2089682 | — |
| 55 | Koay CG, Basser PJ. Analytically exact correction scheme for signal extraction from noisy magnitude MR signals. *J. Magn. Reson.* 2006;179(2):317–322. | https://doi.org/10.1016/j.jmr.2006.01.016 | — |
| 56 | Robson PM, Grant AK, Madhuranthakam AJ, Lattanzi R, Sodickson DK, McKenzie CA. Comprehensive quantification of signal-to-noise ratio and g-factor for image-based and k-space-based parallel imaging reconstructions. *MRM* 2008;60(4):895–907. | https://doi.org/10.1002/mrm.21728 | PMC2838249 |
| 57 | Veraart J, Novikov DS, Christiaens D, Ades-aron B, Sijbers J, Fieremans E. Denoising of diffusion MRI using random matrix theory. *NeuroImage* 2016;142:394–406. | https://doi.org/10.1016/j.neuroimage.2016.08.016 | PMC |

## Already open / already read (no action)

Reiter 2009 (PMC2711212, read in full); Horch 2010 (PMC2933073, read); Luciani 2008 (RSNA PDF, read); Laule 2007
(PMC7479725 / Springer PDF, read); Oros-Peusquens 2019 (Frontiers, read); Jelescu & Budde 2017 (Frontiers, read); McGill
2015 (PLOS, read); Mazzoli 2021 (Frontiers, read); Serafin 2024 (MDPI, read); Mayer 2021 (read); van Baalen 2017 (read);
Li 2017 QIMS (read); Steinbeck & Chmelka 2005 JACS (open PDF, read — the secondary that restates Istratov & Vyvenko's
resolution numbers); Varah 1982 tech report (read); Lanczos pp. 272–279 (your screenshots, read).
