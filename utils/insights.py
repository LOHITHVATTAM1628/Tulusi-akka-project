"""Business insights generation using Gemini and statistical analysis."""

from __future__ import annotations

import json
import os
import re
from typing import Any

import numpy as np
import pandas as pd

from utils.profiling import build_dataset_profile, profile_to_text


def _compute_statistical_insights(df: pd.DataFrame, profile: dict[str, Any]) -> dict[str, Any]:
    """Derive rule-based statistical insights from the dataset."""
    insights: dict[str, Any] = {
        "key_findings": [],
        "trends": [],
        "anomalies": [],
        "correlations": [],
        "revenue_opportunities": [],
        "risk_indicators": [],
        "recommendations": [],
    }

    rows = profile["rows"]
    insights["key_findings"].append(
        f"Dataset contains {rows:,} records across {profile['columns']} features."
    )

    if profile["total_missing"] > 0:
        pct = profile["missing_percentage"]
        insights["risk_indicators"].append(
            f"Missing data detected: {profile['total_missing']:,} values ({pct}% of all cells)."
        )
        insights["recommendations"].append(
            "Impute or remove columns with high missing rates before modeling."
        )

    if profile["duplicate_rows"] > 0:
        insights["risk_indicators"].append(
            f"{profile['duplicate_rows']:,} duplicate rows found — may skew aggregations."
        )
        insights["recommendations"].append("Deduplicate records using a natural key if available.")

    numerical = profile["column_types"]["numerical"]
    if len(numerical) >= 2:
        corr_matrix = df[numerical].corr()
        for i, col_a in enumerate(numerical):
            for col_b in numerical[i + 1 :]:
                value = corr_matrix.loc[col_a, col_b]
                if abs(value) >= 0.7:
                    direction = "positive" if value > 0 else "negative"
                    insights["correlations"].append(
                        f"Strong {direction} correlation ({value:.2f}) between '{col_a}' and '{col_b}'."
                    )

    for col in numerical[:5]:
        if col not in df.columns:
            continue
        series = df[col].dropna()
        if series.empty:
            continue
        q1, q3 = series.quantile(0.25), series.quantile(0.75)
        iqr = q3 - q1
        if iqr > 0:
            outliers = ((series < q1 - 1.5 * iqr) | (series > q3 + 1.5 * iqr)).sum()
            if outliers > 0:
                insights["anomalies"].append(
                    f"'{col}' has {int(outliers)} potential outliers (IQR method)."
                )

    categorical = profile["column_types"]["categorical"]
    for col in categorical[:3]:
        if col not in df.columns:
            continue
        top = df[col].value_counts()
        if len(top) > 0:
            dominant = top.iloc[0] / len(df) * 100
            if dominant >= 60:
                insights["key_findings"].append(
                    f"'{col}' is dominated by '{top.index[0]}' ({dominant:.1f}% of records)."
                )

    # Revenue-oriented heuristics when common column names appear.
    revenue_cols = [c for c in df.columns if re.search(r"revenue|sales|amount|price|total", str(c), re.I)]
    if revenue_cols:
        rev_col = revenue_cols[0]
        total_rev = float(df[rev_col].sum())
        insights["key_findings"].append(f"Total '{rev_col}': {total_rev:,.2f}.")
        insights["revenue_opportunities"].append(
            f"Analyze top segments driving '{rev_col}' to prioritize growth initiatives."
        )

    product_cols = [c for c in df.columns if re.search(r"product|category|segment", str(c), re.I)]
    if revenue_cols and product_cols:
        grouped = df.groupby(product_cols[0])[revenue_cols[0]].sum().sort_values(ascending=False)
        if len(grouped) > 0:
            top_segment = grouped.index[0]
            insights["revenue_opportunities"].append(
                f"Top performer: '{top_segment}' contributes {grouped.iloc[0]:,.2f} in {revenue_cols[0]}."
            )

    date_cols = profile["column_types"]["datetime"]
    if date_cols and numerical:
        date_col = date_cols[0]
        num_col = numerical[0]
        try:
            temp = df[[date_col, num_col]].copy()
            temp[date_col] = pd.to_datetime(temp[date_col], errors="coerce")
            temp = temp.dropna().sort_values(date_col)
            if len(temp) >= 3:
                first_half = temp[num_col].iloc[: len(temp) // 2].mean()
                second_half = temp[num_col].iloc[len(temp) // 2 :].mean()
                if second_half > first_half * 1.1:
                    insights["trends"].append(
                        f"'{num_col}' shows an upward trend over '{date_col}'."
                    )
                elif second_half < first_half * 0.9:
                    insights["trends"].append(
                        f"'{num_col}' shows a downward trend over '{date_col}'."
                    )
        except Exception:  # noqa: BLE001
            pass

    if not insights["recommendations"]:
        insights["recommendations"].append(
            "Explore segment-level KPIs and time-based trends for actionable next steps."
        )

    return insights


def _parse_json_from_llm(text: str) -> dict[str, Any] | None:
    """Extract JSON object from LLM response text."""
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                return None
    return None


def generate_ai_insights(
    df: pd.DataFrame,
    profile: dict[str, Any] | None = None,
    api_key: str | None = None,
    model_name: str = "gemini-2.0-flash",
) -> dict[str, Any]:
    """
    Generate business insights combining statistical analysis and Gemini AI.

    Falls back to statistical-only insights if the API is unavailable.
    """
    if profile is None:
        profile = build_dataset_profile(df)

    statistical = _compute_statistical_insights(df, profile)
    api_key = api_key or os.getenv("GOOGLE_API_KEY")

    if not api_key:
        return statistical

    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        from langchain_core.messages import HumanMessage, SystemMessage

        llm = ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=api_key,
            temperature=0.3,
        )

        system_prompt = """You are a senior business data analyst. Analyze the dataset profile
and return ONLY valid JSON with these keys (each value is a list of concise strings):
key_findings, trends, anomalies, correlations, revenue_opportunities, risk_indicators, recommendations.
Provide 2-4 items per category when relevant. Be specific and actionable."""

        user_prompt = f"""Dataset profile:
{profile_to_text(profile)}

Sample rows (first 3):
{df.head(3).to_string()}

Return business insights as JSON only."""

        response = llm.invoke(
            [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt),
            ]
        )
        content = response.content if hasattr(response, "content") else str(response)
        ai_insights = _parse_json_from_llm(content)

        if ai_insights:
            merged = statistical.copy()
            for key in merged:
                ai_items = ai_insights.get(key, [])
                if isinstance(ai_items, list):
                    merged[key] = list(dict.fromkeys(merged[key] + ai_items))
            return merged

    except Exception:  # noqa: BLE001
        pass

    return statistical


def insights_to_markdown(insights: dict[str, Any]) -> str:
    """Format insights dict as markdown for reports."""
    sections = [
        ("Key Findings", "key_findings"),
        ("Trends", "trends"),
        ("Anomalies", "anomalies"),
        ("Correlations", "correlations"),
        ("Revenue Opportunities", "revenue_opportunities"),
        ("Risk Indicators", "risk_indicators"),
        ("Recommendations", "recommendations"),
    ]
    lines: list[str] = []
    for title, key in sections:
        items = insights.get(key, [])
        if items:
            lines.append(f"## {title}")
            for item in items:
                lines.append(f"- {item}")
            lines.append("")
    return "\n".join(lines)
