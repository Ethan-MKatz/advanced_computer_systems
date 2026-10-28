# Project 2: Cache & Memory Performance Profiling

Timing-based characterization of the cache and memory hierarchy of an Intel Core Ultra 7 255U
(hybrid P / E / low-power E cores) in a ThinkPad X1 Carbon Gen 13. Eight experiments, two plots
each. Hardware performance counters are not available to unprivileged users on this system,
so cache/TLB effects are measured through time, kernel page-fault counts and huge-page backing.

```
src/        benchmarks (C++17): latency, access_patterns (original), read_write_mix, mlp_chase,
            stream_bw, miss_mix, tlb_locality, counter_probe, common.hpp
scripts/    build.sh, collect_env.sh, run_*.sh (one per experiment), analyze_*.py / plot scripts,
            analyze_all.py, cm_style.py (shared plot style)
build/      compiled benchmarks (git-ignored; `scripts/build.sh`)
results/raw/        raw CSVs, environment records, counter probe, run logs, checksums
results/processed/  summaries per experiment
results/plots/      16 plots + MANIFEST.md (original_v1/ keeps the first four plots as they were)
report/     methodology_and_results.md: environment, hypotheses, design, results,
            anomalies, limitations, reproduction, AI-use disclosure
```

| Exp | Topic | Plots | Notes |
|---|---|---|---|
| 1 | Zero-queue latency | 1a, 1b | original data, preserved |
| 2 | Access pattern / stride | 2a, 2b | original data, preserved |
| 3 | Read/write mix | 3a, 3b | |
| 4 | Concurrency + Little's Law | 4a, 4b | |
| 5 | Working-set sweep (latency + bandwidth) | 5a, 5b | |
| 6 | Cache-miss impact | 6a\*, 6b\* | timing-only substitutes; counter plots blocked |
| 7 | TLB impact | 7a\*, 7b | 7a timing-only substitute; counter plot blocked |
| 8 | Measurement pitfalls | 8a, 8b | |

Reproduce: `cd scripts && ./build.sh && ./run_all_new.sh && ../../.venv/bin/python analyze_all.py`.
Details and caveats: [report/methodology_and_results.md](report/methodology_and_results.md).
Plot to data mapping: [results/plots/MANIFEST.md](results/plots/MANIFEST.md).
