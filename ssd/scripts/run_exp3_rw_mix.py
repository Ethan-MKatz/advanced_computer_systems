#!/usr/bin/env python3
"""Experiment 3: read/write mix sweep, 4 KiB random, iodepth=32."""
import fio_runner as fr

MIXES = [100, 70, 50, 0]      # rwmixread (% reads)
RUNTIME = 30

for trial in range(1, fr.TRIALS + 1):
    for mix in MIXES:
        fr.run_fio("exp3_rw_mix", f"exp3_randrw_4k_qd32_read{mix}", "exp3_rw_mix.fio",
                   fr.params(RWMIXREAD=mix, RUNTIME=RUNTIME, SEED=fr.seed(trial)), trial)
