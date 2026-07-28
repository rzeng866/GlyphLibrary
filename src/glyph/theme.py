"""The Glyph visual theme.

A single, cohesive look applied to every Glyph plot: a modern qualitative
palette, restrained gridlines, clean spines, and confident typography. The
theme is applied on import so plots look good with no setup; call
:func:`set_theme` to reapply or tweak it.
"""

from __future__ import annotations

import matplotlib.pyplot as plt
import seaborn as sns

#: Ocean-themed qualitative palette — shades of blue, green, and coral. Used
#: only when a chart must compare groups (a ``hue``); single-series charts use
#: NEUTRAL + HIGHLIGHT instead.
PALETTE = [
    "#1B6CA8",  # ocean blue
    "#E76F51",  # coral
    "#2A9D8F",  # teal green
    "#48B0C4",  # lagoon blue
    "#5FB49C",  # seafoam green
    "#F4A26B",  # soft coral
    "#0A4F6E",  # deep navy
    "#8ED2C3",  # pale aqua
]

#: The quiet default: most marks in a single-series chart use this muted
#: sea-mist so nothing competes for attention.
NEUTRAL = "#A6BCC6"

#: The one loud color: a bright coral reserved for the single data point worth
#: noticing (biggest category, most-incomplete column, median line, strongest
#: correlation).
HIGHLIGHT = "#FF5A36"

#: Sequential colormap for magnitude — an ocean blue→green ramp.
SEQUENTIAL = "crest"

#: Diverging colormap for signed values (e.g. correlations) — teal↓ / coral↑,
#: built once at import so it stays on-theme with the palette.
DIVERGING = sns.diverging_palette(200, 20, s=80, l=55, sep=1, as_cmap=True)

#: Muted gray for secondary text — plot subtitles and report body copy.
MUTED = "#5F6B7A"

_INK = "#22262B"  # near-black for titles and data labels (high contrast)
_TICK = "#7A828C"  # faint gray for ticks and their labels
_SPINE = "#CBD2D9"  # light spine
_GRID = "#EDF0F3"  # very light gridlines


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
            # Clean sans-serif; falls back to DejaVu Sans if Arial/Roboto absent.
            "font.family": "sans-serif",
            "font.sans-serif": ["Arial", "Roboto", "Helvetica Neue", "Helvetica", "DejaVu Sans"],
            "figure.figsize": (8, 5),
            "figure.dpi": 110,
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "axes.axisbelow": True,  # gridlines behind the data
            # Declutter: only the left/bottom spines, light and thin.
            "axes.edgecolor": _SPINE,
            "axes.linewidth": 0.8,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.grid": grid,
            "axes.grid.axis": "y",  # one direction only
            # Hierarchy: big bold title, medium labels, small faint ticks.
            "axes.titlesize": 15,
            "axes.titleweight": "bold",
            "axes.titlepad": 14,
            "axes.titlecolor": _INK,
            "axes.labelsize": 11,
            "axes.labelcolor": _INK,
            "axes.labelweight": "normal",
            "axes.labelpad": 8,
            "text.color": _INK,
            "xtick.color": _TICK,
            "ytick.color": _TICK,
            "xtick.labelsize": 9,
            "ytick.labelsize": 9,
            "xtick.major.size": 0,  # no tick marks; labels carry the axis
            "ytick.major.size": 0,
            "grid.color": _GRID,
            "grid.linewidth": 0.8,
            "legend.frameon": False,
            "legend.fontsize": 10,
            "legend.title_fontsize": 10,
            "savefig.bbox": "tight",
            "savefig.facecolor": "white",
        }
    )


def color(index: int = 0) -> str:
    """Return the palette color at ``index`` (wraps around)."""
    return PALETTE[index % len(PALETTE)]
