import csv
import glob
import os
import re
import matplotlib.pyplot as plt

RAW_DIR = "results/raw"
PLOT_DIR = "results/plots"
os.makedirs(PLOT_DIR, exist_ok=True)

# Load Day 2 CSV results
rows = []

for path in glob.glob(f"{RAW_DIR}/day2_*.csv"):
    match = re.search(
        r"day2_(scalar|simd)_(multiply|saxpy|dot)_(\d+)\.csv$",
        path
    )
    if not match:
        continue

    build, kernel, n = match.groups()

    with open(path, newline="") as f:
        row = next(csv.DictReader(f))

    rows.append({
        "build": build,
        "kernel": kernel,
        "n": int(n),
        "ms": float(row["median_ms"]),
        "bandwidth": float(row["logical_GiB_per_s"]),
    })

if not rows:
    raise SystemExit("ERROR: No Day 2 CSV files found in results/raw/.")

kernels = ["multiply", "saxpy", "dot"]
builds = ["scalar", "simd"]
sizes = sorted({r["n"] for r in rows})

# Check that every kernel/build/size combination exists
expected = len(kernels) * len(builds) * len(sizes)
if len(rows) != expected:
    print(f"WARNING: Expected {expected} result rows, found {len(rows)}.")

def label_points(ax, xs, ys, fmt, offset=5):
    for x, y in zip(xs, ys):
        ax.annotate(
            fmt.format(y),
            (x, y),
            textcoords="offset points",
            xytext=(0, offset),
            ha="center",
            fontsize=7
        )

# --------------------------------------------------
# PLOT 1: Runtime vs. input size, one panel per kernel
# --------------------------------------------------
fig, axes = plt.subplots(1, 3, figsize=(16, 5))

for ax, kernel in zip(axes, kernels):
    for build in builds:
        data = sorted(
            [r for r in rows
             if r["kernel"] == kernel and r["build"] == build],
            key=lambda r: r["n"]
        )

        xs = [r["n"] for r in data]
        ys = [r["ms"] for r in data]

        ax.plot(xs, ys, marker="o", label=build)
        label_points(ax, xs, ys, "{:.3g}")

    ax.set_xscale("log", base=2)
    ax.set_yscale("log")
    ax.set_title(f"Kernel: {kernel}")
    ax.set_xlabel("Input size N (elements)")
    ax.set_ylabel("Median runtime (ms)")
    ax.grid(True, which="both", alpha=0.3)
    ax.legend(title="Build")

fig.suptitle("Day 2: Runtime vs. Input Size")
fig.tight_layout()
fig.savefig(
    f"{PLOT_DIR}/day2_runtime_vs_size.png",
    dpi=300, bbox_inches="tight"
)
plt.close(fig)

# --------------------------------------------------
# PLOT 2: Speedup vs. input size
# --------------------------------------------------
fig, ax = plt.subplots(figsize=(9, 6))

for kernel in kernels:
    speedups = []

    for n in sizes:
        scalar = next(
            (r for r in rows
             if r["kernel"] == kernel
             and r["build"] == "scalar"
             and r["n"] == n),
            None
        )
        simd = next(
            (r for r in rows
             if r["kernel"] == kernel
             and r["build"] == "simd"
             and r["n"] == n),
            None
        )

        if scalar and simd:
            speedups.append((n, scalar["ms"] / simd["ms"]))

    if speedups:
        xs = [p[0] for p in speedups]
        ys = [p[1] for p in speedups]
        ax.plot(xs, ys, marker="o", label=f"Kernel: {kernel}")
        label_points(ax, xs, ys, "{:.2f}x", offset=7)

ax.axhline(1.0, linestyle="--", label="No speedup (1x)")
ax.set_xscale("log", base=2)
ax.set_xlabel("Input size N (elements)")
ax.set_ylabel("Speedup (scalar runtime / optimized runtime)")
ax.set_title("Day 2: Speedup by Kernel")
ax.grid(True, which="both", alpha=0.3)
ax.legend()
fig.tight_layout()
fig.savefig(
    f"{PLOT_DIR}/day2_speedup_vs_size.png",
    dpi=300, bbox_inches="tight"
)
plt.close(fig)

# --------------------------------------------------
# PLOT 3: Effective logical bandwidth, one panel per kernel
# --------------------------------------------------
fig, axes = plt.subplots(1, 3, figsize=(16, 5))

for ax, kernel in zip(axes, kernels):
    for build in builds:
        data = sorted(
            [r for r in rows
             if r["kernel"] == kernel and r["build"] == build],
            key=lambda r: r["n"]
        )

        xs = [r["n"] for r in data]
        ys = [r["bandwidth"] for r in data]

        ax.plot(xs, ys, marker="o", label=build)
        label_points(ax, xs, ys, "{:.2f}")

    ax.set_xscale("log", base=2)
    ax.set_title(f"Kernel: {kernel}")
    ax.set_xlabel("Input size N (elements)")
    ax.set_ylabel("Logical throughput (GiB/s)")
    ax.grid(True, which="both", alpha=0.3)
    ax.legend(title="Build")

fig.suptitle("Day 2: Effective Logical Bandwidth")
fig.tight_layout()
fig.savefig(
    f"{PLOT_DIR}/day2_bandwidth_vs_size.png",
    dpi=300, bbox_inches="tight"
)
plt.close(fig)

print("\nDay 2 plots generated:")
print(f"  {PLOT_DIR}/day2_runtime_vs_size.png")
print(f"  {PLOT_DIR}/day2_speedup_vs_size.png")
print(f"  {PLOT_DIR}/day2_bandwidth_vs_size.png")
print(f"\nLoaded {len(rows)} benchmark result rows.")
print("Kernel labels: multiply, saxpy, dot")
print("Build labels: scalar, simd")

