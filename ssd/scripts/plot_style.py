"""Shared Matplotlib style, data loading, and helpers for the 14 SSD plots.

Error bars everywhere: whiskers span min..max across trials around the median
(n = 3 trials unless the plot says otherwise).
"""

import textwrap
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

SSD_DIR = Path(__file__).resolve().parents[1]
PROC = SSD_DIR / "results" / "processed"
PLOTS = SSD_DIR / "results" / "plots"

# validated reference palette (light surface)
SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK2 = "#52514e"
MUTED = "#898781"
GRID = "#e1e0d9"
BLUE, ORANGE, AQUA, YELLOW = "#2a78d6", "#eb6834", "#1baf7a", "#eda100"
# ordinal ramp for percentiles p50 < p95 < p99 < p99.9 (< p99.99)
PCT_RAMP = ["#86b6ef", "#3987e5", "#1c5cab", "#0d366b", "#06203f"]
PCTS = [("p50_us", "p50"), ("p95_us", "p95"), ("p99_us", "p99"), ("p99_9_us", "p99.9")]

plt.rcParams.update({
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
    "axes.edgecolor": MUTED, "axes.labelcolor": INK, "text.color": INK,
    "xtick.color": INK2, "ytick.color": INK2, "axes.grid": True, "grid.color": GRID,
    "grid.linewidth": 0.6, "axes.axisbelow": True, "axes.spines.top": False,
    "axes.spines.right": False, "font.size": 10, "axes.titlesize": 11,
    "legend.frameon": False, "lines.linewidth": 2, "lines.markersize": 7,
    "figure.dpi": 110, "savefig.dpi": 160,
})


def load_runs():
    df = pd.read_csv(PROC / "all_runs.csv")
    return df


def valid(df, experiment):
    """Valid rows of one experiment; raise loudly if any run of it failed."""
    sub = df[df["experiment"] == experiment]
    bad = sub[sub["valid"] != True]  # noqa: E712
    if len(bad):
        print(f"WARNING {experiment}: {bad['run_id'].nunique()} invalid run(s) excluded: "
              f"{sorted(bad['run_id'].unique())}")
    return sub[sub["valid"] == True].copy()  # noqa: E712


def agg(df, keys, col):
    """Median and min/max across trials -> DataFrame with med, lo, hi, n."""
    g = df.groupby(keys)[col]
    out = pd.DataFrame({"med": g.median(), "lo": g.min(), "hi": g.max(), "n": g.size()})
    return out.reset_index()


def yerr(a):
    return np.vstack([a["med"] - a["lo"], a["hi"] - a["med"]])


def title(fig, main, sub):
    """Bold title + wrapped secondary-ink subtitle; reserves exactly the header height."""
    w_in, h_in = fig.get_size_inches()
    width_chars = int(w_in * 14.8)
    lines = [ln for para in sub.split("\n") for ln in textwrap.wrap(para, width_chars) or [""]]
    fig.text(0.01, 1 - 0.12 / h_in, main, ha="left", va="top", fontsize=13,
             fontweight="bold")
    fig.text(0.01, 1 - 0.42 / h_in, "\n".join(lines), ha="left", va="top", fontsize=9,
             color=INK2, linespacing=1.35)
    fig._header_top = 1 - (0.55 + 0.19 * len(lines)) / h_in


def legend_above(ax, **kw):
    """Legend in a row just above the plot area (never over the data)."""
    kw.setdefault("ncol", 4)
    return ax.legend(loc="lower left", bbox_to_anchor=(0, 1.01), borderaxespad=0, **kw)


def fig_legend(fig, ax=None, ncol=4, **kw):
    """One legend row for the whole figure, placed under the subtitle (call after title)."""
    handles, labels = (ax or fig.axes[0]).get_legend_handles_labels()
    kw.update(handles=handles, labels=labels)
    fig._fig_legend = dict(ncol=ncol, **kw)


def plain_log(ax, axis="y"):
    """Log axis with plain-number tick labels (10, 20, 50, 100 ...) instead of 2x10^1."""
    from matplotlib.ticker import FuncFormatter, LogLocator, NullFormatter
    a = ax.yaxis if axis == "y" else ax.xaxis
    a.set_major_locator(LogLocator(base=10, subs=(1, 2, 5)))
    a.set_major_formatter(FuncFormatter(lambda v, _: f"{v:g}"))
    a.set_minor_formatter(NullFormatter())


def save(fig, name, top=None):
    PLOTS.mkdir(parents=True, exist_ok=True)
    top = getattr(fig, "_header_top", 0.85)
    h_in = fig.get_size_inches()[1]
    leg = getattr(fig, "_fig_legend", None)
    if leg:
        rows = -(-len(leg["labels"]) // leg["ncol"])
        fig.legend(loc="upper left", bbox_to_anchor=(0.01, top), **leg)
        top -= (0.12 + 0.26 * rows) / h_in
    fig.tight_layout(rect=(0, 0, 1, top))
    fig.savefig(PLOTS / name)
    plt.close(fig)
    print("wrote", PLOTS / name)


def kib(bs):
    """'128k' -> 128"""
    return int(str(bs).rstrip("kK"))


ERR_NOTE = "bars/points = median of 3 trials, whiskers = min..max"
