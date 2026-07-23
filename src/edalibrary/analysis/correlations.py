"""Cross-column relationships (currently numeric-numeric Pearson)."""

from __future__ import annotations

from typing import Optional

import pandas as pd

from ..core.dtypes import SemanticType
from ..core.profile import ColumnProfile


def compute_correlations(
    df: pd.DataFrame, column_profiles: dict[str, ColumnProfile]
) -> Optional[pd.DataFrame]:
    """Pearson correlation matrix over columns classified as NUMERIC.

    Returns ``None`` when fewer than two numeric columns exist (a correlation
    matrix would be trivial or undefined).
    """
    numeric_cols = [
        name
        for name, prof in column_profiles.items()
        if prof.semantic_type == SemanticType.NUMERIC
    ]
    if len(numeric_cols) < 2:
        return None
    return df[numeric_cols].corr(method="pearson", numeric_only=True)


def top_correlated_pairs(
    corr: pd.DataFrame, *, limit: int = 10
) -> list[tuple[str, str, float]]:
    """Strongest off-diagonal pairs by absolute correlation, highest first."""
    seen: list[tuple[str, str, float]] = []
    cols = list(corr.columns)
    for i, a in enumerate(cols):
        for b in cols[i + 1 :]:
            value = corr.loc[a, b]
            if pd.notna(value):
                seen.append((a, b, float(value)))
    seen.sort(key=lambda t: abs(t[2]), reverse=True)
    return seen[:limit]
