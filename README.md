# edalibrary

Small, plain-function exploratory data analysis for pandas DataFrames.

Two boring, useful functions. Each takes a DataFrame and returns a plain
pandas object — there are no custom classes to learn.

```python
import pandas as pd
from edalibrary import summarize, missing

df = pd.read_csv("data.csv")

summarize(df)   # per-column overview
missing(df)     # missing values per column
```

## Install

```bash
pip install -e .
```

The only dependency is **pandas**.

## Functions

### `summarize(df)`

One row per column with dtype, non-null count, missing count and percent,
number of unique values, and basic numeric stats (`mean`, `std`, `min`,
`max` — `NaN` for non-numeric columns). Returns a `DataFrame`.

```python
>>> df = pd.DataFrame({"a": [1, 2, None], "b": ["x", "x", "y"]})
>>> summarize(df)[["count", "missing", "unique", "mean", "min", "max"]]
   count  missing  unique  mean  min  max
a      2        1       2   1.5  1.0  2.0
b      3        0       2   NaN  NaN  NaN
```

### `missing(df)`

Missing-value count and percentage per column, most-missing first. Returns
a `DataFrame`.

```python
>>> df = pd.DataFrame({"a": [1, None, None], "b": [1, 2, 3]})
>>> missing(df)
   missing  percent
a        2    66.67
b        0     0.00
```

## Try it

```bash
python examples/quickstart.py
```

## Development

```bash
pip install -e ".[dev]"
pytest
```

## Project layout

```
EDALibrary/
├── src/
│   └── edalibrary/
│       ├── __init__.py
│       └── core.py
├── examples/
├── tests/
├── README.md
├── pyproject.toml
└── LICENSE
```
