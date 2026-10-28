import csv
import statistics
from collections import defaultdict
from pathlib import Path

import cm_style as cs  # noqa: F401  (sets the Agg backend and shared style)

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "cache-memory/results/raw/1a_zero_queue_latency.csv"
PROCESSED = ROOT / "cache-memory/results/processed/1a_zero_queue_latency_summary.csv"
PLOT = ROOT / "cache-memory/results/plots/1a_zero_queue_latency_working_set.png"

groups = defaultdict(list)

with RAW.open(newline="") as f:
    for row in csv.DictReader(f):
        groups[int(row["working_set_KiB"])].append(
            float(row["ns_per_access"])
        )

PROCESSED.parent.mkdir(parents=True, exist_ok=True)
PLOT.parent.mkdir(parents=True, exist_ok=True)

sizes = sorted(groups)
medians = []
q1s = []
q3s = []

def percentile(values, p):
    values = sorted(values)
    pos = (len(values) - 1) * p
    lo = int(pos)
    hi = min(lo + 1, len(values) - 1)
    frac = pos - lo
    return values[lo] * (1 - frac) + values[hi] * frac

with PROCESSED.open("w", newline="") as f:
    fields = [
        "working_set_KiB",
        "trials",
        "median_ns_per_access",
        "q1_ns_per_access",
        "q3_ns_per_access",
        "min_ns_per_access",
        "max_ns_per_access",
    ]
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()

    for size in sizes:
        values = groups[size]
        median = statistics.median(values)
        q1 = percentile(values, 0.25)
        q3 = percentile(values, 0.75)

        medians.append(median)
        q1s.append(q1)
        q3s.append(q3)

        writer.writerow({
            "working_set_KiB": size,
            "trials": len(values),
            "median_ns_per_access": f"{median:.3f}",
            "q1_ns_per_access": f"{q1:.3f}",
            "q3_ns_per_access": f"{q3:.3f}",
            "min_ns_per_access": f"{min(values):.3f}",
            "max_ns_per_access": f"{max(values):.3f}",
        })

        print(
            f"{size:>6} KiB | median={median:>8.3f} ns "
            f"| IQR={q1:.3f}–{q3:.3f} ns "
            f"| trials={len(values)}"
        )


fig, ax = cs.plt.subplots(figsize=(10, 5.6))
ax.errorbar(
    sizes,
    medians,
    yerr=[
        [m - q1 for m, q1 in zip(medians, q1s)],
        [q3 - m for m, q3 in zip(medians, q3s)],
    ],
    marker="o",
    capsize=3,
    color=cs.BLUE,
    label="median of 5 trials (whiskers: IQR)",
)
cs.size_axis(ax, sizes)
ax.set_yscale("log")
cs.plain_log(ax)
cs.nominal_marks(ax)
ax.set_ylabel("Dependent-load latency (ns per access, log scale)")
cs.title(
    fig,
    "1a  Zero-queue (pointer-chasing) latency vs working-set size",
    "Original run (results/raw/1a_zero_queue_latency.csv): one random cyclic chain of 64-byte nodes, "
    "10 M dependent loads per trial, 5 trials, 4 KiB pages, process NOT pinned to a CPU type. "
    "Dashed lines are nominal P-core capacities, not measured transition points; a footprint "
    "category does not prove which level served the loads. See 5a for the pinned re-run.",
)
cs.save(fig, PLOT.name)

print(f"\nSummary CSV: {PROCESSED}")
print(f"Plot saved:  {PLOT}")
