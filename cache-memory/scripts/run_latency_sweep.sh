#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/../.."

BIN="./cache-memory/latency"
OUT="cache-memory/results/raw/1a_zero_queue_latency.csv"

if [[ ! -x "$BIN" ]]; then
    echo "Benchmark executable not found: $BIN" >&2
    echo "Compile cache-memory/src/latency.cpp first." >&2
    exit 1
fi

mkdir -p "$(dirname "$OUT")"

echo "working_set_KiB,accesses,ns_per_access,final_index,trial" > "$OUT"

sizes=(16 32 48 64 512 1024 2048 3072 4096 8192 12288 16384 32768 65536)
repetitions=5
accesses_millions=10

for size in "${sizes[@]}"; do
    for ((trial = 1; trial <= repetitions; trial++)); do
        result=$("$BIN" "$size" "$accesses_millions")
        echo "$result,$trial" >> "$OUT"
        echo "Size=${size} KiB, trial=${trial}: ${result}"
    done
done

echo
echo "Saved raw measurements to $OUT"
