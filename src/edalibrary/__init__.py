"""edalibrary — exploratory data analysis for pandas, rendered to PDF.

    >>> import pandas as pd, edalibrary as eda
    >>> report = eda.profile(pd.read_csv("data.csv"))
    >>> print(report.summary())
    >>> report.to_pdf("report.pdf")
"""

from __future__ import annotations

from .api import profile
from .core import (
    CategoricalStats,
    ColumnProfile,
    DatetimeStats,
    Histogram,
    NumericStats,
    Profile,
    SemanticType,
)

__version__ = "0.1.0"

__all__ = [
    "profile",
    "Profile",
    "ColumnProfile",
    "SemanticType",
    "NumericStats",
    "CategoricalStats",
    "DatetimeStats",
    "Histogram",
    "__version__",
]
