"""Assemble a :class:`Profile` into a PDF report using reportlab.

matplotlib figures are rendered to in-memory PNG buffers and embedded as images,
so the whole report is produced without touching the filesystem until the final
write. reportlab handles page layout, tables, and text flow.
"""

from __future__ import annotations

import io

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    Image,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from ..analysis.correlations import top_correlated_pairs
from ..core.dtypes import SemanticType
from ..core.profile import ColumnProfile, Profile
from . import charts

_ACCENT = colors.HexColor("#3b6ea5")
_LIGHT = colors.HexColor("#eef2f6")


def render_pdf(profile: Profile, path: str, *, title: str = "Exploratory Data Analysis") -> str:
    """Render ``profile`` to a PDF at ``path``; return ``path``."""
    doc = SimpleDocTemplate(
        path,
        pagesize=letter,
        title=title,
        leftMargin=0.75 * inch,
        rightMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
    )
    styles = _styles()
    story: list = []

    _overview_section(story, profile, styles, title)
    _missingness_section(story, profile, styles)
    _correlation_section(story, profile, styles)
    _columns_section(story, profile, styles)

    doc.build(story)
    return path


def _styles():
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            "EdaTitle", parent=styles["Title"], fontSize=22, textColor=_ACCENT, spaceAfter=6
        )
    )
    styles.add(
        ParagraphStyle(
            "EdaH2",
            parent=styles["Heading2"],
            fontSize=14,
            textColor=_ACCENT,
            spaceBefore=14,
            spaceAfter=6,
        )
    )
    styles.add(
        ParagraphStyle(
            "EdaColName",
            parent=styles["Heading3"],
            fontSize=12,
            spaceBefore=10,
            spaceAfter=2,
        )
    )
    styles.add(ParagraphStyle("EdaMuted", parent=styles["Normal"], fontSize=8, textColor=colors.grey))
    return styles


def _fig_to_image(fig, width: float) -> Image:
    """Convert a matplotlib figure to a reportlab Image scaled to ``width`` points."""
    import matplotlib.pyplot as plt

    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    fig_w, fig_h = fig.get_size_inches()
    aspect = fig_h / fig_w
    return Image(buf, width=width, height=width * aspect)


def _kv_table(rows: list[tuple[str, str]], col_widths=(1.6 * inch, 2.4 * inch)) -> Table:
    table = Table([[k, v] for k, v in rows], colWidths=list(col_widths), hAlign="LEFT")
    table.setStyle(
        TableStyle(
            [
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("TEXTCOLOR", (0, 0), (0, -1), colors.grey),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                ("TOPPADDING", (0, 0), (-1, -1), 2),
                ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.white, _LIGHT]),
            ]
        )
    )
    return table


def _overview_section(story, profile: Profile, styles, title: str) -> None:
    story.append(Paragraph(title, styles["EdaTitle"]))
    story.append(
        Paragraph(
            f"{profile.n_rows:,} rows &times; {profile.n_columns:,} columns",
            styles["EdaMuted"],
        )
    )
    story.append(Spacer(1, 10))

    story.append(Paragraph("Dataset overview", styles["EdaH2"]))
    overview = _kv_table(
        [
            ("Rows", f"{profile.n_rows:,}"),
            ("Columns", f"{profile.n_columns:,}"),
            ("Duplicate rows", f"{profile.n_duplicate_rows:,}"),
            (
                "Missing cells",
                f"{profile.n_missing_cells:,} ({profile.missing_cells_pct:.1f}%)",
            ),
        ]
    )
    story.append(overview)

    story.append(Paragraph("Column types", styles["EdaH2"]))
    story.append(
        _kv_table([(str(t), str(n)) for t, n in profile.type_counts().items()])
    )


def _missingness_section(story, profile: Profile, styles) -> None:
    story.append(Paragraph("Missing values", styles["EdaH2"]))
    fig = charts.missingness_bar(profile)
    story.append(_fig_to_image(fig, width=6.5 * inch))


def _correlation_section(story, profile: Profile, styles) -> None:
    if profile.correlations is None:
        return
    story.append(PageBreak())
    story.append(Paragraph("Correlations", styles["EdaH2"]))
    fig = charts.correlation_heatmap(profile.correlations)
    story.append(_fig_to_image(fig, width=5.0 * inch))

    pairs = top_correlated_pairs(profile.correlations, limit=8)
    if pairs:
        story.append(Spacer(1, 8))
        story.append(Paragraph("Strongest pairs", styles["EdaColName"]))
        data = [["Column A", "Column B", "Pearson r"]]
        data += [[a, b, f"{r:+.2f}"] for a, b, r in pairs]
        table = Table(data, hAlign="LEFT")
        table.setStyle(
            TableStyle(
                [
                    ("FONTSIZE", (0, 0), (-1, -1), 8),
                    ("BACKGROUND", (0, 0), (-1, 0), _ACCENT),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, _LIGHT]),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                    ("TOPPADDING", (0, 0), (-1, -1), 3),
                ]
            )
        )
        story.append(table)


def _columns_section(story, profile: Profile, styles) -> None:
    story.append(PageBreak())
    story.append(Paragraph("Columns", styles["EdaH2"]))
    for col in profile:
        _column_block(story, col, styles)


def _column_block(story, col: ColumnProfile, styles) -> None:
    story.append(
        Paragraph(
            f"{col.name} &nbsp;<font size=8 color='grey'>({col.semantic_type})</font>",
            styles["EdaColName"],
        )
    )

    common_rows = [
        ("Stored dtype", col.dtype),
        ("Present", f"{col.n_present:,}"),
        ("Missing", f"{col.n_missing:,} ({col.missing_pct:.1f}%)"),
        ("Distinct", f"{col.n_unique:,} ({col.unique_pct:.1f}%)"),
    ]

    stats_rows = list(common_rows)
    chart_image = None

    if col.numeric is not None:
        s = col.numeric
        stats_rows += [
            ("Mean", f"{s.mean:.4g}"),
            ("Std", f"{s.std:.4g}"),
            ("Min / Max", f"{s.minimum:.4g} / {s.maximum:.4g}"),
            ("Median (IQR)", f"{s.median:.4g} ({s.iqr:.4g})"),
            ("Skew", f"{s.skew:.3g}"),
            ("Zeros / Negatives", f"{s.zeros:,} / {s.negatives:,}"),
        ]
        chart_image = _fig_to_image(charts.numeric_histogram(col), width=3.1 * inch)
    elif col.categorical is not None:
        stats_rows.append(("Categories", f"{col.categorical.n_categories:,}"))
        chart_image = _fig_to_image(charts.categorical_bar(col), width=3.1 * inch)
    elif col.datetime is not None:
        stats_rows += [
            ("Earliest", str(col.datetime.minimum)),
            ("Latest", str(col.datetime.maximum)),
            ("Span", str(col.datetime.span)),
        ]

    left = _kv_table(stats_rows, col_widths=(1.4 * inch, 1.7 * inch))
    right = chart_image if chart_image is not None else Paragraph("", styles["Normal"])

    layout = Table([[left, right]], colWidths=[3.2 * inch, 3.3 * inch], hAlign="LEFT")
    layout.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")]))
    story.append(layout)
    story.append(Spacer(1, 6))
    story.append(_hr())


def _hr():
    line = Table([[""]], colWidths=[6.5 * inch], rowHeights=[1])
    line.setStyle(TableStyle([("LINEBELOW", (0, 0), (-1, -1), 0.5, _LIGHT)]))
    return line
