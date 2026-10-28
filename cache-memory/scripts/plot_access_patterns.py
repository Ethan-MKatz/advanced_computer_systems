#!/usr/bin/env python3

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "cache-memory/results/raw/2_access_patterns.csv"
PROCESSED = ROOT / "cache-memory/results/processed"
PLOTS = ROOT / "cache-memory/results/plots"

PROCESSED.mkdir(parents=True, exist_ok=True)
PLOTS.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(RAW)

# Summarize the five independent trials for each pattern and stride.
summary = (
    df.groupby(["pattern", "stride_bytes"], as_index=False)
    .agg(
        trials=("effective_GB_per_second", "count"),
        median_bandwidth_GB_s=("effective_GB_per_second", "median"),
        q1_bandwidth_GB_s=(
            "effective_GB_per_second",
            lambda x: x.quantile(0.25),
        ),
        q3_bandwidth_GB_s=(
            "effective_GB_per_second",
            lambda x: x.quantile(0.75),
        ),
        median_elapsed_seconds=("elapsed_seconds", "median"),
        median_checksum=("checksum", "median"),
    )
)

summary.to_csv(
    PROCESSED / "2_access_patterns_summary.csv",
    index=False,
)

import cm_style as cs  # noqa: E402

strides = [64, 256, 1024]
patterns = [("sequential", "sequential order", cs.BLUE), ("random", "randomized order", cs.ORANGE)]
x = np.arange(len(strides))
width = 0.36
SUB = ("Original run: 64 MiB buffer of 8-byte words, one element updated every <stride> bytes "
       "(data[i] += 1; checksum += data[i]), 10 passes, 5 trials, process not pinned. "
       "Bar = median, whiskers = IQR. ")

# Per-element time from the same raw rows: elapsed / (elements per pass x passes).
df["accesses"] = (df["working_set_MiB"] * 1024 * 1024 // df["stride_bytes"]) * df["passes"]
df["ns_per_element"] = df["elapsed_seconds"] * 1e9 / df["accesses"]

# Plot 2a: effective throughput by access pattern and stride.
fig, ax = plt.subplots(figsize=(9.5, 5.4))
for i, (pattern, label, color) in enumerate(patterns):
    part = summary[summary["pattern"] == pattern].set_index("stride_bytes").reindex(strides)
    median = part["median_bandwidth_GB_s"].to_numpy()
    err = np.vstack([median - part["q1_bandwidth_GB_s"].to_numpy(),
                     part["q3_bandwidth_GB_s"].to_numpy() - median])
    bars = ax.bar(x + (i - 0.5) * width, median, width * 0.95, label=label, yerr=err,
                  capsize=4, color=color, ecolor=cs.INK2)
    for b, v, top in zip(bars, median, part["q3_bandwidth_GB_s"]):
        ax.text(b.get_x() + b.get_width() / 2, top + 0.04, f"{v:.3f}", ha="center", fontsize=8.5)
ax.set_xticks(x, [f"{s} B" for s in strides])
ax.set_xlabel("Stride between updated elements")
ax.set_ylabel("Software-estimated throughput (GB/s)")
cs.fig_legend(fig, ax)
cs.title(fig, "2a  Effective throughput by access pattern and stride", SUB +
         "GB/s = 16 B (one 8-byte load + one 8-byte store) x updates / elapsed time: a "
         "software-level estimate, NOT measured DRAM traffic (each update moves a whole 64-byte "
         "line, and the 8-byte index vector is streamed too).")
cs.save(fig, "2a_access_pattern_bandwidth.png")

# Plot 2b: elapsed time per updated element.
fig, ax = plt.subplots(figsize=(9.5, 5.4))
per = cs.iqr_summary(df, ["pattern", "stride_bytes"], "ns_per_element")
for i, (pattern, label, color) in enumerate(patterns):
    part = per[per["pattern"] == pattern].set_index("stride_bytes").reindex(strides)
    bars = ax.bar(x + (i - 0.5) * width, part["median"], width * 0.95, label=label,
                  yerr=cs.yerr(part), capsize=4, color=color, ecolor=cs.INK2)
    for b, v, top in zip(bars, part["median"], part["q3"]):
        ax.text(b.get_x() + b.get_width() / 2, top + 0.6, f"{v:.1f}", ha="center", fontsize=8.5)
ax.set_xticks(x, [f"{s} B" for s in strides])
ax.set_xlabel("Stride between updated elements")
ax.set_ylabel("Elapsed time per updated element (ns)")
cs.fig_legend(fig, ax)
cs.title(fig, "2b  Elapsed time per updated element by access pattern and stride", SUB +
         "Raw elapsed time is normalized by the number of updates (stride 64 B: 1,048,576 per "
         "pass; 1024 B: 65,536), because total work differs across strides. Stride-1024 runs "
         "last only 15–28 ms, so they are the most timer- and frequency-sensitive.")
cs.save(fig, "2b_access_pattern_elapsed_time.png")

print("Summary:")
print(summary.to_string(index=False))
print("\nSaved:")
print(PROCESSED / "2_access_patterns_summary.csv")
print(PLOTS / "2a_access_pattern_bandwidth.png")
print(PLOTS / "2b_access_pattern_elapsed_time.png")

