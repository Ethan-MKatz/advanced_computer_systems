#!/usr/bin/env python3
"""Plots 3a/3b: read/write mix sweep (4 KiB random, QD32)."""
import numpy as np

from plot_style import (BLUE, ERR_NOTE, INK2, ORANGE, PCT_RAMP, PCTS, agg, legend_above, load_runs, plt,
                        save, title, fig_legend, plain_log, valid, yerr)

MIXES = [100, 70, 50, 0]
LABELS = ["100% read", "70R / 30W", "50R / 50W", "100% write"]
SUB = ("Fixed: 4 KiB random (rw=randrw, rwmixread varied), iodepth=32, numjobs=1, direct=1, "
       "io_uring, 30 s + 2 s ramp, 4 GiB range.\n" + ERR_NOTE +
       ". fio reports read and write directions separately; they share one queue of 32.")


def main():
    d = valid(load_runs(), "exp3_rw_mix")
    d["mix"] = d["RWMIXREAD"].astype(int)
    d["kiops"] = d["iops"] / 1e3
    x = np.arange(len(MIXES))

    fig, ax = plt.subplots(figsize=(8.5, 4.8))
    bottoms = np.zeros(len(MIXES))
    for ddir, color in (("read", BLUE), ("write", ORANGE)):
        a = agg(d[d["direction"] == ddir], ["mix"], "kiops").set_index("mix").reindex(MIXES)
        vals = a["med"].fillna(0).values
        ax.bar(x, vals, 0.55, bottom=bottoms, color=color, label=f"{ddir} IOPS",
               edgecolor="#fcfcfb", linewidth=2)
        bottoms += vals
    # total per run (read + write of the same run), then median / range across trials
    tot = d.groupby(["mix", "trial"])["kiops"].sum().reset_index()
    bw = d.groupby(["mix", "trial"])["bw_MBps"].sum().reset_index()
    a = agg(tot, ["mix"], "kiops").set_index("mix").reindex(MIXES)
    b = agg(bw, ["mix"], "bw_MBps").set_index("mix").reindex(MIXES)
    ax.errorbar(x, a["med"], yerr=yerr(a), fmt="none", ecolor=INK2, capsize=4)
    for xi, v, mb in zip(x, a["med"], b["med"]):
        ax.annotate(f"{v:.0f}k total\n{mb:.0f} MB/s", (xi, v), xytext=(0, 6),
                    textcoords="offset points", ha="center", fontsize=9)
    ax.set_xticks(x, LABELS)
    ax.set_ylabel("Throughput (kIOPS), stacked read + write")
    ax.set_ylim(0, np.nanmax(a["hi"]) * 1.25)
    legend_above(ax)
    title(fig, "3a  Throughput by read/write mix", SUB + " Whiskers: total IOPS.")
    save(fig, "3a_read_write_mix_throughput.png")

    fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.8), sharey=True)
    w = 0.2
    for ax, ddir in zip(axes, ("read", "write")):
        s = d[d["direction"] == ddir]
        for i, (col, name) in enumerate(PCTS):
            a = agg(s, ["mix"], col).set_index("mix").reindex(MIXES)
            ax.bar(x + (i - 1.5) * w, a["med"], w * 0.92, yerr=yerr(a.fillna(0)), capsize=2,
                   color=PCT_RAMP[i], ecolor=INK2, label=name)
        mean = agg(s, ["mix"], "lat_mean_us").set_index("mix").reindex(MIXES)
        ax.plot(x, mean["med"], "D", color=ORANGE, label="mean")
        for xi, m in zip(x, mean["med"]):
            if np.isnan(m):
                ax.text(xi, 0.04, f"no {ddir}s", ha="center", color=INK2, fontsize=9,
                        transform=ax.get_xaxis_transform())
        ax.set_yscale("log")
        plain_log(ax)
        ax.set_xticks(x, LABELS)
        ax.set_xlim(-0.6, len(MIXES) - 0.4)
        ax.set_title(f"{ddir} latency", loc="left")
    axes[0].set_ylabel("Total latency (µs, log scale)")
    fig_legend(fig, axes[1], ncol=5)
    title(fig, "3b  Latency and tail latency by read/write mix", SUB)
    save(fig, "3b_read_write_mix_latency.png")


if __name__ == "__main__":
    main()
