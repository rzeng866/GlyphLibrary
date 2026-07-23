"""Minimal usage example (pandas only)."""

import pandas as pd

from edalibrary import missing, summarize

df = pd.DataFrame(
    {
        "age": [25, 32, 47, 51, None],
        "city": ["NY", "SF", "NY", "LA", "SF"],
        "income": [50_000, 82_000, None, 120_000, 61_000],
    }
)

print("summarize(df):")
print(summarize(df))

print("\nmissing(df):")
print(missing(df))
