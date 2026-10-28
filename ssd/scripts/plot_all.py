#!/usr/bin/env python3
"""Generate all 14 plots from results/processed/ (run parse_results.py first)."""
import traceback

import plot_exp1
import plot_exp2
import plot_exp3
import plot_exp4
import plot_exp5
import plot_exp6
import plot_exp7

failed = []
for mod in (plot_exp1, plot_exp2, plot_exp3, plot_exp4, plot_exp5, plot_exp6, plot_exp7):
    try:
        mod.main()
    except Exception:  # report, never silently skip
        traceback.print_exc()
        failed.append(mod.__name__)
print("FAILED:" if failed else "all plot scripts completed", *failed)
