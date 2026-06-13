"""Plotly visualization engine for data analysis."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from utils.theme import apply_plotly_dark_theme


CHART_TYPES = {
    "bar": "Bar Chart",
    "line": "Line Chart",
    "pie": "Pie Chart",
    "scatter": "Scatter Plot",
    "histogram": "Histogram",
    "heatmap": "Heatmap",
}


def _validate_column(df: pd.DataFrame, col: str) -> bool:
    return col in df.columns


def create_bar_chart(
    df: pd.DataFrame,
    x_col: str,
    y_col: str | None = None,
    title: str = "Bar Chart",
    color_col: str | None = None,
) -> go.Figure:
    """Create an interactive bar chart."""
    if not _validate_column(df, x_col):
        raise ValueError(f"Column '{x_col}' not found.")

    if y_col and _validate_column(df, y_col):
        fig = px.bar(df, x=x_col, y=y_col, title=title, color=color_col)
    else:
        counts = df[x_col].value_counts().head(20).reset_index()
        counts.columns = [x_col, "count"]
        fig = px.bar(counts, x=x_col, y="count", title=title)

    return apply_plotly_dark_theme(fig)


def create_line_chart(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    title: str = "Line Chart",
    color_col: str | None = None,
) -> go.Figure:
    """Create an interactive line chart."""
    for col in (x_col, y_col):
        if not _validate_column(df, col):
            raise ValueError(f"Column '{col}' not found.")

    plot_df = df.sort_values(x_col)
    fig = px.line(plot_df, x=x_col, y=y_col, title=title, color=color_col)
    return apply_plotly_dark_theme(fig)


def create_pie_chart(
    df: pd.DataFrame,
    names_col: str,
    values_col: str | None = None,
    title: str = "Pie Chart",
) -> go.Figure:
    """Create an interactive pie chart."""
    if not _validate_column(df, names_col):
        raise ValueError(f"Column '{names_col}' not found.")

    if values_col and _validate_column(df, values_col):
        fig = px.pie(df, names=names_col, values=values_col, title=title)
    else:
        counts = df[names_col].value_counts().head(10)
        fig = px.pie(names=counts.index, values=counts.values, title=title)

    return apply_plotly_dark_theme(fig)


def create_scatter_plot(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    title: str = "Scatter Plot",
    color_col: str | None = None,
    size_col: str | None = None,
) -> go.Figure:
    """Create an interactive scatter plot."""
    for col in (x_col, y_col):
        if not _validate_column(df, col):
            raise ValueError(f"Column '{col}' not found.")

    fig = px.scatter(
        df,
        x=x_col,
        y=y_col,
        title=title,
        color=color_col,
        size=size_col,
        opacity=0.7,
    )
    return apply_plotly_dark_theme(fig)


def create_histogram(
    df: pd.DataFrame,
    col: str,
    title: str = "Histogram",
    bins: int = 30,
) -> go.Figure:
    """Create an interactive histogram."""
    if not _validate_column(df, col):
        raise ValueError(f"Column '{col}' not found.")

    fig = px.histogram(df, x=col, nbins=bins, title=title)
    return apply_plotly_dark_theme(fig)


def create_heatmap(
    df: pd.DataFrame,
    title: str = "Correlation Heatmap",
) -> go.Figure:
    """Create a correlation heatmap for numerical columns."""
    numerical = df.select_dtypes(include=[np.number])
    if numerical.shape[1] < 2:
        raise ValueError("At least two numerical columns are required for a heatmap.")

    corr = numerical.corr()
    fig = px.imshow(
        corr,
        text_auto=".2f",
        title=title,
        color_continuous_scale="RdBu_r",
        aspect="auto",
    )
    fig.update_layout(height=500)
    return apply_plotly_dark_theme(fig)


def auto_chart(
    df: pd.DataFrame,
    chart_type: str,
    params: dict[str, Any],
) -> go.Figure:
    """
    Dispatch chart creation based on type and parameters.

    Supported chart_type values: bar, line, pie, scatter, histogram, heatmap.
    """
    chart_type = chart_type.lower().strip()
    title = params.get("title", CHART_TYPES.get(chart_type, "Chart"))

    if chart_type == "bar":
        return create_bar_chart(
            df,
            x_col=params["x"],
            y_col=params.get("y"),
            title=title,
            color_col=params.get("color"),
        )
    if chart_type == "line":
        return create_line_chart(
            df,
            x_col=params["x"],
            y_col=params["y"],
            title=title,
            color_col=params.get("color"),
        )
    if chart_type == "pie":
        return create_pie_chart(
            df,
            names_col=params["names"],
            values_col=params.get("values"),
            title=title,
        )
    if chart_type == "scatter":
        return create_scatter_plot(
            df,
            x_col=params["x"],
            y_col=params["y"],
            title=title,
            color_col=params.get("color"),
            size_col=params.get("size"),
        )
    if chart_type == "histogram":
        return create_histogram(
            df,
            col=params["col"],
            title=title,
            bins=params.get("bins", 30),
        )
    if chart_type == "heatmap":
        return create_heatmap(df, title=title)

    raise ValueError(f"Unsupported chart type: {chart_type}")


def suggest_chart(
    df: pd.DataFrame,
    column_types: dict[str, list[str]],
) -> dict[str, Any] | None:
    """
    Suggest a default chart based on column types.

    Returns chart spec dict with type and params, or None if not possible.
    """
    numerical = column_types.get("numerical", [])
    categorical = column_types.get("categorical", [])
    datetime_cols = column_types.get("datetime", [])

    if len(numerical) >= 2:
        return {
            "type": "heatmap",
            "params": {"title": "Numerical Feature Correlations"},
        }

    if categorical and numerical:
        return {
            "type": "bar",
            "params": {
                "x": categorical[0],
                "y": numerical[0],
                "title": f"{numerical[0]} by {categorical[0]}",
            },
        }

    if categorical:
        return {
            "type": "pie",
            "params": {
                "names": categorical[0],
                "title": f"Distribution of {categorical[0]}",
            },
        }

    if numerical:
        return {
            "type": "histogram",
            "params": {
                "col": numerical[0],
                "title": f"Distribution of {numerical[0]}",
            },
        }

    if datetime_cols and numerical:
        return {
            "type": "line",
            "params": {
                "x": datetime_cols[0],
                "y": numerical[0],
                "title": f"{numerical[0]} over time",
            },
        }

    return None
