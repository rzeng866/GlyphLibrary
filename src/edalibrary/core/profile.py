"""Immutable result objects produced by analysis and consumed by renderers.

These are plain, frozen dataclasses with no pandas objects held long-term (aside
from the optional correlation matrix, which is a value, not a live view). That
keeps results cheap to pass around, serialize, and render without recomputation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

import pandas as pd

from .dtypes import SemanticType


@dataclass(frozen=True)
class Histogram:
    """Precomputed histogram so renderers need no access to the raw data."""

    counts: list[int]
    edges: list[float]  # len == len(counts) + 1


@dataclass(frozen=True)
class NumericStats:
    mean: float
    std: float
    minimum: float
    q25: float
    median: float
    q75: float
    maximum: float
    skew: float
    zeros: int
    negatives: int
    histogram: Optional[Histogram] = None

    @property
    def iqr(self) -> float:
        return self.q75 - self.q25

    @property
    def data_range(self) -> float:
        return self.maximum - self.minimum


@dataclass(frozen=True)
class CategoricalStats:
    n_categories: int
    # Most frequent (value, count) pairs, highest first.
    top: list[tuple[Any, int]] = field(default_factory=list)


@dataclass(frozen=True)
class DatetimeStats:
    minimum: pd.Timestamp
    maximum: pd.Timestamp

    @property
    def span(self) -> pd.Timedelta:
        return self.maximum - self.minimum


@dataclass(frozen=True)
class ColumnProfile:
    """Everything known about one column."""

    name: str
    dtype: str
    semantic_type: SemanticType
    n_rows: int  # total rows including missing
    n_missing: int
    n_unique: int
    numeric: Optional[NumericStats] = None
    categorical: Optional[CategoricalStats] = None
    datetime: Optional[DatetimeStats] = None

    @property
    def n_present(self) -> int:
        return self.n_rows - self.n_missing

    @property
    def missing_pct(self) -> float:
        return 100.0 * self.n_missing / self.n_rows if self.n_rows else 0.0

    @property
    def unique_pct(self) -> float:
        return 100.0 * self.n_unique / self.n_present if self.n_present else 0.0


@dataclass(frozen=True)
class Profile:
    """The full analysis of a dataset."""

    n_rows: int
    n_columns: int
    n_duplicate_rows: int
    columns: dict[str, ColumnProfile]
    # Numeric-numeric Pearson correlation matrix; None if <2 numeric columns.
    correlations: Optional[pd.DataFrame] = None

    def __getitem__(self, name: str) -> ColumnProfile:
        return self.columns[name]

    def __iter__(self):
        return iter(self.columns.values())

    def __len__(self) -> int:
        return len(self.columns)

    @property
    def n_missing_cells(self) -> int:
        return sum(c.n_missing for c in self.columns.values())

    @property
    def missing_cells_pct(self) -> float:
        total = self.n_rows * self.n_columns
        return 100.0 * self.n_missing_cells / total if total else 0.0

    def type_counts(self) -> dict[SemanticType, int]:
        """Number of columns of each semantic type, in enum order."""
        counts: dict[SemanticType, int] = {t: 0 for t in SemanticType}
        for col in self.columns.values():
            counts[col.semantic_type] += 1
        return {t: n for t, n in counts.items() if n}

    def summary(self) -> str:
        """A compact text overview (used by ``__repr__`` and terminal output)."""
        from ..report.text import render_summary

        return render_summary(self)

    def to_pdf(self, path: str, *, title: str = "Exploratory Data Analysis") -> str:
        """Render the full report to a PDF file. Returns the path written."""
        from ..report.pdf import render_pdf

        return render_pdf(self, path, title=title)

    def __repr__(self) -> str:
        return (
            f"<Profile: {self.n_rows} rows x {self.n_columns} cols, "
            f"{self.missing_cells_pct:.1f}% missing>"
        )
