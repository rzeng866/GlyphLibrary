import matplotlib

matplotlib.use("Agg")  # headless backend for tests

import matplotlib.pyplot as plt
import pandas as pd
import pytest
import seaborn as sns

import glyph


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
            "z": [10.0, None, 30.0, None, 50.0, 60.0],
        }
    )


def test_distribution_returns_axes(df):
    ax = glyph.distribution(df, "x")
    assert isinstance(ax, plt.Axes)
    assert "x" in ax.get_title()


def test_distribution_with_hue(df):
    ax = glyph.distribution(df, "x", hue="group")
    assert isinstance(ax, plt.Axes)


def test_counts_returns_axes_and_top(df):
    ax = glyph.counts(df, "group", top=2)
    assert isinstance(ax, plt.Axes)
    # top=2 -> two bars.
    assert len(ax.patches) == 2


def test_correlation_returns_axes(df):
    ax = glyph.correlation(df)
    assert isinstance(ax, plt.Axes)


def test_correlation_needs_two_numeric():
    with pytest.raises(ValueError):
        glyph.correlation(pd.DataFrame({"only": [1.0, 2.0, 3.0]}))


def test_scatter_returns_axes(df):
    ax = glyph.scatter(df, "x", "y", hue="group")
    assert isinstance(ax, plt.Axes)


def test_boxplot_returns_axes(df):
    ax = glyph.boxplot(df, "group", "x")
    assert isinstance(ax, plt.Axes)


@pytest.fixture
def tdf():
    dates = pd.date_range("2023-01-01", periods=24, freq="D")
    return pd.DataFrame(
        {
            "created": list(dates) + list(dates),
            "value": list(range(24)) + list(range(24, 48)),
            "kind": ["a"] * 24 + ["b"] * 24,
        }
    )


def test_timeseries_counts_returns_axes(tdf):
    ax = glyph.timeseries(tdf, "created", freq="W")
    assert isinstance(ax, plt.Axes)
    assert ax.get_ylabel() == "records"


def test_timeseries_value_and_agg(tdf):
    ax = glyph.timeseries(tdf, "created", "value", freq="W", agg="sum")
    assert isinstance(ax, plt.Axes)
    assert "value" in ax.get_ylabel()


def test_timeseries_hue_draws_multiple_lines(tdf):
    ax = glyph.timeseries(tdf, "created", "value", hue="kind", freq="W")
    # One line per category.
    assert len(ax.get_lines()) >= 2


def test_timeseries_parses_string_dates():
    df = pd.DataFrame({"day": ["2023-01-01", "2023-02-01", "2023-03-01"], "v": [1, 2, 3]})
    ax = glyph.timeseries(df, "day", "v")
    assert isinstance(ax, plt.Axes)


def test_timeseries_bad_dates_raise():
    df = pd.DataFrame({"day": ["not", "a", "date"], "v": [1, 2, 3]})
    with pytest.raises(ValueError):
        glyph.timeseries(df, "day", "v")


def test_missing_returns_axes(df):
    ax = glyph.missing(df)
    assert isinstance(ax, plt.Axes)


def test_missing_with_no_missing_values():
    ax = glyph.missing(pd.DataFrame({"a": [1, 2], "b": [3, 4]}))
    assert isinstance(ax, plt.Axes)


def test_pairplot_returns_pairgrid(df):
    grid = glyph.pairplot(df[["x", "y", "z"]])
    assert isinstance(grid, sns.axisgrid.PairGrid)


def test_unknown_column_raises(df):
    with pytest.raises(KeyError):
        glyph.distribution(df, "does_not_exist")


def test_non_dataframe_raises():
    with pytest.raises(TypeError):
        glyph.correlation([1, 2, 3])


def test_public_api():
    for name in ("distribution", "counts", "correlation", "scatter", "boxplot", "timeseries", "missing", "pairplot", "set_theme", "PALETTE"):
        assert hasattr(glyph, name)
