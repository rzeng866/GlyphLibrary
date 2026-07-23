# CLAUDE.md

Guidance for working in this repository. Read this at the start of a session.

## What this is

**Glyph** — a small data-visualization library for data scientists. It provides
plain functions that take a pandas `DataFrame` and return a matplotlib `Axes`,
all sharing one cohesive visual theme. The goal is meaningful, visually
appealing EDA plots with zero setup.

- Import name: `glyph`
- Distribution name: `glyph` (note: this name is taken on PyPI — publishing
  would need a distinct dist name while keeping `import glyph`).

## Architecture

`src/` layout — the installed package, not a top-level folder, is what tests
and users import.

```
src/glyph/
├── __init__.py   # public API; calls set_theme() on import
├── theme.py      # the Glyph look: PALETTE, SEQUENTIAL, DIVERGING, set_theme(), color()
└── plots.py      # the plotting functions (the whole public surface)
tests/            # pytest, Agg backend
examples/gallery.py  # renders glyph_gallery.png (committed for the README preview)
```

Data flow: **DataFrame → plot function → matplotlib `Axes`** (`pairplot` returns
a seaborn `PairGrid`). Presentation (theme) is separated from the plot logic;
`plots.py` never hardcodes colors — it pulls them from `theme`.

## Coding standards & libraries

- Python ≥ 3.9. Start modules with `from __future__ import annotations`.
- **Runtime dependencies are pandas, matplotlib, seaborn only.** Do not add a
  new runtime dependency without discussing it first.
- **Plain functions, no custom classes in the public API.** Return a matplotlib
  `Axes` (or a seaborn grid). Users must never have to learn a Glyph type.
- Function contract for every plot:
  - Signature `plot(df, <positional columns>, *, <keyword-only options>, ax=None)`.
  - Validate inputs with `_require_dataframe(df)` / `_check_columns(df, [...])`.
  - Accept `ax`; create one with `_new_ax()` when `None`.
  - Set a title and axis labels.
  - Take colors from `theme` (`theme.color(i)`, `theme.PALETTE`,
    `theme.SEQUENTIAL`, `theme.DIVERGING`) — never inline hex in `plots.py`.
  - Return the `Axes`.
- Keep the public API small; names are meaningful and boring
  (`distribution`, `counts`, `correlation`, `scatter`, `boxplot`, `missing`,
  `pairplot`).
- Match the surrounding style: snake_case, keyword-only options, concise
  docstrings that state what the plot shows.

## Key commands

```bash
pip install -e ".[dev]"      # install with dev extras (pytest)
pytest                        # run the test suite (headless / Agg)
python examples/gallery.py    # regenerate glyph_gallery.png
```

## Review checklist

Before committing a change to the plotting surface:

- [ ] Public function returns an `Axes` (or a documented seaborn grid), not a
      custom object.
- [ ] Colors come from `theme`, not inline hex.
- [ ] Input validation present (DataFrame check + columns exist).
- [ ] `ax=` parameter supported and honored.
- [ ] Title and axis labels set.
- [ ] Exported in `plots.__all__` **and** `glyph/__init__.py` `__all__`.
- [ ] Test added covering the return type and at least one error path,
      on the Agg backend.
- [ ] README function table and, if the look changed, the committed gallery
      image updated.
- [ ] No new runtime dependency introduced.
- [ ] `pytest` is green.

## Data caveats

- Every function assumes a pandas `DataFrame`; anything else raises `TypeError`.
- `correlation()` and `pairplot()` need **≥ 2 numeric columns**, else
  `ValueError`.
- Column typing is by pandas dtype — Glyph does not re-infer semantic types.
  A low-cardinality integer column is numeric here; pass the intended column to
  the categorical-oriented functions (`counts`, `boxplot` x-axis) yourself.
- Missing values: seaborn drops NaNs per plot. `missing()` reports the NaN
  share per column and shows only columns with > 0 missing.
- High-cardinality categoricals make `counts` unreadable — use `top=N`.
- **The theme is global.** `import glyph` calls `set_theme()`, which mutates
  matplotlib `rcParams` for the whole process. Importing Glyph changes the
  styling of any other matplotlib plot in the same session.
- `distribution()` draws a median line and assumes the column is numeric.
