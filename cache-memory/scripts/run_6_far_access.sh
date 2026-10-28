#!/usr/bin/env bash
# Experiment 6 (timing-only; no cache-miss counters available): designed
# far-access fraction in a dependent chain, three far-buffer footprints, CPU 0.
set -euo pipefail
source "$(dirname "$0")/lib.sh"
CPU=0
OUT=$(new_raw 6_far_access_fraction.csv "far_KiB,far_permille,thp,accesses,seconds,ns_per_access,anon_huge_KiB,checksum,cpu,trial,pinning,ac_online,timestamp")
for trial in 1 2 3 4 5; do
    for far in 1024 8192 262144; do
        for pm in 0 10 20 50 100 200 300 500 750 1000; do
            check_power
            row=$(taskset -c $CPU "$BUILD/miss_mix" $far $pm 5 1 $((300 + trial)))
            echo "$row,$trial,$CPU,$(ac_online),$(stamp)" >> "$OUT"; echo "t$trial $row"
        done
    done
done
