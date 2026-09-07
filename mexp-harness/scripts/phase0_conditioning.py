"""
Phase 0 conditioning sweep (charter §1.2, §4): singular spectrum of the
discretised T2 CPMG kernel vs echo spacing, echo count, T-range dynamic range,
truncation level, and SNR — with the Picard condition as the operational
diagnostic, and the continuum (Mellin / BBP) count as the reference.

No noise is drawn anywhere.  Outputs go to results/ :
    conditioning_sweep.csv      the full grid of counts
    conditioning_summary.md     tables quoted in docs/phase0-findings.md
    fig_*.png                   figures

Run:  python scripts/phase0_conditioning.py
"""
from __future__ import annotations

import csv
import pathlib
import sys

import numpy as np

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from mexp import conditioning as C
from mexp.design import uniform
from mexp.kernels import get
from mexp.params import Theta

OUT = pathlib.Path(__file__).resolve().parents[1] / "results"
OUT.mkdir(exist_ok=True)

# --- dataviz reference palette (light mode) -------------------------------------------
SERIES = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#4a3aa7", "#e34948"]
INK, INK2, MUTED, GRID, BASE, SURF = "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7", "#fcfcfb"
plt.rcParams.update({
    "figure.facecolor": SURF, "axes.facecolor": SURF, "savefig.facecolor": SURF,
    "axes.edgecolor": BASE, "axes.labelcolor": INK2, "xtick.color": MUTED, "ytick.color": MUTED,
    "text.color": INK, "grid.color": GRID, "grid.linewidth": 0.6, "axes.grid": True,
    "axes.spines.top": False, "axes.spines.right": False, "font.family": "sans-serif",
    "font.size": 10, "legend.frameon": False, "lines.linewidth": 2.0, "lines.markersize": 5,
})

k = get("t2_cpmg")
M_GRID = 300
SNRS = [30, 100, 300, 1000]
COL_W = "sqrt_dlog"   # L2(dlogT) quadrature so singular values are comparable across grids


def operator(n, dte, tmin, tmax, start=None):
    d = uniform(n, dte, start=start)
    grid = C.log_grid(tmin, tmax, M_GRID)
    return d, grid, C.discretized_operator(k, d, grid, column_weights=COL_W)


# =====================================================================================
# 1. the sweep: counts vs (dTE, N, gamma, SNR)
# =====================================================================================
rows = []
designs = [(8, 40.0), (8, 10.0), (16, 20.0), (16, 10.0), (32, 10.0), (32, 5.0), (64, 10.0), (64, 5.0), (32, 20.0)]
ranges = [(10.0, 100.0), (10.0, 1000.0), (5.0, 2000.0), (1.0, 10000.0)]
truths = {
    "2c myelin-like (0.2@20, 0.8@80)": Theta([0.2, 0.8], [[20.0], [80.0]]),
    "3c (0.15@15, 0.7@70, 0.15@300)": Theta([0.15, 0.7, 0.15], [[15.0], [70.0], [300.0]]),
}
for n, dte in designs:
    for tmin, tmax in ranges:
        d, grid, A = operator(n, dte, tmin, tmax)
        s = C.singular_spectrum(A)
        gamma = tmax / tmin
        for snr in SNRS:
            r = {"N": n, "dTE": dte, "t_min": d.points[0, 0], "t_max": d.points[-1, 0], "T_min": tmin, "T_max": tmax,
                 "gamma": gamma, "SNR": snr, "n_per_sample": C.effective_rank(s, snr),
                 "bbp": round(C.bbp_count(gamma, snr), 2), "s1_over_s0": s[1] / s[0], "s2_over_s0": s[2] / s[0],
                 "s3_over_s0": s[3] / s[0] if s.size > 3 else np.nan, "s4_over_s0": s[4] / s[0] if s.size > 4 else np.nan}
            for name, th in truths.items():
                b = k.forward(th, d)
                sigma = k.reference_signal(th) / snr
                pr = C.picard(A, b, sigma, per_sample_snr=snr)
                tag = name.split(" ")[0]
                r[f"picard_{tag}"] = pr.n_picard
                r[f"picardraw_{tag}"] = pr.n_above_noise
                r[f"energy_{tag}"] = pr.n_energy
            rows.append(r)

