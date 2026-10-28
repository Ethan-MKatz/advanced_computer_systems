#!/usr/bin/env python3
"""Plots 4a/4b: queue-depth sweep, throughput-latency curve, knee, Little's Law."""
import json

import numpy as np

from plot_style import (BLUE, ERR_NOTE, INK2, MUTED, ORANGE, PROC, agg, legend_above, load_runs, plt, save, fig_legend, plain_log,
                        title, valid, yerr)

SUB = ("Fixed: 4 KiB random read, direct=1, io_uring, 20 s + 2 s ramp, 4 GiB range. "
       "Varied: iodepth per job (numjobs=1 primary curve; numjobs=4 parallel curve, "
       "aggregated with group_reporting). " + ERR_NOTE +
       ". Achieved L = IOPS x mean latency (Little's Law).")
# label a subset of points: the low-depth points sit on top of each other
LABELLED = {1: {1, 16, 32, 64, 128, 256}, 4: {16, 32, 64, 128, 256}}
CURVES = {1: ("numjobs=1 (primary)", BLUE), 4: ("numjobs=4 (parallel)", ORANGE)}


def prep():
    d = valid(load_runs(), "exp4_queue_depth")
    d["QD"] = d["QD"].astype(int)
    d["NJ"] = d["NJ"].astype(int)
    d["total_qd"] = d["QD"] * d["NJ"]
    d["kiops"] = d["iops"] / 1e3
    d["L"] = d["iops"] * d["lat_mean_us"] / 1e6     # outstanding I/Os (Little's Law)
    return d


def main():
    d = prep()
    sel_path = PROC / "exp5_selected_depths.json"
    sel = json.loads(sel_path.read_text()) if sel_path.exists() else None

    fig, ax = plt.subplots(figsize=(9.5, 5.6))
    for nj, (name, color) in CURVES.items():
        s = d[d["NJ"] == nj]
        y = agg(s, ["total_qd"], "kiops").sort_values("total_qd")
        x = agg(s, ["total_qd"], "lat_mean_us").sort_values("total_qd")
        L = agg(s, ["total_qd"], "L").sort_values("total_qd")
        ax.errorbar(x["med"], y["med"], xerr=yerr(x), yerr=yerr(y), marker="o", color=color,
                    capsize=3, label=name)
        for xm, ym, q, l in zip(x["med"], y["med"], x["total_qd"], L["med"]):
            if q not in LABELLED[nj]:
                continue
            cfg = f"QD{q}" if nj == 1 else f"4x{q // 4}"
            ax.annotate(f"{cfg}\nL={l:.1f}", (xm, ym), xytext=(6, -14 if nj == 1 else 6),
                        textcoords="offset points", fontsize=7.5, color=INK2)
    ax.set_xscale("log")
    plain_log(ax, "x")
    ax.set_xlabel("Mean total latency per I/O (µs, log scale)")
    ax.set_ylabel("Throughput (kIOPS)   [x 4.096 = MB/s]")
    ax.set_ylim(bottom=0)
    legend_above(ax)
    title(fig, "4a  Throughput vs latency as queue depth grows",
          SUB + " Labels (subset): configured depth / achieved L.")
    save(fig, "4a_queue_depth_throughput_latency.png")

    fig, axes = plt.subplots(1, 2, figsize=(12, 5), gridspec_kw={"width_ratios": [1.3, 1]})
    ax = axes[0]
    for nj, (name, color) in CURVES.items():
        a = agg(d[d["NJ"] == nj], ["total_qd"], "kiops").sort_values("total_qd")
        ax.errorbar(a["total_qd"], a["med"], yerr=yerr(a), marker="o", color=color,
                    capsize=3, label=name)
    if sel:
        k = sel["knee"]["iodepth"]
        ax.axvline(k, color=MUTED, ls="--", lw=1)
        ax.axhline(0.9 * sel["peak_iops_median"] / 1e3, color=MUTED, ls=":", lw=1)
        ax.annotate(f"knee (numjobs=1): QD{k}\nfirst depth >= 90% of peak IOPS",
                    (k, sel["knee"]["iops_median"] / 1e3), xytext=(8, -40),
                    textcoords="offset points", fontsize=8.5, color=INK2)
    top = d[(d["NJ"] == 1) & (d["QD"] == d[d["NJ"] == 1]["QD"].max())]
    cpu = (top["usr_cpu_pct"] + top["sys_cpu_pct"]).median()
    ax.text(0.02, 0.97, f"numjobs=1 plateau: the single fio job uses {cpu:.0f}% CPU (usr+sys)\n"
            "at QD256: consistent with a host-side submission limit;\n"
            "numjobs=4 keeps scaling at the same total depth.",
            transform=ax.transAxes, va="top", fontsize=8.5, color=INK2)
    ax.set_xscale("log", base=2)
    qds = sorted(d["total_qd"].unique())
    ax.set_xticks(qds, [str(q) for q in qds])
    ax.set_xlabel("Total outstanding I/Os configured (iodepth x numjobs, log2)")
    ax.set_ylabel("Throughput (kIOPS)")
    ax.set_ylim(bottom=0)
    ax.set_title("IOPS vs queue depth", loc="left")

    ax = axes[1]
    for nj, (name, color) in CURVES.items():
        a = agg(d[d["NJ"] == nj], ["total_qd"], "L").sort_values("total_qd")
        ax.errorbar(a["total_qd"], a["med"], yerr=yerr(a), marker="o", color=color,
                    capsize=3, label=name)
    lim = [0.8, max(qds) * 1.3]
    ax.plot(lim, lim, color=MUTED, ls="--", lw=1, label="L = configured depth")
    ax.set_xscale("log", base=2)
    ax.set_yscale("log", base=2)
    ax.set_xticks(qds, [str(q) for q in qds])
    ax.set_yticks(qds, [str(q) for q in qds])
    ax.set_xlabel("Configured outstanding I/Os (log2)")
    ax.set_ylabel("Achieved L = IOPS x mean latency (log2)")
    fig_legend(fig, ax, ncol=3)
    ax.set_title("Little's Law check: configured vs achieved depth", loc="left")
    title(fig, "4b  IOPS vs queue depth and saturation knee", SUB)
    save(fig, "4b_queue_depth_iops.png")


if __name__ == "__main__":
    main()
