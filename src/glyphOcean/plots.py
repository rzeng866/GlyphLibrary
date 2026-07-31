"""glyphOcean plotting functions.

Every function follows the same shape, so once you read one you can read them
all:

    1. Validate the input      -> _check_columns / _require_dataframe
    2. Get an Axes to draw on    -> the caller's `ax`, or a fresh one
    3. Draw with seaborn, taking colors from `theme` (never hard-coded)
    4. Mark the key point        -> highlight a bar, the median line, ...
    5. Add a title, and return the Axes

Each function takes a pandas ``DataFrame`` and returns a matplotlib ``Axes``,
so you can keep customizing the result with the matplotlib/seaborn API you
already know. Colors and fonts live in ``theme.py``; this file only draws.
"""

from __future__ import annotations

from typing import Optional

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from . import theme

__all__ = ["distribution", "counts", "correlation", "scatter", "boxplot"]


def distribution(
    df: pd.DataFrame, column: str, *, hue: Optional[str] = None, ax: Optional[plt.Axes] = None
) -> plt.Axes:
    """Histogram with a KDE curve for a numeric column; the median is marked.

    Pass ``hue`` to split the distribution by a categorical column.
    """
    _check_columns(df, [column] + ([hue] if hue else []))
    ax = ax or _new_ax()

    sns.histplot(
        data=df, x=column, hue=hue, kde=True,
        edgecolor="white", linewidth=0.5, alpha=0.9, ax=ax,
        **_series_colors(df, hue, theme.NEUTRAL),
    )

    # For a single series, mark the median with a bright vertical line.
    if hue is None:
        median = df[column].median()
        ax.axvline(median, color=theme.HIGHLIGHT, linestyle="--", linewidth=1.5)
        ax.text(
            median, ax.get_ylim()[1] * 0.96, f"  median {median:.4g}",
            color=theme.HIGHLIGHT, fontsize=9, fontweight="bold", va="top",
        )

    _titled(ax, f"Distribution of {column}")
    return ax


def counts(
    df: pd.DataFrame, column: str, *, top: Optional[int] = None, ax: Optional[plt.Axes] = None
) -> plt.Axes:
    """Horizontal bar chart of category counts; the most frequent bar is highlighted.

    Pass ``top`` to show only the N most frequent values.
    """
    _check_columns(df, [column])

    frequencies = df[column].value_counts()  # already sorted, most frequent first
    if top is not None:
        frequencies = frequencies.head(top)

    ax = ax or _new_ax()
    sns.barplot(
        x=frequencies.values, y=frequencies.index.astype(str),
        color=theme.NEUTRAL, saturation=1, ax=ax,
    )
    _highlight_patch(ax, 0)  # the first (most frequent) bar
    _label_bars(ax, frequencies.values)
    ax.margins(x=0.12)
    ax.grid(False, axis="y")
    ax.set_xlabel("count")
    ax.set_ylabel(column)

    title = f"Counts of {column}"
    if top is not None:
        title += f" (top {top})"
    _titled(ax, title)
    return ax


def correlation(df: pd.DataFrame, *, ax: Optional[plt.Axes] = None) -> plt.Axes:
    """Heatmap of Pearson correlations between numeric columns.

    The upper triangle is hidden to reduce clutter and the strongest pair is
    outlined. Raises ``ValueError`` if there are fewer than two numeric columns.
    """
    _require_dataframe(df)
    numeric = df.select_dtypes("number")
    if numeric.shape[1] < 2:
        raise ValueError("correlation() needs at least two numeric columns.")

    corr = numeric.corr()
    upper_triangle = np.triu(np.ones_like(corr, dtype=bool), k=1)  # the hidden half

    n_cols = len(corr.columns)
    ax = ax or _new_ax(size=(1.1 * n_cols + 2, 1.0 * n_cols + 1.5))
    sns.heatmap(
        corr, mask=upper_triangle, cmap=theme.DIVERGING, vmin=-1, vmax=1, center=0,
        annot=True, fmt=".2f", annot_kws={"size": 9},
        linewidths=0.5, linecolor="white", square=True,
        cbar_kws={"shrink": 0.75, "label": "pearson r"}, ax=ax,
    )

    # Outline the strongest pair's cell in the bright highlight color.
    cell = _strongest_cell(corr)
    if cell is not None:
        row, col = cell
        ax.add_patch(mpatches.Rectangle(
            (col, row), 1, 1, fill=False, edgecolor=theme.HIGHLIGHT, linewidth=2.5, zorder=5,
        ))

    _titled(ax, "Correlation")
    ax.grid(False)
    ax.tick_params(rotation=0)  # keep labels horizontal
    return ax


def scatter(
    df: pd.DataFrame, x: str, y: str, *, hue: Optional[str] = None, ax: Optional[plt.Axes] = None
) -> plt.Axes:
    """Scatter plot of ``y`` against ``x``, optionally colored by a category."""
    _check_columns(df, [x, y] + ([hue] if hue else []))
    ax = ax or _new_ax(size=(7, 6))

    sns.scatterplot(
        data=df, x=x, y=y, hue=hue,
        alpha=0.75, edgecolor="white", linewidth=0.4, ax=ax,
        **_series_colors(df, hue, theme.color(0)),
    )

    _titled(ax, f"{y} vs {x}")
    return ax


