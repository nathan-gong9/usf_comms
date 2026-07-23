"""A tiny exploratory data analysis (EDA) library.

Data wrangling uses pandas/numpy; every visualization is drawn with
matplotlib only (no seaborn or other plotting backends).

Usage:
    import pandas as pd
    from eda import EDA

    df = pd.read_csv("data.csv")
    report = EDA(df)
    report.overview()          # printed summary
    report.plot_all()          # grid of diagnostic plots
"""

from __future__ import annotations

import math

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


class EDA:
    """Lightweight exploratory data analysis over a pandas DataFrame."""

    def __init__(self, df: pd.DataFrame):
        if not isinstance(df, pd.DataFrame):
            raise TypeError("EDA expects a pandas DataFrame.")
        self.df = df
        self.numeric = df.select_dtypes(include="number").columns.tolist()
        self.categorical = [c for c in df.columns if c not in self.numeric]

    # ------------------------------------------------------------------ #
    # Text summaries
    # ------------------------------------------------------------------ #
    def overview(self) -> pd.DataFrame:
        """Print shape/dtype info and return a per-column summary frame."""
        rows, cols = self.df.shape
        mem = self.df.memory_usage(deep=True).sum() / 1024 ** 2
        print(f"Rows: {rows:,}   Columns: {cols}   Memory: {mem:.2f} MB")
        print(f"Numeric: {len(self.numeric)}   Categorical: {len(self.categorical)}")

        summary = pd.DataFrame(
            {
                "dtype": self.df.dtypes.astype(str),
                "missing": self.df.isna().sum(),
                "missing_%": (self.df.isna().mean() * 100).round(2),
                "unique": self.df.nunique(),
            }
        )
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

    # ------------------------------------------------------------------ #
    # Plot helpers
    # ------------------------------------------------------------------ #
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
            data = self.df[col].dropna()
            ax.hist(data, bins=bins, color="#4c72b0", edgecolor="white")
            ax.set_title(col)
            ax.set_ylabel("count")
        fig.suptitle("Numeric distributions", fontsize=14)
        fig.tight_layout()
        return fig

    def plot_boxplots(self):
        """Boxplot for every numeric column (spot outliers and spread)."""
        if not self.numeric:
            return None
        fig, axes = self._grid(len(self.numeric))
        for ax, col in zip(axes, self.numeric):
            ax.boxplot(self.df[col].dropna(), vert=True, patch_artist=True,
                       boxprops=dict(facecolor="#dd8452"))
            ax.set_title(col)
            ax.set_xticks([])
        fig.suptitle("Boxplots", fontsize=14)
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
            ax.barh(counts.index.astype(str)[::-1], counts.values[::-1], color="#55a868")
            ax.set_title(col)
            ax.set_xlabel("count")
        fig.suptitle("Categorical frequencies", fontsize=14)
        fig.tight_layout()
        return fig

    def plot_correlation(self):
        """Correlation heatmap for numeric columns."""
        if len(self.numeric) < 2:
            return None
        corr = self.df[self.numeric].corr()
        fig, ax = plt.subplots(figsize=(1 + len(corr), 1 + len(corr)))
        im = ax.imshow(corr, cmap="coolwarm", vmin=-1, vmax=1)
        ax.set_xticks(range(len(corr)))
        ax.set_yticks(range(len(corr)))
        ax.set_xticklabels(corr.columns, rotation=45, ha="right")
        ax.set_yticklabels(corr.columns)
        for i in range(len(corr)):
            for j in range(len(corr)):
                ax.text(j, i, f"{corr.iloc[i, j]:.2f}", ha="center", va="center",
                        color="black", fontsize=8)
        fig.colorbar(im, ax=ax, shrink=0.8)
        ax.set_title("Correlation matrix")
        fig.tight_layout()
        return fig

    def plot_scatter(self, x: str, y: str, hue: str | None = None):
        """Scatter plot of two numeric columns, optionally colored by `hue`."""
        for col in (x, y):
            if col not in self.numeric:
                raise ValueError(f"{col!r} is not a numeric column.")
        fig, ax = plt.subplots(figsize=(6, 5))
        if hue and hue in self.df.columns:
            for label, grp in self.df.groupby(hue):
                ax.scatter(grp[x], grp[y], label=str(label), alpha=0.7, s=20)
            ax.legend(title=hue, fontsize=8)
        else:
            ax.scatter(self.df[x], self.df[y], alpha=0.7, s=20, color="#4c72b0")
        ax.set_xlabel(x)
        ax.set_ylabel(y)
        ax.set_title(f"{y} vs {x}")
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
