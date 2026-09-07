# Annotated bibliography (charter G1 — the one running list)

**Version:** 0.1 — opened 2026-09-07. Seeded with every source cited so far in `charter.md` (v0.9), `gaps-register.md` (v0.5), the changelog and the Phase 0 findings. Nothing in this project may cite a source that is not on this list; every source read gets a row.

**Fields.** *Claim / use* — what the project takes from it. *Family / topic* — charter §4 family or topic. *Evidence* — primary (original result), review, dataset/standard, textbook. *Status* — how the project has checked it: `CHECKED-PRIMARY` (the text or table was read), `CHECKED-ABSTRACT` (abstract or reference page read), `BIBLIO-ONLY` (existence and metadata confirmed, e.g. via a search result or database entry), `RECALLED` (cited from memory, not opened in any session). *Survives Phase 2?* — filled when the harness scores the claim.

Rule: a row moves to `CHECKED-*` only in a session that actually opened the source; the session date goes in the last column.

## Foundations (charter §1.2, §4 Phase 0 table)

| Source | Claim / use | Family / topic | Evidence | Status | Where cited | Checked |
|---|---|---|---|---|---|---|
| Lanczos, C. *Applied Analysis*. Prentice-Hall 1956 (Dover reprint 1988), ch. IV, pp. 272–280 | Degeneracy example: 3-exp function reproduced by a 2-exp sum within the table's precision | conditioning | textbook | `RECALLED` (coefficients 2.202/4.45/0.305/1.58 and the two-decimal table are from memory) | §1.2, §4, test #1 | — open book check |
| NIST StRD Lanczos1/2/3 (itl.nist.gov/div898/strd/nls) | Generating function, 24-point grid, certified fits at 14/6/5 digits | conditioning / reference data | dataset | `CHECKED-PRIMARY` (data files and certified values fetched) | §4, `mexp/datasets/lanczos.py` | 2026-09-06 |
| Varah, J. M. *On fitting exponentials by nonlinear least squares*. SIAM J. Sci. Stat. Comput. 6:30–44 (1985); UBC TR 82-02 (1982) | Uses Lanczos's example; the TR version generates its own Δt = 0.1, n = 33 data and does **not** quote Lanczos's 2-exp coefficients | family 1 (NLS) | primary | `CHECKED-PRIMARY` for the 1982 TR; journal version `RECALLED` | §4 provenance flag | 2026-09-06 (TR) |
| Istratov, A. A. & Vyvenko, O. F. *Exponential analysis in physical phenomena*. Rev. Sci. Instrum. 70:1233–1257 (1999) | Anchor review; closed form for the minimum resolvable ratio of adjacent time constants | survey anchor | review | `BIBLIO-ONLY` (paywalled; constant convention unverified) | §1.2, §4, register B1/D1 | — open |
| McWhirter, J. G. & Pike, E. R. *On the numerical inversion of the Laplace transform and similar Fredholm integral equations of the first kind*. J. Phys. A 11:1729–1745 (1978) | Mellin diagonalisation; singular value √(π/cosh πω); resolution limit | conditioning | primary | `RECALLED` | §1.2, `mexp/conditioning.py` | — |
| Bertero, M., Boccacci, P. & Pike, E. R. *On the recovery and resolution of exponential relaxation rates from experimental data: a singular-value analysis of the Laplace transform inversion in the presence of noise*. Proc. R. Soc. Lond. A 383:15–29 (1982) | Count of recoverable components grows as ln SNR; finite support raises it | conditioning | primary | `RECALLED` | §1.2, register A1/D1 | — |
| Bertero, M., Brianzi, P. & Pike, E. R. Part II: optimum choice of sampling points. Proc. R. Soc. Lond. A 393:51–65 (1984) | Geometric sampling in t as the optimum design for Laplace inversion | experimental design | primary | `RECALLED` | register A1 | — |
| Epstein, C. L. & Schotland, J. *The bad truth about Laplace's transform*. SIAM Review 50:504–520 (2008) | Closed-form spectrum of the Laplace transform; decay rate explicit | conditioning | primary | `RECALLED`; Phase 0 found the per-index form is asymptotic, the count check holds | §1.2, §4 | — |
| Ostrowsky, N., Sornette, D., Parker, P. & Pike, E. R. *Exponential sampling method for light scattering polydispersity analysis*. Opt. Acta 28:1059–1070 (1981) | Exponential-sampling theorem in the solution domain; geometric T grids | family 3 grids | primary | `RECALLED` | §4 table, `conditioning.ostrowsky_spacing` | — |
| Transtrum, M. K., Machta, B. B. & Sethna, J. P. PRL 104:060201 (2010); PRE 83:036701 (2011); Transtrum et al. J. Chem. Phys. 143:010901 (2015) | Sloppy models; sum of exponentials as the canonical case; manifold boundaries | §1.3 geometry | primary | `RECALLED` | §1.3, §4 table, register B5 | — |
| Bates, D. M. & Watts, D. G. *Relative curvature measures of nonlinearity*. J. R. Stat. Soc. B 42:1–25 (1980); *Nonlinear Regression Analysis and Its Applications* (Wiley 1988) | Intrinsic vs parameter-effects curvature; when linearised confidence regions fail | §6.2 calibration | primary / textbook | `RECALLED` | §4 table, register B6 | — |
| Rife, D. C. & Boorstyn, R. R. *Single-tone parameter estimation from discrete-time observations*. IEEE Trans. Inf. Theory 20:591–598 (1974) | Frequency CRLB ∝ 1/(SNR·N³): the contrasting Fourier case | §4 table | primary | `RECALLED`; scaling reproduced by `tests/test_crlb.py` | §4 table, register C1–C3 | — |
| Hansen, P. C. *The discrete Picard condition for discrete ill-posed problems*. BIT 30:658–672 (1990) | Discrete Picard condition and its geometric-mean smoothing | conditioning diagnostic | primary | `RECALLED` | `mexp/conditioning.py` | — |

