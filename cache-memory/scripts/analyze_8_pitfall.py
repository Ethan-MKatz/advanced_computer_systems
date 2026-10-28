#!/usr/bin/env python3
"""Experiment 8: measurement pitfalls -> 8a (cold vs warm reuse), 8b (pinning)."""
import numpy as np
import pandas as pd

import cm_style as cs

passes = pd.read_csv(cs.RAW / "8_measurement_pitfall_passes.csv")
cs.require(passes, ["ws_KiB", "pass", "seconds", "GB_per_s", "trial", "pinning"], 5 * 2 * 20,
           "8_measurement_pitfall_passes")
pin = pd.read_csv(cs.RAW / "8_measurement_pitfall_pinning.csv")
cs.require(pin, ["pages", "span_KiB", "ns_per_access", "cpu_start", "cpu_end", "trial", "pinning",
                 "allowed_cpus"], 12 * 2 * 3, "8_measurement_pitfall_pinning")

P_CORES, LPE_CORES = {0, 1, 2, 3}, {12, 13}
def core_type(c):
    return "P-core" if c in P_CORES else ("LP E-core" if c in LPE_CORES else "E-core")
pin["core_type_end"] = pin["cpu_end"].map(core_type)
pin["migrated"] = pin["cpu_start"] != pin["cpu_end"]

s8a = cs.iqr_summary(passes, ["ws_KiB", "pass"], "GB_per_s")
s8a["experiment"] = "8a_passes"
s8b = cs.iqr_summary(pin, ["span_KiB", "pinning"], "ns_per_access")
s8b["cv_pct"] = (pin.groupby(["span_KiB", "pinning"])["ns_per_access"].std()
                 / pin.groupby(["span_KiB", "pinning"])["ns_per_access"].mean() * 100).values
s8b["runs_on_lp_e"] = pin.groupby(["span_KiB", "pinning"])["core_type_end"].apply(lambda c: (c == "LP E-core").sum()).values
s8b["runs_migrated"] = pin.groupby(["span_KiB", "pinning"])["migrated"].sum().values
s8b["experiment"] = "8b_pinning"
pd.concat([s8a, s8b], ignore_index=True).to_csv(cs.PROC / "8_measurement_pitfall_summary.csv", index=False)
print(s8a.pivot(index="pass", columns="ws_KiB", values="median").round(2).to_string())
print(s8b.to_string(index=False))
print(pin.groupby(["span_KiB", "pinning", "cpu_end"]).size().to_string())

fig, ax = cs.plt.subplots(figsize=(10, 5.6))
stats = []
for kib, color, name in ((1024, cs.BLUE, "1 MiB buffer (fits nominal L2)"),
                         (262144, cs.ORANGE, "256 MiB buffer (exceeds nominal L3)")):
    s = s8a[s8a["ws_KiB"] == kib].sort_values("pass")
    ax.errorbar(s["pass"], s["median"], yerr=cs.yerr(s), marker="o", color=color, capsize=3,
                label=name)
    first, best = s["median"].iloc[0], s["median"].max()
    best_pass = int(s.loc[s["median"].idxmax(), "pass"])
    last5 = s["median"].iloc[-5:].median()
    stats.append(f"{cs.kib_label(kib)}: pass 1 {first:.1f} GB/s, best pass ({best_pass}) "
                 f"{best:.1f} GB/s ({best / first:.1f}x), passes 16-20 {last5:.1f} GB/s.")
ax.set_xticks(range(1, 21))
ax.set_xlabel("Pass number over the same buffer (pass 1 follows eviction by a 64 MiB read)")
ax.set_ylabel("Read bandwidth of that pass (GB/s)")
ax.set_ylim(bottom=0)
cs.fig_legend(fig, ax, ncol=2)
cs.title(fig, "8a  Pitfall: cache reuse vs a large working set",
         "Each pass is timed separately (stream_bw perpass read, CPU 0, 200 ms spin first), 5 trials, "
         "median with IQR whiskers. Re-reading a small buffer reports cache bandwidth, not memory "
         "bandwidth: quoting the warm 1 MiB number as 'memory bandwidth' would overstate the cold "
         "first pass several-fold. The 256 MiB buffer cannot be reused from cache. The warm 1 MiB "
         "passes are not stable either (they peak near pass 8, then fall); the cause was not "
         "identified (frequency/power management on battery is one candidate).\n" + " ".join(stats))
cs.save(fig, "8a_cache_reuse_vs_large_working_set.png")

ORDER = [("0", "pinned CPU 0\n(P-core)"), ("12", "pinned CPU 12\n(LP E-core, no L3)"),
         ("unpinned", "unpinned\n(allowed 0-3,12,13)")]
COLORS = {"P-core": cs.BLUE, "LP E-core": cs.ORANGE, "E-core": cs.AQUA}
fig, axes = cs.plt.subplots(1, 2, figsize=(11.5, 5.4))
rng = np.random.default_rng(0)
for ax, kib in zip(axes, (1024, 8192)):
    d = pin[pin["span_KiB"] == kib]
    for i, (p, label) in enumerate(ORDER):
        g = d[d["pinning"].astype(str) == p]
        for ct, gg in g.groupby("core_type_end"):
            ax.scatter(i + rng.uniform(-0.12, 0.12, len(gg)), gg["ns_per_access"], s=28,
                       color=COLORS[ct], edgecolor=cs.SURFACE, linewidth=0.8, zorder=3,
                       label=f"run ended on {ct}")
        m = g["ns_per_access"].median()
        ax.plot([i - 0.25, i + 0.25], [m, m], color=cs.INK, lw=2, zorder=4,
                label="median" if i == 0 else None)
    ax.set_xticks(range(len(ORDER)), [l for _, l in ORDER])
    ax.set_yscale("log")
    cs.plain_log(ax)
    ax.set_ylabel("Time per dependent load (ns, log scale)")
    ax.set_title(f"{cs.kib_label(kib)} random pointer chase", loc="left")
handles, labels = [], []
for ax in axes:
    for h, l in zip(*ax.get_legend_handles_labels()):
        if l not in labels:
            handles.append(h)
            labels.append(l)
fig._fig_legend = dict(handles=handles, labels=labels, ncol=4)
cs.title(fig, "8b  Pitfall: pinned vs unpinned execution on a hybrid CPU",
         "tlb_locality dense chase, 4 KiB pages, 5 M loads, 12 trials per configuration; each dot is "
         "one run, colored by the core type it finished on (sched_getcpu). This shell may run on "
         "CPUs 0-3 (P-cores: 48 KiB L1D, 2 MiB L2, 12 MiB L3) and 12-13 (low-power E-cores: 32 KiB "
         "L1D, 2 MiB L2, no L3 in sysfs).")
cs.save(fig, "8b_pinned_vs_unpinned_variability.png")