with open(OUT / "conditioning_sweep.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)

# =====================================================================================
# 2. figures
# =====================================================================================

def snr_lines(ax, xmax):
    for snr in SNRS:
        ax.axhline(1 / snr, color=GRID, lw=0.8, zorder=0)
        ax.text(xmax, 1 / snr, f"1/SNR, SNR={snr}", color=MUTED, fontsize=8, va="bottom", ha="right")


# ---- Fig 1: spectrum vs echo count / spacing at fixed T-range ------------------------------
fig, ax = plt.subplots(figsize=(7.2, 4.6))
sel = [(8, 40.0), (16, 20.0), (32, 10.0), (64, 5.0), (64, 10.0)]
for i, (n, dte) in enumerate(sel):
    d, grid, A = operator(n, dte, 5.0, 2000.0)
    s = C.singular_spectrum(A)
    ax.semilogy(np.arange(1, min(12, s.size) + 1), (s / s[0])[:12], "o-", color=SERIES[i], ms=5,
                label=f"N={n}, ΔTE={dte:g} ms  (t∈[{d.points[0,0]:g},{d.points[-1,0]:g}] ms)")
snr_lines(ax, 12)
ax.set_xlabel("singular value index i")
ax.set_ylabel("σ_i / σ_1")
ax.set_ylim(1e-6, 2)
ax.set_title("Singular spectrum of exp(−TE/T2), T2 ∈ [5, 2000] ms (γ = 400)", loc="left", color=INK)
ax.legend(fontsize=8, loc="lower left")
fig.tight_layout()
fig.savefig(OUT / "fig1_spectrum_vs_sampling.png", dpi=160)
plt.close(fig)

# ---- Fig 2: spectrum vs dynamic range + continuum curve -----------------------------------------
fig, ax = plt.subplots(figsize=(7.2, 4.6))
for i, (tmin, tmax) in enumerate(ranges):
    d, grid, A = operator(32, 10.0, tmin, tmax)
    s = C.singular_spectrum(A)
    ax.semilogy(np.arange(1, 13), (s / s[0])[:12], "o-", color=SERIES[i], label=f"T2 ∈ [{tmin:g}, {tmax:g}] ms, γ={tmax/tmin:g}")
    # continuum prediction for the same gamma: sigma_n/sigma_0 = 1/sqrt(cosh(n pi^2 / ln gamma))
    n = np.arange(0, 12)
    pred = 1 / np.sqrt(np.cosh(n * np.pi**2 / np.log(tmax / tmin)))
    ax.semilogy(n + 1, pred, ":", color=SERIES[i], lw=1.2)
snr_lines(ax, 12)
ax.plot([], [], ":", color=INK2, label="dotted: continuum (Mellin) prediction, covering window")
ax.set_xlabel("singular value index i")
ax.set_ylabel("σ_i / σ_1")
ax.set_ylim(1e-6, 2)
ax.set_title("Dynamic range: 32 echoes, ΔTE = 10 ms (t ∈ [10, 320] ms)", loc="left", color=INK)
ax.legend(fontsize=8, loc="lower left")
fig.tight_layout()
fig.savefig(OUT / "fig2_spectrum_vs_dynamic_range.png", dpi=160)
plt.close(fig)

# ---- Fig 3: Picard plots ------------------------------------------------------------------------
fig, axes = plt.subplots(1, 2, figsize=(10, 4.4), sharey=True)
d, grid, A = operator(32, 10.0, 5.0, 2000.0)
for ax, (name, th) in zip(axes, truths.items()):
    b = k.forward(th, d)
    snr = 100
    sigma = k.reference_signal(th) / snr
    pr = C.picard(A, b, sigma, per_sample_snr=snr)
    i = np.arange(1, pr.s.size + 1)
    ax.semilogy(i, pr.s, "o-", color=SERIES[0], label="σ_i (singular values)")
    ax.semilogy(i, pr.beta, "s", color=SERIES[1], ms=4, label="|uᵢᵀ b|  (Picard coefficients, noiseless)")
    ax.semilogy(i, pr.beta_smoothed, "-", color=SERIES[1], lw=1.5, label="smoothed |uᵢᵀ b| (geometric mean, q=1)")
    ax.semilogy(i, pr.solution_coeffs, "^-", color=SERIES[2], label="|uᵢᵀ b| / σ_i  (TSVD solution coefficients)")
    ax.axhline(sigma, color=INK2, lw=1, ls="--")
    ax.text(pr.s.size, sigma * 1.3, f"noise level σ (SNR={snr})", color=INK2, fontsize=8, ha="right")
    ax.axvline(pr.n_picard + 0.5, color=GRID, lw=1)
    ax.text(pr.n_picard + 0.7, 1e-8, f"{pr.n_picard} coefficients above noise (smoothed)", color=MUTED, fontsize=8)
    ax.set_title(name, loc="left", color=INK, fontsize=10)
    ax.set_xlabel("index i")
    ax.set_ylim(1e-9, 1e3)
axes[0].set_ylabel("magnitude")
axes[0].legend(fontsize=8, loc="upper right")
fig.suptitle("Discrete Picard condition — 32 echoes, ΔTE 10 ms, T2 grid [5, 2000] ms", x=0.01, ha="left", color=INK)
fig.tight_layout()
fig.savefig(OUT / "fig3_picard.png", dpi=160)
plt.close(fig)

# ---- Fig 4: truncation trade-off -------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(7.2, 4.4))
d, grid, A = operator(32, 10.0, 5.0, 2000.0)
ks = np.arange(1, 9)
mid = (grid > 10) & (grid < 1000)
res = [C.tsvd_resolution(A, kk, grid) for kk in ks]
ratio = [np.nanmedian(r.resolution_ratio[mid]) for r in res]
amp = [r.noise_amplification * C.singular_spectrum(A)[0] for r in res]  # relative to σ_1
ax.plot(ks, ratio, "o-", color=SERIES[0], label="median averaging-kernel width (T2 ratio, FWHM), 10 < T2 < 1000 ms")
ax.set_yscale("log")
ax.set_yticks([2, 3, 5, 10, 20, 50])
ax.get_yaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())
ax.set_ylim(2, 70)
ax.set_xlabel("TSVD truncation level k")
ax.set_ylabel("resolution: T2 ratio spanned by one kernel")
for kk, a, rr in zip(ks, amp, ratio):
    ax.annotate(f"σ₁/σ_k = {a:.0f}", (kk, rr), textcoords="offset points", xytext=(14, 4), ha="left", fontsize=7.5, color=INK2)
