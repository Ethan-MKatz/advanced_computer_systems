import csv
import os
import matplotlib.pyplot as plt

input_file = "results/raw/day3/tail/simd_tail.csv"
output_file = "results/plots/day3_tail_runtime.png"

os.makedirs("results/plots", exist_ok=True)

with open(input_file, newline="") as f:
    rows = list(csv.DictReader(f))

if not rows:
    raise ValueError(f"No benchmark results found in {input_file}")

tails = [int(row["tail_remainder"]) for row in rows]
runtimes = [float(row["runtime_ms"]) for row in rows]

plt.figure(figsize=(8, 5))
plt.plot(tails, runtimes, marker="o")
plt.xlabel("Additional Elements Beyond Base Array Length")
plt.ylabel("Median Runtime (ms)")
plt.title("Elementwise Multiplication: Runtime vs. Tail Length")
plt.xticks(tails)
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(output_file, dpi=160)
plt.close()

print(f"Saved plot to {output_file}")
