"""A tiny exploratory data analysis (EDA) library.

Data wrangling uses pandas/numpy; every visualization is drawn with
matplotlib only (no seaborn or other plotting backends). Charts use a
muted natural palette of browns, beiges, and neutrals, with minimal,
well-labeled styling.

Usage:
    from eda import EDA
    report = EDA(df)           # df is a pandas DataFrame
    report.overview()          # printed summary
    report.plot_all()          # grid of diagnostic plots
"""

from __future__ import annotations

import math

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap

# --- Muted natural palette: browns, beiges, neutrals ------------------- #
INK = "#463f36"        # soft dark brown for text and lines
BG = "#f4efe6"         # warm cream background
GRID = "#e0d8c8"       # pale beige gridlines
PRIMARY = "#8a6f52"    # walnut brown (main series)
SERIES = ["#8a6f52", "#b79b74", "#a7a17d", "#7c7a63", "#cbb894", "#9c7f63"]
# Diverging map for correlations: walnut -> cream -> muted sage
CORR_CMAP = LinearSegmentedColormap.from_list("naturals", ["#8a6f52", "#f4efe6", "#7c8168"])


def _apply_theme() -> None:
    """Set matplotlib rcParams for a minimal, natural look."""
    plt.rcParams.update({
        "figure.facecolor": BG, "axes.facecolor": BG, "savefig.facecolor": BG,
        "axes.edgecolor": GRID, "axes.linewidth": 0.8, "axes.axisbelow": True,
        "axes.grid": False, "axes.spines.top": False, "axes.spines.right": False,
        "grid.color": GRID, "grid.linewidth": 0.7, "text.color": INK,
        "axes.labelcolor": INK, "axes.titlecolor": INK, "xtick.color": INK,
        "ytick.color": INK, "axes.titlesize": 11, "axes.titleweight": "bold",
        "font.size": 9.5, "figure.titlesize": 14, "figure.titleweight": "bold",
    })


_apply_theme()


