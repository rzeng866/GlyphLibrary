"""Render a full narrative Glyph report to glyph_report.png."""

from __future__ import annotations

import numpy as np
import pandas as pd

import glyph


def make_dataset(n: int = 600) -> pd.DataFrame:
    rng = np.random.default_rng(7)
    region = rng.choice(["North", "South", "East", "West"], n, p=[0.35, 0.25, 0.25, 0.15])
    base = {"North": 70, "South": 55, "East": 62, "West": 48}
    spend = np.array([rng.normal(base[r], 12) for r in region]).clip(5)
    start = pd.Timestamp("2022-01-01")
    signup = start + pd.to_timedelta((rng.beta(2.2, 1.6, n) * 730).astype(int), unit="D")
    df = pd.DataFrame(
        {
            "region": region,
            "signup": signup,
            "age": rng.normal(41, 13, n).clip(18, 85),
            "spend": spend.round(2),
            "sessions": rng.poisson(8, n),
            "satisfaction": (spend / 10 + rng.normal(0, 1.5, n)).round(1),
        }
    )
    df.loc[rng.random(n) < 0.12, "spend"] = np.nan
    df.loc[rng.random(n) < 0.05, "age"] = np.nan
    return df


def main() -> str:
    df = make_dataset()
    out = "glyph_report.png"
    glyph.report(
        df,
        title="Customer Metadata — Exploratory Analysis",
        context=(
            "Each row is a signed-up customer with region, sign-up date, age, monthly "
            "spend, session count, and a satisfaction score. The data covers sign-ups "
            "across 2022–2023 and contains some missing spend and age values."
        ),
        objective=(
            "Understand what drives customer satisfaction, so retention efforts can "
            "target the fields that matter most."
        ),
        target="satisfaction",
        units={"age": "years", "spend": "$/mo", "satisfaction": "pts"},
        path=out,
    )
    print(f"Wrote {out}")
    return out


if __name__ == "__main__":
    main()
