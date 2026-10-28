#!/usr/bin/env bash
# Build every cache-memory benchmark into cache-memory/build/ with explicit flags.
# The original binaries in cache-memory/ (latency, access_patterns) are left untouched.
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p build

CXX="${CXX:-g++}"
FLAGS="-std=c++17 -O2 -march=native -Wall -Wextra"

"$CXX" $FLAGS -o build/latency          src/latency.cpp
"$CXX" $FLAGS -o build/access_patterns  src/access_patterns.cpp
"$CXX" $FLAGS -o build/read_write_mix   src/read_write_mix.cpp
"$CXX" $FLAGS -pthread -o build/mlp_chase src/mlp_chase.cpp
"$CXX" -std=c++17 -O3 -march=native -Wall -Wextra -o build/stream_bw src/stream_bw.cpp
"$CXX" $FLAGS -o build/miss_mix         src/miss_mix.cpp
"$CXX" $FLAGS -o build/tlb_locality     src/tlb_locality.cpp
"$CXX" $FLAGS -o build/counter_probe    src/counter_probe.cpp

"$CXX" --version | head -1
echo "flags: $FLAGS (stream_bw: -O3)"
