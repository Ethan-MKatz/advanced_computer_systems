import csv
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

csv_file = Path("results/processed/elementwise_multiply.csv")
out_file = Path("results/plots/roofline.png")
out_file.parent.mkdir(parents=True, exist_ok=True)

with csv_file.open(newline="") as f:
    rows = list(csv.DictReader(f))

if not rows:
    raise SystemExit(f"No data found in {csv_file}")

sizes = [int(r["N"]) for r in rows]
scalar = [float(r["scalar_GiB_per_s"]) for r in rows]
simd = [float(r["simd_GiB_per_s"]) for r in rows]

fig, ax = plt.subplots(figsize=(9, 6))

ax.plot(sizes, scalar, marker="o", linewidth=2, label="Scalar")
ax.plot(sizes, simd, marker="s", linewidth=2, label="SIMD")

ax.set_xscale("log")
ax.set_xlabel("Problem size (elements)")
ax.set_ylabel("Measured bandwidth (GiB/s)")
ax.set_title("Scalar vs SIMD Elementwise Multiply")
ax.grid(True, which="both", linestyle="--", alpha=0.4)
ax.legend()

fig.tight_layout()
fig.savefig(out_file, dpi=200)
plt.close(fig)

print(f"Plot saved to: {out_file}")
print(f"Data points plotted: {len(sizes)}")
for n, s, v in zip(sizes, scalar, simd):
    print(f"N={n:>8,}: scalar={s:.2f} GiB/s, SIMD={v:.2f} GiB/s")