## Noise track (charter §3)

| Source | Claim / use | Family / topic | Evidence | Status | Where cited | Checked |
|---|---|---|---|---|---|---|
| Benedict, T. R. & Soong, T. T. *The joint estimation of signal and noise from the sum envelope*. IEEE Trans. Inf. Theory 13:447–454 (1967) | Joint (A, σ) estimation from a Rician envelope — the K = 1 case, radar | family 7 | primary | `BIBLIO-ONLY` (per v0.7 changelog) | §3.2, register A3 | 2026-09-06 |
| Sijbers, J. & den Dekker, A. J. *Maximum likelihood estimation of signal amplitude and noise variance from MR data*. MRM 51:586–594 (2004) | Joint ML and joint CRLB for the single-amplitude Rician MR case | family 7 | primary | `RECALLED` | §3.2, register A3, `mexp/crlb.py` | — |
| Karlsen, O. T., Verhagen, R. & Bovée, W. M. M. J. MRM 41:614–623 (1999) | Rician ML and bounds for T1 and perfusion parameters | family 7 | primary | `RECALLED` | §3.2 | — |
| Bouhrara, M., Reiter, D. A., Celik, H., Bonny, J.-M., Lukas, V., Fishbein, K. W. & Spencer, R. G. *Incorporation of Rician noise in the analysis of biexponential transverse relaxation in cartilage using a multiple gradient echo sequence at 3 and 7 Tesla*. MRM 73(1):352–366 (2015; online 2014); PMC4171354 | Rician-correct biexponential T2* analysis | family 7 | primary | `BIBLIO-ONLY` (title and PMC ID confirmed 2026-09-07; volume/pages per v0.7 Crossref check) | §3.2, register A3, tissue dictionary | 2026-09-07 |
| Milford, D., Rosbach, N., Bendszus, M. & Heiland, S. PLoS ONE 10(12):e0145255 (2015) | Effect of a free offset term and first-echo exclusion in T2 fitting | family 7 | primary | `BIBLIO-ONLY` (per v0.7 changelog) | §3.2 | 2026-09-06 |
| Veraart, J. et al. *Denoising of diffusion MRI using random matrix theory*. NeuroImage 142:394–406 (2016) | MP-PCA noise level and rank estimation | family 7 (§3.5) | primary | `RECALLED` | §3.4–3.5, register B3 | — |
| Moeller, S. et al. NORDIC. NeuroImage 226:117539 (2021) | Complex-domain PCA denoising | family 7 | primary | `RECALLED` | §3.4 | — |
| Aja-Fernández, S. et al. (local σ and effective-DOF estimators for SENSE/GRAPPA; e.g. MRI 27:1397 (2009), Med. Image Anal. 18:1029 (2014)) | Spatially non-stationary noise estimation | family 7 | primary | `RECALLED` | §3.4, §3.6, register A6 | — |
| Foi, A. *Noise estimation and removal in MR imaging: the variance-stabilization approach*. ISBI 2011 | Rician variance stabilisation | family 7 | primary | `RECALLED` | §3.4 | — |
| Robson, P. M. et al. *Comprehensive quantification of SNR ratio and g-factor for image-based and k-space-based parallel imaging reconstructions*. MRM 60:895–907 (2008) | Pseudo-replica noise measurement | family 7 / simulator | primary | `RECALLED` | §3.4, `mexp/sim` | — |
| Ramani, S., Blu, T. & Unser, M. *Monte-Carlo SURE*. IEEE TIP 17:1540 (2008) | Black-box SURE for regularisation tuning | family 7 | primary | `RECALLED` | §3.4 | — |
| Koay, C. G. & Basser, P. J. *Analytically exact correction scheme for signal extraction from noisy magnitude MR signals*. JMR 179:317–322 (2006) | Rician bias correction | family 7 | primary | `RECALLED` | §2.3, §3.4 | — |

