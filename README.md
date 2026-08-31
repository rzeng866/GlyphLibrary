# glyphOcean

Meaningful, visually appealing plots for data scientists — built on
seaborn/matplotlib.

glyphOcean is a small set of plain functions for the plots you reach for during
exploratory data analysis. Each one takes a pandas DataFrame and returns a
matplotlib `Axes`, so you can keep customizing with the API you already know. A
cohesive theme is applied automatically, so plots look good with zero setup.

```python
import pandas as pd
import glyphOcean as gl          # the recommended alias, like `import numpy as np`

df = pd.read_csv("data.csv")

gl.distribution(df, "age")
gl.correlation(df)
gl.scatter(df, "spend", "satisfaction", hue="region")
```

## Install

```bash
pip install -e .
```

Dependencies: **pandas**, **matplotlib**, **seaborn**.

## Functions

Five plain functions, each answering one common EDA question. Every function
returns a matplotlib `Axes`; pass `ax=` to draw into your own subplot.

| Function | EDA question | What it shows |
|---|---|---|
| `distribution(df, column, hue=None)` | Understand a **numeric** field | Histogram + KDE, median marked |
| `counts(df, column, top=None)` | Understand a **categorical** field | Ordered, labelled bar chart; top bar highlighted |
| `correlation(df)` | **Relationships** across fields | Heatmap of correlations (upper triangle hidden) |
| `scatter(df, x, y, hue=None)` | **Relationship** between two fields | Points, colored by an optional category |
| `boxplot(df, x, y, hue=None)` | Compare a numeric field **across groups** | Boxes per category; highest-median box highlighted |

### Example

```python
import pandas as pd
import glyphOcean as gl

df = pd.DataFrame({
    "region": ["N", "S", "N", "E", "S", "N"],
    "spend":  [70, 55, 82, 60, 48, 75],
    "score":  [8.1, 5.5, 9.0, 6.2, 4.8, 7.7],
})

ax = gl.boxplot(df, "region", "spend")
ax.set_ylabel("monthly spend ($)")   # it's just a matplotlib Axes
ax.figure.savefig("spend_by_region.png")
```

## Theme

The glyphOcean look is applied on import: a clean sans-serif stack, a bold-title /
faint-tick hierarchy, light spines, no background gridlines, and plenty of white
space.
The palette is **ocean-themed** — shades of blue, green, and coral (with a
teal→coral diverging map for correlations). Its color discipline is deliberate:
single-series charts are drawn in one **neutral** blue with a single **highlight**
on the datum that matters — the biggest category, the median line, the
highest-median box. The multi-color palette is reserved for comparing groups
(`hue`), where each category gets a distinct color.

```python
gl.set_theme(context="talk")   # larger fonts for slides
gl.set_theme(grid=True)        # add light horizontal gridlines back
gl.PALETTE                     # the qualitative palette (used for `hue`)
gl.color(2)                    # one palette color by index
```

## Gallery

```bash
python examples/gallery.py   # writes glyph_gallery.png
```

![glyphOcean gallery](glyph_gallery.png)

## Development

```bash
pip install -e ".[dev]"
pytest
```

## Project layout

```
glyphOcean/
├── src/
│   └── glyphOcean/
│       ├── __init__.py   # public API; applies the theme on import
│       ├── theme.py      # the glyphOcean look: palette, colors, set_theme()
│       └── plots.py      # the five plotting functions
├── examples/
│   ├── _data.py          # shared synthetic dataset
│   └── gallery.py        # renders glyph_gallery.png
├── tests/
├── README.md
├── pyproject.toml
└── LICENSE
```
