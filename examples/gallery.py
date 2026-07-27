"""Render a gallery of Glyph plots to a single PNG.

Builds a synthetic user/content-metadata dataset and lays out one example of
each single-axes plotting function, ending with a full-width temporal panel.
"""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import glyph


def make_dataset(n: int = 600) -> pd.DataFrame:
    rng = np.random.default_rng(7)
    region = rng.choice(["North", "South", "East", "West"], n, p=[0.35, 0.25, 0.25, 0.15])
    base = {"North": 70, "South": 55, "East": 62, "West": 48}
    spend = np.array([rng.normal(base[r], 12) for r in region]).clip(5)

    # Sign-up timestamps spread across ~2 years, with a rising trend.
    start = pd.Timestamp("2022-01-01")
    day_offsets = (rng.beta(2.2, 1.6, n) * 730).astype(int)  # skew toward recent
    signup = start + pd.to_timedelta(day_offsets, unit="D")

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


def main() -> str:
    df = make_dataset()

    fig, axd = plt.subplot_mosaic(
        [
            ["dist", "counts", "corr"],
            ["scatter", "box", "missing"],
            ["ts", "ts", "ts"],
        ],
        figsize=(18, 15),
    )

    # Numeric field
    glyph.distribution(df, "age", ax=axd["dist"])
    # Single categorical field
    glyph.counts(df, "region", ax=axd["counts"])
    # Relationships between fields
    glyph.correlation(df, ax=axd["corr"])
    glyph.scatter(df, "spend", "satisfaction", hue="region", ax=axd["scatter"])
    # Numeric compared across a category
    glyph.boxplot(df, "region", "spend", ax=axd["box"])
    # Data quality
    glyph.missing(df, ax=axd["missing"])
    # Temporal metadata (colors compare regions over time)
    glyph.timeseries(df, "signup", "spend", freq="MS", agg="mean", hue="region", ax=axd["ts"])

    fig.suptitle("Glyph gallery", fontsize=22, fontweight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.98))
    out = "glyph_gallery.png"
    fig.savefig(out, dpi=120)
    print(f"Wrote {out}")
    return out


if __name__ == "__main__":
    main()
