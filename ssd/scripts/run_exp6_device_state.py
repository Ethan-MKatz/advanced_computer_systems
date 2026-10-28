#!/usr/bin/env python3
"""Experiment 6: working-set (LBA range) sweep and a bounded sustained-write run.

6a: 4 KiB random read and random write at iodepth=32 over 64 MiB .. 4 GiB ranges.
6b: 90 s of 4 KiB random writes (iodepth=32) with 1 s averaged bandwidth/latency logs,
    two trials separated by an idle period. Bounded on purpose: ~90 s x ~1-2 GB/s per
    trial; this is NOT a full-drive steady-state preconditioning.
"""
import fio_runner as fr

RANGES = ["64m", "256m", "1g", "4g"]
RUNTIME = 20
SUSTAINED_RUNTIME = 90
IDLE_BETWEEN = 120

for trial in range(1, fr.TRIALS + 1):
    for rw in ("randread", "randwrite"):
        for size in RANGES:
            fr.run_fio("exp6_device_state", f"exp6a_{rw}_4k_qd32_range{size}",
                       "exp6_working_set.fio",
                       fr.params(RW=rw, SIZE=size, RUNTIME=RUNTIME, SEED=fr.seed(trial)), trial)

for trial in (1, 2):
    fr.idle(IDLE_BETWEEN, "(let the drive return to idle before the sustained run)")
    name = "exp6b_randwrite_4k_qd32_sustained"
    fr.run_fio("exp6_device_state", name, "exp6_sustained.fio",
               fr.params(RAMP=0, RUNTIME=SUSTAINED_RUNTIME, SEED=fr.seed(trial),
                         LOGPREFIX=f"{name}_t{trial}"), trial)
