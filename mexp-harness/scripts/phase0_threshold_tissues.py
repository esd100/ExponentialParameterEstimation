"""
The charter §1.2 threshold, evaluated over the tissue dictionary (charter v0.10; labels defined v0.14; third label v0.15).

For every T2-kernel entry in mexp.tissues, at (i) the reference acquisition
(32 x 10 ms, first-echo SNR 100) and (ii) the entry's typical acquisition,
compute the Rician (sigma known) CRLB for the visible components and the
delta-method bound on the entry's clinical functional.  Components below the
first echo are dropped and the fractions renormalised (the harness does not
pretend to see a 3 ms component with a 10 ms first echo).

Three labels per row (charter §1.2, v0.14-v0.15):
  'K estimable'          every visible T2 under 25 % relative SD;
  'functional estimable' the clinical functional under 10 % relative SD;
  'clinically estimable' the functional's SD <= |Delta| / 3, with Delta the normal-to-disease change the
                         dictionary records for that functional (`clinical_delta`, schema 2.3) - '—' when
                         no change is on record.

No noise realisation is drawn.  Output: results/threshold_tissues.md
"""
from __future__ import annotations

import pathlib

import numpy as np

from mexp import crlb as CR, tissues as TS
from mexp.design import uniform
from mexp.kernels import get

OUT = pathlib.Path(__file__).resolve().parents[1] / "results"
OUT.mkdir(exist_ok=True)
k = get("t2_cpmg")

K_OK, F_OK = 0.25, 0.10   # "estimable": every visible T2 < 25 % rel SD; functional < 10 % rel SD


def evaluate(e: TS.ComponentSet, n: int, dte: float, snr: float):
    d = uniform(n, dte)
    th = e.theta(min_value=dte)
    sigma = CR.sigma_from_first_echo_snr(k, th, d, snr)
    r = CR.crlb(k, th, d, sigma, "rician")
    relT = np.array(list(r.relative_sd_of("T2").values()))
    rela = np.array(list(r.relative_sd_of("a").values()))
    f_true = f_sd = None
    if e.functional_threshold is not None and th.K > 1:
        g = CR.mass_below_gradient(th, e.functional_threshold)
        f_sd = CR.functional_sd(r, g)
        a = th.amplitudes
        f_true = float((a * (th.nonlinear[:, 0] < e.functional_threshold)).sum() / a.sum())
        if f_true > 0.5:                  # report the minor side (LWF, fat fraction, extracellular fraction)
            f_true = 1.0 - f_true
    return th, relT, rela, f_true, f_sd


lines = ["# §1.2 threshold over the tissue dictionary", "",
         "Rician CRLB with σ known, first-echo SNR as stated; components below the first echo dropped and fractions renormalised. "
         f"'K estimable' = every visible T2 under {K_OK:.0%} relative SD; 'functional estimable' = the entry's clinical "
         f"functional under {F_OK:.0%} relative SD (delta method); 'clinically estimable' (dictionary v2.3, charter v0.15) = the "
         "functional's SD ≤ |Δ|/3 with Δ the normal-to-disease change the dictionary records for that functional (its `clinical_delta`; "
         "'—' where no change is on record), i.e. the change is a 3σ event in one measurement. The status column is the provenance of the component "
         "set (`mexp/tissue_data.py`): PRIMARY / SECONDARY are read from the literature this project opened; THEORY rows are "
         "working configurations for organs with no multi-component study reached (abdominal T2 splits); RECALLED rows are "
         "from memory. Rows marked THEORY or RECALLED shape the question, they do not settle it. Disease rows (pathology axis) are "
         "marked with their condition.", ""]

