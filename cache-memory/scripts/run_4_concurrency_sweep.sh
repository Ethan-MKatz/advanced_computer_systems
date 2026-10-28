#!/usr/bin/env bash
# Experiment 4: K independent pointer chains per thread over 256 MiB (THP),
# 1 thread on CPU 0 and 2 threads on CPUs 0,2 (two different P-cores). 5 trials.
set -euo pipefail
source "$(dirname "$0")/lib.sh"
OUT=$(new_raw 4_concurrency_sweep.csv "ws_MiB,thp,threads,chains_per_thread,steps,seconds,loads_per_s,ns_per_step,anon_huge_KiB,cpus,checksum,trial,ac_online,timestamp")
for trial in 1 2 3 4 5; do
    for k in 1 2 3 4 6 8 10 12 14 16 20 24 32; do
        check_power
        row=$("$BUILD/mlp_chase" 256 $k 4 1 0 $((200 + trial)))
        echo "$row,$trial,$(ac_online),$(stamp)" >> "$OUT"; echo "t$trial T=1 K=$k: $row"
    done
    for k in 1 2 3 4 6 8 10 12 16; do
        check_power
        row=$("$BUILD/mlp_chase" 256 $k 4 1 0,2 $((200 + trial)))
        echo "$row,$trial,$(ac_online),$(stamp)" >> "$OUT"; echo "t$trial T=2 K=$k: $row"
    done
done
