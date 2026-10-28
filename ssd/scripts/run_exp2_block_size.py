#!/usr/bin/env python3
"""Experiment 2: block-size sweep for random and sequential reads at QD=1 and QD=32."""
import fio_runner as fr

BLOCK_SIZES = ["4k", "16k", "32k", "64k", "128k", "256k"]
PATTERNS = ["randread", "read"]
QDS = [1, 32]
RUNTIME = 15

for trial in range(1, fr.TRIALS + 1):
    for qd in QDS:
        for rw in PATTERNS:
            for bs in BLOCK_SIZES:
                fr.run_fio("exp2_block_size", f"exp2_{rw}_{bs}_qd{qd}", "exp2_block_size.fio",
                           fr.params(RW=rw, BS=bs, QD=qd, RUNTIME=RUNTIME, SEED=fr.seed(trial)),
                           trial)
