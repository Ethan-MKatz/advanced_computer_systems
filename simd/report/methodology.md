# Project 1: SIMD Advantage Profiling: Methodology

This file documents how the SIMD data was collected and processed. The written report is
`ACS Report.pdf` in this folder. Everything below is taken from the source code in `src/`,
the plotting scripts in `scripts/`, the configuration notes in `docs/environment.txt` and
`results/day2_configuration.txt`, and the raw CSV files in `results/raw/`. Items that were not
recorded at the time are marked as such.

## 1. Environment (`docs/environment.txt`, recorded 2026-10-19)

| Item | Value |
|---|---|
| Machine / CPU | ThinkPad X1 Carbon Gen 13, Intel Core Ultra 7 255U (hybrid: 2 P-cores with SMT, 8 E-cores, 2 low-power E-cores; 14 logical CPUs) |
| Caches | P-core L1D 48 KiB, L2 2 MiB, shared L3 12 MiB, 64-byte lines |
| SIMD ISA | AVX2 + FMA (256-bit: 8 FP32 or 4 FP64 lanes); no AVX-512 |
| OS / kernel | Ubuntu 24.04.4 LTS, Linux 6.17.0-1033-oem |
| Compiler | g++ 13.3.0 |
| Frequency policy | governor `powersave`, turbo enabled, SMT active (not changed) |
| Threads | single-threaded benchmarks |
| Timer | `std::chrono::steady_clock`, milliseconds |
| Not recorded | CPU pinning (no `taskset` was used, so runs could land on any core type), AC vs battery power, exact per-run command lines |

## 2. Builds

Each benchmark is compiled twice from the same source:

| Build | Flags | Purpose |
|---|---|---|
| scalar | `-O3 -fno-tree-vectorize -fno-tree-slp-vectorize` | full optimization with GCC's loop and SLP auto-vectorizers disabled |
| SIMD ("optimized") | `-O3 -march=native` | auto-vectorization enabled for the host ISA (AVX2) |

`-march=native` also enables other host-specific optimizations, so a speedup is not attributed
to SIMD alone without the vectorization evidence in `results/*vectorization*.txt`
(`-fopt-info-vec` output, for example "loop vectorized using 32 byte vectors").

The exact compile commands were not scripted. They are reconstructed from the flags above and
the binary names in the root `.gitignore`, for example:

```bash
cd simd
g++ -O3 -fno-tree-vectorize -fno-tree-slp-vectorize -o benchmark_day2_scalar src/benchmark_day2.cpp
g++ -O3 -march=native                                -o benchmark_day2_simd   src/benchmark_day2.cpp
```

## 3. Common measurement procedure

- **Data:** FP32 arrays (FP64 as well in the precision study), filled deterministically
  (`std::mt19937` seed 12345 for the day 2 kernels, `i % 17` / `i % 13` patterns elsewhere).
- **Warm-up:** every program runs the kernel once, untimed, before measuring. That call also
  pages in the arrays and is used for the correctness check.
- **Correctness:** each program checks its result against a reference outside the timed region
  (elementwise expected values, or a double / long-double reference sum) and writes `correct`
  or exits on failure.
- **Repetitions:** 9 timed repetitions per configuration, **median** reported (21 for the tail
  study, 10 for the triad / roofline runs).
- **Keeping the work:** outputs are consumed after timing (checksums), so the compiler cannot
  remove the kernel. SAXPY restores its input array outside the timed region before every
  repetition.
- **Logical traffic:** multiply and SAXPY count 12 bytes per element (two 4-byte reads, one
  4-byte write); dot product counts 8 bytes. "Logical bandwidth" = logical bytes / median time,
  reported in GiB/s. It excludes read-for-ownership traffic and cache-line granularity, so it is
  not a measured DRAM bandwidth.
- **FLOPs:** multiply 1 per element; SAXPY, dot product and triad 2 per element.
- **Speedup:** scalar median runtime / SIMD median runtime.

## 4. Experiments

