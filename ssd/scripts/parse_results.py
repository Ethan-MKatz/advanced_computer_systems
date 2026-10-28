#!/usr/bin/env python3
"""Parse raw fio JSON + run metadata into tidy CSVs under results/processed/.

Outputs
  all_runs.csv           one row per (run, direction); failed/unparseable runs are kept
                         with valid=False and empty metrics (never silently dropped)
  summary_by_config.csv  median / min / max / std across trials per (config, direction)
  exp5_latency_bins.csv  full fio latency histogram (json+ bins) for experiment 5
  exp6b_timeseries.csv   1 s averaged IOPS / bandwidth / latency logs for experiment 6b
  exp6b_temperature.csv  1 Hz NVMe temperature trace during experiment 6b
  validation_report.txt  run counts per experiment vs. the expected matrix
All latencies are in microseconds (us); bandwidth in MB/s (10^6 bytes/s).
"""

import json
import math
import sys
from pathlib import Path

import pandas as pd

SSD_DIR = Path(__file__).resolve().parents[1]
RAW = SSD_DIR / "results" / "raw"
OUT = SSD_DIR / "results" / "processed"

PCTS = {"p1": "1.000000", "p5": "5.000000", "p10": "10.000000", "p25": "25.000000",
        "p50": "50.000000", "p75": "75.000000", "p90": "90.000000", "p95": "95.000000",
        "p99": "99.000000", "p99_5": "99.500000", "p99_9": "99.900000",
        "p99_99": "99.990000"}
PARAM_COLS = ["RW", "BS", "QD", "NJ", "SIZE", "DIRECT", "ENGINE", "RWMIXREAD",
              "INVALIDATE", "RUNTIME", "RAMP", "SEED"]

# expected number of completed runs per experiment directory (configs x trials)
EXPECTED = {
    "exp1_qd1": 4 * 3,
    "exp2_block_size": 6 * 2 * 2 * 3,
    "exp3_rw_mix": 4 * 3,
    "exp4_queue_depth": (9 + 7) * 3,
    "exp5_tail": 2 * 3,
    "exp6_device_state": 4 * 2 * 3 + 2,
    "exp7_pitfall": 7 * 3,
}


def load_fio_json(path):
    """fio may print warnings before the JSON object; skip to the first '{'."""
    text = path.read_text()
    start = text.find("{")
    if start < 0:
        raise ValueError("no JSON object in output")
    return json.loads(text[start:])


def iodepth_mean(levels):
    """Approximate mean submitted depth from fio's coarse iodepth_level buckets.

    Bucket '1' = depth 1, '2' = 2, '4' = 3-4, ... '>=64' = 64+; we use the bucket's
    upper label as its representative value (an upper-bound style estimate).
    """
    total, acc = 0.0, 0.0
    for k, pct in levels.items():
        d = 64.0 if k.startswith(">=") else float(k)
        acc += d * pct
        total += pct
    return acc / total if total else math.nan


def direction_rows(meta, data):
    job = data["jobs"][0]
    base_err = job.get("error", 0)
    disk = {d["name"]: d for d in data.get("disk_util", [])}
    util = disk.get("nvme0n1", {}).get("util", math.nan)
    rows = []
    for ddir in ("read", "write"):
        d = job[ddir]
        if d.get("total_ios", 0) == 0:
            continue
        lat = d["lat_ns"]
        pct = lat.get("percentile", {})
        row = {
            "direction": ddir,
            "fio_error": base_err,
            "iops": d["iops"],
            "bw_MBps": d["bw_bytes"] / 1e6,
            "io_bytes": d["io_bytes"],
            "total_ios": d["total_ios"],
            "runtime_ms": d["runtime"],
            "lat_mean_us": lat["mean"] / 1e3,
            "lat_std_us": lat["stddev"] / 1e3,
            "lat_min_us": lat["min"] / 1e3,
            "lat_max_us": lat["max"] / 1e3,
            "clat_mean_us": d["clat_ns"]["mean"] / 1e3,
            "slat_mean_us": d["slat_ns"]["mean"] / 1e3,
            "iodepth_level_mean": iodepth_mean(job["iodepth_level"]),
            "iodepth_level_json": json.dumps(job["iodepth_level"]),
            "usr_cpu_pct": job.get("usr_cpu"),
            "sys_cpu_pct": job.get("sys_cpu"),
            "disk_util_pct": util,
        }
        for col, key in PCTS.items():
            row[f"{col}_us"] = pct[key] / 1e3 if key in pct else math.nan
        rows.append(row)
    return rows


