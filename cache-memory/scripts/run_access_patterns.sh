#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/../.."

BIN="./cache-memory/access_patterns"
OUT="cache-memory/results/raw/2_access_patterns.csv"

mkdir -p cache-memory/results/raw
echo "pattern,stride_bytes,working_set_MiB,passes,elapsed_seconds,effective_GB_per_second,checksum,trial" > "$OUT"

working_set=64
passes=10
repetitions=5

for trial in $(seq 1 "$repetitions"); do
    echo "Trial $trial/$repetitions"

    # Vary the seed between trials to change randomized address order.
    seed=$((12345 + trial))

    result=$("$BIN" "$working_set" "$passes" "$seed")
    echo "$result" | tail -n +2 | while IFS=, read -r pattern stride mib n_passes elapsed bandwidth checksum; do
        echo "$pattern,$stride,$mib,$n_passes,$elapsed,$bandwidth,$checksum,$trial" >> "$OUT"
        echo "  $pattern | stride=${stride}B | ${elapsed}s | ${bandwidth} effective GB/s"
    done
done

echo
echo "Raw results saved to $OUT"
echo "Data rows: $(($(wc -l < "$OUT") - 1))"

