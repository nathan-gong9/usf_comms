"""Smoke + contract tests for the plumage library.

Run from the repo root with ``pytest`` (the pytest config in pyproject puts
``src`` on the path, so no install is required). Everything renders on the
non-interactive Agg backend, so the suite is headless and fast.
"""
import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pytest

import plumage as pl


@pytest.fixture(autouse=True)
def _theme():
    """Apply the theme once per test and always close figures afterwards."""
    pl.use_theme()
    yield
    plt.close("all")


# --- palette / color -------------------------------------------------- #
def test_version_and_primaries():
    assert pl.__version__
    assert pl.PRIMARY == pl.EMERALD[600]
    assert pl.SECONDARY == pl.ESPRESSO[500]


def test_colormaps_registered():
    for name in ("plumage_emerald", "plumage_espresso", "plumage_diverging"):
        assert name in plt.colormaps()


def test_categorical_slots():
    assert len(pl.categorical()) == 8
    assert pl.categorical(3) == pl.CATEGORICAL[:3]
    assert len(pl.CATEGORICAL) == len(pl.CATEGORICAL_NAMES)


def test_categorical_overflow_raises():
    with pytest.raises(ValueError):
        pl.categorical(9)


@pytest.mark.parametrize("family", ["emerald", "espresso"])
def test_sequential(family):
    colors = pl.sequential(5, family)
    assert len(colors) == 5
    assert all(c.startswith("#") for c in colors)
    assert len(pl.sequential(1, family)) == 1


def test_shade_lighten_darken_and_clamp():
    base = pl.PRIMARY
    assert pl.shade(base, 0.0) == matplotlib.colors.to_hex(base)
    assert pl.shade(base, 0.5).startswith("#")
    assert pl.shade(base, -0.5).startswith("#")
    # out-of-range amounts clamp rather than error
    assert pl.shade(base, 5) == pl.shade(base, 1)
    assert pl.shade(base, -5) == pl.shade(base, -1)


# --- charts ----------------------------------------------------------- #
def test_bar_and_grouped_bar():
    assert pl.bar(["a", "b", "c"], [3, 1, 2], title="t").has_data()
    rq = pl.datasets.region_quarters()
    ax = pl.grouped_bar(rq.index, {c: rq[c] for c in rq.columns})
    assert len(ax.patches) == rq.size


def test_line_and_area_accept_pandas():
    mc = pl.datasets.monthly_channels()
    series = {c: mc[c] for c in mc.columns}
    assert pl.line(mc.index, series, title="t").has_data()      # pandas Series -> no KeyError
    assert pl.area(mc.index, series, stacked=True).has_data()


def test_scatter_grouped_and_plain():
    m = pl.datasets.measurements()
    assert pl.scatter(m["x"], m["y"]).has_data()
    assert pl.scatter(m["x"], m["y"], groups=m["group"]).get_legend() is not None


def test_histogram():
    ax = pl.histogram(pl.datasets.measurements()["y"], bins=20)
    assert len(ax.patches) == 20


def test_heatmap_sequential_and_labels():
    grid = np.array([[0.1, 0.5], [0.9, 0.3]])
    ax = pl.heatmap(grid, annotate=True, fmt="{:.0%}")
    assert ax.images  # an AxesImage was drawn


def test_heatmap_diverging_centers_on_zero():
    m = np.array([[-2.0, 0.0], [1.0, 2.0]])
    ax = pl.heatmap(m, diverging=True)
    im = ax.images[0]
    assert im.norm.vmin == -im.norm.vmax


def test_heatmap_masks_nan_without_error():
    m = np.array([[0.2, np.nan], [0.8, 0.5]])
    ax = pl.heatmap(m, annotate=True)          # NaN cell must be skipped, not "nan"
    texts = [t.get_text() for t in ax.texts]
    assert "nan" not in texts and "0.20" in texts


def test_correlation_needs_two_numeric_columns():
    df = pd.DataFrame({"a": [1, 2, 3], "b": [3, 2, 1], "label": ["x", "y", "z"]})
    assert pl.correlation(df).images
    with pytest.raises(ValueError):
        pl.correlation(df[["a", "label"]])
