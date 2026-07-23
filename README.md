# EDALibrary

Exploratory data analysis for pandas DataFrames — rendered to a clean, shareable **PDF report**.

Point it at a DataFrame and get back an immutable profile you can inspect
programmatically or render to a multi-page PDF: dataset overview, per-column
statistics, distributions, missingness, and correlations.

```python
import pandas as pd
import edalibrary as eda

df = pd.read_csv("customers.csv")
report = eda.profile(df)

print(report.summary())          # quick terminal overview
report.to_pdf("report.pdf")      # full PDF report
```

## Install

```bash
pip install -e .
```

Dependencies are pure-Python-installable — `pandas`, `numpy`, `matplotlib`,
and `reportlab`. No system libraries required (no cairo/pango), so the PDF
output works the same on your laptop, a server, or CI.

## What's in the report

- **Dataset overview** — rows, columns, duplicate rows, missing-cell rate.
- **Column-type breakdown** — semantic classification of every column.
- **Missing values** — per-column missingness chart.
- **Correlations** — Pearson heatmap and the strongest numeric pairs.
- **Per-column detail** — statistics table plus a distribution chart
  (histogram for numeric, bar chart for categorical).

## Semantic types

The library infers how each column should be *analyzed*, not just how it's
stored. A column of small integers is treated as an encoded category; a
mostly-unique string column is flagged as an identifier rather than free text.

| Type          | Example                                  |
|---------------|------------------------------------------|
| `NUMERIC`     | continuous measurements                  |
| `CATEGORICAL` | low-cardinality labels or encoded codes  |
| `BOOLEAN`     | true/false flags                         |
| `DATETIME`    | timestamps                               |
| `TEXT`        | high-cardinality free text               |
| `UNIQUE`      | identifiers (near-unique per row)        |
| `CONSTANT`    | a single repeated value                  |
| `EMPTY`       | all values missing                       |

## Design

The library separates three concerns so each can evolve independently:

```
compute (analysis/)  →  model (core/)  →  present (report/)
```

- **`core/`** — semantic type inference and immutable result objects
  (`Profile`, `ColumnProfile`). Results hold no live reference to the source
  DataFrame, so they're cheap to pass around and serialize.
- **`analysis/`** — pure computation. Statistics, missingness, correlations,
  and precomputed histogram bins.
- **`report/`** — presentation only. Text summaries, matplotlib charts, and
  the reportlab PDF assembler. Rendering never recomputes analysis.

## Programmatic access

Everything in the PDF is available on the `Profile` object:

```python
report = eda.profile(df)

report.n_rows, report.n_columns, report.n_missing_cells
report.type_counts()               # {SemanticType.NUMERIC: 3, ...}

col = report["age"]                # a ColumnProfile
col.semantic_type                  # SemanticType.NUMERIC
col.missing_pct                    # 5.2
col.numeric.median, col.numeric.iqr

report.correlations                # pandas DataFrame or None
```

## Try it

```bash
python examples/generate_sample_report.py
```

Builds a synthetic customer dataset and writes `sample_report.pdf`.

## Development

```bash
pip install -e ".[dev]"
pytest
```
