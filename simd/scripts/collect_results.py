import csv
from pathlib import Path

raw_dir = Path("results/raw")
output = Path("results/processed/elementwise_multiply.csv")
output.parent.mkdir(parents=True, exist_ok=True)

rows = []

for scalar_file in sorted(raw_dir.glob("scalar_*.csv")):
    suffix = scalar_file.name.removeprefix("scalar_")
    simd_file = raw_dir / f"simd_{suffix}"

    if not simd_file.exists():
        continue

    with scalar_file.open(newline="") as f:
        scalar = next(csv.DictReader(f))

    with simd_file.open(newline="") as f:
        simd = next(csv.DictReader(f))

    scalar_ms = float(scalar["median_ms"])
    simd_ms = float(simd["median_ms"])

    rows.append({
        "N": int(scalar["N"]),
        "scalar_ms": scalar_ms,
        "simd_ms": simd_ms,
        "speedup": scalar_ms / simd_ms,
        "scalar_GiB_per_s": float(scalar["logical_GiB_per_s"]),
        "simd_GiB_per_s": float(simd["logical_GiB_per_s"]),
        "scalar_checksum": scalar["checksum"],
        "simd_checksum": simd["checksum"],
    })

rows.sort(key=lambda row: row["N"])

if not rows:
    raise SystemExit("No matching scalar/SIMD CSV files found.")

with output.open("w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)

print(f"Saved {len(rows)} comparisons to {output}")
print()
print(
    f"{'N':>10} {'Scalar ms':>12} {'SIMD ms':>12} "
    f"{'Speedup':>10}"
)

for row in rows:
    print(
        f"{row['N']:>10} "
        f"{row['scalar_ms']:>12.6f} "
        f"{row['simd_ms']:>12.6f} "
        f"{row['speedup']:>9.2f}x"
    )
