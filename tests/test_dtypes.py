import numpy as np
import pandas as pd

from edalibrary.core.dtypes import SemanticType, infer_semantic_type


def test_empty_column():
    s = pd.Series([None, None, np.nan], dtype="object")
    assert infer_semantic_type(s) == SemanticType.EMPTY


def test_constant_column():
    assert infer_semantic_type(pd.Series([7, 7, 7, 7])) == SemanticType.CONSTANT


def test_boolean_column():
    assert infer_semantic_type(pd.Series([True, False, True])) == SemanticType.BOOLEAN


def test_datetime_column():
    s = pd.to_datetime(pd.Series(["2020-01-01", "2021-06-01", "2022-03-03"]))
    assert infer_semantic_type(s) == SemanticType.DATETIME


def test_continuous_numeric():
    s = pd.Series(np.linspace(0, 100, 200))
    assert infer_semantic_type(s) == SemanticType.NUMERIC


def test_low_cardinality_integer_is_categorical():
    # An encoded rating 1-5 reads better as categorical.
    s = pd.Series([1, 2, 3, 4, 5] * 20)
    assert infer_semantic_type(s) == SemanticType.CATEGORICAL


def test_high_cardinality_integer_is_numeric():
    s = pd.Series(range(100))
    assert infer_semantic_type(s) == SemanticType.NUMERIC


def test_string_categories():
    s = pd.Series(["a", "b", "c", "a", "b"] * 10)
    assert infer_semantic_type(s) == SemanticType.CATEGORICAL


def test_unique_identifier():
    s = pd.Series([f"id{i}" for i in range(100)])
    assert infer_semantic_type(s) == SemanticType.UNIQUE


def test_free_text():
    # Many distinct-but-repeating strings, below the unique ratio threshold.
    base = [f"note number {i}" for i in range(40)]
    s = pd.Series(base * 3)
    assert infer_semantic_type(s) == SemanticType.TEXT
