"""Chart builders. Each returns a matplotlib Figure the PDF renderer embeds.

matplotlib is imported with the non-interactive ``Agg`` backend so charts render
identically with or without a display (servers, CI, notebooks).
"""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")  # noqa: E402  (must precede pyplot import)

import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

from ..core.profile import ColumnProfile, Profile  # noqa: E402

# Muted, print-friendly palette.
_ACCENT = "#3b6ea5"
_MUTED = "#9aa5b1"
_FIGSIZE = (5.2, 2.6)


def _new_axes():
    fig, ax = plt.subplots(figsize=_FIGSIZE, dpi=150)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    return fig, ax


def numeric_histogram(profile: ColumnProfile):
    """Distribution histogram for a numeric column, from precomputed bins."""
    fig, ax = _new_axes()
    stats = profile.numeric
    if stats is None or stats.histogram is None:
        ax.text(0.5, 0.5, "no data", ha="center", va="center")
        return fig
    edges = stats.histogram.edges
    counts = stats.histogram.counts
    widths = [edges[i + 1] - edges[i] for i in range(len(counts))]
    ax.bar(
        edges[:-1],
        counts,
        width=widths,
        align="edge",
        color=_ACCENT,
        edgecolor="white",
        linewidth=0.4,
    )
    ax.axvline(
        stats.median, color="#c0392b", linestyle="--", linewidth=1, label="median"
    )
    ax.legend(fontsize=7, frameon=False)
    ax.set_ylabel("count", fontsize=8)
    ax.tick_params(labelsize=7)
    fig.tight_layout()
    return fig


def categorical_bar(profile: ColumnProfile):
    """Horizontal bar chart of the most frequent categories."""
    fig, ax = _new_axes()
    cats = profile.categorical
    if cats is None or not cats.top:
        ax.text(0.5, 0.5, "no data", ha="center", va="center")
        return fig
    labels = [str(v)[:24] for v, _ in cats.top][::-1]
    counts = [c for _, c in cats.top][::-1]
    ax.barh(labels, counts, color=_ACCENT)
    ax.set_xlabel("count", fontsize=8)
    ax.tick_params(labelsize=7)
    fig.tight_layout()
    return fig


def missingness_bar(profile: Profile):
    """Percentage of missing values per column, worst first."""
    cols = sorted(profile, key=lambda c: c.missing_pct, reverse=True)
    cols = [c for c in cols if c.missing_pct > 0]
    fig, ax = plt.subplots(figsize=(6.6, max(2.0, 0.28 * len(cols) + 0.6)), dpi=150)
    if not cols:
        ax.text(0.5, 0.5, "No missing values", ha="center", va="center", fontsize=10)
        ax.axis("off")
        return fig
    names = [c.name[:28] for c in cols][::-1]
    pct = [c.missing_pct for c in cols][::-1]
    ax.barh(names, pct, color=_MUTED)
    ax.set_xlabel("% missing", fontsize=8)
    ax.set_xlim(0, 100)
    ax.tick_params(labelsize=7)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    return fig


def correlation_heatmap(corr: pd.DataFrame):
    """Heatmap of a correlation matrix."""
    n = len(corr.columns)
    fig, ax = plt.subplots(figsize=(min(7, 1 + 0.5 * n), min(6, 1 + 0.5 * n)), dpi=150)
    im = ax.imshow(corr.values, cmap="RdBu_r", vmin=-1, vmax=1, aspect="auto")
    ax.set_xticks(range(n))
    ax.set_yticks(range(n))
    ax.set_xticklabels([str(c)[:12] for c in corr.columns], rotation=45, ha="right", fontsize=7)
    ax.set_yticklabels([str(c)[:12] for c in corr.columns], fontsize=7)
    # Annotate cells when the matrix is small enough to stay legible.
    if n <= 8:
        for i in range(n):
            for j in range(n):
                val = corr.values[i, j]
                ax.text(
                    j,
                    i,
                    f"{val:.2f}",
                    ha="center",
                    va="center",
                    fontsize=6,
                    color="white" if abs(val) > 0.5 else "black",
                )
    fig.colorbar(im, ax=ax, shrink=0.8).ax.tick_params(labelsize=7)
    fig.tight_layout()
    return fig
