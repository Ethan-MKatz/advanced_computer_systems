import csv
from pathlib import Path

import cm_style as cs  # noqa: F401  (sets the Agg backend and shared style)

ROOT = Path(__file__).resolve().parents[2]
SUMMARY = ROOT / "cache-memory/results/processed/1a_zero_queue_latency_summary.csv"
PLOT = ROOT / "cache-memory/results/plots/1b_latency_by_working_set_region.png"

# These are approximate working-set categories, not direct hardware
# measurements of individual cache levels.
REGIONS = [
    ("<= nominal L1D\n16–48 KiB", [16, 32, 48]),
    ("just above L1D\n64 KiB", [64]),
    ("<= nominal L2\n512 KiB–2 MiB", [512, 1024, 2048]),
    ("above L2\n3–4 MiB", [3072, 4096]),
    ("<= nominal L3\n8–12 MiB", [8192, 12288]),
    ("above L3\n16–64 MiB", [16384, 32768, 65536]),
]

with SUMMARY.open(newline="") as f:
    rows = {
        int(row["working_set_KiB"]): row
        for row in csv.DictReader(f)
    }

labels = []
medians = []
lower_errors = []
upper_errors = []

for label, sizes in REGIONS:
    available = [rows[s] for s in sizes if s in rows]
    if not available:
        continue

    # Summarize the per-size medians within each descriptive region.
    values = [float(row["median_ns_per_access"]) for row in available]
    q1_values = [float(row["q1_ns_per_access"]) for row in available]
    q3_values = [float(row["q3_ns_per_access"]) for row in available]

    median = sorted(values)[len(values) // 2]
    q1 = sorted(q1_values)[len(q1_values) // 2]
    q3 = sorted(q3_values)[len(q3_values) // 2]

    labels.append(label)
    medians.append(median)
    lower_errors.append(max(0, median - q1))
    upper_errors.append(max(0, q3 - median))


fig, ax = cs.plt.subplots(figsize=(10, 5.4))
x = range(len(labels))
ax.bar(x, medians, 0.6, yerr=[lower_errors, upper_errors], capsize=4, color=cs.BLUE,
       ecolor=cs.INK2)
for xi, m in zip(x, medians):
    ax.text(xi, m * 1.12, f"{m:.1f} ns", ha="center", fontsize=9, color=cs.INK)
ax.set_xticks(list(x), labels)
ax.set_yscale("log")
cs.plain_log(ax)
ax.set_ylabel("Representative median latency (ns per access, log scale)")
ax.set_xlabel("Working-set category (relative to nominal P-core capacities)")
cs.title(
    fig,
    "1b  Pointer-chasing latency by working-set category",
    "Same original unpinned data as 1a. Bar = median of the per-size medians in each category; "
    "whiskers = median of the per-size IQR bounds. Categories describe footprint size relative to "
    "nominal capacities; they do not isolate individual cache levels. The 8–12 MiB category is "
    "far above the 3–4 MiB one even though 12 MiB fits the nominal L3; the pinned P-core re-run "
    "(5a) shows the same rise between 4 and 8 MiB, so it is not explained by core type alone.",
)
cs.save(fig, PLOT.name)
print(f"Plot saved: {PLOT}")
print("\nCategory summaries:")
for label, median, low, high in zip(
    labels, medians, lower_errors, upper_errors
):
    print(
        f"{label.replace(chr(10), ' '):<28} "
        f"median={median:.3f} ns/access "
        f"(representative IQR: {median-low:.3f}–{median+high:.3f})"
    )
