"""Glyph plotting functions.

Each function takes a pandas ``DataFrame`` and returns a matplotlib ``Axes``
(``pairplot`` returns a seaborn ``PairGrid``), so you can keep customizing the
result with the matplotlib/seaborn API you already know. There are no Glyph
classes to learn.
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

    A dashed line marks the median. Pass ``hue`` to split the distribution by
    a categorical column. ``units`` maps column names to unit strings shown on
    the axis; ``describe`` toggles the discovery subtitle.
    """
    _check_columns(df, [column] + ([hue] if hue else []))
    ax = ax or _new_ax()
    sns.histplot(
        data=df,
        x=column,
        hue=hue,
        bins=bins,
        kde=True,
        edgecolor="white",
        linewidth=0.5,
        alpha=0.9,
        ax=ax,
        **_series_colors(df, hue, theme.NEUTRAL),
    )
    if hue is None:
        median = df[column].median()
        ax.axvline(median, color=theme.HIGHLIGHT, linestyle="--", linewidth=1.5)
        ax.text(
            median,
            ax.get_ylim()[1] * 0.96,
            f"  median {median:.4g}",
            color=theme.HIGHLIGHT,
            fontsize=9,
            fontweight="bold",
            va="top",
        )
    unit = (units or {}).get(column)
    _titled(
        ax,
        f"Distribution of {column}",
        insights.distribution_insight(df[column], unit) if describe else None,
    )
    ax.set_xlabel(_axis_label(column, units))
    ax.set_ylabel("count")
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

    Bars are ordered most-frequent first and labelled with their counts. Pass
    ``top`` to show only the N most frequent values; ``describe`` toggles the
    discovery subtitle.
    """
    _check_columns(df, [column])
    order = df[column].value_counts()
    if top is not None:
        order = order.head(top)

    ax = ax or _new_ax()
    sns.barplot(
        x=order.values,
        y=order.index.astype(str),
        color=theme.NEUTRAL,
        saturation=1,  # render theme colors faithfully (no desaturation)
        ax=ax,
    )
    _highlight_patch(ax, 0)  # the most frequent category
    _label_bars(ax, order.values)
    ax.margins(x=0.12)
    ax.grid(False, axis="y")
    title = f"Counts of {column}"
    if top is not None:
        title += f" (top {top})"
    _titled(ax, title, insights.counts_insight(df[column]) if describe else None)
    ax.set_xlabel("count (records)")
    ax.set_ylabel(column)
    return ax


def correlation(
    df: pd.DataFrame,
    *,
    method: str = "pearson",
    describe: bool = True,
    ax: Optional[plt.Axes] = None,
) -> plt.Axes:
    """Annotated heatmap of pairwise correlations between numeric columns.

    The upper triangle is masked to reduce clutter. ``describe`` toggles the
    discovery subtitle. Raises ``ValueError`` if the frame has fewer than two
    numeric columns.
    """
    _require_dataframe(df)
    numeric = df.select_dtypes("number")
    if numeric.shape[1] < 2:
        raise ValueError("correlation() needs at least two numeric columns.")

    corr = numeric.corr(method=method)
    mask = np.triu(np.ones_like(corr, dtype=bool), k=1)

    ax = ax or _new_ax(size=(1.1 * len(corr.columns) + 2, 1.0 * len(corr.columns) + 1.5))
    sns.heatmap(
        corr,
        mask=mask,
        cmap=theme.DIVERGING,
        vmin=-1,
        vmax=1,
        center=0,
        annot=True,
        fmt=".2f",
        annot_kws={"size": 9},
        linewidths=0.5,
        linecolor="white",
        square=True,
        cbar_kws={"shrink": 0.75, "label": f"{method} r"},
        ax=ax,
    )
    # Outline the strongest off-diagonal pair (the key point) in the highlight color.
    pair = insights.strongest_pair(corr)
    if pair is not None:
        i, j = pair[0], pair[1]
        ax.add_patch(
            mpatches.Rectangle(
                (j, i), 1, 1, fill=False, edgecolor=theme.HIGHLIGHT, linewidth=2.5, zorder=5
            )
        )

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

    ``units`` maps column names to unit strings shown on the axes; ``describe``
    toggles the discovery subtitle.
    """
    _check_columns(df, [x, y] + [c for c in (hue, size) if c])
    ax = ax or _new_ax(size=(7, 6))
    sns.scatterplot(
        data=df,
        x=x,
        y=y,
        hue=hue,
        size=size,
        alpha=0.75,
        edgecolor="white",
        linewidth=0.4,
        **_series_colors(df, hue, theme.color(0)),
        ax=ax,
    )
    _titled(ax, f"{y} vs {x}", insights.scatter_insight(df[x], df[y]) if describe else None)
    ax.set_xlabel(_axis_label(x, units))
    ax.set_ylabel(_axis_label(y, units))
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

    Good for comparing a numeric distribution across categories. ``units`` maps
    column names to unit strings shown on the axis; ``describe`` toggles the
    discovery subtitle.
    """
    _check_columns(df, [x, y] + ([hue] if hue else []))
    ax = ax or _new_ax()

    # Fixed category order lets us highlight the highest-median box precisely.
    order = None
    if hue is None:
        medians = df.groupby(x, observed=True)[y].median()
        order = list(medians.index)

    sns.boxplot(
        data=df,
        x=x,
        y=y,
        hue=hue,
        order=order,
        **_series_colors(df, hue, theme.NEUTRAL),
        saturation=1,
        width=0.6,
        fliersize=3,
        ax=ax,
    )
    if hue is None and len(medians):
        _highlight_patch(ax, int(medians.to_numpy().argmax()))  # category with the highest median
    _titled(
        ax,
        f"{y} by {x}",
        insights.boxplot_insight(df, x, y, (units or {}).get(y)) if describe else None,
    )
    ax.set_xlabel(_axis_label(x, units))
    ax.set_ylabel(_axis_label(y, units))
    return ax


def missing(
    df: pd.DataFrame, *, describe: bool = True, ax: Optional[plt.Axes] = None
) -> plt.Axes:
    """Bar chart of the percentage of missing values per column, worst first.

    Only columns with at least one missing value are shown; a clean message is
    drawn when nothing is missing. ``describe`` toggles the discovery subtitle.
    """
    _require_dataframe(df)
    pct = (df.isna().mean() * 100).sort_values(ascending=False)
    pct = pct[pct > 0]

    ax = ax or _new_ax(size=(8, max(2.5, 0.45 * len(pct) + 1)))
    if pct.empty:
        _titled(ax, "Missing values by column")
        ax.text(0.5, 0.5, "No missing values", ha="center", va="center", fontsize=13)
        ax.set_xticks([])
        ax.set_yticks([])
        return ax

    sns.barplot(x=pct.values, y=pct.index.astype(str), color=theme.NEUTRAL, saturation=1, ax=ax)
    _highlight_patch(ax, 0)  # the most-incomplete column
    _label_bars(ax, pct.values, fmt="{:.1f}%")
    ax.set_xlim(0, 100)
    ax.margins(x=0.12)
    ax.grid(False, axis="y")
    _titled(
        ax,
        "Missing values by column",
        insights.missing_insight(df) if describe else None,
    )
    ax.set_xlabel("% missing")
    ax.set_ylabel("")
    return ax


def pairplot(
    df: pd.DataFrame,
    *,
    hue: Optional[str] = None,
    columns: Optional[list[str]] = None,
) -> sns.axisgrid.PairGrid:
    """Grid of pairwise scatter plots for numeric columns, with KDEs on the diagonal.

    Returns a seaborn ``PairGrid``. Uses a lower-triangle ("corner") layout to
    keep the grid uncluttered.
    """
    _require_dataframe(df)
    if columns is not None:
        _check_columns(df, columns + ([hue] if hue else []))
        data = df[columns + ([hue] if hue and hue not in columns else [])]
    else:
        numeric = df.select_dtypes("number")
        if numeric.shape[1] < 2:
            raise ValueError("pairplot() needs at least two numeric columns.")
        data = df[list(numeric.columns) + ([hue] if hue else [])]

    grid = sns.pairplot(
        data,
        hue=hue,
        corner=True,
        diag_kind="kde",
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

    If ``value`` is ``None``, plots the number of records per period (activity
    volume over time). Otherwise aggregates ``value`` per period with ``agg``
    (e.g. ``"mean"``, ``"sum"``, ``"median"``). Pass ``hue`` to draw one colored
    line per category, for comparison. ``units`` maps column names to unit
    strings shown on the axis; ``describe`` toggles the discovery subtitle.

    ``freq`` is a pandas offset alias: ``"D"`` daily, ``"W"`` weekly, ``"MS"``
    monthly, ``"QS"`` quarterly, ``"YS"`` yearly. The ``time`` column is parsed
    with :func:`pandas.to_datetime` if it is not already datetime-typed.
    """
    _check_columns(df, [time] + [c for c in (value, hue) if c])

    work = pd.DataFrame({time: _as_datetime(df[time], time)})
    if value is not None:
        work[value] = df[value].to_numpy()
    if hue is not None:
        work[hue] = df[hue].to_numpy()

    keys: list = [pd.Grouper(key=time, freq=freq)] + ([hue] if hue else [])
    unit = (units or {}).get(value) if value else None
    if value is None:
        series = work.groupby(keys).size()
        ycol, ylabel = "records", "records"
    else:
        series = work.groupby(keys)[value].agg(agg)
        ycol = value
        ylabel = f"{value} ({agg}{', ' + unit if unit else ''})"
    plot_df = series.rename(ycol).reset_index()

    ax = ax or _new_ax(size=(9, 5))
    sns.lineplot(
        data=plot_df,
        x=time,
        y=ycol,
        hue=hue,
        marker="o",
        markersize=5,
        linewidth=2,
        **_series_colors(work, hue, theme.color(0)),
        ax=ax,
    )
    _format_date_axis(ax)
    ax.margins(x=0.02)

    subtitle = None
    if describe:
        if hue is None:
            overall_series = series  # already grouped by period alone
        else:
            overall = work.groupby(pd.Grouper(key=time, freq=freq))
            overall_series = overall.size() if value is None else overall[value].agg(agg)
        subtitle = insights.timeseries_insight(overall_series, unit)
    _titled(ax, ("Records" if value is None else value) + " over time", subtitle)
    ax.set_xlabel(time)
    ax.set_ylabel(ylabel)
    return ax


