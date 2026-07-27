"""Glyph — meaningful, visually appealing plots for data scientists.

Plain functions built on seaborn/matplotlib. Each takes a pandas DataFrame
and returns a matplotlib ``Axes`` you can keep customizing.

    >>> import pandas as pd
    >>> import glyph
    >>> df = pd.read_csv("data.csv")
    >>> glyph.distribution(df, "age")
    >>> glyph.correlation(df)

The Glyph theme is applied on import; call ``glyph.set_theme()`` to reapply
or adjust it.
"""

from __future__ import annotations

from .plots import (
    boxplot,
    correlation,
    counts,
    distribution,
    missing,
    pairplot,
    scatter,
    timeseries,
)
from .theme import PALETTE, color, set_theme

# Apply the Glyph look as soon as the library is imported.
set_theme()

__version__ = "0.1.0"

__all__ = [
    "distribution",
    "counts",
    "correlation",
    "scatter",
    "boxplot",
    "timeseries",
    "missing",
    "pairplot",
    "set_theme",
    "color",
    "PALETTE",
]
