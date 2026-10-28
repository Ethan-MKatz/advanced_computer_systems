#!/usr/bin/env python3
"""Experiment 4: iodepth sweep (numjobs=1 primary curve) plus a numjobs=4 parallel curve."""
import fio_runner as fr

CURVES = {1: [1, 2, 4, 8, 16, 32, 64, 128, 256],   # numjobs -> iodepths
          4: [1, 2, 4, 8, 16, 32, 64]}
RUNTIME = 20

for trial in range(1, fr.TRIALS + 1):
    for nj, qds in CURVES.items():
        for qd in qds:
            fr.run_fio("exp4_queue_depth", f"exp4_randread_4k_nj{nj}_qd{qd}",
                       "exp4_queue_depth.fio",
                       fr.params(QD=qd, NJ=nj, RUNTIME=RUNTIME, SEED=fr.seed(trial)), trial)
