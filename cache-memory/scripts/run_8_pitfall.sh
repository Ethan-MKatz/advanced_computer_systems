#!/usr/bin/env bash
# Experiment 8: measurement pitfalls.
# (a) cold first pass vs warm repeated passes: 20 timed read passes over a
#     1 MiB (cache-resident) and a 256 MiB buffer after evicting caches.
# (b) pinned vs unpinned: dense pointer chase over 1 MiB and 8 MiB pinned to
#     a P-core (CPU 0), pinned to a low-power E-core without L3 (CPU 12), and
#     unpinned (inherits this shell's allowed CPU set). 12 trials each.
set -euo pipefail
source "$(dirname "$0")/lib.sh"
OUT=$(new_raw 8_measurement_pitfall_passes.csv "ws_KiB,pass,seconds,GB_per_s,trial,pinning,ac_online,timestamp")
for trial in 1 2 3 4 5; do
    for kib in 1024 262144; do
        check_power
        taskset -c 0 "$BUILD/stream_bw" perpass read $kib 20 0 2>/dev/null | while IFS= read -r line; do
            echo "$kib,$line,$trial,0,$(ac_online),$(stamp)" >> "$OUT"
        done
        echo "t$trial perpass ${kib}KiB done"
    done
done
OUT=$(new_raw 8_measurement_pitfall_pinning.csv "pages,lines_per_page,lines,span_KiB,thp,accesses,seconds,ns_per_access,setup_minor_faults,anon_huge_KiB,checksum,cpu_start,cpu_end,trial,pinning,allowed_cpus,ac_online,timestamp")
ALLOWED=$(taskset -cp $$ | awk -F': ' '{print $2}')
for trial in $(seq 1 12); do
    for pages in 256 2048; do
        for pin in 0 12 unpinned; do
            check_power
            if [[ $pin == unpinned ]]; then
                row=$("$BUILD/tlb_locality" $pages 64 0 5 $((500 + trial)))
            else
                row=$(taskset -c $pin "$BUILD/tlb_locality" $pages 64 0 5 $((500 + trial)))
            fi
            echo "$row,$trial,$pin,\"$ALLOWED\",$(ac_online),$(stamp)" >> "$OUT"; echo "t$trial pin=$pin $row"
        done
    done
done
