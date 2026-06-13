"""Data loading utilities for CSV and Excel files."""

from __future__ import annotations

import io
from typing import Any

import pandas as pd
import streamlit as st

from utils.security import validate_uploaded_file


def load_dataframe(
    uploaded_file: Any,
    max_mb: float = 25.0,
) -> tuple[pd.DataFrame | None, str | None]:
    """
    Load an uploaded CSV or Excel file into a Pandas DataFrame.

    Args:
        uploaded_file: Streamlit UploadedFile object.
        max_mb: Maximum allowed file size in megabytes.

    Returns:
        Tuple of (dataframe, error_message). error_message is None on success.
    """
    if uploaded_file is None:
        return None, "No file was uploaded."

    is_valid, error = validate_uploaded_file(
        uploaded_file.name,
        uploaded_file.size,
        max_mb=max_mb,
    )
    if not is_valid:
        return None, error

    try:
        filename = uploaded_file.name.lower()
        if filename.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        elif filename.endswith((".xlsx", ".xls")):
            df = pd.read_excel(uploaded_file, engine="openpyxl")
        else:
            return None, "Unsupported file format."

        if df.empty:
            return None, "The uploaded file contains no data."

        # Normalize column names for safer downstream analysis.
        df.columns = [str(col).strip() for col in df.columns]
        return df, None

    except UnicodeDecodeError:
        uploaded_file.seek(0)
        try:
            df = pd.read_csv(uploaded_file, encoding="latin-1")
            df.columns = [str(col).strip() for col in df.columns]
            return df, None
        except Exception as exc:  # noqa: BLE001
            return None, f"Failed to read CSV with alternate encoding: {exc}"

    except Exception as exc:  # noqa: BLE001
        return None, f"Failed to load file: {exc}"


def get_preview(df: pd.DataFrame, n_rows: int = 10) -> pd.DataFrame:
    """Return the first n rows of the dataframe for preview."""
    return df.head(n_rows)


def dataframe_to_csv_bytes(df: pd.DataFrame) -> bytes:
    """Serialize a DataFrame to CSV bytes for download."""
    buffer = io.BytesIO()
    df.to_csv(buffer, index=False)
    return buffer.getvalue()


def get_column_sample_values(df: pd.DataFrame, max_cols: int = 20) -> dict[str, list]:
    """Return sample values per column for schema context."""
    samples: dict[str, list] = {}
    for col in df.columns[:max_cols]:
        non_null = df[col].dropna()
        samples[str(col)] = [str(v) for v in non_null.head(3).tolist()]
    return samples
