# Plot manifest: Project 2 (Cache & Memory)

All plots are generated from measured data by `scripts/analyze_all.py` (or the per-experiment
script listed). No plot uses synthetic data. Originals of the four plots that existed before
this pass are kept in `original_v1/`.

| # | Plot file | Status | Raw data (`results/raw/`) | Processed (`results/processed/`) | Script (`scripts/`) |
|---|---|---|---|---|---|
| 1a | `1a_zero_queue_latency_working_set.png` | generated (restyled; data unchanged) | `1a_zero_queue_latency.csv` | `1a_zero_queue_latency_summary.csv` | `process_latency.py` |
| 1b | `1b_latency_by_working_set_region.png` | generated (labels corrected) | same as 1a | `1a_zero_queue_latency_summary.csv` | `plot_1b_memory_regions.py` |
| 2a | `2a_access_pattern_bandwidth.png` | generated (restyled; data unchanged) | `2_access_patterns.csv` | `2_access_patterns_summary.csv` | `plot_access_patterns.py` |
| 2b | `2b_access_pattern_elapsed_time.png` | generated (now elapsed time **per updated element**, IQR whiskers) | `2_access_patterns.csv` | computed in script from raw | `plot_access_patterns.py` |
| 3a | `3a_read_write_mix_throughput.png` | generated | `3_read_write_mix.csv` | `3_read_write_mix_summary.csv` | `analyze_3_read_write_mix.py` |
| 3b | `3b_read_write_mix_latency.png` | generated (time per operation, dependent reads) | `3_read_write_mix.csv` | `3_read_write_mix_summary.csv` | `analyze_3_read_write_mix.py` |
| 4a | `4a_concurrency_throughput_latency.png` | generated | `4_concurrency_sweep.csv`, `4_concurrency_sweep_extended.csv` | `4_concurrency_sweep_summary.csv` | `analyze_4_concurrency.py` |
| 4b | `4b_concurrency_knee_littles_law.png` | generated | same as 4a | `4_concurrency_sweep_summary.csv`, `4_concurrency_knee_test.csv` | `analyze_4_concurrency.py` |
| 5a | `5a_working_set_latency_regions.png` | generated | `5_working_set_sweep.csv` (+ 1a summary for comparison) | `5_working_set_summary.csv` | `analyze_5_working_set.py` |
| 5b | `5b_working_set_bandwidth.png` | generated | `5_working_set_bandwidth.csv` | `5_working_set_summary.csv` | `analyze_5_working_set.py` |
| 6a | `6a_cache_misses_vs_working_set.png` | **blocked**: needs hardware cache-miss counters (perf_event_open → EACCES) | – | – | – |
| 6a* | `6a_runtime_vs_far_access_fraction.png` | generated (timing-only substitute) | `6_far_access_fraction.csv` | `6_far_access_fraction_summary.csv` | `analyze_6_far_access.py` |
| 6b | `6b_runtime_vs_cache_misses.png` | **blocked**: needs measured miss counts | – | – | – |
| 6b* | `6b_inferred_far_access_cost.png` | generated (timing-only substitute) | `6_far_access_fraction.csv` (+ 5a summary as reference) | `6_cache_miss_impact_summary.csv`, `6_far_access_fits_per_trial.csv` | `analyze_6_far_access.py` |
| 7a | `7a_tlb_misses_vs_page_locality.png` | **blocked**: needs TLB-miss counters | – | – | – |
| 7a* | `7a_latency_vs_page_locality.png` | generated (timing-only substitute) | `7_tlb_impact.csv` (`experiment = 7a_page_locality`) | `7_tlb_impact_summary.csv` | `analyze_7_tlb.py` |
| 7b | `7b_runtime_vs_page_configuration.png` | generated (time, measured page faults, measured AnonHugePages) | `7_tlb_impact.csv` (`experiment = 7b_page_size`) | `7_tlb_impact_summary.csv` | `analyze_7_tlb.py` |
| 8a | `8a_cache_reuse_vs_large_working_set.png` | generated | `8_measurement_pitfall_passes.csv` | `8_measurement_pitfall_summary.csv` | `analyze_8_pitfall.py` |
| 8b | `8b_pinned_vs_unpinned_variability.png` | generated | `8_measurement_pitfall_pinning.csv` | `8_measurement_pitfall_summary.csv` | `analyze_8_pitfall.py` |

\* Filename mapping: the three counter-based plot names requested in the plan are **not** used
for timing data, so that a filename never claims a miss count that was not measured.
`6_far_access_fraction.csv` is the raw file for experiment 6 (planned name:
`6_cache_miss_impact.csv`); its fitted summary keeps the planned name
`6_cache_miss_impact_summary.csv`. Experiment 8's raw data is split into
`8_measurement_pitfall_passes.csv` (8a) and `8_measurement_pitfall_pinning.csv` (8b).

Count: 16 plots generated (13 under the planned names, 3 under honest substitute names);
3 planned counter-based plots blocked.

Note: `processed/8_measurement_pitfall_summary.csv` stacks the 8a rows (`experiment = 8a_passes`,
keyed by `ws_KiB`, `pass`) and the 8b rows (`experiment = 8b_pinning`, keyed by `span_KiB`,
`pinning`); each block leaves the other block's key/statistic columns empty (NaN = not
applicable, not missing data).
