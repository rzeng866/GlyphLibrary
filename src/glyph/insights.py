"""Turn data into short, human-readable findings.

These helpers compute the one-line "what we found" summaries that Glyph shows
as plot subtitles, and the driver ranking used in a report's results section.
They return plain strings / numbers — no plotting here.
"""

from __future__ import annotations

import pandas as pd


def _unit(unit: str | None) -> str:
    return f" {unit}" if unit else ""


def distribution_insight(series: pd.Series, unit: str | None = None) -> str:
    s = pd.to_numeric(series, errors="coerce").dropna()
    if s.empty:
        return "no numeric data"
    med, q1, q3 = s.median(), s.quantile(0.25), s.quantile(0.75)
    skew = s.skew()
    shape = (
        "right-skewed" if skew > 0.5 else "left-skewed" if skew < -0.5 else "roughly symmetric"
    )
    u = _unit(unit)
    return f"{shape.capitalize()}; median {med:.3g}{u}, middle 50% span {q1:.3g}–{q3:.3g}{u}"


def counts_insight(series: pd.Series) -> str:
    vc = series.value_counts()
    if vc.empty:
        return "no data"
    total = int(vc.sum())
    share = 100 * vc.iloc[0] / total
    return f"“{vc.index[0]}” is most common at {share:.0f}% of {total:,} records; {vc.size} categories"


def correlation_insight(numeric: pd.DataFrame) -> str:
    corr = numeric.corr(numeric_only=True)
    best_pair, best_val = None, 0.0
    cols = list(corr.columns)
    for i, a in enumerate(cols):
        for b in cols[i + 1 :]:
            r = corr.loc[a, b]
            if pd.notna(r) and abs(r) >= abs(best_val):
                best_pair, best_val = (a, b), float(r)
    if best_pair is None:
        return "no correlations to report"
    strength = "strong" if abs(best_val) >= 0.6 else "moderate" if abs(best_val) >= 0.3 else "weak"
    return f"Strongest link: {best_pair[0]}–{best_pair[1]} ({strength}, r={best_val:+.2f})"


def scatter_insight(x: pd.Series, y: pd.Series) -> str:
    pair = pd.concat([pd.to_numeric(x, errors="coerce"), pd.to_numeric(y, errors="coerce")], axis=1).dropna()
    if len(pair) < 3:
        return "too few points to assess"
    r = pair.iloc[:, 0].corr(pair.iloc[:, 1])
    if pd.isna(r):
        return "no association"
    strength = "Strong" if abs(r) >= 0.6 else "Moderate" if abs(r) >= 0.3 else "Weak"
    direction = "positive" if r > 0 else "negative"
    return f"{strength} {direction} association (r={r:+.2f})"


def boxplot_insight(df: pd.DataFrame, x: str, y: str, unit: str | None = None) -> str:
    med = df.groupby(x, observed=True)[y].median().sort_values()
    if med.empty:
        return "no data"
    hi, lo = med.index[-1], med.index[0]
    gap = med.iloc[-1] - med.iloc[0]
    return f"“{hi}” has the highest median {y}, “{lo}” the lowest (gap ≈ {gap:.3g}{_unit(unit)})"


def timeseries_insight(period_series: pd.Series, unit: str | None = None) -> str:
    s = period_series.dropna()
    if len(s) < 2:
        return "too short to show a trend"
    first, last = s.iloc[0], s.iloc[-1]
    if first == 0:
        trend = "rising" if last > 0 else "flat"
        return f"Overall {trend} across the period"
    change = 100 * (last - first) / abs(first)
    direction = "rising" if change > 5 else "falling" if change < -5 else "broadly flat"
    return f"Overall {direction} ({change:+.0f}% from first to last period)"


def missing_insight(df: pd.DataFrame) -> str:
    pct = df.isna().mean() * 100
    worst = pct.max()
    if worst == 0:
        return "No missing values — complete dataset"
    n_affected = int((pct > 0).sum())
    return f"“{pct.idxmax()}” is most incomplete at {worst:.1f}% missing ({n_affected} columns affected)"


# --- driver ranking (for a report's results section) ------------------------


def rank_numeric_drivers(df: pd.DataFrame, target: str) -> list[tuple[str, float]]:
    """Numeric columns ranked by absolute Pearson correlation with ``target``."""
    numeric = df.select_dtypes("number")
    if target not in numeric.columns:
        return []
    corr = numeric.corr(numeric_only=True)[target].drop(labels=[target], errors="ignore")
    ranked = [(c, float(r)) for c, r in corr.items() if pd.notna(r)]
    ranked.sort(key=lambda t: abs(t[1]), reverse=True)
    return ranked


def categorical_effect(df: pd.DataFrame, cat: str, target: str) -> float:
    """A simple effect size: range of per-group means in target standard deviations."""
    grouped = df.groupby(cat, observed=True)[target].mean()
    std = df[target].std()
    if std in (0, None) or pd.isna(std) or grouped.empty:
        return 0.0
    return float((grouped.max() - grouped.min()) / std)