## Method families (Phase 1 anchors; none implemented yet — G2)

| Source | Claim / use | Family | Evidence | Status | Where cited | Checked |
|---|---|---|---|---|---|---|
| Golub, G. H. & Pereyra, V. SIAM J. Numer. Anal. 10:413–432 (1973) | Variable projection | 1 | primary | `RECALLED` | §4 | — |
| Kumaresan, R. & Tufts, D. W. IEEE Trans. ASSP 30:833–840 (1982) | Linear-prediction SVD (Prony family) | 2 | primary | `RECALLED` | §4 | — |
| Hua, Y. & Sarkar, T. K. IEEE Trans. ASSP 38:814–824 (1990) | Matrix pencil | 2 | primary | `RECALLED` | §4 | — |
| Mandelshtam, V. A. & Taylor, H. S. J. Chem. Phys. 107:6756 (1997) | Filter diagonalisation | 2 | primary | `RECALLED` | §4 | — |
| Nakatsukasa, Y., Sète, O. & Trefethen, L. N. SIAM J. Sci. Comput. 40:A1494 (2018) | AAA rational approximation | 2 | primary | `RECALLED` | §4, register C2 | — |
| Peter, T. & Plonka, G. Inverse Problems 29:025001 (2013) | Generalised Prony method | 2 | primary | `RECALLED` | §2.3, register C1 | — |
| Vetterli, M., Marziliano, P. & Blu, T. IEEE Trans. SP 50:1417 (2002) | Finite rate of innovation | 2 | primary | `RECALLED` | §2.3, register C3 | — |
| Chen, Y. & Chi, Y. IEEE Trans. IT 60:6576 (2014) (EMaC); Jin, K. H. & Ye, J. C. (ALOHA) | Hankel matrix completion | 2 / sampling | primary | `RECALLED` | §2.3, register C4 | — |
| Pal, P. & Vaidyanathan, P. P. IEEE Trans. SP 58:4167 (2010) (nested); 2011 (co-prime) | Co-array designs | sampling design | primary | `RECALLED`; constructions implemented in `mexp/design.py` | §2.3, register A1 | — |
| Lawson, C. L. & Hanson, R. J. *Solving Least Squares Problems* (1974) | NNLS | 3 | textbook | `RECALLED` | §4 | — |
| Whittall, K. P. & MacKay, A. L. J. Magn. Reson. 84:134–152 (1989) | Regularised NNLS for T2 distributions | 3 | primary | `RECALLED` | §4, `t2_cpmg` docstring | — |
| Provencher, S. W. Comput. Phys. Commun. 27:213–227, 229–242 (1982) | CONTIN | 3 | primary | `RECALLED` | §4 | — |
| Candès, E. J. & Fernandez-Granda, C. Comm. Pure Appl. Math. 67:906 (2014) | Fourier super-resolution | 4 | primary | `RECALLED` | §2.3, §4, register B1 | — |
| Denoyelle, Q., Duval, V. & Peyré, G. J. Fourier Anal. Appl. 23:1153 (2017) | Positivity improves super-resolution | 4 / Phase 3 | primary | `RECALLED` | Phase 3, register B1 | — |
| Bretthorst, G. L. *Bayesian Spectrum Analysis and Parameter Estimation*. Springer 1988 | Bayesian exponential analysis | 5 | textbook | `RECALLED` | §4 | — |
| Backus, G. & Gilbert, F. Geophys. J. R. Astr. Soc. 16:169 (1968) | Best-resolved linear functionals | Phase 3 | primary | `RECALLED` | Phase 3, register B4 | — |
| Lasserre, J. B. SIAM J. Optim. 11:796 (2001) | Moment-SOS hierarchy | Phase 3 | primary | `RECALLED` | Phase 3, register B2 | — |
| Venkataramanan, L., Song, Y.-Q. & Hürlimann, M. D. IEEE Trans. SP 50:1017 (2002) | 2D Laplace inversion | cross-cutting | primary | `RECALLED` | §4 | — |
| Prasloski, T. et al. MRM 67:1803–1814 (2012) | EPG-corrected multi-echo T2 (stimulated echoes) | misspecification / T2 | primary | `RECALLED` | §4, tissue dictionary | — |
| Tamir, J. I. et al. MRM 77:180 (2017) | T2 shuffling (subspace) | spatial/joint | primary | `RECALLED` | §4 | — |
| Deoni, S. C. L. et al. MRM 60:1372 (2008); Lankford, C. L. & Does, M. D. MRM 69:127 (2013) | mcDESPOT and its precision critique | T1 / CRLB | primary | `RECALLED` | §2.3, tissue dictionary | — |

