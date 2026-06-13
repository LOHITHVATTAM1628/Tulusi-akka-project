"""Professional Enterprise Theme - Clean & Minimal Design."""

from __future__ import annotations

import plotly.graph_objects as go

# Beautiful Gradient Color Palette - Modern Glass Design
BG = "#0F172A"
BG_GRADIENT_START = "rgba(99, 102, 241, 0.1)"
BG_GRADIENT_END = "rgba(168, 85, 247, 0.1)"
PRIMARY = "#6366F1"
SECONDARY = "#A855F7"
ACCENT = "#06B6D4"
TERTIARY = "#EC4899"
SURFACE = "rgba(30, 41, 59, 0.7)"
SURFACE_LIGHT = "rgba(51, 65, 85, 0.5)"
BORDER = "rgba(148, 163, 184, 0.2)"
BORDER_GLOW = "rgba(99, 102, 241, 0.5)"
TEXT = "#F1F5F9"
TEXT_SECONDARY = "#CBD5E1"
TEXT_MUTED = "#94A3B8"
SUCCESS = "#10B981"
WARNING = "#F59E0B"
ERROR = "#EF4444"
INFO = "#3B82F6"

ENTERPRISE_CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

/* Global Styles with Beautiful Gradients */
* {{
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}}

html, body, [data-testid="stAppViewContainer"] {{
    background: {BG} !important;
    color: {TEXT} !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
}}

[data-testid="stAppViewContainer"] > .main {{
    background: linear-gradient(135deg, 
        {BG} 0%, 
        rgba(30, 41, 59, 1) 50%, 
        {BG} 100%),
        radial-gradient(ellipse at top right, {BG_GRADIENT_START} 0%, transparent 50%),
        radial-gradient(ellipse at bottom left, {BG_GRADIENT_END} 0%, transparent 50%) !important;
    background-attachment: fixed;
    padding: 1.5rem 2.5rem !important;
    max-width: 1800px;
    margin: 0 auto;
    min-height: 100vh;
}}

/* Remove ALL top padding and margins */
.block-container {{
    padding-top: 1rem !important;
    padding-bottom: 1rem !important;
}}

[data-testid="stVerticalBlock"] {{
    gap: 0.5rem !important;
}}

/* Hide Streamlit Elements */
#MainMenu {{visibility: hidden;}}
footer {{visibility: hidden;}}
header {{visibility: hidden;}}
[data-testid="stToolbar"] {{display: none;}}
[data-testid="stDecoration"] {{display: none;}}
[data-testid="stStatusWidget"] {{display: none;}}
[data-testid="stSidebar"] {{display: none !important;}}
section[data-testid="stSidebar"] {{display: none !important;}}

/* Stunning Page Header */
.page-title {{
    font-size: 2.5rem;
    font-weight: 900;
    background: linear-gradient(135deg, {PRIMARY} 0%, {SECONDARY} 50%, {ACCENT} 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0.5rem;
    letter-spacing: -0.03em;
    text-shadow: 0 0 60px rgba(99, 102, 241, 0.3);
    animation: titleGlow 3s ease-in-out infinite alternate;
}}

@keyframes titleGlow {{
    from {{ filter: brightness(1); }}
    to {{ filter: brightness(1.2); }}
}}

.page-subtitle {{
    font-size: 1.1rem;
    color: {TEXT_SECONDARY};
    margin-bottom: 2rem;
    font-weight: 400;
}}

/* Premium Glass Morphism Cards */
.glass-card {{
    background: {SURFACE};
    backdrop-filter: blur(20px) saturate(180%);
    -webkit-backdrop-filter: blur(20px) saturate(180%);
    border: 1px solid {BORDER};
    border-radius: 24px;
    padding: 2rem;
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3),
                0 0 0 1px rgba(148, 163, 184, 0.1) inset;
    position: relative;
    overflow: hidden;
}}

.glass-card::before {{
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: linear-gradient(
        45deg,
        transparent 30%,
        rgba(99, 102, 241, 0.1) 50%,
        transparent 70%
    );
    animation: shimmer 6s infinite linear;
    pointer-events: none;
}}

