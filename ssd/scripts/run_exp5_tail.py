#!/usr/bin/env python3
"""Experiment 5: tail latency at the mid and near-knee depths selected from experiment 4.

Uses json+ output so the full fio latency histogram (per-I/O, ~1.5% bucket width)
is preserved for the distribution / CCDF plot.
"""
import json

import fio_runner as fr

sel = json.loads((fr.SSD_DIR / "results/processed/exp5_selected_depths.json").read_text())
RUNTIME = 60

for trial in range(1, fr.TRIALS + 1):
    for label in ("mid", "knee"):
        qd = sel[label]["iodepth"]
        fr.run_fio("exp5_tail", f"exp5_randread_4k_{label}_qd{qd}", "exp5_tail_latency.fio",
                   fr.params(QD=qd, RUNTIME=RUNTIME, SEED=fr.seed(trial)), trial,
                   output_format="json+")
