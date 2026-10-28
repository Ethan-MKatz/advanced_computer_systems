# Advanced Computer Systems Lab

Projects and experimental results for ECSE 4320/6320 Advanced Computer Systems.
All measurements were taken on one machine: a ThinkPad X1 Carbon Gen 13 with an Intel Core
Ultra 7 255U (hybrid P / E / low-power E cores; P-core L1D 48 KiB, L2 2 MiB, shared L3 12 MiB),
a Samsung PM9C1a 1 TB NVMe SSD (PCIe 4.0 x4), Ubuntu 24.04 (Linux 6.17) and g++ 13.3.

Each project keeps source, scripts, raw data, processed data, plots and a methodology document
together, so every plot can be traced back to the measurements that produced it.

## Projects

### 1. SIMD Advantage Profiling: [`simd/`](simd/)
Scalar vs. auto-vectorized (`-O3 -march=native`) performance for elementwise multiply, SAXPY,
dot product and triad: working-set locality, alignment, tail handling, stride, FP32 vs. FP64,
vectorization verification and a roofline analysis.
- Methodology: [simd/report/methodology.md](simd/report/methodology.md)
- Report: `simd/report/ACS Report.pdf`

### 2. Cache and Memory Performance Profiling: [`cache-memory/`](cache-memory/)
Pointer-chasing latency, stride and access-pattern sweeps, read/write mixes, a concurrency
(memory-level parallelism) sweep with Little's Law, working-set latency and bandwidth, timing-based
cache-miss and TLB studies (4 KiB vs. huge pages), and two benchmark pitfalls (cache reuse,
pinning on a hybrid CPU). 16 plots. Hardware counters were unavailable, which is documented.
- Methodology, results and limitations: [cache-memory/report/methodology_and_results.md](cache-memory/report/methodology_and_results.md)
- Plot manifest: [cache-memory/results/plots/MANIFEST.md](cache-memory/results/plots/MANIFEST.md)

### 3. SSD Performance Profiling: [`ssd/`](ssd/)
fio-based QD=1 baselines, block-size and pattern sweeps, read/write mixes, queue-depth and
parallelism sweep with Little's Law, tail latency, working-set and burst-vs-later behaviour, and
a buffered-vs-direct I/O pitfall. 14 plots. All I/O targets a disposable 4 GiB file with direct
I/O; no raw device or partition is ever benchmarked.
- Methodology: [ssd/report/methodology.md](ssd/report/methodology.md)
- Plot manifest: [ssd/results/plots/MANIFEST.md](ssd/results/plots/MANIFEST.md)

## Repository layout

```
<project>/
  src/ or configs/     benchmark source (C++) or fio job files
  scripts/             build, run, parse and plot scripts
  results/raw/         raw measurements (never overwritten by the run scripts of projects 2-3)
  results/processed/   summaries derived from raw data
  results/plots/       figures
  report/              methodology and report material
```

## Reproducing

Python analysis uses the virtual environment in `.venv/` (pandas, NumPy, Matplotlib).

```bash
# Project 1 (SIMD): build scalar and SIMD variants, run, then plot (see simd/report/methodology.md)
# Project 2 (cache-memory): ~25 min of pinned benchmarks
cd cache-memory/scripts && ./build.sh && ./run_all_new.sh && ../../.venv/bin/python analyze_all.py
# Project 3 (SSD): ~80 min of fio runs against ssd/testfile/fio_testfile.bin
cd ssd/scripts && ./run_all.sh
```

## Notes

- Results depend on CPU core type, frequency, power state and background load. Projects 2 and 3
  record these per run; project 1 did not pin CPUs or record power state (see its methodology).
- Compiled binaries, the Python virtual environment and the SSD test file are git-ignored.
