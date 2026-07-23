"""The public entry point: ``edalibrary.profile(df)``."""

from __future__ import annotations

import pandas as pd

from .analysis.correlations import compute_correlations
from .analysis.univariate import profile_column
from .core.profile import ColumnProfile, Profile


def profile(
    df: pd.DataFrame,
    *,
    categorical_max_unique: int = 20,
    top_categories: int = 10,
) -> Profile:
    """Analyze a DataFrame and return an immutable :class:`Profile`.

    The result is computed once and can be inspected programmatically
    (``profile["col"]``), summarized (``profile.summary()``), or rendered
    (``profile.to_pdf("report.pdf")``).

    Parameters
    ----------
    df:
        The DataFrame to analyze.
    categorical_max_unique:
        Threshold below which low-cardinality columns are treated as categorical.
    top_categories:
        How many of the most frequent values to retain per categorical column.
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError(f"profile() expects a pandas DataFrame, got {type(df).__name__}")
    if df.shape[1] == 0:
        raise ValueError("Cannot profile a DataFrame with no columns.")

    column_profiles: dict[str, ColumnProfile] = {}
    for name in df.columns:
        column_profiles[str(name)] = profile_column(
            df[name],
            categorical_max_unique=categorical_max_unique,
            top_categories=top_categories,
        )

    correlations = compute_correlations(df, column_profiles)

    return Profile(
        n_rows=int(df.shape[0]),
        n_columns=int(df.shape[1]),
        n_duplicate_rows=int(df.duplicated().sum()),
        columns=column_profiles,
        correlations=correlations,
    )
