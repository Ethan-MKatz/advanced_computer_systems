# Shared helpers for the run_*.sh scripts (sourced, not executed).
# Every raw row gets: trial, pinning (CPU list passed to taskset or "unpinned"),
# ac_online (1/0 from /sys/class/power_supply/AC/online), and an ISO timestamp.
BUILD="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/build"
RAW="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/results/raw"
mkdir -p "$RAW"

ac_online() { cat /sys/class/power_supply/AC/online 2>/dev/null || echo NA; }
stamp() { date -Iseconds; }

# Refuse to start a new run below 20% battery when unplugged.
check_power() {
    local ac cap
    ac=$(ac_online)
    cap=$(cat /sys/class/power_supply/BAT0/capacity 2>/dev/null || echo 100)
    if [[ "$ac" == "0" && "$cap" -lt 20 ]]; then
        echo "battery at ${cap}% and not on AC; stopping" >&2
        exit 2
    fi
}

# Refuse to overwrite an existing raw file (raw data is never overwritten).
new_raw() {
    local f="$RAW/$1"
    if [[ -e "$f" ]]; then
        echo "refusing to overwrite existing raw file $f" >&2
        exit 3
    fi
    echo "$2" > "$f"
    echo "$f"
}
