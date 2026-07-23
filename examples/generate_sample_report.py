"""Build a synthetic dataset and render an EDA report to demonstrate the library."""

from __future__ import annotations

import numpy as np
import pandas as pd

import edalibrary as eda


def make_dataset(n: int = 500) -> pd.DataFrame:
    rng = np.random.default_rng(42)
    df = pd.DataFrame(
        {
            "customer_id": [f"C{i:05d}" for i in range(n)],
            "age": rng.normal(40, 12, n).clip(18, 90).round().astype(int),
            "income": (rng.lognormal(10.5, 0.4, n)).round(2),
            "signup_date": pd.to_datetime("2022-01-01")
            + pd.to_timedelta(rng.integers(0, 900, n), unit="D"),
            "plan": rng.choice(["free", "pro", "enterprise"], n, p=[0.6, 0.3, 0.1]),
            "satisfaction": rng.integers(1, 6, n),
            "churned": rng.random(n) < 0.22,
            "notes": rng.choice(["", "follow up", "vip", "complaint"], n),
        }
    )
    # Inject some missingness.
    df.loc[rng.random(n) < 0.15, "income"] = np.nan
    df.loc[rng.random(n) < 0.05, "age"] = np.nan
    return df


if __name__ == "__main__":
    df = make_dataset()
    report = eda.profile(df)
    print(report.summary())
    out = report.to_pdf("sample_report.pdf", title="Customer Dataset EDA")
    print(f"\nWrote {out}")
