"""
AI Data Analyst — Professional Enterprise Application

Clean, minimal interface for data analysis powered by Google Gemini.
"""

from __future__ import annotations

import os
from datetime import datetime

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from dotenv import load_dotenv

from agents.data_agent import DataAnalystAgent
from utils.charts import auto_chart, suggest_chart
from utils.insights import generate_ai_insights
from utils.loader import load_dataframe
from utils.profiling import build_dataset_profile, get_kpi_metrics
from utils.reports import generate_excel_report, generate_pdf_report
from utils.theme import ENTERPRISE_CSS, apply_plotly_theme

load_dotenv()

st.set_page_config(
    page_title="AI Data Analyst",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

MAX_FILE_MB = float(os.getenv("MAX_FILE_SIZE_MB", "25"))
st.markdown(ENTERPRISE_CSS, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Session state initialization
# ---------------------------------------------------------------------------
def init_session_state() -> None:
    defaults = {
        "df": None,
        "profile": None,
        "kpis": None,
        "chat_history": [],
        "charts": [],
        "insights": None,
        "dataset_summary": None,
        "agent": None,
        "_filename": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def get_agent() -> DataAnalystAgent:
    if st.session_state.agent is None:
        st.session_state.agent = DataAnalystAgent()
    return st.session_state.agent


def reset_on_new_upload() -> None:
    st.session_state.chat_history = []
    st.session_state.charts = []
    st.session_state.insights = None
    st.session_state.dataset_summary = None


# ---------------------------------------------------------------------------
# UI Components
# ---------------------------------------------------------------------------
def render_header() -> None:
    """Render page header with title and upload"""
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown('<p class="page-title">📊 AI Data Analyst</p>', unsafe_allow_html=True)
        st.markdown(
            '<p class="page-subtitle">Upload your dataset and analyze it with natural language powered by AI</p>',
            unsafe_allow_html=True,
        )
    
    with col2:
        api_key = os.getenv("GOOGLE_API_KEY", "")
        if api_key and api_key.startswith("AIzaSy"):
            st.markdown(
                '<div class="badge badge-success" style="margin-top:1rem;">✓ Gemini Connected</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<div class="badge badge-warning" style="margin-top:1rem;">⚠ API Key Required</div>',
                unsafe_allow_html=True,
            )


def render_upload_section() -> None:
    """Render file upload area"""
    st.markdown('<div class="pro-card">', unsafe_allow_html=True)
    st.markdown('<p class="section-header">📁 Upload Dataset</p>', unsafe_allow_html=True)
    
    uploaded = st.file_uploader(
        "Choose a file",
        type=["csv", "xlsx", "xls"],
        help=f"Supported formats: CSV, Excel · Maximum size: {MAX_FILE_MB:.0f} MB",
        label_visibility="collapsed",
    )

    if uploaded is not None:
        df, error = load_dataframe(uploaded, max_mb=MAX_FILE_MB)
        if error:
            st.error(f"❌ {error}")
        elif st.session_state._filename != uploaded.name:
            st.session_state.df = df
            st.session_state._filename = uploaded.name
            st.session_state.profile = build_dataset_profile(df)
            st.session_state.kpis = get_kpi_metrics(df, st.session_state.profile)
            reset_on_new_upload()
            st.success(f"✓ Successfully loaded **{uploaded.name}** with {len(df):,} records")
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)


def render_stats_cards() -> None:
    """Render KPI statistics cards"""
    kpis = st.session_state.kpis
    if not kpis:
        return

    st.markdown('<div class="grid-5">', unsafe_allow_html=True)
    
    metrics = [
        ("Total Records", f"{kpis['total_records']:,}"),
        ("Columns", f"{kpis['numerical_features'] + kpis['categorical_features']}"),
        ("Missing Values", f"{kpis['missing_values']:,}"),
        ("Numerical Features", f"{kpis['numerical_features']}"),
        ("Categorical Features", f"{kpis['categorical_features']}"),
    ]

    for label, value in metrics:
        st.markdown(
            f'''<div class="stat-card">
                <div class="stat-value">{value}</div>
                <div class="stat-label">{label}</div>
            </div>''',
            unsafe_allow_html=True,
        )
    
    st.markdown('</div>', unsafe_allow_html=True)


def render_chat_interface() -> None:
    """Render AI chat interface"""
    df = st.session_state.df
    profile = st.session_state.profile
    if df is None:
        return

    st.markdown('<div class="pro-card">', unsafe_allow_html=True)
    st.markdown('<p class="section-header">💬 AI Assistant</p>', unsafe_allow_html=True)

    # Display chat history
    if not st.session_state.chat_history:
        st.info("👋 Ask me anything about your dataset! For example: 'What are the top 5 values by revenue?'")
    else:
        for idx, msg in enumerate(st.session_state.chat_history):
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
                if msg.get("chart") and isinstance(msg["chart"], go.Figure):
                    st.plotly_chart(msg["chart"], use_container_width=True, key=f"chat_chart_{idx}")

    # Chat input
    prompt = st.chat_input("Ask about your data...")

    if prompt:
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        agent = get_agent()
        history = [
            {"role": m["role"], "content": m["content"]}
            for m in st.session_state.chat_history[:-1]
        ]
        result = agent.analyze(prompt, df, profile, chat_history=history)

        assistant_msg: dict = {"role": "assistant", "content": result["answer"]}
        chart = result.get("chart_figure")
        if chart is not None:
            assistant_msg["chart"] = apply_plotly_theme(chart)
            st.session_state.charts.append(assistant_msg["chart"])

        st.session_state.chat_history.append(assistant_msg)
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)


def render_dataset_preview() -> None:
    """Render dataset preview and info"""
    df = st.session_state.df
    profile = st.session_state.profile
    if df is None or profile is None:
        return

    st.markdown('<div class="pro-card">', unsafe_allow_html=True)
    st.markdown('<p class="section-header">📋 Dataset Overview</p>', unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["Data Preview", "Column Info", "AI Summary"])

    with tab1:
        st.dataframe(df.head(20), use_container_width=True, height=400)

    with tab2:
        col_info = []
        for col in df.columns:
            dtype = str(df[col].dtype)
            missing = df[col].isna().sum()
            unique = df[col].nunique()
            col_info.append({"Column": col, "Type": dtype, "Missing": missing, "Unique": unique})
        
        info_df = pd.DataFrame(col_info)
        st.dataframe(info_df, use_container_width=True, hide_index=True)

    with tab3:
        if st.session_state.dataset_summary is None:
            with st.spinner("Generating AI summary..."):
                agent = get_agent()
                st.session_state.dataset_summary = agent.generate_dataset_summary(df, profile)
        st.markdown(st.session_state.dataset_summary)

    st.markdown('</div>', unsafe_allow_html=True)


def render_visualizations() -> None:
    """Render visualization section"""
    df = st.session_state.df
    profile = st.session_state.profile
    if df is None or profile is None:
        return

    st.markdown('<div class="pro-card">', unsafe_allow_html=True)
    st.markdown('<p class="section-header">📊 Visualizations</p>', unsafe_allow_html=True)

    # Auto-suggested chart
    suggestion = suggest_chart(df, profile["column_types"])
    if suggestion:
        try:
            fig = auto_chart(df, suggestion["type"], suggestion["params"])
            fig = apply_plotly_theme(fig)
            st.plotly_chart(fig, use_container_width=True)
        except Exception as exc:  # noqa: BLE001
            st.warning(f"Unable to generate suggested chart: {exc}")

    # Charts from chat
    if st.session_state.charts:
        st.markdown("**Charts from AI Analysis**")
        for i, fig in enumerate(st.session_state.charts[-3:]):  # Show last 3
            st.plotly_chart(fig, use_container_width=True, key=f"stored_chart_{i}")

    st.markdown('</div>', unsafe_allow_html=True)


def render_insights() -> None:
    """Render business insights"""
    df = st.session_state.df
    profile = st.session_state.profile
    if df is None:
        return

    if st.session_state.insights is None:
        with st.spinner("Analyzing data for insights..."):
            st.session_state.insights = generate_ai_insights(df, profile)

    insights = st.session_state.insights

    st.markdown('<div class="pro-card">', unsafe_allow_html=True)
    st.markdown('<p class="section-header">💡 Business Insights</p>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    sections = [
        ("Key Findings", "key_findings"),
        ("Trends", "trends"),
        ("Anomalies", "anomalies"),
        ("Correlations", "correlations"),
        ("Opportunities", "revenue_opportunities"),
        ("Risks", "risk_indicators"),
    ]

    for idx, (title, key) in enumerate(sections):
        items = insights.get(key, [])
        with (col1 if idx % 2 == 0 else col2):
            with st.expander(f"🔍 {title}", expanded=idx < 2):
                if items:
                    for item in items:
                        st.markdown(f"• {item}")
                else:
                    st.caption("No items found")

    st.markdown('</div>', unsafe_allow_html=True)


def render_reports() -> None:
    """Render download reports section"""
    df = st.session_state.df
    profile = st.session_state.profile
    if df is None:
        return

    insights = st.session_state.insights

    st.markdown('<div class="pro-card">', unsafe_allow_html=True)
    st.markdown('<p class="section-header">📥 Export Reports</p>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1, 2])

    with col1:
        pdf_bytes = generate_pdf_report(
            df, profile, insights,
            title=f"Data Analysis Report - {datetime.now():%Y-%m-%d}",
        )
        st.download_button(
            "📄 Download PDF Report",
            data=pdf_bytes,
            file_name=f"analysis_report_{datetime.now():%Y%m%d_%H%M}.pdf",
            mime="application/pdf",
            use_container_width=True,
        )

    with col2:
        excel_bytes = generate_excel_report(df, profile, insights)
        st.download_button(
            "📊 Download Excel Summary",
            data=excel_bytes,
            file_name=f"data_summary_{datetime.now():%Y%m%d_%H%M}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )
    
    with col3:
        if st.button("🔄 Refresh Insights", use_container_width=True):
            st.session_state.insights = None
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)


def render_welcome() -> None:
    """Render welcome screen"""
    st.markdown('''
    <div class="pro-card" style="text-align:center;padding:4rem 2rem;">
        <div style="font-size:4rem;margin-bottom:1.5rem;">📊</div>
        <h2 style="color:#0F172A;margin-bottom:1rem;">Welcome to AI Data Analyst</h2>
        <p style="color:#475569;font-size:1.1rem;margin-bottom:2rem;">
            Upload a CSV or Excel file to start analyzing your data with artificial intelligence
        </p>
        <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:2rem;margin-top:3rem;text-align:left;">
            <div>
                <div style="font-size:2rem;margin-bottom:0.5rem;">💬</div>
                <h4 style="color:#0F172A;margin-bottom:0.5rem;">Natural Language</h4>
                <p style="color:#64748B;font-size:0.9rem;">Ask questions in plain English</p>
            </div>
            <div>
                <div style="font-size:2rem;margin-bottom:0.5rem;">📈</div>
                <h4 style="color:#0F172A;margin-bottom:0.5rem;">Smart Charts</h4>
                <p style="color:#64748B;font-size:0.9rem;">Automatic visualization generation</p>
            </div>
            <div>
                <div style="font-size:2rem;margin-bottom:0.5rem;">🎯</div>
                <h4 style="color:#0F172A;margin-bottom:0.5rem;">AI Insights</h4>
                <p style="color:#64748B;font-size:0.9rem;">Business recommendations</p>
            </div>
        </div>
    </div>
    ''', unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Main Application
# ---------------------------------------------------------------------------
def main() -> None:
    init_session_state()
    
    render_header()
    
    if st.session_state.df is None:
        render_upload_section()
        render_welcome()
        return

    # Main interface with data loaded
    render_upload_section()
    
    render_stats_cards()

    col1, col2 = st.columns([3, 2], gap="large")
    with col1:
        render_chat_interface()
    with col2:
        render_dataset_preview()

    col3, col4 = st.columns([1, 1], gap="large")
    with col3:
        render_visualizations()
    with col4:
        render_insights()

    render_reports()


if __name__ == "__main__":
    main()