@keyframes shimmer {{
    0% {{ transform: translateX(-100%) translateY(-100%) rotate(45deg); }}
    100% {{ transform: translateX(100%) translateY(100%) rotate(45deg); }}
}}

.glass-card:hover {{
    transform: translateY(-4px);
    border-color: {BORDER_GLOW};
    box-shadow: 0 20px 60px rgba(99, 102, 241, 0.3),
                0 0 0 1px {BORDER_GLOW} inset;
}}

.pro-card {{
    background: {SURFACE};
    backdrop-filter: blur(16px) saturate(180%);
    -webkit-backdrop-filter: blur(16px) saturate(180%);
    border: 1px solid {BORDER};
    border-radius: 20px;
    padding: 1.75rem;
    transition: all 0.3s ease;
    box-shadow: 0 4px 24px rgba(0, 0, 0, 0.2);
}}

.pro-card:hover {{
    border-color: {BORDER_GLOW};
    box-shadow: 0 8px 40px rgba(99, 102, 241, 0.25);
    transform: translateY(-2px);
}}

/* Compact Stat Cards with Gradient Backgrounds - Inline Display */
.stat-card {{
    background: linear-gradient(135deg, 
        rgba(99, 102, 241, 0.15) 0%, 
        rgba(168, 85, 247, 0.15) 100%);
    backdrop-filter: blur(16px);
    border: 1px solid {BORDER};
    border-radius: 14px;
    padding: 1rem 1.25rem;
    text-align: center;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
    overflow: hidden;
    min-height: 85px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
}}

.stat-card::after {{
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, 
        transparent, 
        rgba(255, 255, 255, 0.1), 
        transparent);
    transition: left 0.5s ease;
}}

.stat-card:hover {{
    transform: translateY(-3px) scale(1.01);
    border-color: {BORDER_GLOW};
    box-shadow: 0 10px 40px rgba(99, 102, 241, 0.3);
}}

.stat-card:hover::after {{
    left: 100%;
}}

