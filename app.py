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
# Session state & callbacks
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
        "chat_reset_counter": 0,
        "_filename": None,
        "show_clear_toast": False,
        "pending_refresh_insights": False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def clear_chat_callback() -> None:
    """Fully reset chat UI state (history, charts, widget keys)."""
    st.session_state.chat_history = []
    st.session_state.charts = []
    st.session_state.chat_reset_counter += 1
    st.session_state.show_clear_toast = True


def refresh_insights_callback() -> None:
    st.session_state.pending_refresh_insights = True


def get_agent() -> DataAnalystAgent:
    if st.session_state.agent is None:
        st.session_state.agent = DataAnalystAgent()
    return st.session_state.agent


def reset_on_new_upload() -> None:
    st.session_state.chat_history = []
    st.session_state.charts = []
    st.session_state.insights = None
    st.session_state.dataset_summary = None
    st.session_state.chat_reset_counter += 1


def chat_session_id() -> int:
    return st.session_state.chat_reset_counter


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
def render_sidebar() -> None:
    with st.sidebar:
        st.markdown(
            '<p class="hero-title" style="font-size:1.6rem;margin-bottom:0.25rem;">✦ AI Data Analyst</p>', 
            unsafe_allow_html=True
        )
        st.markdown(
            '<p class="hero-sub" style="margin-bottom:1.5rem;font-size:0.9rem;">Intelligent analysis powered by Gemini</p>', 
            unsafe_allow_html=True
        )

        uploaded = st.file_uploader(
            "Upload Dataset",
            type=["csv", "xlsx", "xls"],
            help=f"Supported: CSV, Excel · Max size: {MAX_FILE_MB:.0f} MB",
            label_visibility="collapsed",
        )

        if uploaded is not None:
            df, error = load_dataframe(uploaded, max_mb=MAX_FILE_MB)
            if error:
                st.error(error)
            elif st.session_state._filename != uploaded.name:
                st.session_state.df = df
                st.session_state._filename = uploaded.name
                st.session_state.profile = build_dataset_profile(df)
                st.session_state.kpis = get_kpi_metrics(df, st.session_state.profile)
                reset_on_new_upload()
                st.success(f"✅ Loaded **{uploaded.name}** · {len(df):,} records")

        st.markdown('<div class="accent-line"></div>', unsafe_allow_html=True)
        
        api_key = os.getenv("GOOGLE_API_KEY", "")
        if api_key and api_key != "your_gemini_api_key_here":
            st.markdown('<span class="badge-connected">● Connected</span>', unsafe_allow_html=True)
        else:
            st.markdown('<span class="badge-warning">⚠ API Key Required</span>', unsafe_allow_html=True)
            st.caption("Configure `GOOGLE_API_KEY` in `.env` file")

        if st.session_state.df is not None:
            st.markdown("### Quick Actions")
            st.button(
                "🔄 Refresh Insights",
                use_container_width=True,
                on_click=refresh_insights_callback,
                key="btn_refresh_insights",
            )
            st.button(
                "🗑️ Clear Chat History",
                use_container_width=True,
                on_click=clear_chat_callback,
                key="btn_clear_chat",
            )
            if st.session_state.chat_history:
                st.caption(f"💬 {len(st.session_state.chat_history)} messages")

        st.divider()
        st.caption("🚀 AI Data Analyst v2.0 Professional Edition")


# ---------------------------------------------------------------------------
# Bento layout components
# ---------------------------------------------------------------------------
def render_hero() -> None:
    st.markdown('<p class="hero-title">AI Data Analyst</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="hero-sub">Transform data into insights with AI · Upload datasets, ask questions in natural language, and generate comprehensive reports</p>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="accent-line"></div>', unsafe_allow_html=True)


