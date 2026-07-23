"""edalibrary — small, plain-function EDA for pandas DataFrames.

    >>> import pandas as pd
    >>> from edalibrary import summarize, missing
    >>> df = pd.read_csv("data.csv")
    >>> summarize(df)   # per-column overview
    >>> missing(df)     # missing values per column
"""

from .core import missing, summarize

__version__ = "0.2.0"

__all__ = ["summarize", "missing"]
