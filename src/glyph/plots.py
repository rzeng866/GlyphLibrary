"""Glyph plotting functions.

Every public function in this module follows the same six steps, so once you
understand one you understand them all:

    1. Validate the input          -> _check_columns / _require_dataframe
    2. Get an Axes to draw on       -> the caller's `ax`, or a fresh one
    3. Draw with seaborn, taking colors from `theme` (never hard-coded)
    4. Mark the key point           -> highlight a bar, the median line, ...
    5. Add the title, a one-line finding subtitle, and axis labels -> _finish
    6. Return the Axes

Each function takes a pandas ``DataFrame`` and returns a matplotlib ``Axes``
(``pairplot`` returns a seaborn ``PairGrid``), so you can keep customizing the
result with the matplotlib/seaborn API you already know. There are no Glyph
classes to learn.

The one-line "findings" (subtitles) and the driver ranking come from
``insights.py``; the colors and fonts come from ``theme.py``. This file only
draws.
"""

from __future__ import annotations

from typing import Optional

import matplotlib.dates as mdates
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from . import insights, theme

__all__ = [
    "distribution",
    "counts",
    "correlation",
    "scatter",
    "boxplot",
    "timeseries",
    "missing",
    "pairplot",
]


def distribution(
    df: pd.DataFrame,
    column: str,
    *,
    hue: Optional[str] = None,
    bins: str | int = "auto",
    units: Optional[dict] = None,
    describe: bool = True,
    ax: Optional[plt.Axes] = None,
) -> plt.Axes:
    """Histogram with a smooth density (KDE) overlay for a numeric column.

    A dashed line marks the median. Pass ``hue`` to split the distribution by a
    categorical column. ``units`` labels the axis; ``describe`` toggles the
    one-line finding shown as a subtitle.
    """
    _check_columns(df, [column] + ([hue] if hue else []))
    ax = ax or _new_ax()

    sns.histplot(
        data=df, x=column, hue=hue, bins=bins, kde=True,
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

    finding = insights.distribution_insight(df[column], _unit(units, column))
    _finish(
        ax,
        title=f"Distribution of {column}",
        subtitle=finding if describe else None,
        xlabel=_axis_label(column, units),
        ylabel="count",
    )
    return ax


def counts(
    df: pd.DataFrame,
    column: str,
    *,
    top: Optional[int] = None,
    describe: bool = True,
    ax: Optional[plt.Axes] = None,
) -> plt.Axes:
    """Horizontal bar chart of value frequencies for a categorical column.

    Bars are ordered most-frequent first and labelled with their counts; the
    most frequent one is highlighted. Pass ``top`` to show only the N most
    frequent values; ``describe`` toggles the finding subtitle.
    """
    _check_columns(df, [column])

    frequencies = df[column].value_counts()  # already sorted, most first
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

    title = f"Counts of {column}"
    if top is not None:
        title += f" (top {top})"
    _finish(
        ax,
        title=title,
        subtitle=insights.counts_insight(df[column]) if describe else None,
        xlabel="count (records)",
        ylabel=column,
    )
    return ax


def correlation(
    df: pd.DataFrame,
    *,
    method: str = "pearson",
    describe: bool = True,
    ax: Optional[plt.Axes] = None,
) -> plt.Axes:
    """Annotated heatmap of pairwise correlations between numeric columns.

    The upper triangle is masked to reduce clutter, and the strongest pair is
    outlined. ``describe`` toggles the finding subtitle. Raises ``ValueError``
    if the frame has fewer than two numeric columns.
    """
    _require_dataframe(df)
    numeric = df.select_dtypes("number")
    if numeric.shape[1] < 2:
        raise ValueError("correlation() needs at least two numeric columns.")

    corr = numeric.corr(method=method)
    upper_triangle = np.triu(np.ones_like(corr, dtype=bool), k=1)  # hidden half

    n_cols = len(corr.columns)
    ax = ax or _new_ax(size=(1.1 * n_cols + 2, 1.0 * n_cols + 1.5))
    sns.heatmap(
        corr, mask=upper_triangle, cmap=theme.DIVERGING, vmin=-1, vmax=1, center=0,
        annot=True, fmt=".2f", annot_kws={"size": 9},
        linewidths=0.5, linecolor="white", square=True,
        cbar_kws={"shrink": 0.75, "label": f"{method} r"}, ax=ax,
    )

    # Outline the strongest pair (its heatmap cell) in the bright highlight color.
    strongest = insights.strongest_pair(corr)
    if strongest is not None:
        row, col = strongest[0], strongest[1]
        ax.add_patch(mpatches.Rectangle(
            (col, row), 1, 1, fill=False,
            edgecolor=theme.HIGHLIGHT, linewidth=2.5, zorder=5,
        ))

    _titled(ax, "Correlation", insights.correlation_insight(corr) if describe else None)
    ax.grid(False)
    ax.tick_params(rotation=0)  # keep all labels horizontal (no slanted text)
    return ax


def scatter(
    df: pd.DataFrame,
    x: str,
    y: str,
    *,
    hue: Optional[str] = None,
    size: Optional[str] = None,
    units: Optional[dict] = None,
    describe: bool = True,
    ax: Optional[plt.Axes] = None,
) -> plt.Axes:
    """Scatter plot of ``y`` against ``x``, optionally colored/sized by columns.

    ``units`` labels the axes; ``describe`` toggles the finding subtitle.
    """
    _check_columns(df, [x, y] + [c for c in (hue, size) if c])
    ax = ax or _new_ax(size=(7, 6))

    sns.scatterplot(
        data=df, x=x, y=y, hue=hue, size=size,
        alpha=0.75, edgecolor="white", linewidth=0.4, ax=ax,
        **_series_colors(df, hue, theme.color(0)),
    )

    _finish(
        ax,
        title=f"{y} vs {x}",
        subtitle=insights.scatter_insight(df[x], df[y]) if describe else None,
        xlabel=_axis_label(x, units),
        ylabel=_axis_label(y, units),
    )
    return ax


def boxplot(
    df: pd.DataFrame,
    x: str,
    y: str,
    *,
    hue: Optional[str] = None,
    units: Optional[dict] = None,
    describe: bool = True,
    ax: Optional[plt.Axes] = None,
) -> plt.Axes:
    """Box plot of numeric ``y`` grouped by categorical ``x``.

    Good for comparing a numeric distribution across categories; the category
    with the highest median is highlighted. ``units`` labels the axis;
    ``describe`` toggles the finding subtitle.
    """
    _check_columns(df, [x, y] + ([hue] if hue else []))
    ax = ax or _new_ax()

    # With no hue we fix the category order so we can highlight the box with the
    # highest median. With a hue there is no single box to highlight.
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
        highest = int(medians.to_numpy().argmax())
        _highlight_patch(ax, highest)

    _finish(
        ax,
        title=f"{y} by {x}",
        subtitle=insights.boxplot_insight(df, x, y, _unit(units, y)) if describe else None,
        xlabel=_axis_label(x, units),
        ylabel=_axis_label(y, units),
    )
    return ax


def missing(
    df: pd.DataFrame, *, describe: bool = True, ax: Optional[plt.Axes] = None
) -> plt.Axes:
    """Bar chart of the percentage of missing values per column, worst first.

    Only columns with at least one missing value are shown; a clean message is
    drawn when nothing is missing. ``describe`` toggles the finding subtitle.
    """
    _require_dataframe(df)

    percent_missing = (df.isna().mean() * 100).sort_values(ascending=False)
    percent_missing = percent_missing[percent_missing > 0]

    ax = ax or _new_ax(size=(8, max(2.5, 0.45 * len(percent_missing) + 1)))

    if percent_missing.empty:
        _titled(ax, "Missing values by column")
        ax.text(0.5, 0.5, "No missing values", ha="center", va="center", fontsize=13)
        ax.set_xticks([])
        ax.set_yticks([])
        return ax

    sns.barplot(
        x=percent_missing.values, y=percent_missing.index.astype(str),
        color=theme.NEUTRAL, saturation=1, ax=ax,
    )
    _highlight_patch(ax, 0)  # the worst (most-incomplete) column
    _label_bars(ax, percent_missing.values, fmt="{:.1f}%")
    ax.set_xlim(0, 100)
    ax.margins(x=0.12)
    ax.grid(False, axis="y")

    _finish(
        ax,
        title="Missing values by column",
        subtitle=insights.missing_insight(df) if describe else None,
        xlabel="% missing",
        ylabel="",
    )
    return ax


def pairplot(
    df: pd.DataFrame,
    *,
    hue: Optional[str] = None,
    columns: Optional[list[str]] = None,
) -> sns.axisgrid.PairGrid:
    """Grid of pairwise scatter plots for numeric columns, KDEs on the diagonal.

    Returns a seaborn ``PairGrid`` in a lower-triangle ("corner") layout to keep
    the grid uncluttered. Pass ``columns`` to choose the columns to compare.
    """
    _require_dataframe(df)

    if columns is not None:
        _check_columns(df, columns + ([hue] if hue else []))
        keep = columns + ([hue] if hue and hue not in columns else [])
    else:
        numeric = df.select_dtypes("number")
        if numeric.shape[1] < 2:
            raise ValueError("pairplot() needs at least two numeric columns.")
        keep = list(numeric.columns) + ([hue] if hue else [])
    data = df[keep]

    grid = sns.pairplot(
        data, hue=hue, corner=True, diag_kind="kde",
        palette=_hue_palette(data[hue]) if hue else None,
        plot_kws={"alpha": 0.7, "edgecolor": "white", "linewidth": 0.3},
    )
    grid.figure.suptitle("Pairwise relationships", y=1.02, fontweight="bold")
    return grid


def timeseries(
    df: pd.DataFrame,
    time: str,
    value: Optional[str] = None,
    *,
    freq: str = "MS",
    agg: str = "mean",
    hue: Optional[str] = None,
    units: Optional[dict] = None,
    describe: bool = True,
    ax: Optional[plt.Axes] = None,
) -> plt.Axes:
    """Line chart of a metric over time, resampled to a regular frequency.

    If ``value`` is ``None`` it plots the number of records per period (activity
    volume); otherwise it aggregates ``value`` per period with ``agg`` (e.g.
    ``"mean"``, ``"sum"``). Pass ``hue`` to draw one colored line per category.
    ``freq`` is a pandas offset alias (``"D"``/``"W"``/``"MS"``/``"QS"``/``"YS"``);
    the ``time`` column is parsed with ``pd.to_datetime`` if it isn't a datetime.
    """
    _check_columns(df, [time] + [c for c in (value, hue) if c])

    # Build a small working frame with a real datetime column, then group it
    # into regular time buckets (plus the hue, if comparing groups).
    work = pd.DataFrame({time: _as_datetime(df[time], time)})
    if value is not None:
        work[value] = df[value].to_numpy()
    if hue is not None:
        work[hue] = df[hue].to_numpy()

    period = pd.Grouper(key=time, freq=freq)
    group_keys = [period, hue] if hue else [period]

    if value is None:
        per_period = work.groupby(group_keys).size()
        y_column = "records"
        y_label = "records"
    else:
        per_period = work.groupby(group_keys)[value].agg(agg)
        y_column = value
        unit = _unit(units, value)
        y_label = f"{value} ({agg}, {unit})" if unit else f"{value} ({agg})"
    plot_data = per_period.rename(y_column).reset_index()

    ax = ax or _new_ax(size=(9, 5))
    sns.lineplot(
        data=plot_data, x=time, y=y_column, hue=hue,
        marker="o", markersize=5, linewidth=2, ax=ax,
        **_series_colors(work, hue, theme.color(0)),
    )
    _format_date_axis(ax)
    ax.margins(x=0.02)

    # The subtitle describes the overall trend, so recompute it without the hue.
    subtitle = None
    if describe:
        overall = work.groupby(period)
        overall = overall.size() if value is None else overall[value].agg(agg)
        subtitle = insights.timeseries_insight(overall, _unit(units, value) if value else None)

    title = ("Records" if value is None else value) + " over time"
    _finish(ax, title=title, subtitle=subtitle, xlabel=time, ylabel=y_label)
    return ax


# --- internal helpers -------------------------------------------------------
# Small, shared building blocks used by the plotting functions above. Nothing
# here draws a whole chart; each does one job.


def _new_ax(size: tuple[float, float] = (8, 5)) -> plt.Axes:
    """Create a new figure and return its Axes."""
    fig, ax = plt.subplots(figsize=size)
    return ax


def _finish(
    ax: plt.Axes,
    title: str,
    subtitle: Optional[str] = None,
    xlabel: Optional[str] = None,
    ylabel: Optional[str] = None,
) -> None:
    """Apply the closing steps every plot shares: title, subtitle, axis labels."""
    _titled(ax, title, subtitle)
    if xlabel is not None:
        ax.set_xlabel(xlabel)
    if ylabel is not None:
        ax.set_ylabel(ylabel)


def _titled(ax: plt.Axes, title: str, subtitle: Optional[str] = None) -> None:
    """Set the bold (title-cased) title and an optional italic subtitle below it."""
    ax.set_title(_titlecase(title), pad=20 if subtitle else 12)
    if subtitle:
        ax.annotate(
            subtitle, xy=(0.5, 1.0), xycoords="axes fraction",
            xytext=(0, 6), textcoords="offset points",
            ha="center", va="bottom", fontsize=9, style="italic",
            color=theme.MUTED, annotation_clip=False,
        )


# Small words that stay lowercase in a title unless they come first.
_MINOR_WORDS = {
    "a", "an", "and", "as", "at", "by", "for", "from", "in", "of",
    "on", "or", "over", "per", "the", "to", "vs", "with",
}


def _titlecase(text: str) -> str:
    """Title-case a heading: capitalize each word except minor words mid-title."""
    words = text.split(" ")
    titled = []
    for position, word in enumerate(words):
        is_minor = word.lower() in _MINOR_WORDS
        if position > 0 and is_minor:
            titled.append(word.lower())
        else:
            titled.append(_capitalize_first_letter(word))
    return " ".join(titled)


def _capitalize_first_letter(word: str) -> str:
    """Uppercase the first letter, keeping any leading punctuation (e.g. "(top")."""
    for index, char in enumerate(word):
        if char.isalpha():
            return word[:index] + char.upper() + word[index + 1:]
    return word  # no letters (e.g. "12)") — leave it as-is


def _axis_label(column: str, units: Optional[dict]) -> str:
    """Column name, with its unit in parentheses when one is provided."""
    unit = _unit(units, column)
    return f"{column} ({unit})" if unit else str(column)


def _unit(units: Optional[dict], column: str) -> Optional[str]:
    """Look up a column's unit string, tolerating ``units=None``."""
    return (units or {}).get(column)


# The ocean palette has this many clearly-distinct hues. With more categories
# than this we switch to an evenly-spaced palette so no two series look alike.
_DISTINCT_HUES = 5


def _hue_palette(values) -> dict:
    """Map each distinct category to a distinct color, keyed by the category value.

    Keying by value (not position) means a category keeps the same color in
    every plot of a figure.
    """
    categories = sorted(pd.Series(values).dropna().unique(), key=str)
    if len(categories) <= _DISTINCT_HUES:
        colors = [theme.color(i) for i in range(len(categories))]
    else:
        colors = sns.husl_palette(len(categories))  # evenly-spaced, all distinct
    return dict(zip(categories, colors))


def _series_colors(df: pd.DataFrame, hue: Optional[str], single: str) -> dict:
    """The seaborn color keyword to use: a per-category palette, or one color."""
    if hue:
        return {"palette": _hue_palette(df[hue])}
    return {"color": single}


def _as_datetime(series: pd.Series, name: str) -> pd.Series:
    """Return ``series`` as datetime, parsing it from strings if necessary."""
    if pd.api.types.is_datetime64_any_dtype(series):
        return series
    try:
        return pd.to_datetime(series)
    except (ValueError, TypeError) as exc:
        raise ValueError(
            f"column {name!r} could not be parsed as datetime for timeseries()"
        ) from exc


def _format_date_axis(ax: plt.Axes) -> None:
    """Give the x-axis readable, automatically-scaled date ticks."""
    locator = mdates.AutoDateLocator()
    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(mdates.ConciseDateFormatter(locator))


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
    missing_columns = [c for c in columns if c not in df.columns]
    if missing_columns:
        raise KeyError(f"columns not found in DataFrame: {missing_columns}")
