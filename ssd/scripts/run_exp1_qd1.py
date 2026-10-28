#!/usr/bin/env python3
"""Experiment 1: QD=1 latency baselines (4 KiB random R/W, 128 KiB sequential R/W)."""
import fio_runner as fr

WORKLOADS = [("randread", "4k"), ("randwrite", "4k"), ("read", "128k"), ("write", "128k")]
RUNTIME = 30

for trial in range(1, fr.TRIALS + 1):          # trials outermost: drift hits all configs
    for rw, bs in WORKLOADS:
        fr.run_fio("exp1_qd1", f"exp1_{rw}_{bs}_qd1", "exp1_qd1_baseline.fio",
                   fr.params(RW=rw, BS=bs, RUNTIME=RUNTIME, SEED=fr.seed(trial)), trial)
