#!/usr/bin/env python3
"""Plots 5a/5b: tail latency at mid-QD vs near-knee QD."""
import json

import numpy as np
import pandas as pd

from plot_style import (BLUE, ERR_NOTE, INK2, MUTED, ORANGE, PCT_RAMP, PROC, agg, legend_above, load_runs, plain_log,
                        plt, save, title, valid, yerr)

PCTS5 = [("p50_us", "p50"), ("p95_us", "p95"), ("p99_us", "p99"), ("p99_9_us", "p99.9"),
         ("p99_99_us", "p99.99")]


def main():
    sel = json.loads((PROC / "exp5_selected_depths.json").read_text())
    qmid, qknee = sel["mid"]["iodepth"], sel["knee"]["iodepth"]
    d = valid(load_runs(), "exp5_tail")
    d["QD"] = d["QD"].astype(int)
    n_ios = int(d["total_ios"].median())
    sub = (f"Fixed: 4 KiB random read, direct=1, io_uring, numjobs=1, 60 s + 2 s ramp, "
           f"4 GiB range. Varied: iodepth = {qmid} (mid) vs {qknee} (near knee, chosen from 4b).\n"
           f"~{n_ios / 1e6:.1f} M I/Os per run, so p99.99 rests on ~{n_ios // 10000} samples. "
           + ERR_NOTE + ".")
    cases = [(qmid, f"mid: QD{qmid}", BLUE), (qknee, f"near knee: QD{qknee}", ORANGE)]

    fig, ax = plt.subplots(figsize=(9, 5))
    x = np.arange(len(PCTS5))
    w = 0.36
    for i, (qd, name, color) in enumerate(cases):
        s = d[d["QD"] == qd]
        meds, errs = [], []
        for col, _ in PCTS5:
            a = agg(s, ["QD"], col)
            meds.append(a["med"].iloc[0])
            errs.append(yerr(a)[:, 0])
        bars = ax.bar(x + (i - 0.5) * w, meds, w * 0.92, yerr=np.array(errs).T, capsize=3,
                      color=color, ecolor=INK2, label=name)
        for b, v in zip(bars, meds):
            ax.text(b.get_x() + b.get_width() / 2, v / 1.25, f"{v:.0f}", ha="center",
                    va="top", fontsize=8.5, color="white", fontweight="bold")
    ax.set_yscale("log")
    plain_log(ax)
    ax.set_ylim(bottom=30)
    ax.set_xticks(x, [n for _, n in PCTS5])
    ax.set_xlabel("Latency percentile")
    ax.set_ylabel("Total latency (µs, log scale)")
    legend_above(ax)
    title(fig, "5a  Tail-latency percentiles at mid vs near-knee queue depth", sub)
    save(fig, "5a_tail_latency_percentiles.png")

    bins = pd.read_csv(PROC / "exp5_latency_bins.csv")
    bins = bins[bins["direction"] == "read"]
    src = bins["source"].iloc[0]
    fig, ax = plt.subplots(figsize=(9, 5))
    for qd, name, color in cases:
        b = bins[bins["QD"] == qd]
        for t, g in b.groupby("trial"):
            g = g.sort_values("latency_us")
            c = g["count"].values
            ccdf = 1.0 - np.cumsum(c) / c.sum()
            ax.step(g["latency_us"], np.clip(ccdf, 1e-9, None), where="post", color=color,
                    lw=1.6, alpha=0.9 if t == 1 else 0.45,
                    label=f"{name} (trial 1; lighter = trials 2-3)" if t == 1 else None)
    for p, lab in ((1e-2, "p99"), (1e-3, "p99.9"), (1e-4, "p99.99")):
        ax.axhline(p, color=MUTED, ls=":", lw=1)
        ax.text(1.01, p, lab, transform=ax.get_yaxis_transform(),
                va="center", fontsize=8, color=INK2)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_ylim(1e-7, 1.5)
    ax.set_xlabel("Total latency (µs, log scale)")
    ax.set_ylabel("P(latency > x)  (log scale)")
    legend_above(ax)
    title(fig, "5b  Latency distribution: complementary CDF (every I/O, fio histogram)",
          sub.split("\n")[0] + f"\nSource: fio json+ '{src}' bins - every completed I/O, "
          "bucketed by fio at ~1.5% relative width; values below 1e-5 rest on few samples.")
    save(fig, "5b_latency_distribution.png")


if __name__ == "__main__":
    main()
