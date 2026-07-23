import numpy as np
import pandas as pd
import pytest

import edalibrary as eda
from edalibrary.core.dtypes import SemanticType


@pytest.fixture
def df():
    rng = np.random.default_rng(0)
    return pd.DataFrame(
        {
            "id": [f"C{i}" for i in range(50)],
            "value": rng.normal(10, 2, 50),
            "grade": rng.choice(["A", "B", "C"], 50),
            "flag": rng.random(50) < 0.5,
            "empty": [np.nan] * 50,
        }
    )


def test_profile_shape(df):
    p = eda.profile(df)
    assert p.n_rows == 50
    assert p.n_columns == 5
    assert len(p) == 5


def test_semantic_types(df):
    p = eda.profile(df)
    assert p["id"].semantic_type == SemanticType.UNIQUE
    assert p["value"].semantic_type == SemanticType.NUMERIC
    assert p["grade"].semantic_type == SemanticType.CATEGORICAL
    assert p["flag"].semantic_type == SemanticType.BOOLEAN
    assert p["empty"].semantic_type == SemanticType.EMPTY


def test_numeric_stats_present(df):
    stats = eda.profile(df)["value"].numeric
    assert stats is not None
    assert stats.minimum <= stats.median <= stats.maximum
    assert stats.histogram is not None
    assert len(stats.histogram.edges) == len(stats.histogram.counts) + 1


def test_missing_accounting():
    df = pd.DataFrame({"a": [1, 2, None, 4], "b": [None, None, 3, 4]})
    p = eda.profile(df)
    assert p["a"].n_missing == 1
    assert p["b"].n_missing == 2
    assert p.n_missing_cells == 3
    assert p["a"].missing_pct == 25.0


def test_duplicate_rows():
    df = pd.DataFrame({"a": [1, 1, 2], "b": ["x", "x", "y"]})
    assert eda.profile(df).n_duplicate_rows == 1


def test_correlations_need_two_numeric():
    one = pd.DataFrame({"a": [1.0, 2.0, 3.0], "b": ["x", "y", "z"]})
    assert eda.profile(one).correlations is None

    # Continuous (non-integral, high-cardinality) values stay NUMERIC.
    a = np.linspace(0.0, 1.0, 30) + 0.001
    two = pd.DataFrame({"a": a, "b": a * 2.0})
    corr = eda.profile(two).correlations
    assert corr is not None
    assert corr.loc["a", "b"] == pytest.approx(1.0)


def test_getitem_and_iteration(df):
    p = eda.profile(df)
    names = [c.name for c in p]
    assert names == list(df.columns)


def test_rejects_non_dataframe():
    with pytest.raises(TypeError):
        eda.profile([1, 2, 3])


def test_rejects_no_columns():
    with pytest.raises(ValueError):
        eda.profile(pd.DataFrame())


def test_summary_is_string(df):
    assert "Dataset overview" in eda.profile(df).summary()
