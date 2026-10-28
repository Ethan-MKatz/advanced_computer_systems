#!/usr/bin/env bash
# Build and run experiments 3-8 (experiments 1-2 were collected earlier and are not re-run).
set -euo pipefail
cd "$(dirname "$0")"
./build.sh
./collect_env.sh
./run_3_read_write_mix.sh
./run_4_concurrency_sweep.sh
./run_4_concurrency_extended.sh
./run_5_working_set.sh
./run_6_far_access.sh
./run_7_tlb.sh
./run_8_pitfall.sh
./collect_env.sh
