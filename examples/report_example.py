"""Render a full narrative Glyph report to glyph_report.png."""

from __future__ import annotations

import glyph
from _data import make_dataset


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
