import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "results/raw/day5/memory_bandwidth.csv"
OUT = ROOT / "results/plots"
OUT.mkdir(parents=True, exist_ok=True)

# Each triad element performs approximately two FLOPs:
# one multiplication and one addition.
FLOPS_PER_ELEMENT = 2.0
BYTES_PER_ELEMENT = 3.0 * 4.0
ARITHMETIC_INTENSITY = FLOPS_PER_ELEMENT / BYTES_PER_ELEMENT

with DATA.open(newline="") as f:
    rows = list(csv.DictReader(f))

for row in rows:
    n = int(row["N"])
    seconds = float(row["median_ms"]) / 1000.0
    row["n"] = n
    row["seconds"] = seconds
    row["gflops"] = n * FLOPS_PER_ELEMENT / seconds / 1e9
    row["bandwidth_gib_s"] = float(row["logical_bandwidth_gib_s"])

# Use the largest observed logical bandwidth as an empirical reference.
# It is not a guaranteed DRAM bandwidth ceiling.
reference_bandwidth_gib_s = max(
    row["bandwidth_gib_s"] for row in rows
)
reference_bandwidth_bytes_s = reference_bandwidth_gib_s * (1024**3)
reference_roof_gflops = (
    reference_bandwidth_bytes_s * ARITHMETIC_INTENSITY / 1e9
)

# Plot 1: achieved GFLOP/s for each measured configuration.
fig, ax = plt.subplots(figsize=(9, 6))
labels = [
    f'{r["build"]}, N={r["n"]:,}' for r in rows
]
values = [r["gflops"] for r in rows]
ax.bar(labels, values)
ax.set_ylabel("Achieved performance (GFLOP/s)")
ax.set_title("Day 5: Triad Kernel Achieved Performance")
ax.tick_params(axis="x", rotation=25)
ax.grid(axis="y", alpha=0.3)
fig.tight_layout()
fig.savefig(OUT / "day5_achieved_gflops.png", dpi=160)
plt.close(fig)

# Plot 2: roofline with an explicitly estimated CPU compute ceiling.
# Assumption: up to 2 FP32 FLOPs/cycle per AVX2 lane using FMA.
# AVX2 has 8 FP32 lanes; FMA performs 2 FLOPs/lane/instruction.
# Use 12 cores and 5.2 GHz only as a rough upper-bound estimate.
# This is NOT a measured sustained all-core peak.
ESTIMATED_PEAK_GFLOPS = 12 * 5.2e9 * 8 * 2 / 1e9

intensities = np.logspace(-2, 2, 300)
bandwidth_roof = reference_bandwidth_bytes_s * intensities / 1e9
roofline = np.minimum(bandwidth_roof, ESTIMATED_PEAK_GFLOPS)

fig, ax = plt.subplots(figsize=(9, 6))
ax.loglog(
    intensities,
    roofline,
    label="Roofline envelope (estimated compute peak)",
)
ax.loglog(
    intensities,
    bandwidth_roof,
    linestyle="--",
    label="Empirical bandwidth reference",
)
ax.axhline(
    ESTIMATED_PEAK_GFLOPS,
    linestyle=":",
    label=f"Estimated CPU peak: {ESTIMATED_PEAK_GFLOPS:.0f} GFLOP/s",
)

for row in rows:
    ax.scatter(
        ARITHMETIC_INTENSITY,
        row["gflops"],
        s=55,
        label=f'{row["build"]}, N={row["n"]:,}',
    )

ax.set_xlabel("Arithmetic intensity (FLOP/byte)")
ax.set_ylabel("Performance (GFLOP/s)")
ax.set_title("Day 5: Roofline Analysis — Triad Kernel")
ax.grid(True, which="both", alpha=0.3)
ax.legend(fontsize=8)
ax.text(
    0.03,
    0.03,
    "Bandwidth reference: highest observed logical bandwidth, not DRAM peak.\\n"
    "Compute ceiling: illustrative upper-bound estimate, not measured peak.",
    transform=ax.transAxes,
    va="bottom",
    fontsize=8,
    wrap=True,
)
fig.tight_layout()
fig.savefig(OUT / "day5_roofline.png", dpi=160)
plt.close(fig)

# Save derived values for the report.
with (ROOT / "results/raw/day5/roofline_metrics.csv").open(
    "w", newline=""
) as f:
    writer = csv.writer(f)
    writer.writerow([
        "N", "build", "median_ms", "logical_bandwidth_gib_s",
        "arithmetic_intensity_flop_byte", "achieved_gflops",
        "empirical_reference_gflops"
    ])
    for row in rows:
        writer.writerow([
            row["n"],
            row["build"],
            row["median_ms"],
            row["bandwidth_gib_s"],
            f"{ARITHMETIC_INTENSITY:.6f}",
            f'{row["gflops"]:.6f}',
            f"{reference_roof_gflops:.6f}",
        ])

print(f"Arithmetic intensity: {ARITHMETIC_INTENSITY:.6f} FLOP/byte")
print(
    "Empirical reference bandwidth: "
    f"{reference_bandwidth_gib_s:.3f} GiB/s"
)
print(
    "Corresponding reference performance at this intensity: "
    f"{reference_roof_gflops:.3f} GFLOP/s"
)
print("\nDerived metrics:")
for row in rows:
    print(
        f'{row["build"]:6s} N={row["n"]:>9,}: '
        f'{row["gflops"]:.3f} GFLOP/s, '
        f'{row["bandwidth_gib_s"]:.3f} GiB/s'
    )

print("\nSaved:")
print(OUT / "day5_achieved_gflops.png")
print(OUT / "day5_roofline.png")
print(ROOT / "results/raw/day5/roofline_metrics.csv")
