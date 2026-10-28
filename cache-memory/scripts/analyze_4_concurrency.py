#!/usr/bin/env python3
"""Experiment 4: summarize results/raw/4_concurrency_sweep.csv and draw 4a/4b."""
import numpy as np
import pandas as pd

import cm_style as cs

COLS = ["ws_MiB", "thp", "threads", "chains_per_thread", "steps", "seconds", "loads_per_s",
        "ns_per_step", "anon_huge_KiB", "cpus", "trial"]
main = pd.read_csv(cs.RAW / "4_concurrency_sweep.csv")
cs.require(main, COLS, 5 * (13 + 9), "4_concurrency_sweep")
ext = pd.read_csv(cs.RAW / "4_concurrency_sweep_extended.csv")
cs.require(ext, COLS, 5 * (2 + 6), "4_concurrency_sweep_extended")
raw = pd.concat([main, ext], ignore_index=True)
raw["L_configured"] = raw["threads"] * raw["chains_per_thread"]
raw["mloads_per_s"] = raw["loads_per_s"] / 1e6

keys = ["threads", "L_configured"]
lam = cs.iqr_summary(raw, keys, "mloads_per_s")
w = cs.iqr_summary(raw, keys, "ns_per_step")
summ = lam.merge(w, on=keys, suffixes=("_mloads_per_s", "_ns_per_step"))
# Unloaded response time W0: one thread, one chain.
w0 = summ.query("threads == 1 and L_configured == 1")["median_ns_per_step"].iloc[0]
summ["littles_L_lambda_x_W"] = summ["median_mloads_per_s"] * 1e6 * summ["median_ns_per_step"] * 1e-9
summ["achieved_mlp_lambda_x_W0"] = summ["median_mloads_per_s"] * 1e6 * w0 * 1e-9
summ["line_traffic_GB_per_s_est"] = summ["median_mloads_per_s"] * 64 / 1e3
summ["min_anon_huge_KiB"] = raw.groupby(keys)["anon_huge_KiB"].min().values
summ.to_csv(cs.PROC / "4_concurrency_sweep_summary.csv", index=False)

# Knee test per curve: first L reaching 90% of that curve's peak, and whether the
# curve is still rising at its last point (gain > 5% means no plateau = no knee).
knees = {}
for t, c in summ.groupby("threads"):
    c = c.sort_values("L_configured")
    peak = c["median_mloads_per_s"].max()
    first90 = int(c[c["median_mloads_per_s"] >= 0.9 * peak]["L_configured"].iloc[0])
    gain = c["median_mloads_per_s"].iloc[-1] / c["median_mloads_per_s"].iloc[-2] - 1
    knees[t] = dict(peak=peak, first90=first90, last_gain=gain, plateau=gain < 0.05)
print(summ.round(3).to_string(index=False))
print(f"W0 = {w0:.1f} ns")
for t, k in knees.items():
    print(f"threads={t}: peak {k['peak']:.1f} M loads/s, first L >= 90% of peak = {k['first90']}, "
          f"gain over last step {k['last_gain']:+.1%}, plateau={k['plateau']}")
pd.DataFrame([dict(threads=t, **k) for t, k in knees.items()]).to_csv(
    cs.PROC / "4_concurrency_knee_test.csv", index=False)

CURVES = {1: ("1 thread (CPU 0)", cs.BLUE), 2: ("2 threads (CPUs 0, 2)", cs.ORANGE),
          4: ("4 threads (CPUs 0-3: 2 P-cores x 2 hyperthreads)", cs.AQUA)}
SUB = ("K independent dependent-load chains per thread over one 256 MiB random cyclic list "
       "(64-byte nodes, transparent huge pages verified via AnonHugePages), 4 M loads per run, "
       "5 trials, median with IQR whiskers. Configured concurrency L = threads x K; threads pinned "
       "with pthread_setaffinity_np (4-thread runs share each P-core between 2 hyperthreads). ")

