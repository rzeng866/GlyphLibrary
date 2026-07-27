import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pytest

import glyph
from glyph import insights


@pytest.fixture(autouse=True)
def _close_figures():
    yield
    plt.close("all")


@pytest.fixture
def df():
    rng = np.random.default_rng(0)
    n = 120
    spend = rng.normal(60, 15, n)
    return pd.DataFrame(
        {
            "region": rng.choice(["N", "S", "E"], n),
            "signup": pd.Timestamp("2022-01-01") + pd.to_timedelta(rng.integers(0, 500, n), unit="D"),
            "age": rng.normal(40, 10, n),
            "spend": spend,
            "satisfaction": spend / 10 + rng.normal(0, 1, n),
        }
    )


def test_report_returns_figure(df):
    fig = glyph.report(df, target="satisfaction")
    assert isinstance(fig, plt.Figure)


def test_report_saves_file(df, tmp_path):
    out = tmp_path / "r.png"
    glyph.report(df, target="satisfaction", path=str(out))
    assert out.exists() and out.stat().st_size > 1000


def test_report_auto_picks_target(df):
    # No target given -> should still render.
    fig = glyph.report(df)
    assert isinstance(fig, plt.Figure)


def test_report_rejects_non_dataframe():
    with pytest.raises(TypeError):
        glyph.report([1, 2, 3])


def test_report_unknown_target_raises(df):
    with pytest.raises(KeyError):
        glyph.report(df, target="nope")


def test_report_handles_minimal_frame():
    # Single categorical column: no numeric target, must not crash.
    small = pd.DataFrame({"kind": ["a", "b", "a", "c"]})
    fig = glyph.report(small)
    assert isinstance(fig, plt.Figure)


# --- units and describe on individual plots ---------------------------------


def test_units_appear_on_axis(df):
    ax = glyph.distribution(df, "spend", units={"spend": "$"})
    assert "($)" in ax.get_xlabel()


def test_describe_adds_subtitle_annotation(df):
    ax = glyph.distribution(df, "spend", describe=True)
    texts = [t.get_text() for t in ax.texts]
    assert any("median" in t for t in texts)


def test_describe_false_no_insight(df):
    ax = glyph.correlation(df, describe=False)
    # Title is still set; no subtitle annotation with "link".
    assert not any("link" in t.get_text().lower() for t in ax.texts)


# --- insight helpers --------------------------------------------------------


def test_distribution_insight_reports_median():
    s = pd.Series([1, 2, 3, 4, 100])
    assert "median" in insights.distribution_insight(s, unit="kg")


def test_rank_numeric_drivers_orders_by_abs_r(df):
    ranked = insights.rank_numeric_drivers(df, "satisfaction")
    names = [name for name, _ in ranked]
    assert names[0] == "spend"  # strongest by construction


def test_missing_insight_when_complete():
    assert "No missing" in insights.missing_insight(pd.DataFrame({"a": [1, 2]}))
