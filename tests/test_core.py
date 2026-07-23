import pandas as pd
import pytest

from edalibrary import missing, summarize


@pytest.fixture
def df():
    return pd.DataFrame(
        {
            "age": [20, 30, 40, None],
            "name": ["a", "b", "c", "d"],
            "grade": ["x", "x", "y", "y"],
        }
    )


def test_summarize_returns_dataframe(df):
    result = summarize(df)
    assert isinstance(result, pd.DataFrame)
    assert list(result.index) == ["age", "name", "grade"]


def test_summarize_counts_and_missing(df):
    result = summarize(df)
    assert result.loc["age", "count"] == 3
    assert result.loc["age", "missing"] == 1
    assert result.loc["age", "missing_pct"] == 25.0
    assert result.loc["name", "missing"] == 0
    assert result.loc["grade", "unique"] == 2


def test_summarize_numeric_stats_only_for_numeric(df):
    result = summarize(df)
    assert result.loc["age", "min"] == 20
    assert result.loc["age", "max"] == 40
    # Non-numeric columns have NaN numeric stats.
    assert pd.isna(result.loc["name", "mean"])


def test_missing_returns_dataframe_sorted(df):
    result = missing(df)
    assert isinstance(result, pd.DataFrame)
    assert list(result.columns) == ["missing", "percent"]
    # Worst first.
    assert result.index[0] == "age"
    assert result.loc["age", "missing"] == 1
    assert result.loc["name", "missing"] == 0


def test_missing_percent(df):
    result = missing(df)
    assert result.loc["age", "percent"] == 25.0


def test_summarize_rejects_non_dataframe():
    with pytest.raises(TypeError):
        summarize([1, 2, 3])


def test_missing_rejects_non_dataframe():
    with pytest.raises(TypeError):
        missing({"a": 1})
