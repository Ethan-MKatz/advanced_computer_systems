#!/usr/bin/env bash
# Full SSD profiling pipeline: prepare file -> experiments 1-7 -> parse -> plots.
# Experiments run strictly one at a time; completed runs are skipped on re-run.
set -euo pipefail
cd "$(dirname "$0")"
PY="${PYTHON:-../../.venv/bin/python}"

"$PY" prepare_testfile.py
"$PY" fio_runner.py                      # safety check only
"$PY" run_exp1_qd1.py
"$PY" run_exp2_block_size.py
"$PY" run_exp3_rw_mix.py
"$PY" run_exp4_queue_depth.py
"$PY" parse_results.py || true           # partial parse to select exp5 depths
"$PY" select_tail_depths.py
"$PY" run_exp5_tail.py
"$PY" run_exp6_device_state.py
"$PY" run_exp7_pitfall.py
"$PY" parse_results.py
"$PY" plot_all.py