fig, ax = cs.plt.subplots(figsize=(10, 5.6))
for t, (name, color) in CURVES.items():
    c = summ[summ["threads"] == t].sort_values("L_configured")
    ax.errorbar(c["median_ns_per_step"], c["median_mloads_per_s"],
                xerr=[c["median_ns_per_step"] - c["q1_ns_per_step"], c["q3_ns_per_step"] - c["median_ns_per_step"]],
                yerr=[c["median_mloads_per_s"] - c["q1_mloads_per_s"], c["q3_mloads_per_s"] - c["median_mloads_per_s"]],
                marker="o", color=color, capsize=2, lw=1, elinewidth=0.8, alpha=0.9, ms=7,
                label=name)
    for _, r in c.iterrows():
        if r["L_configured"] in (1, 4, 8, 16, 32, 64, 128):
            ax.annotate(f"L={int(r['L_configured'])}", (r["median_ns_per_step"], r["median_mloads_per_s"]),
                        xytext=(6, -12 if t == 1 else 6), textcoords="offset points", fontsize=8,
                        color=cs.INK2)
ax.set_xlabel("W: mean time per step of one chain (ns)")
ax.set_ylabel("λ: completed loads per second (millions)")
ax.set_ylim(bottom=0)
cs.fig_legend(fig, ax, ncol=3)
cs.title(fig, "4a  Throughput vs response time as concurrency grows", SUB +
         "λ = L x steps / elapsed and W = elapsed / steps come from the same run, so L = λW holds "
         "by construction; the information is in how W grows as λ stops growing. Points are joined in "
         "order of increasing L; W varies by about ±10% run to run below L = 32, so the path zigzags.")
cs.save(fig, "4a_concurrency_throughput_latency.png")

fig, axes = cs.plt.subplots(1, 2, figsize=(12, 5.2))
ax = axes[0]
for t, (name, color) in CURVES.items():
    c = summ[summ["threads"] == t].sort_values("L_configured")
    ax.errorbar(c["L_configured"], c["median_mloads_per_s"],
                yerr=[c["median_mloads_per_s"] - c["q1_mloads_per_s"], c["q3_mloads_per_s"] - c["median_mloads_per_s"]],
                marker="o", color=color, capsize=3, label=name)
lines = []
for t, k in knees.items():
    if k["plateau"]:
        ax.axvline(k["first90"], color=CURVES[t][1], ls="--", lw=1)
        lines.append(f"{t} thr: knee near L = {k['first90']} (>= 90% of peak, last step {k['last_gain']:+.0%})")
    else:
        lines.append(f"{t} thr: no plateau (last step still {k['last_gain']:+.0%})")
ax.text(0.02, 0.97, "\n".join(lines), transform=ax.transAxes, va="top", fontsize=8.5,
        color=cs.INK2)
ax.set_xscale("log", base=2)
ax.set_xticks([1, 2, 4, 8, 16, 32, 64, 128], ["1", "2", "4", "8", "16", "32", "64", "128"])
ax.minorticks_off()
ax.set_xlabel("Configured concurrency L (outstanding chains, log2)")
ax.set_ylabel("λ (million loads/s)")
ax.set_ylim(bottom=0)
ax.set_title("Throughput vs configured concurrency", loc="left")
ax = axes[1]
for t, (name, color) in CURVES.items():
    c = summ[summ["threads"] == t].sort_values("L_configured")
    ax.plot(c["L_configured"], c["achieved_mlp_lambda_x_W0"], "o-", color=color)
lim = [1, summ["L_configured"].max()]
ax.plot(lim, lim, ls="--", color=cs.MUTED, lw=1, label="ideal: every chain overlaps at W0")
for a_ in ("x", "y"):
    getattr(ax, f"set_{a_}scale")("log", base=2)
ax.set_xticks([1, 2, 4, 8, 16, 32, 64, 128], ["1", "2", "4", "8", "16", "32", "64", "128"])
ax.set_yticks([1, 2, 4, 8, 16, 32, 64, 128], ["1", "2", "4", "8", "16", "32", "64", "128"])
ax.minorticks_off()
ax.set_xlabel("Configured concurrency L (log2)")
ax.set_ylabel(f"λ x W0  (W0 = {w0:.0f} ns, 1 chain)")
ax.set_title("Little's Law: effective overlap = λ x unloaded W", loc="left")
handles, labels = axes[0].get_legend_handles_labels()
h2, l2 = ax.get_legend_handles_labels()
fig._fig_legend = dict(handles=handles + h2, labels=labels + l2, ncol=2)
cs.title(fig, "4b  Concurrency knee and Little's Law", SUB +
         "Right: λ x W0 is the number of loads that would have to be in flight at the unloaded "
         "response time to explain the measured λ; its saturation shows the limit on overlapped "
         "misses (e.g. miss buffers / memory bandwidth), not a directly counted queue depth.")
cs.save(fig, "4b_concurrency_knee_littles_law.png")