for label, acq_of in (("Reference acquisition: 32 echoes × 10 ms, first-echo SNR 100", lambda e: (32, 10.0, 100.0)),
                      ("Entry-specific typical acquisition", lambda e: (int(e.typical_acquisition["n_echoes"]),
                                                                        float(e.typical_acquisition["dTE_ms"]),
                                                                        float(e.typical_acquisition["first_echo_snr"])))):
    lines += [f"## {label}", "",
              "| tissue | status | visible K (of K) | composition (fraction @ T2 ms) | rel SD of T2 (%) | rel SD of fractions (%) | functional | value | SD (abs) | rel SD (%) | Δ (clinical) | K estimable | functional estimable | clinically estimable (SD ≤ \\|Δ\\|/3) |",
              "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for e in TS.entries(kernel="t2_cpmg"):
        n, dte, snr = acq_of(e)
        th, relT, rela, f_true, f_sd = evaluate(e, n, dte, snr)
        entry = TS.get(e.tissue_key)
        delta = entry.delta()
        comp = ", ".join(f"{a:.2f}@{t:g}" for a, t in zip(th.amplitudes, th.nonlinear[:, 0]))
        acq = "" if label.startswith("Reference") else f" ({n}×{dte:g} ms, SNR {snr:g})"
        k_ok = "yes" if np.all(relT < K_OK) else "no"
        d_txt = "—" if delta is None else f"{delta:+.3f}"
        if f_sd is None:
            f_cells = f"{e.functional} | — | — | — | {d_txt} | {k_ok} | — | —"
        else:
            frel = f_sd / f_true if f_true > 0 else np.inf
            c_ok = "—" if delta is None else ("yes" if f_sd <= abs(delta) / 3 else "no")
            f_cells = f"{e.functional} | {f_true:.3f} | {f_sd:.3f} | {100*frel:.0f} | {d_txt} | {k_ok} | {'yes' if frel < F_OK else 'no'} | {c_ok}"
        name = f"{e.tissue} ({e.organ})" + (f" — *{entry.condition['name']}*" if entry.is_pathology else "")
        lines.append(f"| {name}{acq} | {e.status.value} | {th.K} (of {e.K}) | {comp} | "
                     f"{', '.join(f'{100*v:.0f}' for v in relT)} | {', '.join(f'{100*v:.0f}' for v in rela)} | {f_cells} |")
    lines.append("")

# ---- what constraining the long component buys (the price of the free CSF-like component) ------------------
lines += ["## Myelin-type functional under three parameterisations (32 × 10 ms)", "",
          "| tissue | SNR | MWF | SD, free K = 3 | SD, long T2 fixed | SD, long component dropped (K = 2) | myelin T2 rel SD in the K = 2 model (%) |",
          "|---|---|---|---|---|---|---|"]
from mexp.params import Theta
for key in ("brain_wm", "brain_wm_ms_lesion", "brain_gm", "spinal_cord_wm"):
    e = TS.get(key).T2
    th3 = e.theta()
    a2 = th3.amplitudes[:2] / th3.amplitudes[:2].sum()
    th2 = Theta(a2, th3.nonlinear[:2])
    d = uniform(32, 10.0)
    for snr in (100, 300):
        sig = CR.sigma_from_first_echo_snr(k, th3, d, snr)
        r3 = CR.crlb(k, th3, d, sig, "rician")
        g3 = CR.mass_below_gradient(th3, e.functional_threshold)
        sd_free = CR.functional_sd(r3, g3)
        keep = [i for i, l in enumerate(r3.labels) if l != "T22"]
        cov_fix = np.linalg.pinv(r3.fim[np.ix_(keep, keep)])
        sd_fix = float(np.sqrt(g3[keep] @ cov_fix @ g3[keep]))
        sig2 = CR.sigma_from_first_echo_snr(k, th2, d, snr)
        r2 = CR.crlb(k, th2, d, sig2, "rician")
        sd_2 = CR.functional_sd(r2, CR.mass_below_gradient(th2, e.functional_threshold))
        relT0 = 100 * list(r2.relative_sd_of("T2").values())[0]
        lines.append(f"| {e.tissue} | {snr} | {th3.amplitudes[0]:.2f} | {sd_free:.3f} | {sd_fix:.3f} | {sd_2:.3f} | {relT0:.0f} |")
lines.append("")

lines += ["## Reading (dictionary v2.3 — the pathology axis and the third label; the v2.2 reading follows)", "",
          "- **The third label answers a different question from the second, and the prostate shows it.** 'Functional estimable' asks for "
          "10 % relative precision; 'clinically estimable' asks whether the recorded normal-to-disease change Δ is a 3σ event. At Sabouri's "
          "64 × 25 ms train the malignant-PZ row (LWF 0.10 ± 0.012) fails the 10 % criterion (12 % relative) and passes the clinical one "
          "(|Δ|/3 = 0.047): the decision the clinic makes — is the LWF 0.24 or 0.10 — is determined to 4σ at both operating points, "
          "although the disease-state value itself is not known to 10 %. At the reference 32 × 10 ms train both prostate rows fail all "
          "three labels (SD 0.105 / 0.077), the window rule again.",
          "- **Myelin: detecting demyelination needs SNR ~300 or a constrained long component, at the bound.** Δ(MWF) = −0.06 (0.113 → 0.05) "
          "sets |Δ|/3 = 0.020; the free K = 3 bound is 0.074 (normal) / 0.057 (lesion) at SNR 100 and 0.024 / 0.019 at SNR 300; with the long "
          "component fixed or dropped it is 0.030–0.038 at SNR 100 and 0.010–0.013 at SNR 300. So 'this voxel is demyelinated' is a "
          "single-measurement 3σ statement at SNR 300 with the CSF-like component constrained, and not at SNR 100 under any "
          "parameterisation — which is the operating point myelin water imaging in fact uses (3D acquisitions, SNR 300, Prasloski 2012; "
          "MacKay 1994 reported lesion MWF as averages over 95 volumes). The cord's age change (Δ = −0.03, |Δ|/3 = 0.010) is a 3σ event only "
          "at SNR 300 with the long component dropped (0.008).",
          "- **Muscle: the oedema surrogate is marginal at SNR 100, K-estimable, and not functional-estimable.** Araujo 2014's venous-filled "
          "state (0.142 at 181 ms against 0.858 at 32.6 ms, ratio 5.5) is 'K estimable' (5 / 15 % on the T2s) but the vascular fraction's "
          "SD of 0.023 misses both the 10 % criterion (17 %) and |Δ|/3 = 0.021 by a hair — a 6-point rise in a vascular/extracellular "
          "fraction is a 2.7σ event at SNR 100 on a 32 × 10 ms train. The normal Saab 1999 row, evaluated as three visible components, is "
          "nowhere near (SD 0.37): the K = 2 description at 3 T is the clinical picture and the one the Δ should be read against.",
          "- **Steatosis on the T2 axis fails as it should.** Water 36 ms against fat 75 ms (Bydder 2008 Table II) is a ratio-2 pair at the "
          "resolvability floor; the fat fraction's bound is 0.34 at PDFF 10 % and 0.29 at 25 % at the reference train (and > 1 at the 16 × 8 ms "
          "abdominal train), against |Δ|/3 of 0.027 and 0.077 and grade steps of 0.05–0.11. The rows are the fat axis's negative control: "
          "the same fractions are measured to ± 0.01–0.02 by chemical-shift encoding (Yokoo 2011 slope 0.98; Armstrong 2018 limits of "
          "agreement ± 5 %), which is the 'change the question' move of charter §1.3 in the field's own practice — separate by frequency, "
          "not by relaxation. Whether a joint chemical-shift + T2 kernel recovers them is a question for the complex T2* kernel, not this one.",
          "- **Provenance of the axis.** The steatotic rows' T2 pair, the malignant PZ, the venous-filled muscle and the lesion MWF are "
          "PRIMARY (Bydder 2008, Sabouri 2017, Araujo 2014, MacKay 1994); the lesion IE T2 is a THEORY working value (MacKay plots it, does "
          "not tabulate it). Four normal rows carry a measured Δ; the liver, spleen, kidney and pancreas rows carry none on the T2 axis because "
          "their functional is the THEORY vascular tail.",
          "", "### The v2.2 reading (unchanged)", "",
          "- At the reference acquisition no myelin-type entry is 'estimable' by either criterion under a free K = 3 model: the "
          "free long component (2000 ms, unpinned by a 320 ms window) roughly doubles the bound on the myelin water fraction "
          "(white matter: 0.074 free vs 0.038 with the long T2 fixed vs 0.030 with it dropped, at SNR 100, for the Whittall 1997 "
          "MWF of 0.113). With the long component fixed or dropped the white-matter MWF bound is about ±0.03 (1σ) at SNR 100 and "
          "±0.01 at SNR 300 — the familiar experience that myelin water imaging needs high SNR or averaging, now as a bound. "
          "**Class change (cord):** with MacMillan 2011's MWF 0.296 and IE T2 100 ms the cervical cord under the K = 2 model is "
          "estimable at SNR 100 on both criteria (myelin T2 18 % relative, MWF 0.296 ± 0.024, i.e. 8 %), where the v2.1 numbers "
          "(0.23 at 20 ms, IE 75 ms) gave 29 % and 18 %; it stays unestimable under the free K = 3 model.",
          "- The functional is better determined than the parameters (white matter MWF ~27 % relative vs myelin T2 60 % in the "
          "K = 2 model at SNR 100): a first sighting of charter Phase 3's 'estimate functionals, not spectra', at the level of the bound.",
          "- Minor components under ~5 % (grey-matter myelin water, 3.1 % in Whittall 1997) fail outright; muscle's four-component "
          "structure (Saab 1999 Table 1, measured at SNR ~3200 with 1.2 ms echoes at 1.89 T) collapses to an unestimable "
          "three-component fit at clinical SNR — the clinical protocol sees one ~30 ms pool and, at best, the ~115-160 ms "
          "vascular/extracellular tail (Saab's 11 %, Araujo 2014's 8 % at 3 T); well-separated two-component tissues (prostate "
          "luminal water, Sabouri 2017: 0.24 at 545 ms against 0.76 at 90 ms, ratio ~6) are estimable to ~5 % relative on the LWF "
          "at their own 64 × 25 ms train. **Class change (prostate):** at the *reference* 32 × 10 ms train the prostate row is no "
          "longer 'K estimable' (long T2 65 % relative, LWF 0.24 ± 0.105) — the 545 ms component is unpinned by a 320 ms window, "
          "and the v2.1 row (0.35 at 500 ms, 'yes') rested on a recalled fraction that was too large; Sabouri's own protocol, "
          "with its 1600 ms window, is what makes luminal water imaging work, which is the window rule of charter §1.2 in a "
          "clinical protocol.",
          "- The abdominal THEORY rows (liver, pancreas: ratio ~3.5, minor fraction ~0.2) come out 'K estimable' at the reference "
          "acquisition but not at their own shorter, noisier protocols; spleen and kidney (ratio ~2-3) are not estimable anywhere. "
          "These rows test whether T2 can see the vascular compartment that IVIM sees; the physics (fast exchange) says it mostly cannot.",
          "- The entry-specific acquisitions move results mostly through the window (prostate's train reaches 1600 ms; the 16 × 8 ms "
          "abdominal trains lose the 150-220 ms components; the 8 × 12 ms myocardial train is a K = 1 null case), consistent with "
          "the window rule in charter §1.2.",
          "- The adipose row (v2.1) is a 90/10 fat/water mixture at ratio 3.5: the 10 % water fraction is not estimable at the reference "
          "acquisition (relative SD ~ 60 %) even under the pure-exponential model the row is known to violate (J-coupled, chemically "
          "shifted fat) — so it fails twice, once by information and once by model, which is why it is the misspecification row and not a K test.",
          "- Provenance: the brain, cord, muscle, cartilage, bone, tendon and prostate component sets rest on the papers' own tables "
          "(PRIMARY, v2.2); marrow, breast and blood on opened secondary sources; the abdominal T2 splits (liver, spleen, kidney, "
          "pancreas) are THEORY rows built from bulk T2 and IVIM perfusion fractions because no in vivo multi-component T2 study of "
          "those organs was reached; no RECALLED component set remains. Verification moved numbers and two classes (cord under K = 2 "
          "up, prostate at the reference train down); the structure of the conclusion, set by ratios and minor-fraction sizes, stands."]

(OUT / "threshold_tissues.md").write_text("\n".join(lines))
print("\n".join(lines))
