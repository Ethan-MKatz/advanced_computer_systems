#!/usr/bin/env python3
"""Plots 2a/2b: block-size sweep, random vs sequential reads, QD=1 and QD=32."""
from plot_style import (BLUE, ERR_NOTE, ORANGE, agg, legend_above, kib, load_runs, plt, save, title, fig_legend, plain_log,
                        valid, yerr)

PAT = {"randread": ("random read", BLUE), "read": ("sequential read", ORANGE)}
LS = {32: "-", 1: "--"}
SUB = ("Fixed: 100% read, direct=1, io_uring, numjobs=1, 15 s + 2 s ramp, 4 GiB range. "
       "Varied: block size, pattern, iodepth (solid = QD32, dashed = QD1).\n" + ERR_NOTE +
       ". Throughput and latency come from the same runs.")


def series(d, col):
    for qd in (32, 1):
        for rw, (name, color) in PAT.items():
            s = d[(d["QD"] == qd) & (d["RW"] == rw)]
            a = agg(s, ["kib"], col).sort_values("kib")
            yield qd, name, color, a


def main():
    d = valid(load_runs(), "exp2_block_size")
    d["kib"] = d["BS"].map(kib)
    d["QD"] = d["QD"].astype(int)
    d["kiops"] = d["iops"] / 1e3
    ticks = sorted(d["kib"].unique())

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.8))
    for ax, col, lab in ((axes[0], "kiops", "Throughput (kIOPS)"),
                         (axes[1], "bw_MBps", "Throughput (MB/s, 10^6 B/s)")):
        for qd, name, color, a in series(d, col):
            ax.errorbar(a["kib"], a["med"], yerr=yerr(a), ls=LS[qd], marker="o", color=color,
                        capsize=3, label=f"{name}, QD{qd}")
        ax.set_xscale("log", base=2)
        ax.set_xticks(ticks, [f"{t}" for t in ticks])
        ax.set_xlabel("Block size (KiB, log2 scale)")
        ax.set_ylabel(lab)
        ax.set_ylim(bottom=0)
    axes[0].set_title("IOPS (meaningful for small blocks)", loc="left")
    axes[1].set_title("Bandwidth (meaningful for large blocks)", loc="left")
    fig_legend(fig, axes[0])
    title(fig, "2a  Throughput vs block size: random vs sequential reads", SUB)
    save(fig, "2a_block_size_throughput.png")

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.8))
    for ax, qd in zip(axes, (1, 32)):
        for rw, (name, color) in PAT.items():
            s = d[(d["QD"] == qd) & (d["RW"] == rw)]
            for col, ls, mk, lab in (("lat_mean_us", "-", "o", "mean"),
                                     ("p99_us", ":", "^", "p99")):
                a = agg(s, ["kib"], col).sort_values("kib")
                ax.errorbar(a["kib"], a["med"], yerr=yerr(a), ls=ls, marker=mk, color=color,
                            capsize=3, label=f"{name}, {lab}")
        ax.set_xscale("log", base=2)
        ax.set_yscale("log")
        plain_log(ax)
        ax.set_xticks(ticks, [f"{t}" for t in ticks])
        ax.set_xlabel("Block size (KiB, log2 scale)")
        ax.set_ylabel("Total latency per I/O (µs, log scale)")
        ax.set_title(f"iodepth = {qd}", loc="left")
    fig_legend(fig, axes[0])
    title(fig, "2b  Latency vs block size: random vs sequential reads (mean solid, p99 dotted)",
          SUB.replace("(solid = QD32, dashed = QD1)", "(panels: QD1, QD32)"))
    save(fig, "2b_block_size_latency.png")


if __name__ == "__main__":
    main()
