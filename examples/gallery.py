"""Render a gallery of Glyph plots to a single PNG.

Builds a synthetic dataset and lays out one example of each plotting function.
"""

from __future__ import annotations

import matplotlib.pyplot as plt

import glyph
from _data import make_dataset


def main() -> str:
    df = make_dataset()

    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    glyph.distribution(df, "age", ax=axes[0, 0])          # a numeric field
    glyph.counts(df, "region", ax=axes[0, 1])             # a categorical field
    glyph.correlation(df, ax=axes[0, 2])                  # relationships (matrix)
    glyph.scatter(df, "spend", "satisfaction", hue="region", ax=axes[1, 0])  # relationship
    glyph.boxplot(df, "region", "spend", ax=axes[1, 1])   # numeric across categories
    axes[1, 2].axis("off")                                # spare cell

    fig.suptitle("Glyph gallery", fontsize=22, fontweight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.97))
    out = "glyph_gallery.png"
    fig.savefig(out, dpi=120)
    print(f"Wrote {out}")
    return out


if __name__ == "__main__":
    main()