.stat-value {{
    font-size: 1.75rem;
    font-weight: 800;
    background: linear-gradient(135deg, {TEXT} 0%, {PRIMARY} 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.35rem;
    line-height: 1;
    text-shadow: 0 0 20px rgba(99, 102, 241, 0.5);
}}

.stat-label {{
    font-size: 0.8rem;
    color: {TEXT_SECONDARY};
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    line-height: 1.2;
}}

/* Beautiful Section Headers */
.section-header {{
    font-size: 1.5rem;
    font-weight: 700;
    background: linear-gradient(135deg, {TEXT} 0%, {PRIMARY} 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 1.5rem;
    display: flex;
    align-items: center;
    gap: 0.75rem;
}}

/* Glowing Upload Area */
.upload-glow {{
    background: linear-gradient(135deg, {SURFACE_LIGHT}, {SURFACE});
    border: 2px dashed {BORDER};
    border-radius: 16px;
    padding: 2rem;
    text-align: center;
    transition: all 0.4s ease;
    position: relative;
}}

.upload-glow:hover {{
    border-color: {BORDER_GLOW};
    box-shadow: 0 0 40px rgba(99, 102, 241, 0.3);
}}

/* Streamlit Components - Glass Effect */
[data-testid="stFileUploader"] {{
    background: {SURFACE} !important;
    backdrop-filter: blur(16px) !important;
    border: 2px dashed {BORDER} !important;
    border-radius: 16px !important;
    padding: 2rem !important;
    transition: all 0.3s ease !important;
}}

[data-testid="stFileUploader"]:hover {{
    border-color: {BORDER_GLOW} !important;
    box-shadow: 0 0 40px rgba(99, 102, 241, 0.2) !important;
}}

/* Beautiful Gradient Buttons */
.stButton > button {{
    background: linear-gradient(135deg, {PRIMARY} 0%, {SECONDARY} 100%) !important;
    color: white !important;
    border: none !important;
    padding: 0.75rem 2rem !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    box-shadow: 0 4px 20px rgba(99, 102, 241, 0.4) !important;
    position: relative;
    overflow: hidden;
}}

.stButton > button::before {{
    content: '';
    position: absolute;
    top: 50%;
    left: 50%;
    width: 0;
    height: 0;
    background: rgba(255, 255, 255, 0.2);
    border-radius: 50%;
    transform: translate(-50%, -50%);
    transition: width 0.6s, height 0.6s;
}}

.stButton > button:hover {{
    transform: translateY(-3px) !important;
    box-shadow: 0 8px 32px rgba(99, 102, 241, 0.6) !important;
}}

.stButton > button:hover::before {{
    width: 300px;
    height: 300px;
}}

[data-testid="stDownloadButton"] > button {{
    background: linear-gradient(135deg, {SUCCESS} 0%, {ACCENT} 100%) !important;
    color: white !important;
    border: none !important;
    padding: 0.75rem 2rem !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
    box-shadow: 0 4px 20px rgba(16, 185, 129, 0.4) !important;
}}

[data-testid="stDownloadButton"] > button:hover {{
    transform: translateY(-3px) !important;
    box-shadow: 0 8px 32px rgba(16, 185, 129, 0.6) !important;
}}

/* Modern Tabs with Glass Effect */
.stTabs [data-baseweb="tab-list"] {{
    gap: 0.75rem;
    background: {SURFACE};
    backdrop-filter: blur(12px);
    padding: 0.75rem;
    border-radius: 16px;
    border: 1px solid {BORDER};
}}

.stTabs [data-baseweb="tab"] {{
    background: transparent !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.75rem 1.5rem !important;
    font-weight: 600 !important;
    color: {TEXT_SECONDARY} !important;
    transition: all 0.3s ease !important;
}}

.stTabs [data-baseweb="tab"]:hover {{
    background: {SURFACE_LIGHT} !important;
    color: {TEXT} !important;
}}

.stTabs [aria-selected="true"] {{
    background: linear-gradient(135deg, {PRIMARY}, {SECONDARY}) !important;
    color: white !important;
    box-shadow: 0 4px 16px rgba(99, 102, 241, 0.4) !important;
}}

/* Glass Data Tables */
[data-testid="stDataFrame"] {{
    background: {SURFACE} !important;
    backdrop-filter: blur(12px) !important;
    border: 1px solid {BORDER} !important;
    border-radius: 16px !important;
    overflow: hidden !important;
}}

/* Beautiful Chat Messages */
[data-testid="stChatMessage"] {{
    background: {SURFACE} !important;
    backdrop-filter: blur(16px) !important;
    border: 1px solid {BORDER} !important;
    border-radius: 16px !important;
    padding: 1.25rem !important;
    margin-bottom: 1rem !important;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1) !important;
}}

[data-testid="stChatInput"] {{
    background: {SURFACE} !important;
    backdrop-filter: blur(16px) !important;
    border: 2px solid {BORDER} !important;
    border-radius: 16px !important;
}}

[data-testid="stChatInput"]:focus-within {{
    border-color: {BORDER_GLOW} !important;
    box-shadow: 0 0 24px rgba(99, 102, 241, 0.3) !important;
}}

/* Expanders with Glass Effect */
div[data-testid="stExpander"] {{
    background: {SURFACE} !important;
    backdrop-filter: blur(12px) !important;
    border: 1px solid {BORDER} !important;
    border-radius: 14px !important;
    margin-bottom: 1rem !important;
}}

/* Colored Badges */
.badge {{
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem 1.25rem;
    border-radius: 999px;
    font-size: 0.875rem;
    font-weight: 600;
    backdrop-filter: blur(12px);
}}

.badge-success {{
    background: linear-gradient(135deg, rgba(16, 185, 129, 0.2), rgba(6, 182, 212, 0.2));
    border: 1px solid rgba(16, 185, 129, 0.4);
    color: {SUCCESS};
    box-shadow: 0 4px 16px rgba(16, 185, 129, 0.2);
}}

.badge-warning {{
    background: linear-gradient(135deg, rgba(245, 158, 11, 0.2), rgba(251, 191, 36, 0.2));
    border: 1px solid rgba(245, 158, 11, 0.4);
    color: {WARNING};
    box-shadow: 0 4px 16px rgba(245, 158, 11, 0.2);
}}

.badge-info {{
    background: linear-gradient(135deg, rgba(59, 130, 246, 0.2), rgba(99, 102, 241, 0.2));
    border: 1px solid rgba(59, 130, 246, 0.4);
    color: {INFO};
    box-shadow: 0 4px 16px rgba(59, 130, 246, 0.2);
}}

/* Beautiful Scrollbar */
::-webkit-scrollbar {{
    width: 10px;
    height: 10px;
}}

::-webkit-scrollbar-track {{
    background: rgba(30, 41, 59, 0.5);
    border-radius: 10px;
}}

::-webkit-scrollbar-thumb {{
    background: linear-gradient(135deg, {PRIMARY}, {SECONDARY});
    border-radius: 10px;
}}

::-webkit-scrollbar-thumb:hover {{
    background: linear-gradient(135deg, {SECONDARY}, {ACCENT});
}}

/* Grid Layouts - Force Single Row for Stats */
.grid-5 {{
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 1rem;
}}

.grid-4 {{
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1.5rem;
}}

.grid-3 {{
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1.5rem;
}}

.grid-2 {{
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 1.5rem;
}}

/* Responsive Design - Keep stats side by side on larger screens */
@media (max-width: 1400px) {{
    .grid-5 {{ 
        grid-template-columns: repeat(5, 1fr);
        gap: 0.75rem;
    }}
}}

@media (max-width: 1100px) {{
    .grid-5 {{ 
        grid-template-columns: repeat(5, 1fr);
        gap: 0.5rem;
    }}
    .stat-card {{
        padding: 0.875rem 1rem;
    }}
    .stat-value {{
        font-size: 1.5rem;
    }}
    .stat-label {{
        font-size: 0.7rem;
    }}
}}

@media (max-width: 900px) {{
    .grid-5 {{ grid-template-columns: repeat(3, 1fr); }}
}}

@media (max-width: 768px) {{
    .grid-5, .grid-4, .grid-3, .grid-2 {{ grid-template-columns: 1fr; }}
    [data-testid="stAppViewContainer"] > .main {{ padding: 1rem !important; }}
    .page-title {{ font-size: 1.75rem; }}
}}

/* Metrics Enhancement */
[data-testid="stMetricValue"] {{
    color: {PRIMARY} !important;
    font-weight: 800 !important;
}}

hr {{
    border: none;
    height: 1px;
    background: linear-gradient(90deg, transparent, {BORDER}, transparent);
    margin: 2rem 0;
}}
</style>
"""


def apply_plotly_theme(fig: go.Figure) -> go.Figure:
    """Apply beautiful glassmorphism theme to Plotly figures."""
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(30, 41, 59, 0)",
        plot_bgcolor="rgba(51, 65, 85, 0.3)",
        font=dict(
            color=TEXT,
            family="Inter, -apple-system, BlinkMacSystemFont, sans-serif",
            size=13,
        ),
        colorway=[PRIMARY, SECONDARY, ACCENT, TERTIARY, SUCCESS, INFO, WARNING],
        height=fig.layout.height or 420,
        margin=dict(l=50, r=50, t=60, b=50),
        title=dict(
            font=dict(size=17, color=TEXT, family="Inter", weight=700),
            pad=dict(t=15, b=15),
        ),
        legend=dict(
            bgcolor="rgba(30, 41, 59, 0.9)",
            bordercolor="rgba(148, 163, 184, 0.3)",
            borderwidth=1,
            font=dict(size=12, color=TEXT_SECONDARY),
        ),
        hoverlabel=dict(
            bgcolor="rgba(30, 41, 59, 0.95)",
            bordercolor="rgba(99, 102, 241, 0.5)",
            font=dict(family="Inter", size=12, color=TEXT),
        ),
        xaxis=dict(
            gridcolor="rgba(148, 163, 184, 0.1)",
            zerolinecolor="rgba(148, 163, 184, 0.2)",
        ),
        yaxis=dict(
            gridcolor="rgba(148, 163, 184, 0.1)",
            zerolinecolor="rgba(148, 163, 184, 0.2)",
        ),
    )
    return fig


# Export for backward compatibility
DARK_THEME_CSS = ENTERPRISE_CSS
apply_plotly_dark_theme = apply_plotly_theme
