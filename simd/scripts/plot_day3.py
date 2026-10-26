import csv
import glob
import os
import re
import matplotlib.pyplot as plt

RAW_DIR = "results/raw/day3"
PLOT_DIR = "results/plots"

os.makedirs(PLOT_DIR, exist_ok=True)


def read_results(pattern):
    rows = []

    for filename in glob.glob(pattern):
        with open(filename, newline="") as f:
            reader = csv.DictReader(f)

            for row in reader:
                row["N"] = int(row["N"])
                row["runtime_ms"] = float(
                    row.get("runtime_ms", row.get("median_ms", 0))
                )

                if "stride" in row:
                    row["parameter"] = int(row["stride"])
                else:
                    row["parameter"] = int(row["offset_floats"])

                match = re.search(r"/(scalar|simd)_", filename)
                row["build"] = match.group(1) if match else "unknown"
                rows.append(row)

    return rows


def plot_experiment(rows, parameter_name, filename_prefix, title):
    if not rows:
        print(f"No data found for {title}")
        return

    sizes = sorted(set(row["N"] for row in rows))
    parameters = sorted(set(row["parameter"] for row in rows))

    # Plot 1: runtime by parameter, with separate panels for input size.
    fig, axes = plt.subplots(
        1, len(sizes), figsize=(6 * len(sizes), 5), squeeze=False
    )

    for index, n in enumerate(sizes):
        ax = axes[0][index]

        for build in ("scalar", "simd"):
            for row_parameter in parameters:
                selected = [
                    row for row in rows
                    if row["N"] == n
                    and row["parameter"] == row_parameter
                    and row["build"] == build
                ]

                if selected:
                    ax.scatter(
                        [row_parameter for row in selected],
                        [row["runtime_ms"] for row in selected],
                        label=f"{build}, {parameter_name}={row_parameter}",
                    )

        ax.set_title(f"N = {n:,}")
        ax.set_xlabel(parameter_name)
        ax.set_ylabel("Median runtime (ms)")
        ax.grid(True, alpha=0.3)

    handles, labels = axes[0][0].get_legend_handles_labels()
    if handles:
        fig.legend(handles, labels, loc="upper center",
                   bbox_to_anchor=(0.5, 1.02), ncol=3, fontsize=8)

    fig.suptitle(f"{title}: Runtime", y=1.10)
    fig.tight_layout()
    fig.savefig(
        f"{PLOT_DIR}/{filename_prefix}_runtime.png",
        dpi=160, bbox_inches="tight"
    )
    plt.close(fig)

    # Plot 2: SIMD speedup over scalar.
    fig, axes = plt.subplots(
        1, len(sizes), figsize=(6 * len(sizes), 5), squeeze=False
    )

    for index, n in enumerate(sizes):
        ax = axes[0][index]

        speedups = []

        for row_parameter in parameters:
            scalar_rows = [
                row for row in rows
                if row["N"] == n
                and row["parameter"] == row_parameter
                and row["build"] == "scalar"
            ]
            simd_rows = [
                row for row in rows
                if row["N"] == n
                and row["parameter"] == row_parameter
                and row["build"] == "simd"
            ]

            if scalar_rows and simd_rows:
                scalar_time = scalar_rows[0]["runtime_ms"]
                simd_time = simd_rows[0]["runtime_ms"]

                if simd_time > 0:
                    speedups.append(
                        (row_parameter, scalar_time / simd_time)
                    )

        if speedups:
            x_values, y_values = zip(*speedups)
            ax.plot(x_values, y_values, marker="o", label="SIMD speedup")
            ax.axhline(1.0, linestyle="--", label="Equal performance")

        ax.set_title(f"N = {n:,}")
        ax.set_xlabel(parameter_name)
        ax.set_ylabel("Speedup (scalar / SIMD)")
        ax.grid(True, alpha=0.3)
        ax.legend()

    fig.suptitle(f"{title}: SIMD Speedup", y=1.05)
    fig.tight_layout()
    fig.savefig(
        f"{PLOT_DIR}/{filename_prefix}_speedup.png",
        dpi=160, bbox_inches="tight"
    )
    plt.close(fig)

    print(f"Generated {filename_prefix} runtime and speedup plots.")


stride_rows = read_results(f"{RAW_DIR}/scalar_N*_S*.csv")
stride_rows += read_results(f"{RAW_DIR}/simd_N*_S*.csv")

alignment_rows = read_results(
    f"{RAW_DIR}/alignment/*.csv"
)

plot_experiment(
    stride_rows,
    "Stride (elements)",
    "day3_stride",
    "Stride experiment",
)

plot_experiment(
    alignment_rows,
    "Starting offset (floats)",
    "day3_alignment",
    "Alignment experiment",
)

print("Day 3 plots saved in", PLOT_DIR)