| Report section | Program | Varied | Fixed | Raw data | Plot script |
|---|---|---|---|---|---|
| Scalar vs. auto-vectorized, per kernel | `src/benchmark_day2.cpp` | kernel (multiply, SAXPY, dot) × N ∈ {2¹⁰, 2¹³, 2¹⁶, 2²⁰, 2²³} × build | FP32, 9 reps | `results/raw/day2_<build>_<kernel>_<N>.csv` | `scripts/plot_day2.py` |
| Locality sweep | `src/benchmark_day2.cpp` (elementwise multiply runs from the row above) | N from 2¹⁰ (12 KiB) to 2²³ (96 MiB) × build | FP32, 9 reps | `results/raw/day2_<build>_multiply_<N>.csv` | `scripts/plot_locality.py` |
| Day 1 baseline (early runs) | `src/benchmark.cpp` (elementwise multiply) | N ∈ {2¹⁰, 2¹³, 2¹⁶, 2²⁰} × build (SIMD also 2²³) | FP32, 9 reps | `results/raw/scalar_*.csv`, `simd_*.csv` → `results/processed/elementwise_multiply.csv` (`scripts/collect_results.py`) | `scripts/plot_results.py` |
| Alignment | `src/benchmark_day3_alignment.cpp` | start offset ∈ {0, 1, 2, 4, 8} floats from a 64-byte-aligned (`posix_memalign`) base × N ∈ {65,536; 1,048,576; 8,388,608} × build | multiply, 9 reps | `results/raw/day3/alignment/` | `scripts/plot_day3.py` |
| Tail handling | `src/benchmark_day3_tail.cpp` | N = 2²⁰ + r, r = 0…7 | SIMD build, multiply, 21 reps | `results/raw/day3/tail/simd_tail.csv` | `scripts/plot_day3_tail.py` |
| Stride / gather | `src/benchmark_day3.cpp` | stride ∈ {1, 2, 4, 8} × N ∈ {65,536; 1,048,576; 8,388,608} × build | multiply (`out[i] = a[i·s] * b[i·s]`), 64-byte aligned, 9 reps | `results/raw/day3/<build>_N<N>_S<s>.csv` | `scripts/plot_day3.py` |
| Data type | `src/benchmark_day4_precision.cpp` | float32 vs float64 × kernel × N ∈ {2¹⁰ … 2²³} × build | 64-byte aligned, 9 reps; relative error against a `long double` reference | `results/raw/day4_corrected/` (the plots use this re-run; the first run in `results/raw/day4/` is kept for reference) | `scripts/plot_day4.py` |
| Vectorization verification | compiler reports | – | `-fopt-info-vec` output | `results/vectorization.txt`, `results/day2_vectorization.txt`, `results/day2_kernel_vectorization.txt`, `results/benchmark_vectorization.txt`; assembly `results/plots/day3_alignment.s` | – |
| Roofline / negative example | `src/memory_bandwidth.cpp` (triad `a[i] = b[i] + s·c[i]`, `noinline`) | N ∈ {8,388,608; 16,777,216} × build | 10 reps | `results/raw/day5/memory_bandwidth.csv`, `roofline_metrics.csv` | `scripts/plot_day5.py` |

**Roofline parameters (`scripts/plot_day5.py`):**
- Arithmetic intensity of triad: 2 FLOPs / 12 bytes = 0.167 FLOP/byte.
- Bandwidth roof: the largest observed triad logical bandwidth, 15.6 GiB/s (about 16.75 GB/s;
  the report rounds it to about 16.5 GB/s). This is an empirical reference, not an independent
  DRAM measurement.
- Compute roof: an estimate, 12 cores × 5.2 GHz × 8 FP32 lanes × 2 FLOPs (FMA) ≈ 998 GFLOP/s.
  It is not a measured sustained peak; the hybrid cores do not all reach 5.2 GHz.

## 5. Limitations

1. No CPU pinning: on this hybrid CPU a run could execute on a P-core, an E-core or a
   low-power E-core (which has no L3), and the scheduler could migrate it. This is a likely
   source of the irregular points noted in the report (for example the stride and tail
   anomalies). The cache-memory project measured a 3.8× latency difference between core types.
2. Power state and actual clock frequency were not recorded; the governor was `powersave`.
3. Nine repetitions with only the median kept: run-to-run spread is not saved in the raw CSVs,
   so plots have no error bars.
4. Logical bandwidth ignores read-for-ownership and line granularity, and the roofline ceilings
   are estimates.
5. Hardware performance counters were not available (`perf_event_paranoid = 4`, no perf for the
   running kernel), so vectorization is verified from compiler reports and assembly, not from
   instruction counts.

## 6. Reproduction

```bash
cd simd
# build both variants of a benchmark (see section 2), then run, e.g.
./benchmark_day2_scalar multiply 1048576 results/raw/day2_scalar_multiply_1048576.csv
./benchmark_day2_simd   multiply 1048576 results/raw/day2_simd_multiply_1048576.csv
# usage strings: benchmark_day3 <N> <stride> <out.csv>; benchmark_day3_alignment <N> <offset_floats> <out.csv>;
# benchmark_day3_tail <base_N> <out.csv>; memory_bandwidth [N] [repetitions]
../.venv/bin/python scripts/plot_day2.py    # likewise plot_day3.py, plot_day3_tail.py, plot_day4.py, plot_day5.py, plot_locality.py
```
To reduce the limitations above on a re-run, pin each benchmark with `taskset -c 0` (a P-core)
and record AC power and the governor.
