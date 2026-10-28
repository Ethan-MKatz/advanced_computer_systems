#!/usr/bin/env bash
# Experiment 5: (a) pointer-chase latency with the unchanged src/latency.cpp,
# now pinned to CPU 0 and with a finer size grid; (b) streaming read/write
# bandwidth with src/stream_bw.cpp. 5 trials each.
set -euo pipefail
source "$(dirname "$0")/lib.sh"
CPU=0
OUT=$(new_raw 5_working_set_sweep.csv "working_set_KiB,accesses,ns_per_access,final_index,trial,pinning,ac_online,timestamp")
SIZES="4 8 16 24 32 40 48 56 64 80 96 128 192 256 384 512 768 1024 1536 2048 2560 3072 4096 6144 8192 10240 12288 14336 16384 24576 32768 65536 131072 262144"
for trial in 1 2 3 4 5; do
    for kib in $SIZES; do
        check_power
        m=$([[ $kib -ge 16384 ]] && echo 5 || echo 10)
        row=$(taskset -c $CPU "$BUILD/latency" $kib $m)
        echo "$row,$trial,$CPU,$(ac_online),$(stamp)" >> "$OUT"; echo "t$trial latency $row"
    done
done
OUT=$(new_raw 5_working_set_bandwidth.csv "mode,ws_KiB,passes,seconds,GB_per_s,checksum,cpu,trial,pinning,ac_online,timestamp")
BW_SIZES="16 32 48 64 96 128 256 512 1024 1536 2048 3072 4096 6144 8192 12288 16384 32768 65536 262144"
for trial in 1 2 3 4 5; do
    for mode in read write; do
        for kib in $BW_SIZES; do
            check_power
            row=$(taskset -c $CPU "$BUILD/stream_bw" sweep $mode $kib 2048 0)
            echo "$row,$trial,$CPU,$(ac_online),$(stamp)" >> "$OUT"; echo "t$trial bw $row"
        done
    done
done
