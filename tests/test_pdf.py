import numpy as np
import pandas as pd

import edalibrary as eda


def _dataset():
    rng = np.random.default_rng(1)
    return pd.DataFrame(
        {
            "id": [f"C{i}" for i in range(60)],
            "x": rng.normal(0, 1, 60),
            "y": rng.normal(5, 2, 60),
            "cat": rng.choice(["p", "q", "r"], 60),
            "when": pd.to_datetime("2023-01-01") + pd.to_timedelta(rng.integers(0, 365, 60), unit="D"),
        }
    )


def test_to_pdf_writes_file(tmp_path):
    out = tmp_path / "report.pdf"
    result = eda.profile(_dataset()).to_pdf(str(out))
    assert result == str(out)
    assert out.exists()
    # A real PDF starts with the %PDF magic bytes and is non-trivial in size.
    header = out.read_bytes()[:5]
    assert header == b"%PDF-"
    assert out.stat().st_size > 1000


def test_to_pdf_without_correlations(tmp_path):
    # Single numeric column -> no correlation section; must still render.
    df = pd.DataFrame({"only": [1.0, 2.0, 3.0, 4.0], "label": ["a", "b", "c", "d"]})
    out = tmp_path / "r.pdf"
    eda.profile(df).to_pdf(str(out))
    assert out.exists()
