#!/usr/bin/env python3
"""Experiment 3: summarize results/raw/3_read_write_mix.csv and draw 3a/3b."""
import numpy as np
import pandas as pd

import cm_style as cs

MIXES = [0, 30, 50, 100]                     # write percentage
LABELS = ["100% read", "70R / 30W", "50R / 50W", "100% write"]
FOOTPRINTS = [(1024, "1 MiB (fits nominal L2)"), (262144, "256 MiB (exceeds nominal L3)")]
COLS = ["ws_KiB", "write_pct", "mode", "ops", "seconds", "ns_per_op", "mops_per_s",
        "payload_GB_per_s", "trial", "pinning"]

raw = pd.read_csv(cs.RAW / "3_read_write_mix.csv")
cs.require(raw, COLS, 4 * 2 * 2 * 5, "3_read_write_mix")
assert set(raw["pinning"].astype(str)) == {"0"}

keys = ["ws_KiB", "mode", "write_pct"]
summ = None
for col in ("mops_per_s", "ns_per_op", "payload_GB_per_s"):
    s = cs.iqr_summary(raw, keys, col).rename(columns=lambda c: c if c in keys else f"{col}_{c}")
    summ = s if summ is None else summ.merge(s, on=keys)
summ["ops"] = raw.groupby(keys)["ops"].first().values
summ.to_csv(cs.PROC / "3_read_write_mix_summary.csv", index=False)
print(summ[keys + ["mops_per_s_median", "ns_per_op_median"]].to_string(index=False))

SUB = ("Random 8-byte reads (acc += data[i]) and plain stores (data[i] = v) over a fixed buffer, "
       "addresses from an in-register xorshift PRNG (no index array), writes spread evenly by a "
       "Bresenham pattern; pinned to CPU 0 (P-core), 5 trials, bar = median, whiskers = IQR. ")

# 3a: throughput, independent (overlapping) operations.
x = np.arange(len(MIXES))
fig, axes = cs.plt.subplots(1, 2, figsize=(11.5, 5))
for ax, (ws, name) in zip(axes, FOOTPRINTS):
    a = summ[(summ["ws_KiB"] == ws) & (summ["mode"] == "independent")].set_index("write_pct").loc[MIXES]
    err = np.vstack([a["mops_per_s_median"] - a["mops_per_s_q1"], a["mops_per_s_q3"] - a["mops_per_s_median"]])
    bars = ax.bar(x, a["mops_per_s_median"], 0.6, yerr=err, capsize=4, color=cs.BLUE, ecolor=cs.INK2)
    for b, m, g in zip(bars, a["mops_per_s_median"], a["payload_GB_per_s_median"]):
        ax.text(b.get_x() + b.get_width() / 2, m / 2, f"{m:.0f} M/s\n{g:.2f} GB/s", ha="center",
                va="center", fontsize=8.5, color="white", fontweight="bold")
    ax.set_xticks(x, LABELS)
    ax.set_ylabel("Operations per second (millions)")
    ax.set_title(name, loc="left")
cs.title(fig, "3a  Throughput by read/write mix (independent operations)", SUB +
         "Fixed op count per footprint (1 MiB: 50 M, 256 MiB: 20 M). GB/s label = 8 payload bytes x "
         "ops / time, a software count: not DRAM bandwidth (stores also cost a read-for-ownership "
         "and a later write-back that are not counted).")
cs.save(fig, "3a_read_write_mix_throughput.png")

# 3b: time per operation when every read depends on the previous read,
# compared with a linear mix of the two pure endpoints.
fig, axes = cs.plt.subplots(1, 2, figsize=(11.5, 5))
for ax, (ws, name) in zip(axes, FOOTPRINTS):
    a = summ[(summ["ws_KiB"] == ws) & (summ["mode"] == "dependent")].set_index("write_pct").loc[MIXES]
    err = np.vstack([a["ns_per_op_median"] - a["ns_per_op_q1"], a["ns_per_op_q3"] - a["ns_per_op_median"]])
    ax.bar(x, a["ns_per_op_median"], 0.6, yerr=err, capsize=4, color=cs.ORANGE, ecolor=cs.INK2,
           label="measured (dependent reads)")
    r, w = a.loc[0, "ns_per_op_median"], a.loc[100, "ns_per_op_median"]
    pred = [(1 - p / 100) * r + p / 100 * w for p in MIXES]
    ax.plot(x, pred, "D--", color=cs.INK2, lw=1.2, label="linear mix of the 100% endpoints")
    top = a["ns_per_op_q3"].max()
    for xi, m in zip(x, a["ns_per_op_median"]):
        inside = m > 0.25 * top
        ax.text(xi + 0.15 if not inside else xi, m * 0.5 if inside else m + 0.04 * top,
                f"{m:.1f}", ha="center", va="center" if inside else "bottom", fontsize=9,
                color="white" if inside else cs.INK, fontweight="bold" if inside else None)
    ax.set_xticks(x, LABELS)
    ax.set_ylabel("Mean time per operation (ns)")
    ax.set_title(name, loc="left")
cs.fig_legend(fig, axes[0])
cs.title(fig, "3b  Time per operation by read/write mix (dependent reads)", SUB +
         "Dependent mode: each address mixes in the previous read value, so reads are serialized "
         "and their latency is exposed; stores do not wait. The value is elapsed / all operations "
         "(reads and writes combined), NOT a separate per-read or per-write latency. Fixed op "
         "count: 1 MiB 20 M, 256 MiB 5 M.")
cs.save(fig, "3b_read_write_mix_latency.png")
