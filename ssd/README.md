# Project 3: SSD Performance Profiling

fio-based characterization of a Samsung PM9C1a 1 TB NVMe SSD (PCIe 4.0 x4) in a ThinkPad X1 Carbon
Gen 13. All I/O targets one disposable 4 GiB regular file on ext4, `testfile/fio_testfile.bin`,
with direct I/O. No raw device is ever touched.

```
configs/            fio job files (one per experiment + one-time file preparation)
scripts/            fio_runner.py (safety checks + metadata), run_exp*.py, parse_results.py,
                    select_tail_depths.py, plot_exp*.py, plot_all.py, run_all.sh
results/raw/        fio JSON, per-run metadata (*.meta.json), stderr, fio logs, run_log.txt
results/processed/  tidy CSVs, summary, validation report
results/plots/      the 14 plots + MANIFEST.md
report/             methodology.md (environment, safety, workload matrix, reproduction)
testfile/           disposable fio target (git-ignored)
```

Reproduce everything: `cd scripts && ./run_all.sh` (about 80 minutes; completed runs are skipped).
See [report/methodology.md](report/methodology.md) for details.
