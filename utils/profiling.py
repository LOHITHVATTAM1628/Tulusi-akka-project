"""Dataset profiling and metadata extraction."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd


def detect_column_types(df: pd.DataFrame) -> dict[str, list[str]]:
    """
    Classify columns into numerical, categorical, and datetime groups.

    Uses dtype heuristics and cardinality checks for object columns.
    """
    numerical: list[str] = []
    categorical: list[str] = []
    datetime_cols: list[str] = []

    for col in df.columns:
        series = df[col]
        dtype = series.dtype

        if pd.api.types.is_datetime64_any_dtype(dtype):
            datetime_cols.append(str(col))
        elif pd.api.types.is_numeric_dtype(dtype):
            numerical.append(str(col))
        else:
            col_name = str(col).lower()
            looks_like_date = any(
                token in col_name for token in ("date", "time", "timestamp", "month", "year")
            )
            if looks_like_date:
                parsed = pd.to_datetime(series, errors="coerce", utc=False)
                valid_ratio = parsed.notna().mean()
                if valid_ratio >= 0.8:
                    datetime_cols.append(str(col))
                    continue
            categorical.append(str(col))

    return {
        "numerical": numerical,
        "categorical": categorical,
        "datetime": datetime_cols,
    }


def get_missing_values(df: pd.DataFrame) -> dict[str, int]:
    """Return missing value counts per column."""
    missing = df.isnull().sum()
    return {str(col): int(count) for col, count in missing.items() if count > 0}


def get_summary_statistics(df: pd.DataFrame) -> dict[str, Any]:
    """Compute descriptive statistics for numerical columns."""
    numerical = df.select_dtypes(include=[np.number])
    if numerical.empty:
        return {}
    desc = numerical.describe().round(2)
    return desc.to_dict()


def build_dataset_profile(df: pd.DataFrame) -> dict[str, Any]:
    """
    Build a comprehensive dataset profile for UI display and AI context.

    Returns metadata including shape, dtypes, missing values, and stats.
    """
    column_types = detect_column_types(df)
    missing = get_missing_values(df)
    total_missing = int(df.isnull().sum().sum())

    profile: dict[str, Any] = {
        "rows": int(len(df)),
        "columns": int(len(df.columns)),
        "column_names": [str(c) for c in df.columns],
        "dtypes": {str(k): str(v) for k, v in df.dtypes.items()},
        "column_types": column_types,
        "missing_values": missing,
        "total_missing": total_missing,
        "missing_percentage": round(total_missing / max(df.size, 1) * 100, 2),
        "duplicate_rows": int(df.duplicated().sum()),
        "memory_usage_mb": round(df.memory_usage(deep=True).sum() / 1024**2, 2),
        "summary_statistics": get_summary_statistics(df),
    }

    # Top categories for low-cardinality categorical columns.
    top_categories: dict[str, list[dict[str, Any]]] = {}
    for col in column_types["categorical"][:10]:
        if col not in df.columns:
            continue
        counts = df[col].value_counts().head(5)
        top_categories[col] = [
            {"value": str(idx), "count": int(cnt)} for idx, cnt in counts.items()
        ]
    profile["top_categories"] = top_categories

    return profile


def profile_to_text(profile: dict[str, Any]) -> str:
    """Convert a dataset profile dict into a readable text summary for the LLM."""
    lines = [
        f"Rows: {profile['rows']:,}",
        f"Columns: {profile['columns']}",
        f"Column names: {', '.join(profile['column_names'])}",
        f"Numerical columns: {', '.join(profile['column_types']['numerical']) or 'None'}",
        f"Categorical columns: {', '.join(profile['column_types']['categorical']) or 'None'}",
        f"Datetime columns: {', '.join(profile['column_types']['datetime']) or 'None'}",
        f"Total missing values: {profile['total_missing']} ({profile['missing_percentage']}%)",
        f"Duplicate rows: {profile['duplicate_rows']}",
    ]

    if profile.get("summary_statistics"):
        lines.append("Numerical summary statistics are available.")

    if profile.get("top_categories"):
        lines.append("Top category distributions are available for categorical columns.")

    return "\n".join(lines)


def get_kpi_metrics(df: pd.DataFrame, profile: dict[str, Any]) -> dict[str, Any]:
    """Extract KPI dashboard metrics from the dataset profile."""
    kpis: dict[str, Any] = {
        "total_records": profile["rows"],
        "total_columns": profile["columns"],
        "missing_values": profile["total_missing"],
        "missing_pct": profile["missing_percentage"],
        "numerical_features": len(profile["column_types"]["numerical"]),
        "categorical_features": len(profile["column_types"]["categorical"]),
        "datetime_features": len(profile["column_types"]["datetime"]),
        "duplicate_rows": profile["duplicate_rows"],
        "top_categories": profile.get("top_categories", {}),
    }

    numerical_cols = profile["column_types"]["numerical"]
    if numerical_cols:
        first_num = numerical_cols[0]
        if first_num in df.columns:
            kpis["primary_numeric_col"] = first_num
            kpis["primary_numeric_mean"] = round(float(df[first_num].mean()), 2)
            kpis["primary_numeric_sum"] = round(float(df[first_num].sum()), 2)

    return kpis
