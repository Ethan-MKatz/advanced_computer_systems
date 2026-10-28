#!/usr/bin/env python3
"""Experiment 5: summarize the pinned working-set sweep and draw 5a/5b."""
import pandas as pd

import cm_style as cs

lat = pd.read_csv(cs.RAW / "5_working_set_sweep.csv")
cs.require(lat, ["working_set_KiB", "accesses", "ns_per_access", "trial", "pinning"], 34 * 5,
           "5_working_set_sweep")
bw = pd.read_csv(cs.RAW / "5_working_set_bandwidth.csv")
cs.require(bw, ["mode", "ws_KiB", "passes", "seconds", "GB_per_s", "trial", "pinning"], 20 * 2 * 5,
           "5_working_set_bandwidth")
orig = pd.read_csv(cs.PROC / "1a_zero_queue_latency_summary.csv")

ls = cs.iqr_summary(lat, ["working_set_KiB"], "ns_per_access")
ls["source"] = "latency"
bs = cs.iqr_summary(bw, ["mode", "ws_KiB"], "GB_per_s").rename(columns={"ws_KiB": "working_set_KiB"})
bs["source"] = "stream_" + bs.pop("mode")
summ = pd.concat([ls.rename(columns=lambda c: c if c in ("working_set_KiB", "source", "n") else f"{c}"),
                  bs], ignore_index=True)
summ.insert(0, "metric", summ["source"].map(lambda s: "ns_per_access" if s == "latency" else "GB_per_s"))
summ.to_csv(cs.PROC / "5_working_set_summary.csv", index=False)
print(ls[["working_set_KiB", "median", "q1", "q3"]].to_string(index=False))
print(bs.pivot(index="working_set_KiB", columns="source", values="median").round(2).to_string())

fig, ax = cs.plt.subplots(figsize=(11, 5.8))
ax.plot(orig["working_set_KiB"], orig["median_ns_per_access"], "s--", color=cs.MUTED, lw=1.2,
        ms=5, label="experiment 1 original run (unpinned)")
ax.errorbar(ls["working_set_KiB"], ls["median"], yerr=cs.yerr(ls), marker="o", color=cs.BLUE,
            capsize=3, label="this sweep, pinned to CPU 0 (P-core)")
ax.set_yscale("log")
cs.plain_log(ax)
cs.size_axis(ax, [4, 16, 48, 128, 512, 2048, 4096, 12288, 32768, 262144])
cs.nominal_marks(ax)
ax.set_ylabel("Dependent-load latency (ns per access, log scale)")
cs.fig_legend(fig, ax)
cs.title(fig, "5a  Pointer-chasing latency across working-set sizes (pinned re-run)",
         "Unchanged src/latency.cpp (random cyclic chain of 64-byte nodes, 4 KiB pages), "
         "built with -O2 -march=native, taskset -c 0, 34 sizes from 4 KiB to 256 MiB, 10 M loads "
         "(5 M from 16 MiB up), 5 trials, median with IQR whiskers. Dashed verticals are nominal "
         "P-core capacities used as reference points only; large footprints also include 4 KiB-page "
         "translation cost (see experiment 7).")
cs.save(fig, "5a_working_set_latency_regions.png")

fig, ax = cs.plt.subplots(figsize=(11, 5.8))
for mode, color, name in (("read", cs.BLUE, "read (sum of every 8-byte word)"),
                          ("write", cs.ORANGE, "write (store to every 8-byte word)")):
    s = bs[bs["source"] == f"stream_{mode}"].sort_values("working_set_KiB")
    ax.errorbar(s["working_set_KiB"], s["median"], yerr=cs.yerr(s), marker="o", color=color,
                capsize=3, label=name)
cs.size_axis(ax, [16, 48, 128, 512, 2048, 4096, 12288, 32768, 262144])
cs.nominal_marks(ax)
ax.set_ylim(bottom=0)
ax.set_ylabel("Software-counted bandwidth (GB/s)")
cs.fig_legend(fig, ax)
cs.title(fig, "5b  Streaming bandwidth across working-set sizes",
         "src/stream_bw.cpp (-O3 -march=native, AVX2-vectorized), single thread pinned to CPU 0, "
         "about 2 GiB moved per measurement (at least 5 passes) after one warm-up pass and a 200 ms "
         "spin, 5 trials, median with IQR whiskers. GB/s = buffer bytes x passes / time (10^9 B/s); "
         "write traffic excludes read-for-ownership and write-back, so it is not DRAM bandwidth.")
cs.save(fig, "5b_working_set_bandwidth.png")
