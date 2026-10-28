#!/usr/bin/env bash
# Record the hardware/software environment (no root needed) to results/raw/.
set -uo pipefail
source "$(dirname "$0")/lib.sh"
OUT="$RAW/environment_$(date +%Y%m%d_%H%M%S).txt"
{
    echo "# collected $(stamp)"
    echo "## OS / kernel"; lsb_release -d; uname -a
    echo "## compiler"; g++ --version | head -1
    echo "## CPU"; lscpu
    echo "## per-CPU caches (sysfs)"
    for c in /sys/devices/system/cpu/cpu[0-9]*; do
        n=${c##*cpu}; line="cpu$n:"
        for i in $c/cache/index*; do
            line="$line L$(cat $i/level)$(cut -c1 $i/type)=$(cat $i/size)[$(cat $i/shared_cpu_list)]"
        done
        echo "$line"
    done
    echo "## core types"; echo "cpu_core (P): $(cat /sys/devices/cpu_core/cpus)"; echo "cpu_atom (E/LP-E): $(cat /sys/devices/cpu_atom/cpus)"
    echo "## affinity of this shell"; taskset -cp $$
    echo "## frequency scaling"
    echo "driver=$(cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_driver) governor=$(cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor) epp=$(cat /sys/devices/system/cpu/cpu0/cpufreq/energy_performance_preference) no_turbo=$(cat /sys/devices/system/cpu/intel_pstate/no_turbo 2>/dev/null) platform_profile=$(cat /sys/firmware/acpi/platform_profile 2>/dev/null)"
    for c in 0 2 12; do echo "cpu$c max=$(cat /sys/devices/system/cpu/cpu$c/cpufreq/cpuinfo_max_freq) kHz"; done
    echo "## power"; echo "AC online=$(ac_online) battery=$(cat /sys/class/power_supply/BAT0/capacity)% $(cat /sys/class/power_supply/BAT0/status)"
    echo "## CPU0 frequency under a 1 s single-thread load (scaling_cur_freq, kHz)"
    (taskset -c 0 "$BUILD/miss_mix" 16 0 400 0 1 >/dev/null &)
    for i in 1 2 3 4; do sleep 0.25; cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq; done
    wait
    echo "## memory"; free -h; grep -i -E "huge" /proc/meminfo
    echo "## transparent huge pages"; echo "enabled: $(cat /sys/kernel/mm/transparent_hugepage/enabled)"; echo "defrag: $(cat /sys/kernel/mm/transparent_hugepage/defrag)"
    echo "## perf"; echo "perf_event_paranoid=$(cat /proc/sys/kernel/perf_event_paranoid)"; perf --version 2>&1 | head -1
    echo "## perf_event_open probe (build/counter_probe)"; "$BUILD/counter_probe"
} > "$OUT" 2>&1
"$BUILD/counter_probe" > "$RAW/counter_probe.csv"
echo "$OUT"
