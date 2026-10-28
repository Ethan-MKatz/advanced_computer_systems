#!/usr/bin/env python3
"""Plots 6a/6b: working-set (LBA range) sweep and burst vs later sustained writes."""
import numpy as np
import pandas as pd

from plot_style import (BLUE, ERR_NOTE, INK2, MUTED, ORANGE, PROC, agg, legend_above, fig_legend, load_runs, plt, save,
                        title, valid, yerr)

SIZES = {"64m": 64, "256m": 256, "1g": 1024, "4g": 4096}
BURST = (0, 10)       # seconds
LATE = (60, 90)


def main():
    d = valid(load_runs(), "exp6_device_state")
    a6 = d[d["name"].str.startswith("exp6a")].copy()
    a6["mib"] = a6["SIZE"].map(SIZES)
    a6["kiops"] = a6["iops"] / 1e3

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.8))
    for rw, color in (("randread", BLUE), ("randwrite", ORANGE)):
        s = a6[a6["RW"] == rw]
        a = agg(s, ["mib"], "kiops").sort_values("mib")
        axes[0].errorbar(a["mib"], a["med"], yerr=yerr(a), marker="o", color=color,
                         capsize=3, label=rw.replace("rand", "random "))
        a = agg(s, ["mib"], "p99_us").sort_values("mib")
        axes[1].errorbar(a["mib"], a["med"], yerr=yerr(a), marker="o", color=color,
                         capsize=3, label=rw.replace("rand", "random "))
    for ax in axes:
        ax.set_xscale("log", base=2)
        ax.set_xticks(list(SIZES.values()), ["64 MiB", "256 MiB", "1 GiB", "4 GiB"])
        ax.set_xlabel("Accessed range of the test file (working set, log2)")
    axes[0].set_ylabel("Throughput (kIOPS)")
    axes[0].set_ylim(bottom=0)
    axes[0].set_title("Throughput", loc="left")
    axes[1].set_ylabel("p99 total latency (µs)")
    axes[1].set_ylim(bottom=0)
    axes[1].set_title("p99 latency (same runs)", loc="left")
    fig_legend(fig, axes[0])
    title(fig, "6a  Throughput vs working-set (LBA range) size",
          "Fixed: 4 KiB random, iodepth=32, numjobs=1, direct=1, io_uring, 20 s + 2 s ramp; "
          "range starts at file offset 0. Varied: range size, read vs write.\n" + ERR_NOTE +
          ". Ranges are file ranges; ext4 maps them to device LBAs (contiguity not verified).")
    save(fig, "6a_working_set_throughput.png")

    ts = pd.read_csv(PROC / "exp6b_timeseries.csv")
    temps = pd.read_csv(PROC / "exp6b_temperature.csv")
    fig, axes = plt.subplots(3, 1, figsize=(10, 8), sharex=True,
                             gridspec_kw={"height_ratios": [1.3, 1, 0.8]})
    colors = {1: BLUE, 2: ORANGE}
    notes = []
    for trial, g in ts.groupby("trial"):
        iops = g[g["metric"] == "iops"].sort_values("time_s")
        # fio appends a final partial-interval sample at the same timestamp while the
        # queue drains; keep the first (full 1 s) sample per timestamp
        iops = iops.drop_duplicates("time_s", keep="first")
        lat = g[g["metric"] == "lat_ns"].sort_values("time_s").drop_duplicates("time_s",
                                                                               keep="first")
        axes[0].plot(iops["time_s"], iops["value"] / 1e3, color=colors[trial], lw=1.6,
                     label=f"trial {trial}")
        axes[1].plot(lat["time_s"], lat["value"] / 1e3, color=colors[trial], lw=1.6)
        tt = temps[temps["trial"] == trial]
        axes[2].plot(tt["time_s"], tt["nvme_temp_c"], color=colors[trial], lw=1.6)
        win = lambda df, lo, hi: df[(df["time_s"] > lo) & (df["time_s"] <= hi)]["value"]  # noqa
        b, l = win(iops, *BURST).mean() / 1e3, win(iops, *LATE).mean() / 1e3
        notes.append(f"trial {trial}: {b:.0f}k IOPS in {BURST[0]}-{BURST[1]} s vs {l:.0f}k in "
                     f"{LATE[0]}-{LATE[1]} s ({(l / b - 1) * 100:+.0f}%)")
    for ax in axes:
        for lo, hi, lab in ((*BURST, "early window"), (*LATE, "late window")):
            ax.axvspan(lo, hi, color=MUTED, alpha=0.12, lw=0)
    axes[0].text(BURST[0] + 0.5, 0.04, "early", transform=axes[0].get_xaxis_transform(),
                 fontsize=8, color=INK2)
    axes[0].text(LATE[0] + 0.5, 0.04, "late", transform=axes[0].get_xaxis_transform(),
                 fontsize=8, color=INK2)
    axes[0].set_ylabel("kIOPS (1 s avg)")
    axes[0].set_ylim(bottom=0)
    fig_legend(fig, axes[0])
    axes[0].text(0.5, 0.30, "\n".join(notes), transform=axes[0].transAxes, va="top",
                 ha="center", fontsize=9, color=INK2)
    axes[1].set_ylabel("Mean latency (µs, 1 s avg)")
    axes[1].set_ylim(bottom=0)
    axes[2].set_ylabel("NVMe composite\ntemp (°C)")
    axes[2].set_xlabel("Time since start of run (s)")
    title(fig, "6b  Burst vs later behaviour: sustained 4 KiB random writes",
          "Fixed: 4 KiB random write, iodepth=32, numjobs=1, direct=1, io_uring, 4 GiB range, "
          "90 s, no ramp (to capture the burst); 120 s idle before each trial.\n"
          "Bounded test (~90 s of writes), not full-drive preconditioning: a later-window change "
          "is device-state evidence only if it repeats across trials. The final partial-interval "
          "log sample fio writes at t = 90 s is omitted.")
    save(fig, "6b_burst_vs_steady_state.png")


if __name__ == "__main__":
    main()
