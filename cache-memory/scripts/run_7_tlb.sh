#!/usr/bin/env bash
# Experiment 7 (timing-only; no TLB counters available), CPU 0, 5 trials.
# (a) 8192 lines (512 KiB of data) spread over 128..8192 pages, 4 KiB vs THP.
# (b) dense random chase over 2..256 MiB, 4 KiB pages vs THP.
set -euo pipefail
source "$(dirname "$0")/lib.sh"
CPU=0
HDR="pages,lines_per_page,lines,span_KiB,thp,accesses,seconds,ns_per_access,setup_minor_faults,anon_huge_KiB,checksum,cpu_start,cpu_end,experiment,trial,pinning,ac_online,timestamp"
OUT=$(new_raw 7_tlb_impact.csv "$HDR")
for trial in 1 2 3 4 5; do
    for pages in 128 256 512 1024 2048 4096 8192; do
        for thp in 0 1; do
            check_power
            row=$(taskset -c $CPU "$BUILD/tlb_locality" $pages $((8192 / pages)) $thp 20 $((400 + trial)))
            echo "$row,7a_page_locality,$trial,$CPU,$(ac_online),$(stamp)" >> "$OUT"; echo "t$trial 7a $row"
        done
    done
    for pages in 512 4096 16384 65536; do
        for thp in 0 1; do
            check_power
            row=$(taskset -c $CPU "$BUILD/tlb_locality" $pages 64 $thp 10 $((400 + trial)))
            echo "$row,7b_page_size,$trial,$CPU,$(ac_online),$(stamp)" >> "$OUT"; echo "t$trial 7b $row"
        done
    done
done
