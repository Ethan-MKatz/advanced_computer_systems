#!/usr/bin/env python3
"""Plots 1a/1b: QD=1 baseline latency."""
import numpy as np

from plot_style import (BLUE, ERR_NOTE, INK2, PCT_RAMP, PCTS, agg, legend_above, load_runs, plt, save,
                        title, valid, yerr)

ORDER = [("randread", "4k", "4 KiB random\nread"), ("randwrite", "4k", "4 KiB random\nwrite"),
         ("read", "128k", "128 KiB seq.\nread"), ("write", "128k", "128 KiB seq.\nwrite")]
SUB = ("Fixed: direct=1, io_uring, iodepth=1, numjobs=1, 30 s + 2 s ramp, 4 GiB file range, "
       "ext4 file on Samsung PM9C1a.\nQD=1 = one outstanding I/O: a software-path + device "
       "baseline, not a hardware minimum. " + ERR_NOTE + ".")


def main():
    d = valid(load_runs(), "exp1_qd1")
    labels = [lbl for *_, lbl in ORDER]
    x = np.arange(len(ORDER))

    fig, ax = plt.subplots(figsize=(8, 4.8))
    a = agg(d, ["RW", "BS"], "lat_mean_us").set_index(["RW", "BS"]).loc[[(r, b) for r, b, _ in ORDER]]
    bars = ax.bar(x, a["med"], 0.55, yerr=yerr(a), capsize=4, color=BLUE, ecolor=INK2)
    p50 = agg(d, ["RW", "BS"], "p50_us").set_index(["RW", "BS"]).loc[[(r, b) for r, b, _ in ORDER]]
    ax.plot(x, p50["med"], "D", color="#0d366b", markersize=7, label="median (p50) latency")
    for b, v in zip(bars, a["med"]):
        ax.annotate(f"{v:.1f} µs", (b.get_x() + b.get_width() / 2, v / 2), ha="center",
                    fontsize=9.5, color="white", fontweight="bold")
    ax.set_xticks(x, labels)
    ax.set_ylabel("Mean total latency per I/O (µs)")
    legend_above(ax, handles=[bars.patches[0], ax.lines[-1]],
                 labels=["mean latency", "median (p50) latency"])
    title(fig, "1a  QD=1 baseline latency", SUB)
    save(fig, "1a_qd1_baseline_latency.png")

    fig, ax = plt.subplots(figsize=(9, 5))
    w = 0.2
    for i, (col, name) in enumerate(PCTS):
        a = agg(d, ["RW", "BS"], col).set_index(["RW", "BS"]).loc[[(r, b) for r, b, _ in ORDER]]
        ax.bar(x + (i - 1.5) * w, a["med"], w * 0.92, yerr=yerr(a), capsize=2,
               color=PCT_RAMP[i], ecolor=INK2, label=name)
    ax.set_yscale("log")
    ax.set_xticks(x, labels)
    ax.set_ylabel("Total latency (µs, log scale)")
    legend_above(ax)
    title(fig, "1b  QD=1 tail latency: p50 / p95 / p99 / p99.9", SUB +
          "\np99.9 rests on >= 0.1% of ~10^5-10^6 samples per run (hundreds of I/Os).")
    save(fig, "1b_qd1_tail_latency.png")


if __name__ == "__main__":
    main()