ax.set_title("What each retained singular value buys (resolution) and costs (noise gain σ₁/σ_k)", loc="left", color=INK, fontsize=10)
ax.legend(fontsize=8)
fig.tight_layout()
fig.savefig(OUT / "fig4_truncation_tradeoff.png", dpi=160)
plt.close(fig)

# ---- Fig 5: numerical count vs continuum count, as a function of SNR and time window ----------------
fig, ax = plt.subplots(figsize=(7.2, 4.6))
snr_axis = np.geomspace(10, 3000, 40)
gamma = 100.0
windows = [(8, 40.0, None), (32, 10.0, None), (64, 10.0, None), (2000, 0.5, 0.05)]
labels = ["8 echoes, ΔTE 40 (t 40–320)", "32 echoes, ΔTE 10 (t 10–320)", "64 echoes, ΔTE 10 (t 10–640)",
          "2000 samples, t 0.05–1000 (covering window)"]
for i, ((n, dte, st), lab) in enumerate(zip(windows, labels)):
    d, grid, A = operator(n, dte, 10.0, 1000.0, start=st)
    s = C.singular_spectrum(A)
    ax.plot(snr_axis, [C.effective_rank(s, x) for x in snr_axis], color=SERIES[i], label=lab, drawstyle="steps-post")
