---
name: add-plot
description: Workflow for adding a new plotting function to the glyphOcean visualization library. Use when asked to add a new chart type or plot to glyphOcean (e.g. lineplot, heatmap, regression, barh), so the new function matches glyphOcean's conventions — theme colors, the (df, ..., ax=None) contract, exports, tests, gallery, and README.
---

# Add a new glyphOcean plot

Follow these steps in order to add a plotting function that matches the rest of
the library. The whole public surface lives in `src/glyphOcean/plots.py`; the look
lives in `src/glyphOcean/theme.py`.

## 1. Confirm the contract

Every plot function MUST:

- Have signature `name(df, <positional columns>, *, hue=None, ax=None)`.
- Call `_require_dataframe(df)` and `_check_columns(df, [...])` first.
- Use `ax = ax or _new_ax()` (pass `size=(w, h)` for non-default figure sizes).
- Take **all** colors from `theme`, never inline hex: `theme.NEUTRAL` for a
  single series, `theme.HIGHLIGHT` / `_highlight_patch` for the key datum,
  `_series_colors(df, hue, single)` when comparing groups, `theme.DIVERGING`
  for signed matrices.
- Set the title via `_titled(ax, title)` (it title-cases automatically).
- `return ax`.

Prefer a seaborn call (`sns.<plot>`) for the drawing, styled by the active
theme, over hand-rolled matplotlib.

## 2. Write the function

Add it to `src/glyphOcean/plots.py`. Copy the shape of the closest existing function:

- Single-series over a column → mirror `distribution` / `counts`.
- Relationship between columns → mirror `scatter` / `boxplot`.
- Whole-frame matrix → mirror `correlation`.

Raise `ValueError` for data that cannot support the plot (e.g. "needs ≥ 2
numeric columns"), matching `correlation()`.

## 3. Export it

Add the name to **both**:

- `__all__` in `src/glyphOcean/plots.py`
- the `from .plots import (...)` list and `__all__` in `src/glyphOcean/__init__.py`

Keep the lists alphabetized-ish and consistent with the existing entries.

## 4. Test it

Add tests to `tests/test_plots.py` (Agg backend is already configured there):

- returns a `plt.Axes`;
- honors any `top`/`hue`/option that changes structure (assert on
  `len(ax.patches)`, lines, etc.);
- raises on the documented error paths (`KeyError` unknown column,
  `TypeError` non-DataFrame, `ValueError` unsupported data);
- add the new name to `test_public_api`.

Run:

```bash
pytest -q
```

## 5. Document and preview

- Add a row to the **Functions** table in `README.md`.
- If the plot is broadly useful, add one call to `examples/gallery.py` and
  regenerate the preview:

  ```bash
  python examples/gallery.py   # rewrites glyph_gallery.png
  ```

  Then visually confirm the new panel looks consistent (palette, spines,
  labels). The gallery PNG is committed, so include it in the change.

## 6. Final check

Walk the review checklist in `CLAUDE.md` before committing. In particular:
no new runtime dependency, colors from the theme, and `pytest` green.
