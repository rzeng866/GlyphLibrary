"""glyphOcean — meaningful, visually appealing plots for data scientists.

Plain functions built on seaborn/matplotlib. Each takes a pandas DataFrame
and returns a matplotlib ``Axes`` you can keep customizing.

    >>> import pandas as pd
    >>> import glyphOcean as gl          # recommended alias, like `import numpy as np`
    >>> df = pd.read_csv("data.csv")
    >>> gl.distribution(df, "age")
    >>> gl.correlation(df)

The glyphOcean theme is applied on import; call ``gl.set_theme()`` to reapply
or adjust it.
"""

from __future__ import annotations

from .plots import boxplot, correlation, counts, distribution, scatter
from .theme import PALETTE, color, set_theme

# Apply the glyphOcean look as soon as the library is imported.
set_theme()

__version__ = "0.2.0"

__all__ = [
    "distribution",
    "counts",
    "correlation",
    "scatter",
    "boxplot",
    "set_theme",
    "color",
    "PALETTE",
]
