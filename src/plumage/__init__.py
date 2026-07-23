"""plumage — a compact matplotlib data-visualization library.

Purple is the *primary* hue family (headline series, lead categorical slot,
default sequential ramp); muted brown is the *secondary* family (supporting
series, alternate ramp, warm pole of the purple<->brown diverging map). Drawn
with matplotlib only. Chart helpers return the Axes so results compose with
matplotlib. House rules: one hue per series in fixed order (never cycled), a
legend only for >= 2 series, selective direct labels, recessive chrome.

    >>> import plumage as pl; pl.use_theme()
    >>> df = pl.datasets.monthly_channels()
    >>> pl.line(df.index, {c: df[c] for c in df.columns}, title="Sessions")
"""
from __future__ import annotations

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from cycler import cycler
from matplotlib.colors import LinearSegmentedColormap, to_hex, to_rgb

from . import datasets  # noqa: F401  (re-exported convenience)

__version__ = "0.1.0"

# Ink & surface (warm, near-neutral chrome).
INK, INK_SOFT = "#2e2838", "#6a6276"
SURFACE, GRID, AXIS = "#faf8f5", "#e7e1da", "#cfc7bd"

# Sequential ramps, light->dark (steps 100..700): purple primary, brown secondary.
PURPLE = {100: "#f2ecfa", 200: "#dccbf0", 300: "#c0a4e3", 400: "#a179d3",
          500: "#8352bf", 600: "#67399e", 700: "#4a2775"}
BROWN = {100: "#f2ebe2", 200: "#e0d0bb", 300: "#caac82", 400: "#b0895a",
         500: "#916a43", 600: "#6f4f33", 700: "#4d3623"}
PRIMARY, SECONDARY = PURPLE[500], BROWN[400]

# Categorical: purple-led, interleaved with browns so neighbours differ.
CATEGORICAL = ["#5b3a8c", "#b0895a", "#9575cd", "#6f4f33",
               "#7e4f9e", "#caac82", "#3f2266", "#916a43"]
CATEGORICAL_NAMES = ["amethyst", "sienna", "lavender", "umber",
                     "orchid", "fawn", "indigo", "walnut"]
DIVERGING_STOPS = [PURPLE[700], PURPLE[400], "#f4efe6", BROWN[400], BROWN[700]]


def _ramp(name, steps):
    return LinearSegmentedColormap.from_list(name, [steps[k] for k in sorted(steps)])

PURPLE_CMAP = _ramp("plumage_purple", PURPLE)
BROWN_CMAP = _ramp("plumage_brown", BROWN)
DIVERGING_CMAP = LinearSegmentedColormap.from_list("plumage_diverging", DIVERGING_STOPS)
_CMAPS = {"plumage_purple": PURPLE_CMAP, "plumage_purple_r": PURPLE_CMAP.reversed(),
          "plumage_brown": BROWN_CMAP, "plumage_brown_r": BROWN_CMAP.reversed(),
          "plumage_diverging": DIVERGING_CMAP, "plumage_diverging_r": DIVERGING_CMAP.reversed()}


def register_colormaps():
    """Register the plumage colormaps with matplotlib (idempotent)."""
    for name, cmap in _CMAPS.items():
        mpl.colormaps.register(cmap, name=name, force=True)


def categorical(n=None):
    """First ``n`` categorical slots (max 8; fold extras into 'Other')."""
    if n is None:
        return list(CATEGORICAL)
    if n > len(CATEGORICAL):
        raise ValueError(f"{len(CATEGORICAL)} categorical slots; asked for {n}")
    return CATEGORICAL[:n]


def sequential(n, family="purple"):
    """``n`` evenly spaced colors sampled from the purple or brown ramp."""
    cmap = {"purple": PURPLE_CMAP, "brown": BROWN_CMAP}[family]
    return [to_hex(cmap(0.6))] if n == 1 else [to_hex(cmap(i / (n - 1))) for i in range(n)]


def shade(color, amount):
    """Lighten (``amount`` > 0) or darken (``amount`` < 0) a hex color."""
    a = max(-1.0, min(1.0, amount))
    r, g, b = to_rgb(color)
    r, g, b = ((c + (1 - c) * a for c in (r, g, b)) if a >= 0
               else (c * (1 + a) for c in (r, g, b)))
    return to_hex((r, g, b))


