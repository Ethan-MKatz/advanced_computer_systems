#!/usr/bin/env python3
"""Plots 7a/7b: misleading setup - buffered (page cache) vs direct I/O."""
import numpy as np

from plot_style import (BLUE, ERR_NOTE, INK2, ORANGE, agg, legend_above, load_runs, plt, save, title,
                        valid, yerr, plain_log)

CASES = [("exp7_randread_direct", "read: direct\n(device)", BLUE, ""),
         ("exp7_randread_buffered_cold", "read: buffered,\ncold cache*", ORANGE, "//"),
         ("exp7_randread_buffered_warm", "read: buffered,\nwarm cache*", ORANGE, "//"),
         ("exp7_randwrite_direct", "write: direct\n(device)", BLUE, ""),
         ("exp7_randwrite_buffered", "write: buffered*", ORANGE, "//")]
SUB = ("Fixed: 4 KiB random, psync (synchronous) engine, iodepth=1, numjobs=1, first 1 GiB of "
       "the test file, 15 s. Varied: direct=1 vs direct=0 (buffered), cache state.\n"
       "* = OS page-cache-inclusive measurement, NOT SSD device performance. Cold = file pages "
       "dropped via posix_fadvise first, no ramp; warm = after a buffered pass.\n" + ERR_NOTE + ".")


def main():
    d = valid(load_runs(), "exp7_pitfall")
    d["kiops"] = d["iops"] / 1e3
    names = [c[0] for c in CASES]
    x = np.arange(len(CASES))

    fig, ax = plt.subplots(figsize=(10, 5.2))
    a = agg(d, ["name"], "kiops").set_index("name").loc[names]
    bars = ax.bar(x, a["med"], 0.6, yerr=yerr(a), capsize=4, ecolor=INK2,
                  color=[c[2] for c in CASES], hatch=None, edgecolor="#fcfcfb")
    for b, c in zip(bars, CASES):
        if c[3]:
            b.set_hatch(c[3])
            b.set_edgecolor("#a8441c")
    for b, v in zip(bars, a["med"]):
        ax.annotate(f"{v:.1f}k", (b.get_x() + b.get_width() / 2, v), xytext=(0, 3),
                    textcoords="offset points", ha="center", fontsize=9)
    ax.set_yscale("log")
    plain_log(ax)
    ax.set_xticks(x, [c[1] for c in CASES])
    ax.set_ylabel("Throughput (kIOPS, log scale)")
    ax.bar([0], [0], color=BLUE, label="direct I/O (device)")
    ax.bar([0], [0], color=ORANGE, hatch="//", edgecolor="#a8441c",
           label="buffered I/O (page-cache-inclusive)")
    legend_above(ax)
    title(fig, "7a  Misleading setup: buffered vs direct I/O throughput", SUB)
    save(fig, "7a_buffered_vs_direct.png")

    fig, ax = plt.subplots(figsize=(10, 5.2))
    w = 0.38
    for i, (col, lab, ink) in enumerate((("lat_mean_us", "mean", None),
                                         ("p99_us", "p99", None))):
        a = agg(d, ["name"], col).set_index("name").loc[names]
        bars = ax.bar(x + (i - 0.5) * w, a["med"], w * 0.92, yerr=yerr(a), capsize=3,
                      ecolor=INK2, color=[c[2] for c in CASES], alpha=1.0 if i == 0 else 0.55,
                      edgecolor="#fcfcfb")
        for b, c, v in zip(bars, CASES, a["med"]):
            if c[3]:
                b.set_hatch(c[3])
                b.set_edgecolor("#a8441c")
    ax.set_yscale("log")
    plain_log(ax)
    ax.set_xticks(x, [c[1] for c in CASES])
    for lab, alpha in (("mean (solid)", 1.0), ("p99 (lighter)", 0.55)):
        ax.bar([0], [0], color=INK2, alpha=alpha, label=lab)
    legend_above(ax)
    ax.set_ylabel("Total latency per I/O (µs, log scale)")
    ax.margins(y=0.25)
    title(fig, "7b  Misleading setup: buffered vs direct I/O latency (mean and p99)",
          SUB)
    save(fig, "7b_buffered_vs_direct_latency.png")


if __name__ == "__main__":
    main()
