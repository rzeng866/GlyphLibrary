# CLAUDE.md

Guidance for working in this repository. Read this at the start of a session.

## What this is

**glyphOcean** — a small data-visualization library for data scientists. It provides
plain functions that take a pandas `DataFrame` and return a matplotlib `Axes`,
all sharing one cohesive visual theme. The goal is meaningful, visually
appealing EDA plots with zero setup.

- Import name: `glyphOcean`
- Distribution name: `glyphOcean` (unlike the generic `glyph`, this name appears
  free on PyPI — verify before publishing).

## Architecture

`src/` layout — the installed package, not a top-level folder, is what tests
and users import.

```
src/glyphOcean/
├── __init__.py   # public API; calls set_theme() on import
├── theme.py      # the glyphOcean look: PALETTE, NEUTRAL, HIGHLIGHT (line accent), HIGHLIGHT_MUTED (fill accent), SEQUENTIAL, DIVERGING, set_theme(), color()
└── plots.py      # the five plotting functions (the whole public surface)
tests/            # pytest, Agg backend
examples/_data.py     # shared synthetic dataset
examples/gallery.py   # renders glyph_gallery.png (committed for the README)
```

The library is deliberately small: five plots plus a theme, and nothing else.
Data flow: **DataFrame → plot function → matplotlib `Axes`**. Presentation
(theme) is separated from plot logic; `plots.py` never hardcodes colors — it
pulls them from `theme`. `plots.py` is self-contained (only depends on
`theme`).

## Coding standards & libraries

- Python ≥ 3.9. Start modules with `from __future__ import annotations`.
- **Runtime dependencies are pandas, matplotlib, seaborn only.** Do not add a
  new runtime dependency without discussing it first.
- **Plain functions, no custom classes in the public API.** Return a matplotlib
  `Axes` (or a seaborn grid). Users must never have to learn a glyphOcean type.
- Function contract for every plot:
  - Signature `plot(df, <positional columns>, *, hue=None, ax=None)`.
  - Validate inputs with `_require_dataframe(df)` / `_check_columns(df, [...])`.
  - Accept `ax`; create one with `_new_ax()` when `None`.
  - Take colors from `theme`, never inline hex. Follow the palette discipline:
    a single-series chart uses `theme.NEUTRAL` for every mark, with the one datum
    worth noticing marked in `theme.HIGHLIGHT` (a line/outline) or highlighted as
    a fill via `_highlight_patch` (`theme.HIGHLIGHT_MUTED`); `theme.color(i)` (via
    `_series_colors`) is only for comparing groups (a `hue`); `theme.DIVERGING`
    for signed matrices.
  - Keep tick labels horizontal (no rotation); rely on horizontal-bar layouts
    for long category names.
  - Set the title via `_titled(ax, title)`, which applies proper title case
    automatically — pass a plain title, don't hand-capitalize.
  - Return the `Axes`.
- Keep the public API small; names are meaningful and boring
  (`distribution`, `counts`, `correlation`, `scatter`, `boxplot`).
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
- [ ] Title set via `_titled` (proper title case).
- [ ] Exported in `plots.__all__` **and** `glyphOcean/__init__.py` `__all__`.
- [ ] Test added covering the return type and at least one error path,
      on the Agg backend.
- [ ] README function table and, if the look changed, the committed gallery
      image updated.
- [ ] No new runtime dependency introduced.
- [ ] `pytest` is green.

## Data caveats

- Every function assumes a pandas `DataFrame`; anything else raises `TypeError`.
- `correlation()` needs **≥ 2 numeric columns**, else `ValueError`.
- Column typing is by pandas dtype — glyphOcean does not re-infer semantic types.
  A low-cardinality integer column is numeric here; pass the intended column to
  the categorical-oriented functions (`counts`, `boxplot` x-axis) yourself.
- Missing values: seaborn drops NaNs per plot.
- High-cardinality categoricals make `counts` unreadable — use `top=N`.
- **The theme is global.** `import glyphOcean` calls `set_theme()`, which mutates
  matplotlib `rcParams` for the whole process. Importing glyphOcean changes the
  styling of any other matplotlib plot in the same session.
- `distribution()` draws a median line and assumes the column is numeric.
