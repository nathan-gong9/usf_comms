"""Render the example gallery into ``reports/figures/``.

Run from the project root::

    python -m plumage.gallery

Each figure exercises one chart helper on a synthetic dataset so the palette
and theme can be eyeballed end to end. These PNGs are what the README shows.
The palette *card* (``swatches``) lives here rather than in the core library —
it's a reporting utility, not a chart primitive.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

import plumage as pl


def swatches(ax=None, figsize=(8, 3.4)):
    """Render the full plumage palette as labelled swatches (a palette card)."""
    if ax is None:
        _, ax = plt.subplots(figsize=figsize)
    ax.set_axis_off()

    def row(y, colors, names, heading):
        ax.text(-0.4, y + 0.55, heading, color=pl.INK_SOFT, fontweight="bold",
                fontsize=plt.rcParams["legend.fontsize"])
        for i, (c, name) in enumerate(zip(colors, names)):
            ax.add_patch(plt.Rectangle((i, y), 0.9, 0.9, facecolor=c,
                                       edgecolor=pl.SURFACE, linewidth=2))
            ax.text(i + 0.45, y - 0.22, name, ha="center", va="top",
                    color=pl.INK_SOFT, fontsize=8)

    steps = [str(k) for k in sorted(pl.PURPLE)]
    row(4.0, pl.CATEGORICAL, pl.CATEGORICAL_NAMES, "Categorical")
    row(2.0, [pl.PURPLE[k] for k in sorted(pl.PURPLE)], steps, "Purple (primary)")
    row(0.0, [pl.BROWN[k] for k in sorted(pl.BROWN)], steps, "Brown (secondary)")
    ax.set_xlim(-0.6, len(pl.CATEGORICAL) + 0.2)
    ax.set_ylim(-0.6, 5.4)
    ax.set_aspect("equal")
    return ax


def _figures_dir() -> Path:
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "reports" / "figures").exists():
            return parent / "reports" / "figures"
    out = here.parents[2] / "reports" / "figures"
    out.mkdir(parents=True, exist_ok=True)
    return out


def render_all(outdir: Path | None = None) -> list[Path]:
    pl.use_theme()
    outdir = Path(outdir) if outdir else _figures_dir()
    outdir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []

    def save(ax, name: str):
        ax.figure.savefig(outdir / name)
        plt.close(ax.figure)
        written.append(outdir / name)

    mc = pl.datasets.monthly_channels()
    rq = pl.datasets.region_quarters()
    tot = pl.datasets.category_totals()
    m = pl.datasets.measurements()

    save(swatches(), "palette.png")
    save(pl.bar(tot.index, tot.values, horizontal=True, title="Sessions by device",
                xlabel="Sessions"), "bar.png")
    save(pl.grouped_bar(rq.index, {c: rq[c] for c in rq.columns},
                        title="Revenue by region", ylabel="Index"), "grouped_bar.png")
    save(pl.line(mc.index, {c: mc[c] for c in mc.columns},
                 title="Monthly sessions", ylabel="Thousands"), "line.png")
    save(pl.area(mc.index, {c: mc[c] for c in mc.columns},
                 title="Composition over time", ylabel="Thousands"), "area.png")
    save(pl.scatter(m["x"], m["y"], groups=m["group"], title="y vs x",
                    xlabel="x", ylabel="y"), "scatter.png")
    save(pl.histogram(m["y"], bins=32, title="Distribution of y"), "histogram.png")
    save(pl.correlation(m, title="Correlation"), "correlation.png")
    grid = np.random.default_rng(5).random((6, 8)) ** 1.4
    save(pl.heatmap(grid, annotate=False, cbar_label="intensity",
                    title="Sequential heatmap"), "heatmap.png")
    return written


if __name__ == "__main__":
    paths = render_all()
    print(f"Wrote {len(paths)} figures:")
    for p in paths:
        print(f"  {p}")