def boxplot(
    df: pd.DataFrame, x: str, y: str, *, hue: Optional[str] = None, ax: Optional[plt.Axes] = None
) -> plt.Axes:
    """Box plot of numeric ``y`` grouped by categorical ``x``.

    Good for comparing a numeric distribution across categories; the category
    with the highest median is highlighted.
    """
    _check_columns(df, [x, y] + ([hue] if hue else []))
    ax = ax or _new_ax()

    # With no hue we fix the order so we can highlight the highest-median box.
    category_order = None
    medians = None
    if hue is None:
        medians = df.groupby(x, observed=True)[y].median()
        category_order = list(medians.index)

    sns.boxplot(
        data=df, x=x, y=y, hue=hue, order=category_order,
        saturation=1, width=0.6, fliersize=3, ax=ax,
        **_series_colors(df, hue, theme.NEUTRAL),
    )
    if medians is not None and len(medians):
        _highlight_patch(ax, int(medians.to_numpy().argmax()))

    _titled(ax, f"{y} by {x}")
    return ax


# --- internal helpers -------------------------------------------------------
# Small, shared building blocks. Nothing here draws a whole chart; each does one
# job so the plotting functions above stay short.


def _new_ax(size: tuple[float, float] = (8, 5)) -> plt.Axes:
    """Create a new figure and return its Axes."""
    fig, ax = plt.subplots(figsize=size)
    return ax


# Small words that stay lowercase in a title unless they come first.
_MINOR_WORDS = {
    "a", "an", "and", "as", "at", "by", "for", "from", "in", "of",
    "on", "or", "over", "per", "the", "to", "vs", "with",
}


def _titlecase(text: str) -> str:
    """Title-case a heading: capitalize each word except minor words mid-title."""
    words = []
    for position, word in enumerate(text.split()):
        if position > 0 and word.lower() in _MINOR_WORDS:
            words.append(word.lower())
        else:
            words.append(word[:1].upper() + word[1:])
    return " ".join(words)


def _titled(ax: plt.Axes, title: str) -> None:
    """Set a bold, properly-capitalized title."""
    ax.set_title(_titlecase(title))


# The ocean palette has this many clearly-distinct hues; with more categories we
# switch to an evenly-spaced palette so no two series look alike.
_DISTINCT_HUES = 5


def _hue_palette(values) -> dict:
    """Map each category to a distinct color, keyed by the category value.

    Keying by value (not position) keeps a category the same color everywhere.
    """
    categories = sorted(pd.Series(values).dropna().unique(), key=str)
    if len(categories) <= _DISTINCT_HUES:
        colors = [theme.color(i) for i in range(len(categories))]
    else:
        colors = sns.husl_palette(len(categories))  # evenly spaced, all distinct
    return dict(zip(categories, colors))


def _series_colors(df: pd.DataFrame, hue: Optional[str], single: str) -> dict:
    """The seaborn color keyword to use: a per-category palette, or one color."""
    if hue:
        return {"palette": _hue_palette(df[hue])}
    return {"color": single}


def _strongest_cell(corr: pd.DataFrame) -> Optional[tuple[int, int]]:
    """(row, col) of the largest-magnitude correlation below the diagonal, or None."""
    best = None
    values = corr.to_numpy()
    for i in range(len(values)):
        for j in range(i):  # lower triangle only (the shown half)
            r = values[i, j]
            if pd.notna(r) and (best is None or abs(r) > abs(best[2])):
                best = (i, j, r)
    return None if best is None else (best[0], best[1])


def _highlight_patch(ax: plt.Axes, index: int) -> None:
    """Recolor one bar/box (by draw order) in the muted-coral highlight fill."""
    if 0 <= index < len(ax.patches):
        ax.patches[index].set_facecolor(theme.HIGHLIGHT_MUTED)


def _label_bars(ax: plt.Axes, values, fmt: str = "{:,.0f}") -> None:
    """Write each bar's value just past the end of the bar."""
    for bar, value in zip(ax.patches, values):
        y_center = bar.get_y() + bar.get_height() / 2
        ax.text(
            bar.get_width(), y_center, "  " + fmt.format(value),
            va="center", ha="left", fontsize=9, color=theme._INK,
        )


def _require_dataframe(df: object) -> None:
    """Raise ``TypeError`` unless ``df`` is a pandas DataFrame."""
    if not isinstance(df, pd.DataFrame):
        raise TypeError(f"expected a pandas DataFrame, got {type(df).__name__}")


def _check_columns(df: pd.DataFrame, columns: list[str]) -> None:
    """Raise if ``df`` isn't a DataFrame or is missing any of ``columns``."""
    _require_dataframe(df)
    missing = [c for c in columns if c not in df.columns]
    if missing:
        raise KeyError(f"columns not found in DataFrame: {missing}")
