"""Plain-text summary rendering (terminal output, ``Profile.summary()``)."""

from __future__ import annotations

from ..core.profile import Profile


def render_summary(profile: Profile) -> str:
    lines: list[str] = []
    lines.append("Dataset overview")
    lines.append("-" * 40)
    lines.append(f"Rows            : {profile.n_rows:,}")
    lines.append(f"Columns         : {profile.n_columns:,}")
    lines.append(f"Duplicate rows  : {profile.n_duplicate_rows:,}")
    lines.append(
        f"Missing cells   : {profile.n_missing_cells:,} "
        f"({profile.missing_cells_pct:.1f}%)"
    )

    lines.append("")
    lines.append("Column types")
    lines.append("-" * 40)
    for stype, count in profile.type_counts().items():
        lines.append(f"{str(stype):<14}: {count}")

    lines.append("")
    lines.append("Columns")
    lines.append("-" * 40)
    for col in profile:
        lines.append(
            f"{col.name:<24} {str(col.semantic_type):<12} "
            f"missing={col.missing_pct:5.1f}%  unique={col.n_unique:,}"
        )
    return "\n".join(lines)