class EDA:
    """Lightweight exploratory data analysis over a pandas DataFrame."""

    def __init__(self, df: pd.DataFrame):
        if not isinstance(df, pd.DataFrame):
            raise TypeError("EDA expects a pandas DataFrame.")
        self.df = df
        self.numeric = df.select_dtypes(include="number").columns.tolist()
        self.categorical = [c for c in df.columns if c not in self.numeric]

    def overview(self) -> pd.DataFrame:
        """Print shape/dtype info and return a per-column summary frame."""
        rows, cols = self.df.shape
        mem = self.df.memory_usage(deep=True).sum() / 1024 ** 2
        print(f"Rows: {rows:,}   Columns: {cols}   Memory: {mem:.2f} MB")
        print(f"Numeric: {len(self.numeric)}   Categorical: {len(self.categorical)}")
        summary = pd.DataFrame({
            "dtype": self.df.dtypes.astype(str),
            "missing": self.df.isna().sum(),
            "missing_%": (self.df.isna().mean() * 100).round(2),
            "unique": self.df.nunique(),
        })
        print("\n" + summary.to_string())
        return summary

    def describe(self) -> pd.DataFrame:
        """Return descriptive statistics for numeric columns."""
        if not self.numeric:
            print("No numeric columns to describe.")
            return pd.DataFrame()
        return self.df[self.numeric].describe().T

    def missing(self) -> pd.DataFrame:
        """Return columns that contain missing values, sorted worst first."""
        miss = self.df.isna().sum()
        miss = miss[miss > 0].sort_values(ascending=False)
        return pd.DataFrame({"missing": miss, "percent": (miss / len(self.df) * 100).round(2)})

    @staticmethod
    def _grid(n: int, ncols: int = 3, size: float = 4.0):
        """Create a right-sized subplot grid and return (fig, flat_axes)."""
        ncols = min(ncols, max(n, 1))
        nrows = math.ceil(n / ncols)
        fig, axes = plt.subplots(nrows, ncols, figsize=(size * ncols, size * nrows))
        axes = np.atleast_1d(axes).ravel()
        for ax in axes[n:]:
            ax.set_visible(False)
        return fig, axes

    def plot_histograms(self, bins: int = 30):
        """Histogram for every numeric column."""
        if not self.numeric:
            return None
        fig, axes = self._grid(len(self.numeric))
        for ax, col in zip(axes, self.numeric):
            ax.hist(self.df[col].dropna(), bins=bins, color=PRIMARY, edgecolor=BG, linewidth=0.5)
            ax.set_title(col)
            ax.set_ylabel("Count")
            ax.grid(axis="y")
        fig.suptitle("Distributions", y=1.0)
        fig.tight_layout()
        return fig

    def plot_boxplots(self):
        """Boxplot for every numeric column (spot outliers and spread)."""
        if not self.numeric:
            return None
        fig, axes = self._grid(len(self.numeric))
        for ax, col in zip(axes, self.numeric):
            ax.boxplot(
                self.df[col].dropna(), vert=True, widths=0.5, patch_artist=True,
                boxprops=dict(facecolor=SERIES[1], edgecolor=INK),
                medianprops=dict(color=INK, linewidth=1.4),
                whiskerprops=dict(color=INK), capprops=dict(color=INK),
                flierprops=dict(marker="o", markersize=3, markerfacecolor=PRIMARY,
                                markeredgecolor="none", alpha=0.5))
            ax.set_title(col)
            ax.set_xticks([])
            ax.grid(axis="y")
        fig.suptitle("Spread & outliers", y=1.0)
        fig.tight_layout()
        return fig

    def plot_bars(self, top: int = 10):
        """Bar chart of the most frequent values per categorical column."""
        cats = [c for c in self.categorical if self.df[c].nunique() <= 50]
        if not cats:
            return None
        fig, axes = self._grid(len(cats))
        for ax, col in zip(axes, cats):
            counts = self.df[col].value_counts().head(top)
            ax.barh(counts.index.astype(str)[::-1], counts.values[::-1], color=PRIMARY)
            ax.set_title(col)
            ax.set_xlabel("Count")
            ax.grid(axis="x")
        fig.suptitle(f"Top {top} categories", y=1.0)
        fig.tight_layout()
        return fig

    def plot_correlation(self):
        """Correlation heatmap for numeric columns."""
        if len(self.numeric) < 2:
            return None
        corr = self.df[self.numeric].corr()
        n = len(corr)
        fig, ax = plt.subplots(figsize=(1.2 + n, 1.2 + n))
        im = ax.imshow(corr, cmap=CORR_CMAP, vmin=-1, vmax=1)
        ax.set_xticks(range(n), corr.columns, rotation=45, ha="right")
        ax.set_yticks(range(n), corr.columns)
        ax.tick_params(length=0)
        for i in range(n):
            for j in range(n):
                ax.text(j, i, f"{corr.iloc[i, j]:.2f}", ha="center", va="center",
                        color=INK, fontsize=8)
        cbar = fig.colorbar(im, ax=ax, shrink=0.75, label="Correlation")
        cbar.outline.set_edgecolor(GRID)
        ax.set_title("Correlation")
        fig.tight_layout()
        return fig

    def plot_scatter(self, x: str, y: str, hue: str | None = None):
        """Scatter plot of two numeric columns, optionally colored by `hue`."""
        for col in (x, y):
            if col not in self.numeric:
                raise ValueError(f"{col!r} is not a numeric column.")
        fig, ax = plt.subplots(figsize=(6, 5))
        if hue and hue in self.df.columns:
            for i, (label, grp) in enumerate(self.df.groupby(hue)):
                ax.scatter(grp[x], grp[y], label=str(label), s=22, alpha=0.8,
                           color=SERIES[i % len(SERIES)], edgecolor="none")
            ax.legend(title=hue, frameon=False, fontsize=8)
        else:
            ax.scatter(self.df[x], self.df[y], s=22, alpha=0.8, color=PRIMARY, edgecolor="none")
        ax.set_xlabel(x)
        ax.set_ylabel(y)
        ax.set_title(f"{y} vs {x}")
        ax.grid(True)
        fig.tight_layout()
        return fig

    def plot_all(self, show: bool = True):
        """Render every applicable diagnostic plot; return the figures."""
        figs = [f for f in (self.plot_histograms(), self.plot_boxplots(),
                            self.plot_bars(), self.plot_correlation()) if f]
        if show:
            plt.show()
        return figs


__all__ = ["EDA"]
