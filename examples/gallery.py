"""Render a gallery of Glyph plots to a single PNG.

Builds a synthetic dataset and lays out one example of each plotting function.
"""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import glyph


def make_dataset(n: int = 400) -> pd.DataFrame:
    rng = np.random.default_rng(7)
    region = rng.choice(["North", "South", "East", "West"], n, p=[0.35, 0.25, 0.25, 0.15])
    base = {"North": 70, "South": 55, "East": 62, "West": 48}
    spend = np.array([rng.normal(base[r], 12) for r in region]).clip(5)
    df = pd.DataFrame(
        {
            "region": region,
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

    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    glyph.distribution(df, "age", ax=axes[0, 0])
    glyph.counts(df, "region", ax=axes[0, 1])
    glyph.correlation(df, ax=axes[0, 2])
    glyph.scatter(df, "spend", "satisfaction", hue="region", ax=axes[1, 0])
    glyph.boxplot(df, "region", "spend", ax=axes[1, 1])
    glyph.missing(df, ax=axes[1, 2])

    fig.suptitle("Glyph gallery", fontsize=20, fontweight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.97))
    out = "glyph_gallery.png"
    fig.savefig(out, dpi=120)
    print(f"Wrote {out}")
    return out


if __name__ == "__main__":
    main()
