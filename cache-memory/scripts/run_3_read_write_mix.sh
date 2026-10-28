#!/usr/bin/env bash
# Experiment 3: read/write mix. 4 mixes x 2 modes x 2 footprints x 5 trials, CPU 0.
set -euo pipefail
source "$(dirname "$0")/lib.sh"
OUT=$(new_raw 3_read_write_mix.csv "ws_KiB,write_pct,mode,ops,seconds,ns_per_op,mops_per_s,payload_GB_per_s,checksum,cpu,trial,pinning,ac_online,timestamp")
CPU=0
for trial in 1 2 3 4 5; do
    for ws in 1024 262144; do
        for mode in independent dependent; do
            # Fixed op count per (footprint, mode), identical across mixes.
            if [[ $ws == 1024 ]]; then ops=$([[ $mode == independent ]] && echo 50 || echo 20)
            else ops=$([[ $mode == independent ]] && echo 20 || echo 5); fi
            for wpct in 0 30 50 100; do
                check_power
                row=$(taskset -c $CPU "$BUILD/read_write_mix" $ws $ops $wpct $mode $((100 + trial)))
                echo "$row,$trial,$CPU,$(ac_online),$(stamp)" >> "$OUT"
                echo "t$trial ws=${ws}KiB $mode write=${wpct}%: $row"
            done
        done
    done
done
