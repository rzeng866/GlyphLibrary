"""Compose a one-page narrative EDA report from a DataFrame.

Layout, top to bottom:

1. **Header** — title, background/context, and a clear objective.
2. **Graphs** — the most informative plots for the data, each carrying a
   one-line discovery subtitle and units on its axes.
3. **Results** — which variables matter most, and what that means.

Returns a matplotlib ``Figure`` (optionally saved to ``path``). Text content
(``context``, ``objective``) is yours to supply — Glyph cannot know the domain.
"""

from __future__ import annotations

import textwrap
from typing import Optional

import matplotlib.pyplot as plt
import pandas as pd

from . import insights, plots, theme


def report(
    df: pd.DataFrame,
    *,
    title: str = "Exploratory Data Analysis",
    context: str = "",
    objective: str = "",
    target: Optional[str] = None,
    units: Optional[dict] = None,
    freq: str = "MS",
    path: Optional[str] = None,
) -> plt.Figure:
    """Render a narrative EDA report for ``df``.

    Parameters
    ----------
    title, context, objective:
        Header text. ``context`` gives background; ``objective`` states the
        question the analysis answers.
    target:
        The variable of interest. Other fields are ranked by how strongly they
        relate to it in the results section. If omitted, Glyph picks the most
        central numeric column.
    units:
        Maps column names to unit strings (e.g. ``{"age": "years", "spend": "$"}``)
        shown on axes and in findings.
    freq:
        Resampling frequency for the temporal panel (pandas offset alias).
    path:
        If given, the figure is also saved here (PNG/PDF/SVG by extension).
    """
    plots._require_dataframe(df)
    if df.shape[1] == 0:
        raise ValueError("cannot build a report for a DataFrame with no columns")

    units = units or {}
    sel = _select_columns(df, target)

    fig, axd = plt.subplot_mosaic(
        [
            ["head", "head", "head"],
            ["p1", "p2", "p3"],
            ["p4", "p5", "p6"],
            ["foot", "foot", "foot"],
        ],
        figsize=(18, 20),
        height_ratios=[1.15, 3, 3, 1.5],
        layout="constrained",
    )

    _header(axd["head"], title, context, objective)
    _fill_panels(axd, df, sel, units, freq)
    _footer(axd["foot"], df, sel, units)

    if path:
        fig.savefig(path, dpi=120, facecolor="white")
    return fig


# --- column selection -------------------------------------------------------


def _select_columns(df: pd.DataFrame, target: Optional[str]) -> dict:
    numeric = list(df.select_dtypes("number").columns)
    categorical = [
        c
        for c in df.columns
        if _is_categorical_like(df[c]) and 2 <= df[c].nunique(dropna=True) <= 30
    ]
    datetimes = list(df.select_dtypes(include=["datetime", "datetimetz"]).columns)

    if target is not None and target not in df.columns:
        raise KeyError(f"target {target!r} is not a column in the DataFrame")
    if target is None and numeric:
        target = _most_central_numeric(df[numeric])

    # Rank drivers once here; reused for the driver panel and the results text.
    drivers = insights.rank_numeric_drivers(df, target) if target in numeric else []

    return {
        "numeric": numeric,
        "categorical": categorical,
        "datetimes": datetimes,
        "target": target,
        "primary_cat": _best_categorical(df, categorical, target, numeric),
        "driver": drivers[0][0] if drivers else None,
        "drivers": drivers,
    }


def _is_categorical_like(series: pd.Series) -> bool:
    """Non-numeric, non-datetime columns (plus bool/Categorical) read as categories."""
    from pandas.api import types as pdt

    if pdt.is_bool_dtype(series) or isinstance(series.dtype, pd.CategoricalDtype):
        return True
    return not pdt.is_numeric_dtype(series) and not pdt.is_datetime64_any_dtype(series)


def _most_central_numeric(numeric_df: pd.DataFrame) -> str:
    if numeric_df.shape[1] == 1:
        return numeric_df.columns[0]
    corr = numeric_df.corr(numeric_only=True).abs()
    strength = (corr.sum() - 1).sort_values(ascending=False)  # minus self-corr
    return str(strength.index[0])


def _best_categorical(df, categorical, target, numeric) -> Optional[str]:
    if not categorical:
        return None
    if target is None or target not in numeric:
        return categorical[0]
    scored = sorted(
        categorical,
        key=lambda c: insights.categorical_effect(df, c, target),
        reverse=True,
    )
    return scored[0]


# --- header / footer text ---------------------------------------------------