# --- internal helpers -------------------------------------------------------


def _new_ax(size: tuple[float, float] = (8, 5)) -> plt.Axes:
    _, ax = plt.subplots(figsize=size)
    return ax


# Words kept lowercase in titles unless they lead the title.
_MINOR_WORDS = {
    "a", "an", "and", "as", "at", "by", "for", "from", "in", "of", "on",
    "or", "over", "per", "the", "to", "vs", "with",
}


def _cap_first_alpha(word: str) -> str:
    """Capitalize the first alphabetic character, preserving leading punctuation."""
    i = next((k for k, c in enumerate(word) if c.isalpha()), None)
    return word if i is None else word[:i] + word[i].upper() + word[i + 1 :]


def _titlecase(text: str) -> str:
    """Proper title case: significant words capitalized, minor words kept lower."""
    return " ".join(
        w.lower() if i and w.lower() in _MINOR_WORDS else _cap_first_alpha(w)
        for i, w in enumerate(text.split(" "))
    )


def _titled(ax: plt.Axes, title: str, subtitle: Optional[str] = None) -> None:
    """Set the bold title and an optional italic discovery subtitle beneath it."""
    ax.set_title(_titlecase(title), pad=20 if subtitle else 12)
    if subtitle:
        ax.annotate(
            subtitle,
            xy=(0.5, 1.0),
            xycoords="axes fraction",
            xytext=(0, 6),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=9,
            style="italic",
            color=theme.MUTED,
            annotation_clip=False,
        )


