# Project 2: Cache & Memory Performance Profiling: Methodology, Results, Limitations

Each section separates what was **measured** directly (timers, kernel counters such as page
faults, sysfs/procfs values) from what was **derived** in software (throughput formulas, fits,
Little's Law products) and from **interpretation**. Numbers are medians across trials unless
stated otherwise.

## 1. Environment (recorded in `results/raw/environment_*.txt`)

| Item | Value |
|---|---|
| Machine / CPU | ThinkPad X1 Carbon Gen 13, Intel Core Ultra 7 255U (hybrid), 14 logical CPUs |
| Core types (sysfs) | CPUs 0–3: P-cores (2 cores × 2 threads, max 5.2 GHz); 4–11: E-cores (4.3 GHz); 12–13: low-power E-cores (2.4 GHz) |
| Caches (sysfs) | P-core: L1D 48 KiB, L1I 64 KiB, L2 2 MiB per core, L3 12 MiB shared by CPUs 0–11. E-core: L1D 32 KiB, L2 2 MiB per 4-core cluster. LP E-core (12–13): L1D 32 KiB, L2 2 MiB, **no L3 listed** |
| Cache line | 64 B |
| Allowed CPUs for this shell | 0–3, 12, 13 (affinity mask 0x300f, inherited; not changed) |
| OS / kernel | Ubuntu 24.04.4 LTS, Linux 6.17.0-1033-oem |
| Compiler | g++ 13.3.0; `-std=c++17 -O2 -march=native -Wall -Wextra` (`stream_bw`: `-O3`) |
| Frequency scaling | intel_pstate, governor `powersave`, EPP `balance_power` during the runs (was `balance_performance` earlier on AC), turbo enabled; **not changed** |
| Measured clock under load | CPU 0 ≈ 2.82–2.90 GHz (scaling_cur_freq) during a single-thread load, below the 5.2 GHz maximum |
| Power | **All experiment 3–8 rows were collected on battery** (AC offline, 99 → 95 %); logged per row in `ac_online`. Power state for the original experiment 1–2 runs was not recorded |
| Pages | 4 KiB default; transparent huge pages `enabled=madvise`, `defrag=madvise` (unprivileged `madvise(MADV_HUGEPAGE)` works) |
| Hardware counters | **Unavailable.** `perf` is not installed for this kernel and `perf_event_paranoid = 4`; `build/counter_probe` shows `perf_event_open` returns EACCES for hardware, cache, TLB **and** software events (`results/raw/counter_probe.csv`) |
| Python | `../.venv`: pandas, NumPy, Matplotlib |

No `sudo`, governor, kernel-parameter or service change was made. CPU pinning uses `taskset`
and `pthread_setaffinity_np`, both unprivileged.

## 2. Hypotheses

| Exp | Hypothesis |
|---|---|
| 1 | Dependent-load latency rises in steps as the footprint exceeds each cache capacity |
| 2 | Sequential order beats randomized order only while consecutive accesses share lines or are prefetchable (stride 64 B); at ≥ 256 B both pay roughly one miss per access |
| 3 | Independent random writes sustain more operations/s than reads (stores retire into the store buffer); with dependent reads, time per operation falls linearly as the write share grows |
| 4 | With K independent chains, throughput grows ~linearly with K until miss-handling or bandwidth limits, after which W (response time) grows and λ flattens (a knee) |
| 5 | Latency steps and bandwidth drops appear near nominal L1/L2/L3 capacities, not exactly at them |
| 6 | Runtime of a dependent chain is linear in the fraction of far accesses; the slope approximates the far-access latency of that footprint |
| 7 | With constant data size, spreading lines over more 4 KiB pages slows access once the page count exceeds TLB reach; 2 MiB pages remove most of that cost |
| 8 | Reusing a small buffer measures cache rather than memory bandwidth; on a hybrid CPU, unpinned or wrongly pinned runs change both the result and its variance |

## 3. Experiments: design, controlled variables, results

Error bars are interquartile ranges (IQR) across trials unless stated.

### Experiment 1: Zero-queue latency (original data, preserved)
- **Design:** `src/latency.cpp`: one random cyclic permutation of 64-byte nodes (32-bit
  next index), warm-up of 2 × nodes steps, 10 M dependent loads; 14 sizes 16 KiB–64 MiB,
  5 trials, process **not pinned**. Data: `raw/1a_zero_queue_latency.csv` (70 rows, verified;
  SHA-256 checksums in `raw/checksums_existing_data.sha256` are unchanged).
- **Measured:** 3.3–3.8 ns at 16–48 KiB; 6.0 ns at 64 KiB; 10–17.6 ns at 512 KiB–2 MiB;
  27.6–34.2 ns at 3–4 MiB; **318.7 ns at 8 MiB and 256.4 ns at 12 MiB**; 345–403 ns at 16–64 MiB.
- **Interpretation:** latency grows strongly with footprint, but the transitions do not align
  with nominal capacities. The 64 KiB step is consistent with leaving L1D. The largest step
  sits between 4 and 8 MiB, although 8–12 MiB fits the nominal 12 MiB L3. 12 MiB < 8 MiB is
  non-monotonic. Values are measured pointer-chase latencies for these footprints, not
  isolated L1/L2/L3/DRAM latencies.
- **Corrections to the plots:** 1b previously labelled 64 KiB as "L1-sized" (64 KiB > 48 KiB
  L1D); the categories are now named relative to nominal capacities.

### Experiment 2: Access pattern and stride (original data, preserved)
- **Design:** `src/access_patterns.cpp`: 64 MiB of 8-byte words, update one element every
  `stride` bytes (`data[i] += 1; checksum += data[i]`) in sequential or shuffled order, 10
  passes, 5 trials (seed 12345 + trial), not pinned. 6 configurations × 5 trials = 30 rows (verified).
- **Measured and verified medians** (software-estimated GB/s = 16 B × updates / time):

| Pattern | 64 B | 256 B | 1024 B |
|---|---:|---:|---:|
| sequential | 2.489 | 0.468 | 0.383 |
| randomized | 0.531 | 0.392 | 0.409 |

  These match the expected values exactly. Elapsed time per update: sequential 6.4 / 34.2 /
  41.8 ns, randomized 30.1 / 40.8 / 39.2 ns.
- **Caveats:** the GB/s figure is a software count, not DRAM traffic. Every update moves a
  whole 64-byte line (×4 the counted 16 B at stride 64 B), and the 8-byte `std::size_t` index
  vector (8 MiB at stride 64 B) is streamed in the timed loop. Stride-1024 runs last only
  15–28 ms, so they are timer- and frequency-sensitive (sequential trial 4 measured 0.692 GB/s).
  2b now plots time per update because raw elapsed time compares different amounts of work.

### Experiment 3: Read/write mix (`src/read_write_mix.cpp`, new)
- **Design:** random 8-byte reads (`acc += data[i]`) or plain stores (`data[i] = i`) over a
  power-of-two buffer. Addresses come from an in-register xorshift64 generator, so **no index
  array** is streamed during timing. That is the confound in the planned prototype design
  (pre-generated index and op-type arrays add their own sequential traffic and cache
  pollution). Writes are placed by a Bresenham accumulator (exact %, period ≤ 10, so the
  branch is predictable). Mixes: 0/30/50/100 % writes; footprints 1 MiB and 256 MiB; modes
  *independent* (operations overlap) and *dependent* (next address mixes in the previous read
  value, always 0 at runtime, so reads serialize). Fixed op count per (footprint, mode) across
  mixes; seed 100 + trial; 5 trials; `taskset -c 0`. 80 rows.
- **Measured (independent, Mops/s):** 1 MiB: 297 / 333 / 331 / 360 for 100R / 70R / 50R / 100W;
  256 MiB: 29.9 / 31.0 / 31.3 / 55.3.
- **Measured (dependent, ns per operation, reads and writes combined):** 1 MiB: 11.5 / 9.2 /
  6.3 / 3.5; 256 MiB: 418.5 / 294.8 / 214.3 / 19.6. At 256 MiB the mixed values are within
  2.2 % of a linear mix of the two endpoints (298.8 and 219.0 predicted). At 1 MiB the 50/50
  value is 16 % below the linear prediction.
- **Limits:** "ns per operation" is elapsed / all operations, **not** a separate per-read or
  per-write latency. Store throughput hides the read-for-ownership and the eventual
  write-back, which are not counted in the "payload GB/s". Buffers use 4 KiB pages, so the
  256 MiB runs include page-walk cost.

### Experiment 4: Concurrency sweep and Little's Law (`src/mlp_chase.cpp`, new)
- **Design:** one random cyclic list of 64-byte nodes over 256 MiB (THP requested). Each
  thread walks K independent chains that start at evenly spaced cycle positions (no overlap:
  4 M loads ≤ 4.19 M nodes). Each chain has at most one outstanding load, so configured
  concurrency L = threads × K. Threads: 1 (CPU 0), 2 (CPUs 0, 2 = two P-cores), and 4
  (CPUs 0–3, two P-cores × two hyperthreads, extension run). 5 trials, seed 200 + trial.
  150 rows.
- **Variables:** λ = completed loads / s (measured from elapsed time); W = elapsed / steps =
  mean time between successive loads of one chain (ns). Because both come from the same
  elapsed time, **L = λW holds by construction** and is not an independent test. The useful
  derived quantity is **λ × W0** (W0 = 350 ns, the one-chain response time): the number of
  loads that would have to be overlapped at unloaded latency to deliver λ.
- **Measured:**
  - 1 thread: λ rises from 2.9 M/s (L = 1) to 64.6 M/s (L = 32), still +21 % at the last
    step. W stays at 350–450 ns, then 495 ns at L = 32. **No knee** within L ≤ 32.
  - 2 threads: 129.7 M/s at L = 64 (+9 % over L = 48), **no clear plateau**.
  - 4 threads: 186.8 M/s at L = 96 and 185.2 M/s at L = 128 (−1 %) while W rises
    514 → 691 ns. This is the **only knee observed**, near L ≈ 96 (≈ 12 GB/s of
    line-granular traffic). Evidence is limited: these runs last only ~20–30 ms each.
  - λ × W0 tracks L closely up to ~32, then falls below it (65 at L = 128).
- **Limits:** this is a memory-level-parallelism model, not a queue-depth model with a request
  queue. The 4-thread runs share each core's miss buffers between two hyperthreads. THP
  backing was full in 146 of 150 runs and 228–252 MiB in the remaining 4.

### Experiment 5: Working-set sweep (pinned re-run)
- **Design (5a):** the **unchanged** `src/latency.cpp`, rebuilt with explicit flags, pinned to
  CPU 0 (P-core), 34 sizes 4 KiB–256 MiB, 10 M loads (5 M from 16 MiB up), 5 trials, 4 KiB
  pages. 170 rows. **(5b):** `src/stream_bw.cpp`, AVX2-vectorized read (4 accumulators) and
  store loops, ~2 GiB per measurement (≥ 5 passes) after a warm-up pass and a 200 ms spin,
  CPU 0, 20 sizes, read and write, 5 trials. 200 rows.
- **Measured latency:** 3.4–4.4 ns up to 48 KiB; 8.4–11.6 ns from 56 KiB to 768 KiB;
  13.4 ns (1 MiB), 23.6 ns (2 MiB), 30.3 ns (3 MiB), 54.3 ns (4 MiB), **192 ns (6 MiB),
  334 ns (8 MiB)**, 357–379 ns (10–16 MiB), 419 ns (256 MiB).
- **Measured bandwidth (software-counted):** read 54–60 GB/s up to 128 KiB, 47–55 GB/s up to
  2 MiB, ~30 GB/s at 4–6 MiB, 11–12 GB/s at ≥ 16 MiB. Write 73–75 GB/s at ≤ 48 KiB,
  ~45 GB/s from 64 KiB to 1 MiB, 8–9 GB/s at ≥ 32 MiB.
- **Interpretation:** the L1D transition (48 → 56 KiB) and a gradual L2 transition near
  1.5–2 MiB line up with nominal capacities. The step to near-DRAM latency happens between
  4 and 8 MiB **even on a P-core**, well before the nominal 12 MiB L3. So the experiment 1
  anomaly is not explained by core type alone. Plausible contributors include 4 KiB-page
  translation cost, L3 sharing, replacement policy and power-managed L3 behaviour on
  battery, but none of these is proven here. Bandwidth is software-counted and single-thread.

### Experiment 6: Cache-miss impact (timing only) (`src/miss_mix.cpp`, new)
- **Counter status:** **blocked.** `perf_event_open` returns EACCES, so no miss counts exist
  and `6a_cache_misses_vs_working_set.png` / `6b_runtime_vs_cache_misses.png` were not made.
- **Substitute design:** one dependent load chain. A **designed** fraction f (0–1, Bresenham
  placement) of loads go to random lines of a far buffer (1 MiB, 8 MiB, 256 MiB; THP); the
  rest go to a 16 KiB near buffer. The address select is branchless, and a zero-valued data
  dependency serializes loads. 5 M loads, 5 trials, CPU 0. 150 rows. Per-trial least-squares
  fit ns = a + b·f.
- **Derived slope b (incremental cost per far access):** 1 MiB 3.5 ns (min R² 0.79); 8 MiB
  81.5 ns (IQR 53–88, min R² 0.61); 256 MiB 359.3 ns (min R² 0.997, near the THP pointer-chase
  latency 362 ns of 7b).
- **Interpretation:** a far access into a DRAM-sized buffer adds a fixed ~360 ns, and runtime
  is linear in f. The 8 MiB buffer is unstable: some trials behave like L3 hits, others like
  DRAM (compare 8b). These are inferred costs, not measured miss penalties.

### Experiment 7: TLB impact (timing only) (`src/tlb_locality.cpp`, new)
- **Counter status:** TLB-miss counts are **blocked** (same EACCES);
  `7a_tlb_misses_vs_page_locality.png` was not made.
- **Measured instead:** time per load, minor page faults during setup (getrusage), and
  AnonHugePages backing (/proc/self/smaps_rollup). Huge pages were requested with
  unprivileged `madvise`; no system setting was changed.
- **7a design:** fixed 8192 lines (512 KiB < nominal L2) spread over 128 … 8192 page slots
  (64 … 1 line per page, random offsets), one random cyclic chain, 20 M loads; 4 KiB vs THP.
- **7a measured:** 4 KiB pages flat at 9–10 ns up to 2048 pages, then **15.8 ns (4096) and
  21.0 ns (8192)**. THP stays at 5.9–9.0 ns throughout. Interpretation: the slowdown appears
  once the touched 4 KiB pages exceed a translation reach of roughly 2048 pages (8 MiB); this
  is inferred from timing only.
- **7b measured (4 KiB vs THP):** 2 MiB 15.4 vs 10.0 ns; 16 MiB 360 vs 326 ns; 64 MiB 396 vs
  354 ns; 256 MiB 421 vs 362 ns. Setup page faults are 4097 / 16385 / 65537 (4 KiB) vs
  9 / 33 / 129 (THP). THP backing was complete except in one 256 MiB trial (44 MiB backed,
  405 ns) and another partial one (208 MiB, 372 ns).

### Experiment 8: Measurement pitfalls
- **8a (cache reuse vs large working set):** 20 separately timed read passes after evicting
  with a 64 MiB read, CPU 0, 5 trials. **1 MiB:** pass 1 9.6 GB/s (cold), best pass 39.2 GB/s
  (4.1×), passes 16–20 ~24 GB/s. **256 MiB:** 9.4–12.9 GB/s throughout. Pitfall
  demonstrated: quoting a repeated small-buffer number as "memory bandwidth" overstates the
  cold pass several-fold. Anomaly: pass 2 of the 1 MiB buffer is still cold-speed, and the warm
  passes drift down after pass ~10; the cause was not identified.
- **8b (pinned vs unpinned on a hybrid CPU):** dense 4 KiB-page chase, 12 trials per
  configuration, CPU recorded at start and end.
  - **1 MiB:** CPU 0 (P-core) 12.8 ns (CV 13 %). CPU 12 (LP E-core) 48.5 ns (CV 100 %,
    outliers to 273 ns). Unpinned 16.2 ns, CV 155 %; 7 of 12 runs migrated between CPUs
    (all P-cores), one outlier 186 ns.
  - **8 MiB:** CPU 0 298 ns but bimodal (107–342 ns, CV 34 %). CPU 12 355 ns (CV 1.8 %:
    always DRAM-like, consistent with no L3). Unpinned 236 ns (CV 32 %), 8 of 12 migrated.
  - **Pitfall demonstrated:** the CPU a run lands on changes the answer by ~4× at 1 MiB, and
    unpinned runs add migration outliers. No unpinned run ended on an LP E-core in this
    sample, so the original experiment 1 anomaly cannot be attributed to LP E-cores.

## 4. Anomalies and limitations (summary)
1. Experiments 3–8 ran on battery at ~2.9 GHz with EPP `balance_power`, so absolute numbers
   are lower than a plugged-in, turbo-boosted run. The original experiment 1–2 data has no
   recorded power state.
2. No hardware counters: every cache/TLB statement is inferred from timing; three planned
   counter plots are blocked.
3. The latency transition to near-DRAM latency occurs between 4 and 8 MiB, below the nominal
   12 MiB L3, on both pinned and unpinned runs. 8 MiB results are bimodal; the cause is open.
4. THP is best-effort: 4 experiment 4 runs, 4 experiment 6 runs and 2 experiment 7b runs got
   partial huge-page backing (recorded per row).
5. Experiment 4's only knee (4 threads, L ≈ 96) comes from 20–30 ms runs and uses
   hyperthreads; the 1- and 2-thread curves never plateau.
6. Experiment 2 throughput is a software estimate that ignores line granularity and the
   index vector; stride-1024 runs are very short.
7. Software-counted write bandwidth excludes read-for-ownership and write-back traffic.
8. Single machine, single session; 5 trials (12 for 8b). IQR whiskers describe run-to-run
   spread, not confidence intervals.

## 5. Reproduction

```bash
cd cache-memory/scripts
./build.sh                         # compiles all benchmarks into ../build with explicit flags
./collect_env.sh                   # environment + counter probe -> ../results/raw/
./run_all_new.sh                   # experiments 3-8 (~20 min); refuses to overwrite raw files
../../.venv/bin/python analyze_all.py   # all summaries and 16 plots
```
Per experiment: `run_3_read_write_mix.sh`, `run_4_concurrency_sweep.sh`,
`run_4_concurrency_extended.sh`, `run_5_working_set.sh`, `run_6_far_access.sh`, `run_7_tlb.sh`,
`run_8_pitfall.sh`; analysis: `analyze_<n>_*.py`. Experiments 1–2 originals:
`run_latency_sweep.sh`, `run_access_patterns.sh` (these overwrite their raw files when run, so
they were **not** re-run). Single binaries can be smoke-tested directly, e.g.
`taskset -c 0 ../build/read_write_mix 1024 10 30 independent 1`.
To re-run a new experiment, move its raw CSV aside first (the scripts refuse to overwrite).

## 6. AI-use disclosure
Claude (Anthropic) assisted throughout this project. It inspected the existing code and data;
verified the experiment 1–2 raw files and summaries; implemented the new benchmarks
(`read_write_mix`, `mlp_chase`, `stream_bw`, `miss_mix`, `tlb_locality`, `counter_probe`,
`common.hpp`) and the run, processing and plotting scripts; ran the bounded smoke tests and
measurement campaigns; restyled the four existing plots without changing their data; and
drafted this methodology/results document. All numbers come from the raw CSVs in
`results/raw/`; none were typed in by hand. Interpretations are marked as such and should be
reviewed by the student before submission.