## Tissue dictionary sources (`mexp/tissues.py`; all entries RECALLED until the verification pass)

| Source | Used for | Status |
|---|---|---|
| MacKay, A. et al. MRM 31:673–677 (1994) | brain WM myelin water | `RECALLED` |
| Whittall, K. P. et al. MRM 37:34–43 (1997) | brain WM/GM T2 components and water contents | `BIBLIO-ONLY` (PubMed/Wiley entries found 2026-09-07; abstract not readable) |
| Laule, C. et al. Neurotherapeutics 4:460–484 (2007) | MWI review | `RECALLED` |
| MacMillan, E. L. et al. NeuroImage 54:1083–1090 (2011) | spinal cord MWF | `RECALLED` |
| Saab, G., Thompson, R. T. & Marsh, G. D. MRM 42:150–157 (1999) | skeletal muscle multi-component T2 | `RECALLED` |
| Araujo, E. C. A. et al. Biophys. J. 106:2267–2274 (2014) | muscle T2 compartments at 3 T | `RECALLED` |
| Reiter, D. A., Lin, P.-C., Fishbein, K. W. & Spencer, R. G. MRM 61:803–809 (2009) | cartilage multi-component T2 | `RECALLED` |
| Sabouri, S. et al. MRM 77:2038–2046 (2017); Radiology 284:451 (2017) | prostate luminal water imaging | `RECALLED` |
| Horch, R. A., Nyman, J. S., Gochberg, D. F., Dortch, R. D. & Does, M. D. MRM 64:680–687 (2010) | cortical bone bound/pore water | `RECALLED` |
| Du, J. et al. Magn. Reson. Imaging 28:178–184 (2010) | UTE bicomponent T2* (tendon) | `RECALLED` |
| Labadie, C. et al. MRM 71:375–387 (2014) | multi-component T1 in WM | `RECALLED` |
| Le Bihan, D. et al. Radiology 168:497–505 (1988); Luciani, A. et al. Radiology 249:891–899 (2008) | liver IVIM | `RECALLED` |
| Giri, S. et al. J. Cardiovasc. Magn. Reson. 11:56 (2009) | myocardial T2 | `RECALLED` |
| St Pierre, T. G. et al. Blood 105:855 (2005); Wood, J. C. et al. Blood 106:1460 (2005) | liver iron / T2, T2* | `RECALLED` |

## Benchmarks and infrastructure (register E1 nearest neighbours)

| Source | Used for | Status |
|---|---|---|
| ISMRM/NIST system phantom (Stupic et al. MRM 86:1194 (2021)) | single-component T1/T2 physical ground truth | `RECALLED` |
| ISMRM 2020 T1 mapping reproducibility challenge (Boudreau et al. MRM 2024) | multi-site single-component T1 | `RECALLED` |
| ISMRM 2015 white-matter modelling challenge; MEMENTO (Fick et al. 2021) | diffusion-specific challenges | `RECALLED` |
| DECAES (Doucette et al. Z. Med. Phys. 2020); UBC MWI toolbox; qMRLab (Karakuzu et al. JOSS 2020); MRiLab; JEMRIS; KomaMRI | per-group simulators/toolboxes | `RECALLED` |
