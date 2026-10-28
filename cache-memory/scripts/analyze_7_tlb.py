#!/usr/bin/env python3
"""Experiment 7 (timing-only): page locality and page size -> 7a/7b.

TLB-miss counters were unavailable (perf_event_open: EACCES), so the
counter-based plot 7a_tlb_misses_vs_page_locality.png is BLOCKED; 7a here shows
time per access versus the number of distinct pages touched instead.
"""
import numpy as np
import pandas as pd

import cm_style as cs

raw = pd.read_csv(cs.RAW / "7_tlb_impact.csv")
cs.require(raw, ["pages", "lines_per_page", "lines", "span_KiB", "thp", "ns_per_access",
                 "setup_minor_faults", "anon_huge_KiB", "experiment", "trial", "pinning"],
           5 * (14 + 8), "7_tlb_impact")
keys = ["experiment", "pages", "lines_per_page", "span_KiB", "thp"]
summ = cs.iqr_summary(raw, keys, "ns_per_access")
summ["median_setup_minor_faults"] = raw.groupby(keys)["setup_minor_faults"].median().values
summ["min_anon_huge_KiB"] = raw.groupby(keys)["anon_huge_KiB"].min().values
summ["max_anon_huge_KiB"] = raw.groupby(keys)["anon_huge_KiB"].max().values
summ.to_csv(cs.PROC / "7_tlb_impact_summary.csv", index=False)
print(summ.drop(columns=["min", "max"]).to_string(index=False))

PAGE = {0: ("4 KiB pages (MADV_NOHUGEPAGE)", cs.BLUE), 1: ("2 MiB transparent huge pages (MADV_HUGEPAGE)", cs.ORANGE)}
NOTE = ("Timing only: TLB-miss counters are unavailable (perf_event_open returns EACCES), so no TLB "
        "miss counts are shown. Pinned to CPU 0, 5 trials, median with IQR whiskers. ")

a = summ[summ["experiment"] == "7a_page_locality"]
fig, ax = cs.plt.subplots(figsize=(10, 5.6))
for thp, (name, color) in PAGE.items():
    s = a[a["thp"] == thp].sort_values("pages")
    ax.errorbar(s["pages"], s["median"], yerr=cs.yerr(s), marker="o", color=color, capsize=3,
                label=name)
pages = sorted(a["pages"].unique())
ax.set_xscale("log", base=2)
ax.set_xticks(pages, [f"{p}\n({8192 // p}/page)" for p in pages])
ax.minorticks_off()
ax.set_xlabel("Distinct 4 KiB page slots touched (lines per page)")
ax.set_ylabel("Time per dependent load (ns)")
ax.set_ylim(bottom=0)
cs.fig_legend(fig, ax, ncol=2)
cs.title(fig, "7a  Latency vs page locality (fixed 512 KiB of data)", NOTE +
         "The same 8192 cache lines (512 KiB, smaller than the nominal 2 MiB L2) are spread over "
         "128 to 8192 page slots (span 512 KiB to 32 MiB), random line offsets, one random cyclic "
         "chain, 20 M loads. Only page spread changes, so the growth is attributed to address "
         "translation reach; this is an inference from timing.")
cs.save(fig, "7a_latency_vs_page_locality.png")

b = summ[summ["experiment"] == "7b_page_size"].sort_values(["span_KiB", "thp"])
spans = sorted(b["span_KiB"].unique())
fig, ax = cs.plt.subplots(figsize=(10, 5.6))
x = np.arange(len(spans))
w = 0.38
for i, (thp, (name, color)) in enumerate(PAGE.items()):
    s = b[b["thp"] == thp].set_index("span_KiB").loc[spans]
    bars = ax.bar(x + (i - 0.5) * w, s["median"], w * 0.95, yerr=cs.yerr(s), capsize=3,
                  color=color, ecolor=cs.INK2, label=name)
    for bar, m, flt, hp, q3 in zip(bars, s["median"], s["median_setup_minor_faults"],
                                   s["min_anon_huge_KiB"], s["q3"]):
        ax.text(bar.get_x() + bar.get_width() / 2, q3 * 1.08,
                f"{m:.0f} ns\n{int(flt)} faults\nTHP {hp / 1024:.0f} MiB", ha="center",
                va="bottom", fontsize=7.5, color=cs.INK2)
ax.set_xticks(x, [cs.kib_label(s) for s in spans])
ax.set_yscale("log")
cs.plain_log(ax)
ax.margins(y=0.3)
ax.set_xlabel("Working set (dense random pointer chase, all 64 lines of every 4 KiB slot)")
ax.set_ylabel("Time per dependent load (ns, log scale)")
cs.fig_legend(fig, ax, ncol=2)
cs.title(fig, "7b  Runtime vs page configuration", NOTE +
         "10 M loads. Labels: median time, minor page faults during buffer setup (getrusage) and the "
         "smallest AnonHugePages backing seen across trials (/proc/self/smaps_rollup): measured "
         "evidence of which page size was actually used. THP backing is not guaranteed: at 256 MiB one "
         "trial got only 44 MiB of huge pages (405 ns, close to the 4 KiB result) while fully backed "
         "trials took 343–362 ns.")
cs.save(fig, "7b_runtime_vs_page_configuration.png")
