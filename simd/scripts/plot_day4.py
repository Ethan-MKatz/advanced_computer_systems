import glob
import os

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd

DATA_DIR = "results/raw/day4_corrected"
PLOT_DIR = "results/plots"

os.makedirs(PLOT_DIR, exist_ok=True)

files = glob.glob(os.path.join(DATA_DIR, "*.csv"))
if not files:
    raise SystemExit(f"No CSV files found in {DATA_DIR}")

frames = []

for path in files:
    df = pd.read_csv(path)

    filename = os.path.basename(path)
    if filename.startswith("scalar_"):
        df["build"] = "Scalar"
    elif filename.startswith("simd_"):
        df["build"] = "SIMD"
    else:
        continue

    frames.append(df)

data = pd.concat(frames, ignore_index=True)

data["N"] = pd.to_numeric(data["N"])
data["median_ms"] = pd.to_numeric(data["median_ms"])
data["relative_error"] = pd.to_numeric(data["relative_error"])

kernels = ["multiply", "saxpy", "dot"]
precisions = ["float32", "float64"]
builds = ["Scalar", "SIMD"]

# 1. Runtime vs input size: one plot per kernel.
for kernel in kernels:
    fig, ax = plt.subplots()

    subset = data[data["kernel"] == kernel]

    for precision in precisions:
        for build in builds:
            series = subset[
                (subset["precision"] == precision)
                & (subset["build"] == build)
            ].sort_values("N")

            if not series.empty:
                ax.plot(
                    series["N"],
                    series["median_ms"],
                    marker="o",
                    label=f"{precision.upper()} {build}",
                )

    ax.set_xscale("log", base=2)
    ax.set_yscale("log")
    ax.set_xlabel("Input size N (elements)")
    ax.set_ylabel("Median runtime (ms)")
    ax.set_title(f"Day 4: {kernel.capitalize()} runtime")
    ax.grid(True, which="both", linestyle=":")
    ax.legend()
    fig.tight_layout()
    fig.savefig(
        os.path.join(PLOT_DIR, f"day4_{kernel}_runtime.png"),
        dpi=200,
    )
    plt.close(fig)

# 2. FP32/FP64 relative error vs input size.
for kernel in kernels:
    fig, ax = plt.subplots()
    subset = data[data["kernel"] == kernel]

    for precision in precisions:
        for build in builds:
            series = subset[
                (subset["precision"] == precision)
                & (subset["build"] == build)
            ].sort_values("N")

            if not series.empty:
                ax.plot(
                    series["N"],
                    series["relative_error"],
                    marker="o",
                    label=f"{precision.upper()} {build}",
                )

    ax.set_xscale("log", base=2)
    ax.set_yscale("log")
    ax.set_xlabel("Input size N (elements)")
    ax.set_ylabel("Relative error")
    ax.set_title(f"Day 4: {kernel.capitalize()} numerical error")
    ax.grid(True, which="both", linestyle=":")
    ax.legend()
    fig.tight_layout()
    fig.savefig(
        os.path.join(PLOT_DIR, f"day4_{kernel}_error.png"),
        dpi=200,
    )
    plt.close(fig)

# 3. FP32 vs FP64 runtime ratio for each build and kernel.
# Ratio > 1 means FP64 takes longer than FP32.
for kernel in kernels:
    fig, ax = plt.subplots()
    subset = data[data["kernel"] == kernel]

    for build in builds:
        ratios = []

        for n in sorted(subset["N"].unique()):
            pair = subset[
                (subset["N"] == n)
                & (subset["build"] == build)
            ]

            fp32 = pair[pair["precision"] == "float32"]
            fp64 = pair[pair["precision"] == "float64"]

            if not fp32.empty and not fp64.empty:
                ratio = (
                    fp64.iloc[0]["median_ms"]
                    / fp32.iloc[0]["median_ms"]
                )
                ratios.append((n, ratio))

        if ratios:
            xs, ys = zip(*ratios)
            ax.plot(xs, ys, marker="o", label=build)

    ax.axhline(1.0, linestyle="--")
    ax.set_xscale("log", base=2)
    ax.set_xlabel("Input size N (elements)")
    ax.set_ylabel("FP64 runtime / FP32 runtime")
    ax.set_title(f"Day 4: Precision performance cost — {kernel}")
    ax.grid(True, which="both", linestyle=":")
    ax.legend()
    fig.tight_layout()
    fig.savefig(
        os.path.join(PLOT_DIR, f"day4_{kernel}_precision_cost.png"),
        dpi=200,
    )
    plt.close(fig)

print("Day 4 plots saved to", PLOT_DIR)

