import matplotlib

matplotlib.use("Agg")  # headless backend for tests

import matplotlib.colors as mcolors
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import pandas as pd
import pytest

import glyphOcean
from glyphOcean import theme
from glyphOcean.plots import _hue_palette


@pytest.fixture(autouse=True)
def _close_figures():
    yield
    plt.close("all")


@pytest.fixture
def df():
    return pd.DataFrame(
        {
            "group": ["a", "b", "a", "c", "b", "a"],
            "x": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0],
            "y": [2.0, 1.0, 4.0, 3.0, 6.0, 5.0],
        }
    )


# --- return types & titles --------------------------------------------------


def test_distribution_returns_axes_with_title(df):
    ax = glyphOcean.distribution(df, "x")
    assert isinstance(ax, plt.Axes)
    assert ax.get_title() == "Distribution of X"


def test_distribution_with_hue(df):
    assert isinstance(glyphOcean.distribution(df, "x", hue="group"), plt.Axes)


def test_scatter_returns_axes(df):
    assert isinstance(glyphOcean.scatter(df, "x", "y", hue="group"), plt.Axes)


def test_titles_are_properly_capitalized(df):
    assert glyphOcean.scatter(df, "x", "y").get_title() == "Y vs X"
    assert glyphOcean.boxplot(df, "group", "x").get_title() == "X by Group"
    assert glyphOcean.counts(df, "group").get_title() == "Counts of Group"


# --- counts -----------------------------------------------------------------


def test_counts_top_limits_bars(df):
    ax = glyphOcean.counts(df, "group", top=2)
    assert len(ax.patches) == 2


def test_counts_highlights_most_frequent_bar(df):
    ax = glyphOcean.counts(df, "group")
    top = mcolors.to_hex(ax.patches[0].get_facecolor())
    rest = mcolors.to_hex(ax.patches[1].get_facecolor())
    assert top.lower() == theme.HIGHLIGHT_MUTED.lower()
    assert rest.lower() == theme.NEUTRAL.lower()


# --- correlation ------------------------------------------------------------


def test_correlation_returns_axes(df):
    assert isinstance(glyphOcean.correlation(df), plt.Axes)


def test_correlation_needs_two_numeric():
    with pytest.raises(ValueError):
        glyphOcean.correlation(pd.DataFrame({"only": [1.0, 2.0, 3.0]}))


def test_correlation_outlines_strongest_cell(df):
    ax = glyphOcean.correlation(df)
    outlines = [
        p
        for p in ax.patches
        if isinstance(p, mpatches.Rectangle)
        and not p.get_fill()
        and mcolors.to_hex(p.get_edgecolor()).lower() == theme.HIGHLIGHT.lower()
    ]
    assert len(outlines) == 1


# --- boxplot ----------------------------------------------------------------


def test_boxplot_highlights_highest_median():
    data = pd.DataFrame({"g": ["a"] * 5 + ["b"] * 5, "v": [1, 1, 1, 1, 1, 9, 9, 9, 9, 9]})
    ax = glyphOcean.boxplot(data, "g", "v")  # "b" has the higher median
    highlighted = [
        i
        for i, p in enumerate(ax.patches)
        if mcolors.to_hex(p.get_facecolor()).lower() == theme.HIGHLIGHT_MUTED.lower()
    ]
    assert highlighted == [1]


# --- colors -----------------------------------------------------------------


def test_few_categories_use_brand_palette():
    pal = _hue_palette(pd.Series(["a", "b", "c"]))
    assert [mcolors.to_hex(c) for c in pal.values()] == [
        theme.color(0).lower(),
        theme.color(1).lower(),
        theme.color(2).lower(),
    ]


def test_many_categories_are_all_distinct():
    levels = [f"cat{i}" for i in range(9)]
    pal = _hue_palette(pd.Series(levels))
    hexes = [mcolors.to_hex(c) for c in pal.values()]
    assert len(set(hexes)) == 9


# --- error paths & API ------------------------------------------------------


def test_unknown_column_raises(df):
    with pytest.raises(KeyError):
        glyphOcean.distribution(df, "nope")


def test_non_dataframe_raises():
    with pytest.raises(TypeError):
        glyphOcean.correlation([1, 2, 3])


def test_public_api():
    for name in ("distribution", "counts", "correlation", "scatter", "boxplot", "set_theme", "PALETTE"):
        assert hasattr(glyphOcean, name)
