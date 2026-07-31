"""Shared synthetic dataset for the Glyph examples."""

from __future__ import annotations

import numpy as np
import pandas as pd


def make_dataset(n: int = 600) -> pd.DataFrame:
    """A synthetic customer dataset used by the gallery example."""
    rng = np.random.default_rng(7)
    region = rng.choice(["North", "South", "East", "West"], n, p=[0.35, 0.25, 0.25, 0.15])
    base = {"North": 70, "South": 55, "East": 62, "West": 48}
    spend = np.array([rng.normal(base[r], 12) for r in region]).clip(5)

    # Sign-up timestamps spread across ~2 years, skewed toward recent.
    start = pd.Timestamp("2022-01-01")
    signup = start + pd.to_timedelta((rng.beta(2.2, 1.6, n) * 730).astype(int), unit="D")

    df = pd.DataFrame(
        {
            "region": region,
            "signup": signup,
            "age": rng.normal(41, 13, n).clip(18, 85),
            "spend": spend.round(2),
            "sessions": rng.poisson(8, n),
            "satisfaction": (spend / 10 + rng.normal(0, 1.5, n)).round(1),
        }
    )
    df.loc[rng.random(n) < 0.12, "spend"] = np.nan
    df.loc[rng.random(n) < 0.05, "age"] = np.nan
    return df
