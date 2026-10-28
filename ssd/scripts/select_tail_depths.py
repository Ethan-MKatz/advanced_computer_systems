#!/usr/bin/env python3
"""Pick the experiment-5 depths from the experiment-4 numjobs=1 curve.

knee: smallest iodepth whose median IOPS reaches >= 90% of the curve's maximum median
      IOPS (beyond it, extra depth mostly adds latency, not throughput).
mid:  iodepth = knee / 4 (at least 2), a point well before saturation.
Writes results/processed/exp5_selected_depths.json with the numbers used.
"""
import json
from pathlib import Path

import pandas as pd

SSD_DIR = Path(__file__).resolve().parents[1]
PROC = SSD_DIR / "results" / "processed"
KNEE_FRACTION = 0.90


def main():
    s = pd.read_csv(PROC / "summary_by_config.csv")
    c = s[(s["experiment"] == "exp4_queue_depth") & (s["NJ"] == 1)].copy()
    c["QD"] = c["QD"].astype(int)
    c = c.sort_values("QD")
    peak = c["iops_median"].max()
    knee = int(c[c["iops_median"] >= KNEE_FRACTION * peak]["QD"].iloc[0])
    qds = list(c["QD"])
    mid = max(2, knee // 4)
    mid = max(q for q in qds if q <= mid)
    pick = lambda q: c[c["QD"] == q].iloc[0]  # noqa: E731
    out = {
        "rule": f"knee = smallest QD with median IOPS >= {KNEE_FRACTION:.0%} of max; "
                "mid = knee/4 (>=2)",
        "peak_iops_median": peak,
        "knee": {"iodepth": knee, "iops_median": pick(knee)["iops_median"],
                 "lat_mean_us_median": pick(knee)["lat_mean_us_median"]},
        "mid": {"iodepth": mid, "iops_median": pick(mid)["iops_median"],
                "lat_mean_us_median": pick(mid)["lat_mean_us_median"]},
    }
    (PROC / "exp5_selected_depths.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
