"""Small synthetic datasets for demos, docs, and the figure gallery.

Everything here is generated deterministically with a fixed seed so the
gallery and docs render identically on every machine — no files in ``data/``
required to try the library out.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

_MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
           "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def monthly_channels(seed: int = 7) -> pd.DataFrame:
    """Monthly signal across three channels (for line/area charts)."""
    rng = np.random.default_rng(seed)
    base = {
        "Organic": np.linspace(40, 95, 12) + rng.normal(0, 4, 12),
        "Referral": np.linspace(30, 55, 12) + rng.normal(0, 4, 12),
        "Paid": np.linspace(20, 70, 12) + rng.normal(0, 5, 12),
    }
    return pd.DataFrame(base, index=_MONTHS).clip(lower=0).round(1)


def category_totals(seed: int = 3) -> pd.Series:
    """Totals per category (for a single-series bar chart)."""
    rng = np.random.default_rng(seed)
    cats = ["Mobile", "Desktop", "Tablet", "Kiosk", "Embedded"]
    vals = rng.integers(120, 900, size=len(cats))
    return pd.Series(sorted(vals, reverse=True), index=cats, name="sessions")


def region_quarters(seed: int = 11) -> pd.DataFrame:
    """Region x quarter matrix (for grouped bars)."""
    rng = np.random.default_rng(seed)
    quarters = ["Q1", "Q2", "Q3", "Q4"]
    regions = ["North", "South", "West"]
    data = {r: rng.integers(40, 160, size=len(quarters)) for r in regions}
    return pd.DataFrame(data, index=quarters)


def measurements(seed: int = 19, n: int = 260) -> pd.DataFrame:
    """Numeric table with a categorical group (for scatter/correlation)."""
    rng = np.random.default_rng(seed)
    group = rng.choice(["alpha", "beta", "gamma"], size=n, p=[0.45, 0.35, 0.20])
    shift = {"alpha": 0.0, "beta": 2.2, "gamma": -1.6}
    x = rng.normal(0, 1, n) + np.array([shift[g] for g in group])
    y = 1.4 * x + rng.normal(0, 1.1, n)
    z = -0.7 * x + rng.normal(0, 1.3, n)
    w = 0.5 * y + 0.5 * z + rng.normal(0, 0.9, n)
    return pd.DataFrame({"x": x, "y": y, "z": z, "w": w, "group": group})


__all__ = [
    "monthly_channels", "category_totals", "region_quarters", "measurements",
]
