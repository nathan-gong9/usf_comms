# Palette

The color system is the point of the library. It is built from two hue
families defined once at the top of `src/plumage/__init__.py`.

![Palette](../reports/figures/palette.png)

## Primary — purple

A single-hue sequential ramp, `PURPLE[100]` (lightest) → `PURPLE[700]`
(darkest). It supplies the lead categorical slot, the default `image.cmap`
(`plumage_purple`), and the headline series in every chart.

```python
import plumage as pl
pl.PRIMARY            # "#8352bf"
pl.sequential(5)      # 5 evenly spaced purples
```

## Secondary — muted brown

A parallel single-hue ramp, `BROWN[100]` → `BROWN[700]`. It supplies the
supporting series, the `plumage_brown` colormap, and the warm pole of the
diverging map.

```python
pl.SECONDARY               # "#b0895a"
pl.sequential(5, "brown")  # 5 evenly spaced browns
```

## Categorical

Eight fixed slots, purple-led and interleaved with browns so that
*neighbouring* series come from different hue families and stay easy to tell
apart. Slots are assigned in order and **never cycled** — a ninth series folds
into "Other" or becomes small multiples.

```python
pl.categorical()      # all 8
pl.categorical(3)     # first 3
pl.categorical(9)     # ValueError — don't invent a hue
```

## Diverging

`plumage_diverging` runs purple → cream → brown: two families that read as
opposites, meeting at a warm neutral midpoint that reads as "nothing." Use it
for signed data such as correlations.

```python
pl.correlation(df)                      # centered on zero automatically
pl.heatmap(matrix, diverging=True)      # same map, any matrix
```

## House rules

- Color follows identity, in fixed order; never re-color survivors when a
  filter changes the series count.
- One soft y-grid behind the data; no top/right spines; muted axis ink.
- Selective direct labels instead of a number on every mark.
- A legend appears only for two or more series.