ax.plot(snr_axis, [C.bbp_count(gamma, x) for x in snr_axis], "--", color=INK2, label="continuum: (ln γ/π²)·arccosh(SNR²)")
ax.set_xscale("log")
ax.set_xlabel("SNR (per-sample convention: threshold σ_i/σ_1 > 1/SNR)")
ax.set_ylabel("count of singular values above 1/SNR")
ax.set_title("Numerical count vs continuum expression, T2 ∈ [10, 1000] ms (γ = 100)", loc="left", color=INK, fontsize=10)
ax.legend(fontsize=8, loc="upper left")
fig.tight_layout()
fig.savefig(OUT / "fig5_count_vs_continuum.png", dpi=160)
plt.close(fig)

# =====================================================================================
# 3. summary tables
# =====================================================================================
lines = ["# Conditioning sweep — summary tables", "",
         f"Grid: {M_GRID} log-spaced T2 points, column weighting {COL_W}. Counts are #{{i: σ_i/σ_1 > 1/SNR}} "
         "(per-sample SNR convention) unless stated; 'Picard' counts are the last index whose smoothed |uᵢᵀb| (geometric mean over 3 neighbours) exceeds σ for the named truth "
         "(σ = Σa / SNR, harness SNR definition); 'energy' uses ||s||/σ as the threshold.", ""]

def table(filter_fn, title, cols):
    lines.append(f"## {title}")
    lines.append("")
    lines.append("| " + " | ".join(cols) + " |")
    lines.append("|" + "---|" * len(cols))
    for r in rows:
        if filter_fn(r):
            lines.append("| " + " | ".join(f"{r[c]:g}" if isinstance(r[c], float) else str(r[c]) for c in cols) + " |")
    lines.append("")

table(lambda r: r["T_min"] == 5.0 and r["T_max"] == 2000.0 and r["SNR"] in (100, 1000),
      "Echo count × spacing (T2 ∈ [5, 2000] ms, γ = 400)",
      ["N", "dTE", "t_min", "t_max", "SNR", "n_per_sample", "energy_2c", "picard_2c", "energy_3c", "picard_3c", "bbp"])
table(lambda r: r["N"] == 32 and r["dTE"] == 10.0,
      "Dynamic range × SNR (32 echoes, ΔTE 10 ms)",
      ["T_min", "T_max", "gamma", "SNR", "n_per_sample", "energy_2c", "picard_2c", "energy_3c", "picard_3c", "bbp"])
table(lambda r: r["N"] in (8, 16) and r["T_min"] == 10.0 and r["T_max"] == 1000.0,
      "Austere / moderate budgets (T2 ∈ [10, 1000] ms, γ = 100)",
      ["N", "dTE", "t_min", "t_max", "SNR", "n_per_sample", "energy_2c", "picard_2c", "energy_3c", "picard_3c", "bbp"])

# resolution table
lines.append("## Continuum resolution ratio δ = exp(π² / arccosh(SNR²)) and what the finite window achieves (γ = 100, 32 echoes, ΔTE 10)")
lines.append("")
lines.append("| SNR | δ (continuum) | count (continuum) | count (32×10 ms) | implied δ = γ^(1/count) |")
lines.append("|---|---|---|---|---|")
d, grid, A = operator(32, 10.0, 10.0, 1000.0)
s = C.singular_spectrum(A)
for snr in SNRS:
    n_num = C.effective_rank(s, snr)
    lines.append(f"| {snr} | {C.bbp_resolution_ratio(snr):.2f} | {C.bbp_count(100.0, snr):.2f} | {n_num} | {C.resolution_ratio_from_count(100.0, n_num):.2f} |")
lines.append("")

# truncation table
lines.append("## TSVD truncation (32 echoes, ΔTE 10 ms, T2 grid [5, 2000] ms)")
lines.append("")
lines.append("| k | σ₁/σ_k (noise gain) | median kernel width, T2 ratio (10<T2<1000) |")
lines.append("|---|---|---|")
for kk, a, rr in zip(ks, amp, ratio):
    lines.append(f"| {kk} | {a:.1f} | {rr:.2f} |")
lines.append("")

(OUT / "conditioning_summary.md").write_text("\n".join(lines))
print("\n".join(lines))
print("wrote", OUT)
