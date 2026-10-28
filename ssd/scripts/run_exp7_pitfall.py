#!/usr/bin/env python3
"""Experiment 7: misleading setup - buffered (page-cache) I/O vs direct I/O.

All runs use the synchronous psync engine, 4 KiB random I/O over the first 1 GiB of
the test file, so the only intended difference is direct=0 vs direct=1.
  direct          : direct=1, true device I/O
  buffered_cold   : direct=0, file pages dropped first (invalidate=1), no ramp
  buffered_warm   : direct=0, after a buffered sequential pass that loads the 1 GiB
                    range into the page cache (invalidate=0)
Extra wrong-queue-depth demo: psync with iodepth=32 (sync engine -> effective QD 1).
"""
import fio_runner as fr

SIZE = "1g"
RUNTIME = 15


def run(trial, name, **kw):
    p = fr.params(ENGINE="psync", SIZE=SIZE, RUNTIME=RUNTIME, QD=1, SEED=fr.seed(trial))
    p.update(kw)
    fr.run_fio("exp7_pitfall", name, "exp7_buffered_vs_direct.fio", p, trial)


for trial in range(1, fr.TRIALS + 1):
    run(trial, "exp7_randread_direct", RW="randread", DIRECT=1, INVALIDATE=1)
    run(trial, "exp7_randread_buffered_cold", RW="randread", DIRECT=0, INVALIDATE=1, RAMP=0)
    # warm the page cache: one buffered sequential pass over the 1 GiB range
    run(trial, "exp7_warmup_seqread_buffered", RW="read", DIRECT=0, INVALIDATE=1, RAMP=0,
        RUNTIME=3)
    run(trial, "exp7_randread_buffered_warm", RW="randread", DIRECT=0, INVALIDATE=0)
    run(trial, "exp7_randwrite_direct", RW="randwrite", DIRECT=1, INVALIDATE=1)
    run(trial, "exp7_randwrite_buffered", RW="randwrite", DIRECT=0, INVALIDATE=0)
    fr.idle(10, "(let dirty page-cache writeback drain)")
    run(trial, "exp7_randread_direct_psync_qd32", RW="randread", DIRECT=1, INVALIDATE=1, QD=32)