def use_theme(base=10.5):
    """Apply the plumage look globally via rcParams (idempotent)."""
    register_colormaps()
    plt.rcParams.update({
        "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
        "savefig.bbox": "tight", "savefig.dpi": 150, "figure.dpi": 110,
        "figure.constrained_layout.use": True,
        "axes.edgecolor": AXIS, "axes.linewidth": 1.0, "axes.axisbelow": True,
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.grid": True, "axes.grid.axis": "y", "grid.color": GRID, "grid.linewidth": 0.8,
        "axes.prop_cycle": cycler(color=CATEGORICAL), "image.cmap": "plumage_purple",
        "patch.edgecolor": SURFACE, "patch.force_edgecolor": True,
        "text.color": INK, "axes.labelcolor": INK, "axes.titlecolor": INK,
        "xtick.color": INK_SOFT, "ytick.color": INK_SOFT,
        "xtick.labelcolor": INK_SOFT, "ytick.labelcolor": INK_SOFT,
        "xtick.major.size": 0.0, "ytick.major.size": 0.0,
        "font.family": "sans-serif", "font.size": base,
        "axes.titlesize": base + 3, "axes.titleweight": "bold", "axes.titlelocation": "left",
        "axes.titlepad": 12, "axes.labelsize": base, "legend.fontsize": base - 1,
        "figure.titlesize": base + 6, "figure.titleweight": "bold",
        "legend.frameon": False, "lines.linewidth": 2.2, "lines.solid_capstyle": "round",
    })


def _ax(ax, figsize):
    if ax is None:
        _, ax = plt.subplots(figsize=figsize)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(AXIS)
    ax.tick_params(length=0)
    ax.set_axisbelow(True)
    return ax


def _done(ax, title=None, xlabel=None, ylabel=None):
    """Set optional axis labels + left-aligned title, then return the Axes."""
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if title:
        ax.set_title(title)
    return ax


def _legend(ax, n):
    if n > 1:
        ax.legend(ncol=min(n, 4), loc="upper left", bbox_to_anchor=(0, 1.02))


def bar(labels, values, *, ax=None, color=None, horizontal=False,
        title=None, xlabel=None, ylabel=None, figsize=(7, 4.4)):
    """Single-series bar chart; nominal bars share one hue (length is the value)."""
    ax = _ax(ax, figsize)
    pos = np.arange(len(labels))
    if horizontal:
        b = ax.barh(pos, values, color=color or CATEGORICAL[0], height=0.72, zorder=3)
        ax.set_yticks(pos, labels), ax.invert_yaxis()
        ax.grid(axis="x"), ax.grid(axis="y", visible=False)
    else:
        b = ax.bar(pos, values, color=color or CATEGORICAL[0], width=0.72, zorder=3)
        ax.set_xticks(pos, labels)
    ax.bar_label(b, fmt=lambda v: f"{v:,.0f}", padding=3, color=INK,
                 fontsize=plt.rcParams["legend.fontsize"])
    return _done(ax, title, xlabel, ylabel)


def grouped_bar(labels, series, *, ax=None, title=None, xlabel=None,
                ylabel=None, figsize=(8, 4.6)):
    """Clustered bars: one color per named series, in fixed palette order."""
    ax = _ax(ax, figsize)
    names, pos = list(series), np.arange(len(labels))
    colors, width = categorical(len(list(series))), 0.8 / max(len(series), 1)
    for i, name in enumerate(names):
        ax.bar(pos + (i - (len(names) - 1) / 2) * width, series[name],
               width=width * 0.92, color=colors[i], label=name, zorder=3)
    ax.set_xticks(pos, labels)
    _legend(ax, len(names))
    return _done(ax, title, xlabel, ylabel)


def line(x, series, *, ax=None, markers=False, label_ends=True,
         title=None, xlabel=None, ylabel=None, figsize=(8, 4.6)):
    """Line chart, one color per series, with optional direct end-labels."""
    ax = _ax(ax, figsize)
    names, x, colors = list(series), list(x), categorical(len(list(series)))
    for i, name in enumerate(names):
        y = np.asarray(series[name], dtype=float)
        ax.plot(x, y, color=colors[i], label=name, marker="o" if markers else None,
                markersize=5, markeredgecolor=SURFACE, markeredgewidth=1.0, zorder=3)
        if label_ends and len(y):
            ax.annotate(name, (x[-1], y[-1]), (8, 0), textcoords="offset points",
                        va="center", color=colors[i], fontweight="bold",
                        fontsize=plt.rcParams["legend.fontsize"])
    ax.margins(x=0.08) if label_ends else _legend(ax, len(names))
    ax.grid(axis="x", visible=False)
    return _done(ax, title, xlabel, ylabel)


