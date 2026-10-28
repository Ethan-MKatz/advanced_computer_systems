"""Shared Matplotlib style and helpers for the cache-memory plots.

Error bars: median across trials with whiskers spanning the interquartile
range (IQR) unless a plot says otherwise.
"""

import textwrap
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "results" / "raw"
PROC = ROOT / "results" / "processed"
PLOTS = ROOT / "results" / "plots"

SURFACE, INK, INK2, MUTED, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#898781", "#e1e0d9"
BLUE, ORANGE, AQUA, YELLOW = "#2a78d6", "#eb6834", "#1baf7a", "#eda100"
SERIES = [BLUE, ORANGE, AQUA, YELLOW]
RAMP = ["#86b6ef", "#3987e5", "#1c5cab", "#0d366b"]

# Nominal capacities of the P-cores (CPUs 0-3) from sysfs. Reference marks only.
NOMINAL = [(48, "L1D 48 KiB"), (2048, "L2 2 MiB"), (12288, "L3 12 MiB")]

plt.rcParams.update({
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
    "axes.edgecolor": MUTED, "axes.labelcolor": INK, "text.color": INK,
    "xtick.color": INK2, "ytick.color": INK2, "axes.grid": True, "grid.color": GRID,
    "grid.linewidth": 0.6, "axes.axisbelow": True, "axes.spines.top": False,
    "axes.spines.right": False, "font.size": 10, "axes.titlesize": 11,
    "legend.frameon": False, "lines.linewidth": 2, "lines.markersize": 6,
    "figure.dpi": 110, "savefig.dpi": 160,
})


def iqr_summary(df, keys, col):
    """Median, q1, q3, min, max, n of `col` across trials for each key group."""
    g = df.groupby(keys)[col]
    out = pd.DataFrame({
        "median": g.median(), "q1": g.quantile(0.25), "q3": g.quantile(0.75),
        "min": g.min(), "max": g.max(), "n": g.size(),
    })
    return out.reset_index()


def yerr(a):
    return np.vstack([a["median"] - a["q1"], a["q3"] - a["median"]])


def title(fig, main, sub):
    """Bold title + wrapped secondary subtitle; reserves exactly the header height."""
    w_in, h_in = fig.get_size_inches()
    lines = [ln for para in sub.split("\n") for ln in textwrap.wrap(para, int(w_in * 14.8)) or [""]]
    fig.text(0.01, 1 - 0.12 / h_in, main, ha="left", va="top", fontsize=13, fontweight="bold")
    fig.text(0.01, 1 - 0.42 / h_in, "\n".join(lines), ha="left", va="top", fontsize=9,
             color=INK2, linespacing=1.35)
    fig._header_top = 1 - (0.55 + 0.19 * len(lines)) / h_in


def fig_legend(fig, ax=None, ncol=4, **kw):
    """One legend row for the whole figure, under the subtitle."""
    handles, labels = (ax or fig.axes[0]).get_legend_handles_labels()
    fig._fig_legend = dict(handles=handles, labels=labels, ncol=ncol, **kw)


def plain_log(ax, axis="y", base=10):
    from matplotlib.ticker import FuncFormatter, LogLocator, NullFormatter
    a = ax.yaxis if axis == "y" else ax.xaxis
    a.set_major_locator(LogLocator(base=base, subs=(1, 2, 5) if base == 10 else (1,)))
    a.set_major_formatter(FuncFormatter(lambda v, _: f"{v:g}"))
    a.set_minor_formatter(NullFormatter())


def kib_label(k):
    k = float(k)
    if k >= 1024 * 1024:
        return f"{k / 1024 / 1024:g} GiB"
    if k >= 1024:
        return f"{k / 1024:g} MiB"
    return f"{k:g} KiB"


def size_axis(ax, ticks_kib, label="Working-set size (log2 scale)"):
    ax.set_xscale("log", base=2)
    ax.set_xticks(ticks_kib, [kib_label(t) for t in ticks_kib], rotation=45, ha="right")
    ax.minorticks_off()
    ax.set_xlabel(label)


def nominal_marks(ax, text=True):
    """Dashed reference lines at nominal P-core cache capacities."""
    for kib, lab in NOMINAL:
        ax.axvline(kib, color=MUTED, ls="--", lw=1, zorder=0)
        if text:
            ax.text(kib * 1.06, 0.02, lab + "\n(nominal)", transform=ax.get_xaxis_transform(),
                    va="bottom", fontsize=7.5, color=INK2)


def save(fig, name):
    PLOTS.mkdir(parents=True, exist_ok=True)
    top = getattr(fig, "_header_top", 0.85)
    leg = getattr(fig, "_fig_legend", None)
    if leg:
        h_in = fig.get_size_inches()[1]
        rows = -(-len(leg["labels"]) // leg["ncol"])
        fig.legend(loc="upper left", bbox_to_anchor=(0.01, top), **leg)
        top -= (0.12 + 0.26 * rows) / h_in
    fig.tight_layout(rect=(0, 0, 1, top))
    fig.savefig(PLOTS / name)
    plt.close(fig)
    print("wrote", PLOTS / name)


def require(df, cols, expected_rows, name):
    """Validate columns and row count; raise loudly instead of silently plotting less."""
    missing = [c for c in cols if c not in df.columns]
    if missing:
        raise ValueError(f"{name}: missing columns {missing}")
    if len(df) != expected_rows:
        raise ValueError(f"{name}: expected {expected_rows} rows, found {len(df)}")
    if df[cols].isna().any().any():
        raise ValueError(f"{name}: NaN values in {cols}")
