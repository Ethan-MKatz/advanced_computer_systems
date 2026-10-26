import csv
import matplotlib.pyplot as plt
from pathlib import Path

# Define project paths
input_file = Path("results/processed/elementwise_multiply.csv")
output_dir = Path("results/plots")
output_dir.mkdir(parents=True, exist_ok=True)

# Read benchmark results
with open(input_file, "r", newline="") as file:
    reader = csv.DictReader(file)
    rows = list(reader)

# Sort results by input size
rows.sort(key=lambda row: int(row["N"]))

# Extract data
n = [int(row["N"]) for row in rows]
scalar_ms = [float(row["scalar_ms"]) for row in rows]
simd_ms = [float(row["simd_ms"]) for row in rows]
speedup = [float(row["speedup"]) for row in rows]

# Plot 1: Runtime versus input size
plt.figure(figsize=(9, 6))
plt.plot(n, scalar_ms, marker="o", label="Scalar")
plt.plot(n, simd_ms, marker="s", label="SIMD")
plt.xscale("log")
plt.yscale("log")
plt.xlabel("Input Size (number of float elements)")
plt.ylabel("Median Runtime (ms)")
plt.title("Scalar vs. SIMD Runtime for Elementwise Multiplication")
plt.grid(True, which="both", linestyle="--", alpha=0.5)
plt.legend()
plt.tight_layout()

runtime_path = output_dir / "runtime_vs_input_size.png"
plt.savefig(runtime_path, dpi=300)
plt.close()

# Plot 2: Speedup versus input size
plt.figure(figsize=(9, 6))
plt.plot(n, speedup, marker="o", label="Measured speedup")
plt.axhline(y=1, linestyle="--", label="Equal performance")
plt.xscale("log")
plt.xlabel("Input Size (number of float elements)")
plt.ylabel("Speedup (Scalar Runtime / SIMD Runtime)")
plt.title("SIMD Speedup versus Input Size")
plt.grid(True, which="both", linestyle="--", alpha=0.5)
plt.legend()
plt.tight_layout()

speedup_path = output_dir / "speedup_vs_input_size.png"
plt.savefig(speedup_path, dpi=300)
plt.close()

print(f"Runtime plot saved to: {runtime_path}")
print(f"Speedup plot saved to: {speedup_path}")
print(f"Number of data points: {len(rows)}")