def _header(ax: plt.Axes, title: str, context: str, objective: str) -> None:
    ax.axis("off")
    ax.text(0, 1.0, title, fontsize=22, fontweight="bold", va="top", color=theme._INK)
    y = 0.66
    if context:
        ax.text(0, y, "BACKGROUND", fontsize=10, fontweight="bold", color=theme.MUTED, va="top")
        ax.text(
            0.11, y, textwrap.fill(context, width=120), fontsize=11, va="top", color=theme._INK
        )
        y -= 0.34
    if objective:
        ax.text(0, y, "OBJECTIVE", fontsize=10, fontweight="bold", color=theme.MUTED, va="top")
        ax.text(
            0.11, y, textwrap.fill(objective, width=120), fontsize=11, va="top", color=theme._INK
        )


def _footer(ax: plt.Axes, df: pd.DataFrame, sel: dict, units: dict) -> None:
    ax.axis("off")
    ax.text(0, 1.0, "RESULTS — what matters most", fontsize=14, fontweight="bold", va="top", color=theme._INK)

    lines = _results_lines(df, sel, units)
    ax.text(0, 0.74, "\n".join(lines), fontsize=11, va="top", color=theme._INK, linespacing=1.5)


def _results_lines(df: pd.DataFrame, sel: dict, units: dict) -> list[str]:
    target = sel["target"]
    if target is None or target not in sel["numeric"]:
        return [
            "No numeric target to rank against — see the correlation panel and the",
            "per-field summaries above for the main structure of the data.",
        ]

    drivers = sel["drivers"][:3]
    tunit = f" {units[target]}" if units.get(target) else ""
    lines: list[str] = []

    if drivers:
        parts = [f"{name} (r={r:+.2f})" for name, r in drivers]
        lines.append(f"Ranked by association with {target}{tunit}:  " + "   ·   ".join(parts))
        top_name, top_r = drivers[0]
        move = "higher" if top_r > 0 else "lower"
        lines.append(
            f"→ {top_name} matters most: {move} {top_name} tends to accompany higher {target} "
            f"(r={top_r:+.2f})."
        )

    if sel["primary_cat"]:
        eff = insights.categorical_effect(df, sel["primary_cat"], target)
        lines.append(
            f"Among categories, {sel['primary_cat']} is the most differentiating: group means of "
            f"{target} span ≈ {eff:.1f}× its standard deviation."
        )

    lines.append(
        f"Takeaway: focus on {drivers[0][0] if drivers else sel['primary_cat']} when modeling or "
        f"acting on {target}; the weakly-associated fields add little signal."
    )
    return lines


# --- graph panels -----------------------------------------------------------


def _fill_panels(axd: dict, df: pd.DataFrame, sel: dict, units: dict, freq: str) -> None:
    numeric, target = sel["numeric"], sel["target"]
    cat, driver, datetimes = sel["primary_cat"], sel["driver"], sel["datetimes"]

    # p1 — the numeric field of interest.
    if target is not None:
        plots.distribution(df, target, units=units, ax=axd["p1"])
    elif numeric:
        plots.distribution(df, numeric[0], units=units, ax=axd["p1"])
    else:
        _placeholder(axd["p1"], "No numeric column")

    # p2 — a single categorical field.
    if cat is not None:
        plots.counts(df, cat, top=12, ax=axd["p2"])
    else:
        _placeholder(axd["p2"], "No categorical column")

    # p3 — relationships across fields.
    if len(numeric) >= 2:
        plots.correlation(df, ax=axd["p3"])
    else:
        _placeholder(axd["p3"], "Need ≥ 2 numeric columns for correlation")

    # p4 — target vs its strongest driver.
    if target is not None and driver is not None:
        plots.scatter(df, driver, target, hue=cat, units=units, ax=axd["p4"])
    elif cat is not None and target is not None:
        plots.boxplot(df, cat, target, units=units, ax=axd["p4"])
    else:
        _placeholder(axd["p4"], "No relationship to show")

    # p5 — temporal trend, else how the target varies across categories.
    if datetimes and target is not None:
        plots.timeseries(df, datetimes[0], target, freq=freq, hue=cat, units=units, ax=axd["p5"])
    elif datetimes:
        plots.timeseries(df, datetimes[0], freq=freq, ax=axd["p5"])
    elif cat is not None and target is not None:
        plots.boxplot(df, cat, target, units=units, ax=axd["p5"])
    else:
        _placeholder(axd["p5"], "No temporal column")

    # p6 — data quality.
    plots.missing(df, ax=axd["p6"])


def _placeholder(ax: plt.Axes, message: str) -> None:
    ax.axis("off")
    ax.text(0.5, 0.5, message, ha="center", va="center", fontsize=11, color=theme.MUTED, style="italic")
