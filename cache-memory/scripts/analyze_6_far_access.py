#!/usr/bin/env python3
"""Experiment 6 (timing-only): far-access fraction sweep -> 6a/6b.

Hardware cache-miss counters were unavailable (perf_event_open: EACCES), so the
counter-based plots 6a_cache_misses_vs_working_set.png and
6b_runtime_vs_cache_misses.png are BLOCKED. These plots use designed access
fractions, not measured miss counts.
"""
import numpy as np
import pandas as pd

import cm_style as cs

raw = pd.read_csv(cs.RAW / "6_far_access_fraction.csv")
cs.require(raw, ["far_KiB", "far_permille", "thp", "ns_per_access", "anon_huge_KiB", "trial",
                 "pinning"], 3 * 10 * 5, "6_far_access_fraction")
raw["f"] = raw["far_permille"] / 1000
FAR = [(1024, "far = 1 MiB (fits nominal L2)", cs.BLUE),
       (8192, "far = 8 MiB (fits nominal L3)", cs.ORANGE),
       (262144, "far = 256 MiB (exceeds nominal L3)", cs.AQUA)]

summ = cs.iqr_summary(raw, ["far_KiB", "far_permille"], "ns_per_access")
summ.to_csv(cs.PROC / "6_far_access_fraction_summary.csv", index=False)

# Per-trial least-squares fit ns = a + b f; slope b = incremental cost of a far access.
fits = []
for (far, trial), g in raw.groupby(["far_KiB", "trial"]):
    b, a = np.polyfit(g["f"], g["ns_per_access"], 1)
    pred = a + b * g["f"]
    r2 = 1 - ((g["ns_per_access"] - pred) ** 2).sum() / ((g["ns_per_access"] - g["ns_per_access"].mean()) ** 2).sum()
    fits.append({"far_KiB": far, "trial": trial, "intercept_ns": a, "slope_ns_per_far_access": b, "r2": r2})
fits = pd.DataFrame(fits)
fsum = cs.iqr_summary(fits, ["far_KiB"], "slope_ns_per_far_access")
fsum["median_intercept_ns"] = fits.groupby("far_KiB")["intercept_ns"].median().values
fsum["min_r2"] = fits.groupby("far_KiB")["r2"].min().values
fsum.to_csv(cs.PROC / "6_cache_miss_impact_summary.csv", index=False)
fits.to_csv(cs.PROC / "6_far_access_fits_per_trial.csv", index=False)
print(fsum.to_string(index=False))

SUB = ("Timing only: hardware cache-miss counters are unavailable (perf_event_open returns EACCES, "
       "perf_event_paranoid = 4), so no miss counts are shown. One dependent load chain, pinned to "
       "CPU 0: a designed fraction f of loads go to random lines of a far buffer (THP), the rest to "
       "a 16 KiB near buffer. 5 M loads per run, 5 trials. ")

fig, ax = cs.plt.subplots(figsize=(10, 5.6))
for far, name, color in FAR:
    s = summ[summ["far_KiB"] == far].sort_values("far_permille")
    ax.errorbar(s["far_permille"] / 1000, s["median"], yerr=cs.yerr(s), marker="o", color=color,
                capsize=3, label=name)
ax.set_xlabel("Designed fraction of far accesses f (set by construction, not a measured miss rate)")
ax.set_ylabel("Mean time per dependent load (ns)")
ax.set_ylim(bottom=0)
cs.fig_legend(fig, ax, ncol=3)
cs.title(fig, "6a  Runtime vs designed far-access fraction", SUB +
         "Median with IQR whiskers. A straight line means each far access adds a fixed cost.")
cs.save(fig, "6a_runtime_vs_far_access_fraction.png")

ref = pd.read_csv(cs.PROC / "5_working_set_summary.csv")
ref = ref[ref["source"] == "latency"].set_index("working_set_KiB")["median"]
fig, ax = cs.plt.subplots(figsize=(10, 5.4))
x = np.arange(len(FAR))
bars = ax.bar(x, fsum["median"], 0.55, yerr=cs.yerr(fsum), capsize=4,
              color=[c for *_, c in FAR], ecolor=cs.INK2, label="fitted slope (cost per far access)")
for xi, (far, *_), m, r2 in zip(x, FAR, fsum["median"], fsum["min_r2"]):
    ax.text(xi + 0.33, m, f"{m:.1f} ns\nmin R² {r2:.3f}", ha="left", va="center",
            fontsize=9, color=cs.INK)
    if far in ref.index:
        ax.plot([xi - 0.3, xi + 0.3], [ref[far]] * 2, color=cs.INK, lw=2,
                label="5a pointer-chase latency at that size" if xi == 0 else None)
ax.set_xticks(x, [n.replace("far = ", "") for _, n, _ in FAR])
ax.set_yscale("log")
cs.plain_log(ax)
ax.set_ylabel("ns per far access (log scale)")
cs.fig_legend(fig, ax)
cs.title(fig, "6b  Inferred cost of a far access (slope of 6a)", SUB +
         "Bar = median across trials of the per-trial least-squares slope, whiskers = IQR. This is "
         "an inferred incremental cost, NOT a measured miss penalty or miss count; the 1 MiB far "
         "buffer is not guaranteed to miss L2.")
cs.save(fig, "6b_inferred_far_access_cost.png")