def parse_all():
    rows, bins = [], []
    for meta_path in sorted(RAW.glob("exp*/*.meta.json")):
        meta = json.loads(meta_path.read_text())
        common = {
            "experiment": meta["experiment"], "name": meta["name"], "run_id": meta["run_id"],
            "trial": meta["trial"], "job_file": meta["job_file"],
            "started_utc": meta["started_utc"], "returncode": meta["returncode"],
            "nvme_temp_before_c": meta["nvme_temp_before_c"],
            "nvme_temp_max_c": meta["nvme_temp_max_c"],
            "ac_online": meta["power"]["ac_online"],
            "raw_json": str((meta_path.parent / f"{meta['run_id']}.json").relative_to(SSD_DIR)),
        }
        for p in PARAM_COLS:
            common[p] = meta["params"].get(p)
        json_path = meta_path.parent / f"{meta['run_id']}.json"
        try:
            if meta["returncode"] != 0:
                raise ValueError(f"fio returncode {meta['returncode']}")
            data = load_fio_json(json_path)
            drows = direction_rows(meta, data)
            if not drows:
                raise ValueError("no completed I/O")
            for r in drows:
                rows.append({**common, **r, "valid": r["fio_error"] == 0, "parse_error": ""})
            if meta["output_format"] == "json+":
                for ddir in ("read", "write"):
                    b = data["jobs"][0][ddir]["lat_ns"].get("bins") \
                        or data["jobs"][0][ddir]["clat_ns"].get("bins")
                    if data["jobs"][0][ddir]["total_ios"] and b:
                        src = "lat_ns" if data["jobs"][0][ddir]["lat_ns"].get("bins") else "clat_ns"
                        for ns, count in b.items():
                            bins.append({"run_id": meta["run_id"], "name": meta["name"],
                                         "trial": meta["trial"], "QD": common["QD"],
                                         "direction": ddir, "source": src,
                                         "latency_us": int(ns) / 1e3, "count": count})
        except Exception as e:  # keep failed runs visible
            rows.append({**common, "direction": "", "valid": False, "parse_error": str(e)})
    return pd.DataFrame(rows), pd.DataFrame(bins)


def parse_exp6b_logs():
    ts, temps = [], []
    d = RAW / "exp6_device_state"
    for meta_path in sorted(d.glob("exp6b_*.meta.json")):
        meta = json.loads(meta_path.read_text())
        prefix = meta["params"]["LOGPREFIX"]
        for metric, fname in (("bw_KiBps", "bw"), ("iops", "iops"), ("lat_ns", "lat"),
                              ("clat_ns", "clat")):
            for log in sorted(d.glob(f"{prefix}_{fname}.*.log")):
                df = pd.read_csv(log, header=None, skipinitialspace=True)
                for _, r in df.iterrows():
                    ts.append({"run_id": meta["run_id"], "trial": meta["trial"],
                               "metric": metric, "time_s": r[0] / 1000.0, "value": r[1],
                               "direction": {0: "read", 1: "write"}.get(int(r[2]), r[2])})
        for t, c in meta["nvme_temp_trace"]:
            temps.append({"run_id": meta["run_id"], "trial": meta["trial"],
                          "time_s": t, "nvme_temp_c": c})
    return pd.DataFrame(ts), pd.DataFrame(temps)


def summarize(df):
    ok = df[df["valid"] == True]  # noqa: E712
    keys = ["experiment", "name", "direction"] + PARAM_COLS[:-1]  # all params except SEED
    metrics = ["iops", "bw_MBps", "lat_mean_us", "clat_mean_us", "p50_us", "p95_us",
               "p99_us", "p99_9_us", "p99_99_us", "iodepth_level_mean", "total_ios",
               "nvme_temp_max_c", "disk_util_pct"]
    g = ok.fillna({k: "" for k in keys}).groupby(keys, dropna=False)
    out = g[metrics].agg(["median", "min", "max", "std"])
    out.columns = [f"{m}_{s}" for m, s in out.columns]
    out["n_trials"] = g.size()
    return out.reset_index()


def validate(df, bins, ts):
    lines = []
    ok_all = True
    for exp, expected in EXPECTED.items():
        sub = df[df["experiment"] == exp]
        runs = sub["run_id"].nunique()
        valid_runs = sub[sub["valid"] == True]["run_id"].nunique()  # noqa: E712
        bad = sorted(set(sub["run_id"]) - set(sub[sub["valid"] == True]["run_id"]))  # noqa: E712
        status = "OK" if valid_runs == expected and not bad else "INCOMPLETE"
        ok_all &= status == "OK"
        lines.append(f"{exp:20s} expected={expected:3d} found={runs:3d} valid={valid_runs:3d} "
                     f"{status}" + (f"  invalid: {bad}" if bad else ""))
    lines.append(f"exp5 histogram bins: {len(bins)} rows")
    lines.append(f"exp6b timeseries:   {len(ts)} rows")
    # sanity checks on units: percentiles must be monotone and >= min latency
    v = df[df["valid"] == True]  # noqa: E712
    mono = ((v["p50_us"] <= v["p95_us"]) & (v["p95_us"] <= v["p99_us"])
            & (v["p99_us"] <= v["p99_9_us"])).all() if len(v) else True
    lines.append(f"percentiles monotone (p50<=p95<=p99<=p99.9): {bool(mono)}")
    ok_all &= bool(mono)
    return ok_all, "\n".join(lines)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    df, bins = parse_all()
    if df.empty:
        sys.exit("no runs found under results/raw/exp*/")
    df.to_csv(OUT / "all_runs.csv", index=False)
    summarize(df).to_csv(OUT / "summary_by_config.csv", index=False)
    if not bins.empty:
        bins.to_csv(OUT / "exp5_latency_bins.csv", index=False)
    ts, temps = parse_exp6b_logs()
    if not ts.empty:
        ts.to_csv(OUT / "exp6b_timeseries.csv", index=False)
        temps.to_csv(OUT / "exp6b_temperature.csv", index=False)
    ok, report = validate(df, bins, ts)
    (OUT / "validation_report.txt").write_text(report + "\n")
    print(report)
    print("validation:", "PASS" if ok else "INCOMPLETE (see above)")


if __name__ == "__main__":
    main()