def area(x, series, *, ax=None, stacked=True, title=None, xlabel=None,
         ylabel=None, figsize=(8, 4.6)):
    """Stacked (default) or overlaid area chart, with a 2px surface gap."""
    ax = _ax(ax, figsize)
    names, colors = list(series), categorical(len(list(series)))
    if stacked:
        ax.stackplot(x, [series[n] for n in names], labels=names, colors=colors,
                     edgecolor=SURFACE, linewidth=1.5, zorder=3)
    else:
        for i, name in enumerate(names):
            ax.fill_between(x, series[name], color=colors[i], alpha=0.28, zorder=2)
            ax.plot(x, series[name], color=colors[i], label=name, zorder=3)
    _legend(ax, len(names))
    ax.margins(x=0), ax.grid(axis="x", visible=False)
    return _done(ax, title, xlabel, ylabel)


def scatter(x, y, *, groups=None, ax=None, size=34, title=None,
            xlabel=None, ylabel=None, figsize=(6.4, 5.2)):
    """Scatter plot, optionally colored by a categorical ``groups`` array."""
    ax = _ax(ax, figsize)
    x, y = np.asarray(x), np.asarray(y)
    if groups is None:
        ax.scatter(x, y, s=size, color=CATEGORICAL[0], alpha=0.85,
                   edgecolor=SURFACE, linewidth=0.6, zorder=3)
    else:
        groups = np.asarray(groups)
        labels = list(dict.fromkeys(groups))
        for label, color in zip(labels, categorical(len(labels))):
            m = groups == label
            ax.scatter(x[m], y[m], s=size, color=color, alpha=0.85, label=str(label),
                       edgecolor=SURFACE, linewidth=0.6, zorder=3)
        if len(labels) > 1:
            ax.legend(loc="best")
    ax.grid(axis="x")
    return _done(ax, title, xlabel, ylabel)


def histogram(values, *, bins=30, ax=None, color=None, title=None,
              xlabel=None, ylabel="Count", figsize=(7, 4.4)):
    """Single-series histogram in the primary purple."""
    ax = _ax(ax, figsize)
    ax.hist(np.asarray(values), bins=bins, color=color or PRIMARY,
            edgecolor=SURFACE, linewidth=0.7, zorder=3)
    return _done(ax, title, xlabel, ylabel)


def heatmap(matrix, *, row_labels=None, col_labels=None, ax=None,
            cmap="plumage_purple", diverging=False, annotate=True,
            fmt="{:.2f}", cbar_label=None, title=None, figsize=(6.5, 5.4)):
    """Heatmap for a 2-D array or DataFrame; ``diverging=True`` centers on zero."""
    ax = _ax(ax, figsize)
    ax.grid(False)
    m = np.asarray(getattr(matrix, "values", matrix), dtype=float)
    lim = float(np.nanmax(np.abs(m))) if diverging else None
    im = ax.imshow(m, cmap="plumage_diverging" if diverging else cmap,
                   vmin=-lim if diverging else None, vmax=lim, aspect="auto")
    rows = row_labels if row_labels is not None else list(getattr(matrix, "index", []))
    cols = col_labels if col_labels is not None else list(getattr(matrix, "columns", []))
    if len(cols):
        ax.set_xticks(range(m.shape[1]), cols, rotation=40, ha="right")
    if len(rows):
        ax.set_yticks(range(m.shape[0]), rows)
    ax.tick_params(length=0)
    if annotate:
        for i in range(m.shape[0]):
            for j in range(m.shape[1]):  # label color from cell luminance
                r, g, b, _ = im.cmap(im.norm(m[i, j]))
                txt = INK if 0.299 * r + 0.587 * g + 0.114 * b > 0.6 else SURFACE
                ax.text(j, i, fmt.format(m[i, j]), ha="center", va="center",
                        color=txt, fontsize=plt.rcParams["legend.fontsize"])
    cbar = ax.figure.colorbar(im, ax=ax, shrink=0.82, pad=0.02)
    cbar.outline.set_edgecolor(GRID), cbar.ax.tick_params(length=0, colors=INK_SOFT)
    if cbar_label:
        cbar.set_label(cbar_label, color=INK_SOFT)
    return _done(ax, title)


def correlation(df, *, ax=None, title="Correlation", figsize=(6.5, 5.6)):
    """Diverging correlation heatmap for a DataFrame's numeric columns."""
    corr = df.select_dtypes(include="number").corr()
    if corr.shape[1] < 2:
        raise ValueError("need at least two numeric columns")
    return heatmap(corr, ax=ax, diverging=True, cbar_label="Pearson r",
                   title=title, figsize=figsize)
