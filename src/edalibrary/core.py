"""Small exploratory-data-analysis helpers for pandas DataFrames.

Every function takes a pandas ``DataFrame`` and returns a pandas object
(a ``DataFrame`` or ``Series``). There are no custom classes to learn: the
results are ordinary pandas objects you already know how to use, filter,
and display.
"""

from __future__ import annotations

import pandas as pd


def summarize(df: pd.DataFrame) -> pd.DataFrame:
    """Return a per-column summary of ``df``.

    One row per column. Columns of the result:

    ``dtype``, ``count`` (non-null values), ``missing``, ``missing_pct``,
    ``unique``, and the numeric statistics ``mean``, ``std``, ``min``,
    ``max`` (``NaN`` for non-numeric columns).

    Example
    -------
    >>> import pandas as pd
    >>> from edalibrary import summarize
    >>> df = pd.DataFrame({"a": [1, 2, None], "b": ["x", "x", "y"]})
    >>> summarize(df)[["count", "missing", "unique"]]
           count  missing  unique
    a          2        1       2
    b          3        0       2
    """
    _require_dataframe(df)

    summary = pd.DataFrame(index=df.columns)
    summary["dtype"] = df.dtypes.astype(str)
    summary["count"] = df.count()
    summary["missing"] = df.isna().sum()
    summary["missing_pct"] = (df.isna().mean() * 100).round(2)
    summary["unique"] = df.nunique(dropna=True)

    numeric = df.select_dtypes("number")
    summary["mean"] = numeric.mean()
    summary["std"] = numeric.std()
    summary["min"] = numeric.min()
    summary["max"] = numeric.max()

    return summary


def missing(df: pd.DataFrame) -> pd.DataFrame:
    """Return missing-value counts and percentages per column, worst first.

    Columns of the result: ``missing`` (count of NA values) and ``percent``
    (percentage of NA values), sorted from most to least missing.

    Example
    -------
    >>> import pandas as pd
    >>> from edalibrary import missing
    >>> df = pd.DataFrame({"a": [1, None, None], "b": [1, 2, 3]})
    >>> missing(df)
       missing  percent
    a        2    66.67
    b        0     0.00
    """
    _require_dataframe(df)

    result = pd.DataFrame(
        {
            "missing": df.isna().sum(),
            "percent": (df.isna().mean() * 100).round(2),
        }
    )
    return result.sort_values("missing", ascending=False)


def _require_dataframe(df: object) -> None:
    if not isinstance(df, pd.DataFrame):
        raise TypeError(
            f"expected a pandas DataFrame, got {type(df).__name__}"
        )
