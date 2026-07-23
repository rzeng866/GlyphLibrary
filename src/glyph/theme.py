"""The Glyph visual theme.

A single, cohesive look applied to every Glyph plot: a modern qualitative
palette, restrained gridlines, clean spines, and confident typography. The
theme is applied on import so plots look good with no setup; call
:func:`set_theme` to reapply or tweak it.
"""

from __future__ import annotations

import matplotlib.pyplot as plt
import seaborn as sns

#: Qualitative palette for categorical series — distinct but harmonious.
PALETTE = [
    "#3A7CA5",  # blue
    "#E76F51",  # coral
    "#2A9D8F",  # teal
    "#E9C46A",  # gold
    "#8E7DBE",  # violet
    "#6D9F71",  # sage
    "#D1495B",  # rose
    "#577590",  # slate
]

#: Sequential colormap for magnitude (e.g. counts, density).
SEQUENTIAL = "mako"

#: Diverging colormap for signed values (e.g. correlations).
DIVERGING = "vlag"

_INK = "#2B2B2B"
_GRID = "#E4E7EB"


def set_theme(*, context: str = "notebook", grid: bool = True) -> None:
    """Apply the Glyph theme to matplotlib/seaborn.

    Parameters
    ----------
    context:
        seaborn scaling context — ``"paper"``, ``"notebook"``, ``"talk"``,
        or ``"poster"``. Larger contexts scale fonts and line widths up.
    grid:
        Whether to draw a light horizontal grid.
    """
    sns.set_theme(
        context=context,
        style="whitegrid" if grid else "white",
        palette=PALETTE,
    )
    plt.rcParams.update(
        {
            "figure.figsize": (8, 5),
            "figure.dpi": 110,
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "axes.edgecolor": _INK,
            "axes.linewidth": 1.0,
            "axes.grid": grid,
            "axes.grid.axis": "y",
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.titlesize": 14,
            "axes.titleweight": "bold",
            "axes.titlepad": 12,
            "axes.titlecolor": _INK,
            "axes.labelsize": 11,
            "axes.labelcolor": _INK,
            "axes.labelweight": "normal",
            "text.color": _INK,
            "xtick.color": _INK,
            "ytick.color": _INK,
            "xtick.labelsize": 10,
            "ytick.labelsize": 10,
            "grid.color": _GRID,
            "grid.linewidth": 0.9,
            "legend.frameon": False,
            "legend.fontsize": 10,
            "savefig.bbox": "tight",
            "savefig.facecolor": "white",
        }
    )


def color(index: int = 0) -> str:
    """Return the palette color at ``index`` (wraps around)."""
    return PALETTE[index % len(PALETTE)]