def render_kpi_bento() -> None:
    kpis = st.session_state.kpis
    if not kpis:
        return

    metrics = [
        ("Total Records", f"{kpis['total_records']:,}"),
        ("Missing Values", f"{kpis['missing_values']:,}"),
        ("Numerical", str(kpis["numerical_features"])),
        ("Categorical", str(kpis["categorical_features"])),
        ("Duplicates", f"{kpis['duplicate_rows']:,}"),
    ]

    st.markdown('<div class="bento-grid">', unsafe_allow_html=True)
    cols = st.columns(5)
    for col, (label, value) in zip(cols, metrics):
        with col:
            st.markdown(
                f'<div class="kpi-card"><div class="kpi-value">{value}</div>'
                f'<div class="kpi-label">{label}</div></div>',
                unsafe_allow_html=True,
            )
    st.markdown("</div>", unsafe_allow_html=True)


def render_chat_bento() -> None:
    df = st.session_state.df
    profile = st.session_state.profile
    if df is None:
        return

    reset_id = chat_session_id()

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<p class="section-title">💬 <span>AI Chat Analyst</span></p>', unsafe_allow_html=True)
    st.caption("✨ Ask questions in plain English · Get instant answers with visualizations")

    chat_container = st.container()
    with chat_container:
        if not st.session_state.chat_history:
            st.markdown(
                '<div style="text-align:center;padding:3rem 1rem;color:#94A3B8;">'
                '<div style="font-size:3rem;margin-bottom:1rem;">💭</div>'
                '<p style="font-size:1.1rem;font-weight:600;margin-bottom:0.5rem;">Start a conversation</p>'
                '<p style="font-size:0.9rem;">Ask anything about your dataset and I\'ll help you analyze it</p>'
                '</div>',
                unsafe_allow_html=True,
            )
        else:
            for idx, msg in enumerate(st.session_state.chat_history):
                with st.chat_message(msg["role"], key=f"chat_msg_{reset_id}_{idx}"):
                    st.markdown(msg["content"])
                    if msg.get("chart") and isinstance(msg["chart"], go.Figure):
                        st.plotly_chart(
                            msg["chart"],
                            use_container_width=True,
                            key=f"chat_chart_{reset_id}_{idx}",
                        )

    prompt = st.chat_input(
        "Ask me anything about your data… e.g., 'Show top 5 regions by revenue'",
        key=f"chat_input_{reset_id}",
    )

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
            assistant_msg["chart"] = apply_plotly_dark_theme(chart)
            st.session_state.charts.append(assistant_msg["chart"])

        st.session_state.chat_history.append(assistant_msg)
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


def render_dataset_bento() -> None:
    df = st.session_state.df
    profile = st.session_state.profile
    if df is None or profile is None:
        return

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<p class="section-title">📋 <span>Dataset Overview</span></p>', unsafe_allow_html=True)

    tab_preview, tab_metadata, tab_summary = st.tabs(["Preview", "Metadata", "AI Summary"])

    with tab_preview:
        st.dataframe(df.head(15), use_container_width=True, height=320)

    with tab_metadata:
        c1, c2 = st.columns(2)
        with c1:
            for ctype, cols in profile["column_types"].items():
                st.markdown(f"**{ctype.title()}** ({len(cols)})")
                st.caption(", ".join(cols) or "—")
        with c2:
            if profile["missing_values"]:
                miss_df = pd.DataFrame(
                    list(profile["missing_values"].items()),
                    columns=["Column", "Missing"],
                )
                st.dataframe(miss_df, use_container_width=True, hide_index=True)
            else:
                st.success("No missing values")

    with tab_summary:
        if st.session_state.dataset_summary is None:
            with st.spinner("Generating summary…"):
                agent = get_agent()
                st.session_state.dataset_summary = agent.generate_dataset_summary(df, profile)
        st.markdown(st.session_state.dataset_summary)

    st.markdown("</div>", unsafe_allow_html=True)


