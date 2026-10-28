#!/usr/bin/env bash
# Experiment 4 extension: push total concurrency past L = 32 to look for a knee.
# 2 threads (CPUs 0,2) with K = 24, 32 and 4 threads (CPUs 0-3: two P-cores,
# both hyperthreads of each) with K = 4..32. Same workload as run_4_concurrency_sweep.sh.
set -euo pipefail
source "$(dirname "$0")/lib.sh"
OUT=$(new_raw 4_concurrency_sweep_extended.csv "ws_MiB,thp,threads,chains_per_thread,steps,seconds,loads_per_s,ns_per_step,anon_huge_KiB,cpus,checksum,trial,ac_online,timestamp")
for trial in 1 2 3 4 5; do
    for k in 24 32; do
        check_power
        row=$("$BUILD/mlp_chase" 256 $k 4 1 0,2 $((200 + trial)))
        echo "$row,$trial,$(ac_online),$(stamp)" >> "$OUT"; echo "t$trial T=2 K=$k: $row"
    done
    for k in 4 8 12 16 24 32; do
        check_power
        row=$("$BUILD/mlp_chase" 256 $k 4 1 0,1,2,3 $((200 + trial)))
        echo "$row,$trial,$(ac_online),$(stamp)" >> "$OUT"; echo "t$trial T=4 K=$k: $row"
    done
done