def _axis_label(col: str, units: Optional[dict]) -> str:
    """Column name, with a unit in parentheses when one is provided."""
    if units and units.get(col):
        return f"{col} ({units[col]})"
    return str(col)


def _hue_palette(values) -> list[str]:
    """A palette sized to the number of distinct hue categories."""
    n = int(pd.Series(values).nunique(dropna=True))
    return [theme.color(i) for i in range(max(n, 1))]


def _series_colors(df: pd.DataFrame, hue: Optional[str], single: str) -> dict:
    """seaborn color kwargs: a per-category palette when comparing groups, else one color."""
    return {"palette": _hue_palette(df[hue])} if hue else {"color": single}


def _as_datetime(series: pd.Series, name: str) -> pd.Series:
    """Return ``series`` as datetime, parsing strings if necessary."""
    if pd.api.types.is_datetime64_any_dtype(series):
        return series
    try:
        return pd.to_datetime(series)
    except (ValueError, TypeError) as exc:
        raise ValueError(
            f"column {name!r} could not be parsed as datetime for timeseries()"
        ) from exc


def _format_date_axis(ax: plt.Axes) -> None:
    """Apply readable, auto-scaled date ticks to the x-axis."""
    locator = mdates.AutoDateLocator()
    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(mdates.ConciseDateFormatter(locator))


def _highlight_patch(ax: plt.Axes, index: int) -> None:
    """Recolor a single bar/box in the highlight color to draw the eye to it."""
    if 0 <= index < len(ax.patches):
        ax.patches[index].set_facecolor(theme.HIGHLIGHT)


def _label_bars(ax: plt.Axes, values, fmt: str = "{:,.0f}") -> None:
    """Annotate horizontal bars just past their end."""
    for patch, value in zip(ax.patches, values):
        ax.text(
            patch.get_width(),
            patch.get_y() + patch.get_height() / 2,
            "  " + fmt.format(value),
            va="center",
            ha="left",
            fontsize=9,
            color=theme._INK,
        )


def _require_dataframe(df: object) -> None:
    if not isinstance(df, pd.DataFrame):
        raise TypeError(f"expected a pandas DataFrame, got {type(df).__name__}")


def _check_columns(df: pd.DataFrame, columns: list[str]) -> None:
    _require_dataframe(df)
    missing_cols = [c for c in columns if c not in df.columns]
    if missing_cols:
        raise KeyError(f"columns not found in DataFrame: {missing_cols}")
