import csv
import os
import matplotlib.pyplot as plt

RAW_DIR = "results/raw"
PLOT_DIR = "results/plots"
os.makedirs(PLOT_DIR, exist_ok=True)

sizes = [1024, 8192, 65536, 1048576, 8388608]
results = []

for n in sizes:
    runtimes = {}

    for build in ["scalar", "simd"]:
        path = f"{RAW_DIR}/day2_{build}_multiply_{n}.csv"

        with open(path, newline="") as f:
            row = next(csv.DictReader(f))

        runtimes[build] = float(row["median_ms"])

    results.append((n, runtimes["scalar"] / runtimes["simd"]))

fig, ax = plt.subplots(figsize=(9, 6))

x = [n for n, speedup in results]
y = [speedup for n, speedup in results]

ax.plot(x, y, marker="o", linewidth=2, label="Elementwise multiplication")

for n, speedup in results:
    ax.annotate(
        f"{speedup:.2f}x",
        (n, speedup),
        xytext=(0, 9),
        textcoords="offset points",
        ha="center"
    )

ax.axhline(1.0, linestyle="--", label="No speedup (1x)")

ax.set_xscale("log", base=2)
ax.set_xticks(sizes)
ax.set_xticklabels([f"{n:,}" for n in sizes], rotation=20)
ax.set_xlabel("Input size N (FP32 elements)")
ax.set_ylabel("Speedup (scalar runtime / optimized runtime)")
ax.set_title("Locality Sweep: Elementwise Multiplication")
ax.grid(True, which="both", alpha=0.3)
ax.legend()

# Annotate the region of declining speedup, if present.
ax.annotate(
    "Speedup compresses\nas input size grows",
    xy=(1048576, results[3][1]),
    xytext=(65536, max(y) * 0.65),
    arrowprops={"arrowstyle": "->"},
    fontsize=9
)

fig.tight_layout()
output = f"{PLOT_DIR}/locality_multiply_speedup.png"
fig.savefig(output, dpi=300, bbox_inches="tight")
plt.close(fig)

print(f"Saved: {output}")
print("\nSpeedup results:")
for n, speedup in results:
    print(f"N={n:>9,}: {speedup:.2f}x")
