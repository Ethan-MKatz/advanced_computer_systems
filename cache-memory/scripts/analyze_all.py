#!/usr/bin/env python3
"""Regenerate every processed CSV and plot (experiments 1-8) from raw data."""
import runpy
import traceback
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPTS = ["process_latency.py", "plot_1b_memory_regions.py", "plot_access_patterns.py",
           "analyze_3_read_write_mix.py", "analyze_4_concurrency.py", "analyze_5_working_set.py",
           "analyze_6_far_access.py", "analyze_7_tlb.py", "analyze_8_pitfall.py"]
failed = []
for s in SCRIPTS:
    print(f"=== {s}")
    try:
        runpy.run_path(str(HERE / s), run_name="__main__")
    except Exception:
        traceback.print_exc()
        failed.append(s)
print("FAILED:" if failed else "all analysis scripts completed", *failed)
