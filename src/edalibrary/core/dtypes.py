"""Semantic type inference.

pandas dtypes (``int64``, ``object``, ...) tell us how data is *stored*, not how
it should be *analyzed*. A column of small integers might be a true numeric
measure or an encoded category; a string column might be free text or a handful
of repeated labels. The ``SemanticType`` classification drives which statistics
and which chart we compute for each column.
"""

from __future__ import annotations

from enum import Enum

import pandas as pd
from pandas.api import types as pdt


class SemanticType(str, Enum):
    """How a column should be treated for analysis, independent of storage dtype."""

    NUMERIC = "numeric"
    CATEGORICAL = "categorical"
    BOOLEAN = "boolean"
    DATETIME = "datetime"
    TEXT = "text"
    CONSTANT = "constant"  # a single repeated value (after dropping NA)
    UNIQUE = "unique"  # (near-)unique per row, e.g. an identifier
    EMPTY = "empty"  # all values missing

    def __str__(self) -> str:  # nicer report labels
        return self.value


# A low-cardinality numeric column is more useful analyzed as a category.
# e.g. an integer 1-5 satisfaction score. Tunable via ``infer_semantic_type``.
_DEFAULT_CATEGORICAL_MAX_UNIQUE = 20


def infer_semantic_type(
    series: pd.Series,
    *,
    categorical_max_unique: int = _DEFAULT_CATEGORICAL_MAX_UNIQUE,
    unique_ratio_threshold: float = 0.9,
) -> SemanticType:
    """Classify a single column.

    Parameters
    ----------
    series:
        The column to classify.
    categorical_max_unique:
        Numeric columns with no more than this many distinct values are treated
        as categorical (e.g. an encoded rating).
    unique_ratio_threshold:
        Non-numeric columns whose distinct-value ratio exceeds this are treated
        as identifiers (``UNIQUE``) rather than categories or text.
    """
    non_null = series.dropna()
    n = len(non_null)

    if n == 0:
        return SemanticType.EMPTY

    n_unique = non_null.nunique()
    if n_unique == 1:
        return SemanticType.CONSTANT

    if pdt.is_bool_dtype(series):
        return SemanticType.BOOLEAN

    if pdt.is_datetime64_any_dtype(series):
        return SemanticType.DATETIME

    if pdt.is_numeric_dtype(series):
        # Small integer-like domains read better as categories.
        if n_unique <= categorical_max_unique and _looks_integral(non_null):
            return SemanticType.CATEGORICAL
        return SemanticType.NUMERIC

    # Object / string / category dtypes below.
    if isinstance(series.dtype, pd.CategoricalDtype):
        return SemanticType.CATEGORICAL

    unique_ratio = n_unique / n
    if unique_ratio >= unique_ratio_threshold:
        return SemanticType.UNIQUE
    if n_unique <= categorical_max_unique:
        return SemanticType.CATEGORICAL
    return SemanticType.TEXT


def _looks_integral(non_null: pd.Series) -> bool:
    """True if every value is a whole number (int dtype, or float with no fraction)."""
    if pdt.is_integer_dtype(non_null):
        return True
    if pdt.is_float_dtype(non_null):
        return bool(((non_null % 1) == 0).all())
    return False