def render_visualizations_bento() -> None:
    df = st.session_state.df
    profile = st.session_state.profile
    if df is None or profile is None:
        return

    reset_id = chat_session_id()

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<p class="section-title">📊 <span>Visualizations</span></p>', unsafe_allow_html=True)

    suggestion = suggest_chart(df, profile["column_types"])
    if suggestion:
        try:
            fig = auto_chart(df, suggestion["type"], suggestion["params"])
            st.plotly_chart(fig, use_container_width=True, key=f"suggested_chart_{reset_id}")
        except Exception as exc:  # noqa: BLE001
            st.warning(f"Chart error: {exc}")

    if st.session_state.charts:
        st.markdown("**From AI Analysis**")
        for i, fig in enumerate(st.session_state.charts):
            st.plotly_chart(fig, use_container_width=True, key=f"stored_chart_{reset_id}_{i}")

    with st.expander("🎨 Custom Chart Builder"):
        chart_type = st.selectbox("Type", ["bar", "line", "pie", "scatter", "histogram", "heatmap"])
        numerical = profile["column_types"]["numerical"]
        categorical = profile["column_types"]["categorical"]
        all_cols = list(df.columns)
        params: dict = {"title": "Custom Chart"}

        if chart_type == "histogram":
            params["col"] = st.selectbox("Column", numerical or all_cols)
        elif chart_type == "pie":
            params["names"] = st.selectbox("Category", categorical or all_cols)
            if numerical:
                params["values"] = st.selectbox("Values (opt.)", [None] + numerical)
        elif chart_type == "heatmap":
            pass
        elif chart_type in ("scatter", "line"):
            params["x"] = st.selectbox("X", all_cols)
            params["y"] = st.selectbox("Y", numerical or all_cols)
        else:
            params["x"] = st.selectbox("X", all_cols)
            if numerical:
                params["y"] = st.selectbox("Y (opt.)", [None] + numerical)

        if st.button("Generate", key="btn_gen_chart"):
            try:
                fig = auto_chart(df, chart_type, params)
                st.plotly_chart(fig, use_container_width=True)
            except Exception as exc:  # noqa: BLE001
                st.error(str(exc))

    st.markdown("</div>", unsafe_allow_html=True)


def render_insights_bento() -> None:
    df = st.session_state.df
    profile = st.session_state.profile
    if df is None:
        return

    if st.session_state.pending_refresh_insights:
        with st.spinner("Refreshing insights…"):
            st.session_state.insights = generate_ai_insights(df, profile)
        st.session_state.pending_refresh_insights = False

    if st.session_state.insights is None:
        with st.spinner("Analyzing insights…"):
            st.session_state.insights = generate_ai_insights(df, profile)

    insights = st.session_state.insights
    sections = [
        ("🔍 Key Findings", "key_findings"),
        ("📈 Trends", "trends"),
        ("⚠️ Anomalies", "anomalies"),
        ("🔗 Correlations", "correlations"),
        ("💰 Opportunities", "revenue_opportunities"),
        ("🚨 Risks", "risk_indicators"),
        ("✅ Actions", "recommendations"),
    ]

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<p class="section-title">💡 <span>Business Insights</span></p>', unsafe_allow_html=True)

    cols = st.columns(2)
    for idx, (title, key) in enumerate(sections):
        items = insights.get(key, [])
        with cols[idx % 2]:
            with st.expander(title, expanded=idx < 2 and bool(items)):
                if items:
                    for item in items:
                        st.markdown(f'<div class="insight-box">{item}</div>', unsafe_allow_html=True)
                else:
                    st.caption("No items")

    st.markdown("</div>", unsafe_allow_html=True)


def render_reports_bento() -> None:
    df = st.session_state.df
    profile = st.session_state.profile
    if df is None:
        return

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<p class="section-title">📥 <span>Download Reports</span></p>', unsafe_allow_html=True)

    insights = st.session_state.insights
    c1, c2 = st.columns(2)

    with c1:
        pdf_bytes = generate_pdf_report(
            df, profile, insights,
            title=f"AI Data Analyst Report — {datetime.now():%Y-%m-%d}",
        )
        st.download_button(
            "📄 Download PDF Report",
            data=pdf_bytes,
            file_name=f"report_{datetime.now():%Y%m%d_%H%M}.pdf",
            mime="application/pdf",
            use_container_width=True,
            key="dl_pdf",
        )

    with c2:
        excel_bytes = generate_excel_report(df, profile, insights)
        st.download_button(
            "📊 Download Excel Summary",
            data=excel_bytes,
            file_name=f"summary_{datetime.now():%Y%m%d_%H%M}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
            key="dl_excel",
        )

    st.markdown("</div>", unsafe_allow_html=True)


