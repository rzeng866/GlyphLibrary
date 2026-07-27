# Glyph

Meaningful, visually appealing plots for data scientists — built on
seaborn/matplotlib.

Glyph is a small set of plain functions for the plots you actually reach for
during exploratory data analysis. Each one takes a pandas DataFrame and
returns a matplotlib `Axes`, so you can keep customizing with the API you
already know. A cohesive theme is applied automatically, so plots look good
with zero setup.

```python
import pandas as pd
import glyph

df = pd.read_csv("data.csv")

glyph.distribution(df, "age")
glyph.correlation(df)
glyph.scatter(df, "spend", "satisfaction", hue="region")
```

## Built for user & content metadata

Glyph covers the questions you ask of metadata, each with a readable,
comparison-friendly plot:

| Question | Function(s) |
|---|---|
| Understanding a single **categorical** field | `counts` |
| Understanding a **numeric** field | `distribution`, `boxplot` |
| **Relationships** between fields | `scatter`, `correlation`, `pairplot` |
| **Temporal** metadata (trends over time) | `timeseries` |

## Install

```bash
pip install -e .
```

Dependencies: **pandas**, **matplotlib**, **seaborn**.

## Functions

Every function returns a matplotlib `Axes` (except `pairplot`, which returns a
seaborn `PairGrid`). Pass `ax=` to draw into your own subplot.

| Function | What it shows |
|---|---|
| `distribution(df, column, hue=None)` | Histogram + KDE, with a median line |
| `counts(df, column, top=None)`       | Ordered, labelled bar chart of category frequencies |
| `correlation(df, method="pearson")`  | Annotated correlation heatmap (upper triangle masked) |
| `scatter(df, x, y, hue=None, size=None)` | Relationship between two numeric columns |
| `boxplot(df, x, y, hue=None)`         | A numeric distribution compared across categories |
| `timeseries(df, time, value=None, freq="MS", agg="mean", hue=None)` | A metric (or record count) over time, resampled; `hue` compares groups |
| `missing(df)`                         | % missing per column, worst first |
| `pairplot(df, hue=None, columns=None)`| Grid of pairwise relationships (corner layout) |

### Example

```python
import pandas as pd, glyph

df = pd.DataFrame({
    "region": ["N", "S", "N", "E", "S", "N"],
    "spend":  [70, 55, 82, 60, 48, 75],
    "score":  [8.1, 5.5, 9.0, 6.2, 4.8, 7.7],
})

ax = glyph.boxplot(df, "region", "spend")
ax.set_ylabel("monthly spend ($)")   # it's just a matplotlib Axes
ax.figure.savefig("spend_by_region.png")
```

## Theme

The Glyph look — a modern palette, light gridlines, clean spines, confident
titles — is applied on import. Reapply or adjust it with `set_theme`:

```python
glyph.set_theme(context="talk")   # larger fonts for slides
glyph.set_theme(grid=False)       # drop the gridlines
glyph.PALETTE                     # the qualitative color list
glyph.color(2)                    # one palette color by index
```

## Gallery

```bash
python examples/gallery.py   # writes glyph_gallery.png
```

![Glyph gallery](glyph_gallery.png)

## Development

```bash
pip install -e ".[dev]"
pytest
```

## Project layout

```
GlyphLibrary/
├── src/
│   └── glyph/
│       ├── __init__.py
│       ├── theme.py     # the Glyph look
│       └── plots.py     # the plotting functions
├── examples/gallery.py
├── tests/test_plots.py
├── README.md
├── pyproject.toml
└── LICENSE
```
