"""Render a gallery of Glyph plots to a single PNG.

Builds a synthetic user/content-metadata dataset and lays out one example of
each single-axes plotting function, ending with a full-width temporal panel.
"""

from __future__ import annotations

import matplotlib.pyplot as plt

import glyph
from _data import make_dataset


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