def render_welcome() -> None:
    render_hero()
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown(
        """
        <div style="text-align:center;padding:2rem 1rem;">
        <div style="font-size:4rem;margin-bottom:1.5rem;">📊</div>
        <h3 style="color:#F1F5F9;margin-bottom:1rem;">Get Started with AI-Powered Data Analysis</h3>
        <p style="color:#CBD5E1;font-size:1.05rem;line-height:1.7;margin-bottom:2rem;">
        Upload a CSV or Excel file from the sidebar to begin your intelligent data exploration journey.
        </p>
        </div>
        
        <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:1.5rem;margin-top:2rem;">
        <div style="padding:1.5rem;background:rgba(99,102,241,0.08);border-radius:12px;border:1px solid rgba(99,102,241,0.2);">
        <div style="font-size:2rem;margin-bottom:0.75rem;">💬</div>
        <h4 style="color:#F1F5F9;margin-bottom:0.5rem;">Natural Language Queries</h4>
        <p style="color:#94A3B8;font-size:0.9rem;">Ask questions in plain English and get instant insights</p>
        </div>
        
        <div style="padding:1.5rem;background:rgba(168,85,247,0.08);border-radius:12px;border:1px solid rgba(168,85,247,0.2);">
        <div style="font-size:2rem;margin-bottom:0.75rem;">📈</div>
        <h4 style="color:#F1F5F9;margin-bottom:0.5rem;">Smart Visualizations</h4>
        <p style="color:#94A3B8;font-size:0.9rem;">Automatic chart generation with interactive plots</p>
        </div>
        
        <div style="padding:1.5rem;background:rgba(59,130,246,0.08);border-radius:12px;border:1px solid rgba(59,130,246,0.2);">
        <div style="font-size:2rem;margin-bottom:0.75rem;">🎯</div>
        <h4 style="color:#F1F5F9;margin-bottom:0.5rem;">Business Insights</h4>
        <p style="color:#94A3B8;font-size:0.9rem;">AI-generated recommendations and trends</p>
        </div>
        </div>
        
        <div style="margin-top:2.5rem;padding:1.5rem;background:rgba(17,24,39,0.5);border-radius:12px;border:1px solid rgba(99,102,241,0.15);">
        <h4 style="color:#F1F5F9;margin-bottom:1rem;">💡 Example Questions</h4>
        <ul style="color:#CBD5E1;font-size:0.95rem;line-height:2;list-style:none;padding:0;">
        <li>→ What are the top 10 values in [column name]?</li>
        <li>→ Calculate average of [numeric] grouped by [category]</li>
        <li>→ Show me correlations between numerical features</li>
        <li>→ Which segment has the highest revenue?</li>
        <li>→ Display revenue trends over time</li>
        </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Main — Bento grid layout
# ---------------------------------------------------------------------------
def main() -> None:
    init_session_state()
    render_sidebar()

    if st.session_state.show_clear_toast:
        st.toast("Chat cleared successfully!", icon="✅")
        st.session_state.show_clear_toast = False

    if st.session_state.df is None:
        render_welcome()
        return

    render_hero()
    render_kpi_bento()

    # Bento row: Chat (wide) + Dataset (narrow)
    col_chat, col_data = st.columns([2, 1])
    with col_chat:
        render_chat_bento()
    with col_data:
        render_dataset_bento()

    # Bento row: Visualizations + Insights side by side
    col_viz, col_ins = st.columns(2)
    with col_viz:
        render_visualizations_bento()
    with col_ins:
        render_insights_bento()

    render_reports_bento()


if __name__ == "__main__":
    main()
