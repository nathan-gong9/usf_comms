"""Mike Trout's 2023 swing rate by pitch type x zone bucket.

A worked example that exercises the plumage library on a real Statcast dataset
(one row per pitch Trout saw in 2023). It computes his swing rate in each
pitch-type x zone-bucket cell and renders it as a sequential-purple heatmap.

Usage::

    python reports/trout_swing_rate.py [path/to/trout_2023.csv]

Defaults to ``data/raw/trout_2023.csv``. Writes
``reports/figures/trout_swing_rate.png`` and a tidy
``reports/trout_swing_rate_summary.csv``.
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import plumage as pl

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CSV = ROOT / "data" / "raw" / "trout_2023.csv"
MIN_CELL = 15   # hide swing rate for cells with fewer than this many pitches

# Statcast zones -> vertical buckets (1-9 in-zone grid, 11-14 chase quadrants).
ZONE_BUCKET = {11: "Chase up", 12: "Chase up", 1: "Up", 2: "Up", 3: "Up",
               4: "Middle", 5: "Middle", 6: "Middle", 7: "Low", 8: "Low",
               9: "Low", 13: "Chase low", 14: "Chase low"}
BUCKET_ORDER = ["Chase up", "Up", "Middle", "Low", "Chase low"]  # top -> bottom
PITCH_LABEL = {"FF": "4-Seam", "SI": "Sinker", "FC": "Cutter", "SL": "Slider",
               "ST": "Sweeper", "CU": "Curve", "CH": "Change", "KC": "Knuckle-C",
               "FS": "Splitter", "SV": "Slurve", "CS": "Slow Curve"}


def load(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, low_memory=False)
    df = df.dropna(subset=["pitch_type", "zone", "swing"]).copy()
    df["bucket"] = df["zone"].astype(int).map(ZONE_BUCKET)
    df = df.dropna(subset=["bucket"])
    # Keep pitch types with >= 100 pitches; fold the rest into "Other".
    counts = df["pitch_type"].value_counts()
    keep = counts[counts >= 100].index
    df["pitch"] = np.where(df["pitch_type"].isin(keep),
                           df["pitch_type"].map(PITCH_LABEL), "Other")
    order = [PITCH_LABEL[t] for t in counts.index if t in keep] + ["Other"]
    df["pitch"] = pd.Categorical(df["pitch"], categories=order, ordered=True)
    return df


def swing_rate_matrix(df: pd.DataFrame):
    rate = df.pivot_table("swing", "pitch", "bucket", aggfunc="mean", observed=True)
    n = df.pivot_table("swing", "pitch", "bucket", aggfunc="size", observed=True)
    rate, n = rate.reindex(columns=BUCKET_ORDER), n.reindex(columns=BUCKET_ORDER)
    return rate.mask(n < MIN_CELL), n


def main(path: Path) -> None:
    if not path.exists():
        sys.exit(f"CSV not found: {path}\nPass the path: python {Path(__file__).name} <csv>")
    df = load(path)
    rate, n = swing_rate_matrix(df)
    overall = df["swing"].mean()

    pl.use_theme()
    ax = pl.heatmap(rate, cmap="plumage_purple", fmt="{:.0%}",
                    cbar_label="Swing rate", figsize=(7.6, 5.6))
    ax.set_xlabel("Zone bucket (top of strike zone → bottom)")
    ax.set_ylabel("Pitch type")
    # Two-line header stacked above the plot so it never overlaps the grid.
    ax.annotate("Mike Trout — 2023 swing rate", xy=(0, 1.0),
                xycoords="axes fraction", xytext=(0, 40), textcoords="offset points",
                color=pl.INK, fontweight="bold",
                fontsize=plt.rcParams["axes.titlesize"], va="bottom")
    ax.annotate(f"{len(df):,} pitches · overall swing rate {overall:.0%} · "
                f"cells with < {MIN_CELL} pitches left blank",
                xy=(0, 1.0), xycoords="axes fraction", xytext=(0, 20),
                textcoords="offset points", color=pl.INK_SOFT, va="bottom",
                fontsize=plt.rcParams["legend.fontsize"])

    fig_out = ROOT / "reports" / "figures" / "trout_swing_rate.png"
    ax.figure.savefig(fig_out)
    summary = (rate.round(3).stack().rename("swing_rate").reset_index()
               .merge(n.stack().rename("pitches").reset_index()))
    csv_out = ROOT / "reports" / "trout_swing_rate_summary.csv"
    summary.to_csv(csv_out, index=False)
    print(f"overall swing rate: {overall:.1%}  ({len(df):,} pitches)")
    print(f"wrote {fig_out.relative_to(ROOT)} and {csv_out.relative_to(ROOT)}")


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_CSV)
