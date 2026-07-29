# Palette

The color system is the point of the library. It is built from two hue
families defined once at the top of `src/plumage/__init__.py`, on a warm paper
surface with serif titles over a clean sans.

![Palette](../reports/figures/palette.png)

## Primary — emerald

A single-hue sequential ramp, `EMERALD[100]` (lightest) → `EMERALD[700]`
(darkest). It supplies the lead categorical slot, the default `image.cmap`
(`plumage_emerald`), and the headline series in every chart.

```python
import plumage as pl
pl.PRIMARY            # "#107a55"
pl.sequential(5)      # 5 evenly spaced emeralds
```

## Secondary — espresso

A parallel single-hue ramp, `ESPRESSO[100]` → `ESPRESSO[700]`. It supplies the
supporting series, the `plumage_espresso` colormap, and the warm pole of the
diverging map.

```python
pl.SECONDARY                  # "#7a583a"
pl.sequential(5, "espresso")  # 5 evenly spaced espressos
```

## Categorical

Eight fixed slots, emerald-led and interleaved with espressos so that
*neighbouring* series come from different hue families and stay easy to tell
apart. Slots are assigned in order and **never cycled** — a ninth series folds
into "Other" or becomes small multiples.

```python
pl.categorical()      # all 8
pl.categorical(3)     # first 3
pl.categorical(9)     # ValueError — don't invent a hue
```

## Diverging

`plumage_diverging` runs emerald → cream → espresso: two families that read as
opposites, meeting at a warm neutral midpoint that reads as "nothing." Use it
for signed data such as correlations.

```python
pl.correlation(df)                      # centered on zero automatically
pl.heatmap(matrix, diverging=True)      # same map, any matrix
```

## Type & chrome

- Titles are set in a **serif** (Liberation Serif → DejaVu Serif → Georgia →
  Times), left-aligned and bold, for an editorial headline feel.
- Axis labels, ticks, legends, and annotations use a clean **sans** (Liberation
  Sans → Helvetica → Arial → DejaVu Sans).
- The surface is a warm paper cream; ink is a soft espresso-black.

## House rules

- Color follows identity, in fixed order; never re-color survivors when a
  filter changes the series count.
- One soft y-grid behind the data; no top/right spines; muted axis ink.
- Selective direct labels instead of a number on every mark.
- A legend appears only for two or more series.
