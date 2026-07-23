"""Per-column analysis: turn a pandas Series into a ``ColumnProfile``."""

from __future__ import annotations

import numpy as np
import pandas as pd

from ..core.dtypes import SemanticType, infer_semantic_type
from ..core.profile import (
    CategoricalStats,
    ColumnProfile,
    DatetimeStats,
    Histogram,
    NumericStats,
)

# How many of the most-frequent categories to retain for reporting.
DEFAULT_TOP_CATEGORIES = 10


def profile_column(
    series: pd.Series,
    *,
    categorical_max_unique: int = 20,
    top_categories: int = DEFAULT_TOP_CATEGORIES,
) -> ColumnProfile:
    """Compute a full ``ColumnProfile`` for a single column."""
    semantic_type = infer_semantic_type(
        series, categorical_max_unique=categorical_max_unique
    )
    non_null = series.dropna()

    common = dict(
        name=str(series.name),
        dtype=str(series.dtype),
        semantic_type=semantic_type,
        n_rows=len(series),
        n_missing=int(series.isna().sum()),
        n_unique=int(non_null.nunique()),
    )

    if semantic_type == SemanticType.NUMERIC:
        return ColumnProfile(**common, numeric=_numeric_stats(non_null))

    if semantic_type == SemanticType.DATETIME and len(non_null):
        return ColumnProfile(
            **common,
            datetime=DatetimeStats(minimum=non_null.min(), maximum=non_null.max()),
        )

    if semantic_type in (
        SemanticType.CATEGORICAL,
        SemanticType.BOOLEAN,
        SemanticType.CONSTANT,
    ):
        return ColumnProfile(
            **common, categorical=_categorical_stats(non_null, top_categories)
        )

    # TEXT, UNIQUE, EMPTY: common fields are enough.
    return ColumnProfile(**common)


def _numeric_stats(non_null: pd.Series) -> NumericStats:
    values = pd.to_numeric(non_null)
    q = values.quantile([0.25, 0.5, 0.75])
    # skew is undefined for <3 points or zero variance; report 0.0 there.
    skew = values.skew()
    return NumericStats(
        mean=float(values.mean()),
        std=float(values.std()) if len(values) > 1 else 0.0,
        minimum=float(values.min()),
        q25=float(q.loc[0.25]),
        median=float(q.loc[0.5]),
        q75=float(q.loc[0.75]),
        maximum=float(values.max()),
        skew=float(skew) if pd.notna(skew) else 0.0,
        zeros=int((values == 0).sum()),
        negatives=int((values < 0).sum()),
        histogram=_histogram(values),
    )


def _histogram(values: pd.Series) -> Histogram:
    n_bins = min(30, max(5, values.nunique()))
    counts, edges = np.histogram(values, bins=n_bins)
    return Histogram(counts=counts.tolist(), edges=edges.tolist())


def _categorical_stats(non_null: pd.Series, top_categories: int) -> CategoricalStats:
    counts = non_null.value_counts()
    top = [(value, int(count)) for value, count in counts.head(top_categories).items()]
    return CategoricalStats(n_categories=int(counts.size), top=top)
