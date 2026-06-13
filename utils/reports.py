"""PDF and Excel report generation."""

from __future__ import annotations

import io
from datetime import datetime
from typing import Any

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from utils.insights import insights_to_markdown
from utils.profiling import build_dataset_profile


def generate_excel_report(
    df: pd.DataFrame,
    profile: dict[str, Any] | None = None,
    insights: dict[str, Any] | None = None,
) -> bytes:
    """
    Generate a multi-sheet Excel summary report.

    Sheets: Overview, Data Preview, Statistics, Insights.
    """
    if profile is None:
        profile = build_dataset_profile(df)

    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        # Overview sheet
        overview_rows = [
            ["Metric", "Value"],
            ["Total Rows", profile["rows"]],
            ["Total Columns", profile["columns"]],
            ["Missing Values", profile["total_missing"]],
            ["Missing %", profile["missing_percentage"]],
            ["Duplicate Rows", profile["duplicate_rows"]],
            ["Numerical Features", len(profile["column_types"]["numerical"])],
            ["Categorical Features", len(profile["column_types"]["categorical"])],
            ["Datetime Features", len(profile["column_types"]["datetime"])],
            ["Memory Usage (MB)", profile["memory_usage_mb"]],
        ]
        pd.DataFrame(overview_rows[1:], columns=overview_rows[0]).to_excel(
            writer, sheet_name="Overview", index=False
        )

        df.head(100).to_excel(writer, sheet_name="Data Preview", index=False)

        numerical = df.select_dtypes(include="number")
        if not numerical.empty:
            numerical.describe().T.to_excel(writer, sheet_name="Statistics")

        if insights:
            insight_rows: list[list[str]] = [["Category", "Insight"]]
            for category, items in insights.items():
                if isinstance(items, list):
                    for item in items:
                        insight_rows.append([category.replace("_", " ").title(), str(item)])
            pd.DataFrame(insight_rows[1:], columns=insight_rows[0]).to_excel(
                writer, sheet_name="Insights", index=False
            )

    return buffer.getvalue()


def generate_pdf_report(
    df: pd.DataFrame,
    profile: dict[str, Any] | None = None,
    insights: dict[str, Any] | None = None,
    title: str = "AI Data Analyst Report",
) -> bytes:
    """Generate a PDF summary report with overview, stats, and insights."""
    if profile is None:
        profile = build_dataset_profile(df)

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.75 * inch)
    styles = getSampleStyleSheet()
    story: list[Any] = []

    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Heading1"],
        fontSize=20,
        spaceAfter=12,
        textColor=colors.HexColor("#1f4e79"),
    )
    story.append(Paragraph(title, title_style))
    story.append(
        Paragraph(
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            styles["Normal"],
        )
    )
    story.append(Spacer(1, 0.25 * inch))

    # Overview table
    overview_data = [
        ["Metric", "Value"],
        ["Total Records", f"{profile['rows']:,}"],
        ["Columns", str(profile["columns"])],
        ["Missing Values", f"{profile['total_missing']:,} ({profile['missing_percentage']}%)"],
        ["Numerical Features", str(len(profile["column_types"]["numerical"]))],
        ["Categorical Features", str(len(profile["column_types"]["categorical"]))],
    ]
    table = Table(overview_data, colWidths=[2.5 * inch, 3 * inch])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f4e79")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f0f4f8")]),
            ]
        )
    )
    story.append(Paragraph("Dataset Overview", styles["Heading2"]))
    story.append(table)
    story.append(Spacer(1, 0.25 * inch))

    # Column types
    story.append(Paragraph("Column Types", styles["Heading2"]))
    for ctype, cols in profile["column_types"].items():
        col_list = ", ".join(cols) if cols else "None"
        story.append(Paragraph(f"<b>{ctype.title()}:</b> {col_list}", styles["Normal"]))
    story.append(Spacer(1, 0.25 * inch))

    # Insights
    if insights:
        story.append(Paragraph("Business Insights", styles["Heading2"]))
        markdown = insights_to_markdown(insights)
        for line in markdown.split("\n"):
            if line.startswith("## "):
                story.append(Paragraph(line[3:], styles["Heading3"]))
            elif line.startswith("- "):
                story.append(Paragraph(f"• {line[2:]}", styles["Normal"]))
            elif line.strip():
                story.append(Paragraph(line, styles["Normal"]))

    doc.build(story)
    return buffer.getvalue()
