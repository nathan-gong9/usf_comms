# eda

A tiny exploratory data analysis (EDA) library. Data wrangling uses
pandas/numpy; **every visualization is drawn with matplotlib only** — no
seaborn or other plotting backends. The whole thing is a single ~170-line
module.

## Install

```bash
pip install -r requirements.txt
```

## Quick start

```python
import pandas as pd
from eda import EDA

df = pd.read_csv("data.csv")
report = EDA(df)

report.overview()      # shape, dtypes, missing %, unique counts
report.describe()      # numeric summary stats
report.missing()       # columns with missing values, worst first
report.plot_all()      # histograms, boxplots, bar charts, correlation heatmap
```

## API

| Method | Description |
| --- | --- |
| `overview()` | Print dataset shape/memory and return a per-column summary frame. |
| `describe()` | Descriptive statistics for numeric columns. |
| `missing()` | Columns containing missing values, sorted worst first. |
| `plot_histograms(bins=30)` | Histogram per numeric column. |
| `plot_boxplots()` | Boxplot per numeric column (spread and outliers). |
| `plot_bars(top=10)` | Bar chart of top values per categorical column. |
| `plot_correlation()` | Correlation heatmap for numeric columns. |
| `plot_scatter(x, y, hue=None)` | Scatter of two numeric columns, optionally colored by `hue`. |
| `plot_all(show=True)` | Render every applicable diagnostic plot. |

Each `plot_*` method returns the matplotlib `Figure`, so you can further
customize or save it with `fig.savefig(...)`.
