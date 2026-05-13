import streamlit as st
import plotly.graph_objects as go

COLORS = {
    "blue":   "#3b82f6",
    "green":  "#10b981",
    "amber":  "#f59e0b",
    "purple": "#8b5cf6",
    "cyan":   "#06b6d4",
    "pink":   "#ec4899",
    "red":    "#ef4444"
}

PLOT_BG  = "#ffffff"
PAPER_BG = "#ffffff"
FONT_CLR = "#1e293b"
GRID_CLR = "#e2e8f0"


def inject_css():
    st.markdown("""
    <style>

    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        color: #0f172a;
    }

    .stApp {
        background: #f8fafc;
        color: #0f172a;
    }

    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        padding-left: 2rem;
        padding-right: 2rem;
        max-width: 100% !important;
    }

    section[data-testid="stSidebar"] {
        background: #dbeafe !important;
        border-right: 1px solid #93c5fd;
    }

    section[data-testid="stSidebar"] * {
        color: #0f172a !important;
    }

    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        color: #0f172a !important;
        font-weight: 700;
    }

    section[data-testid="stSidebar"] .stRadio label {
        background: transparent;
        padding: 10px 14px;
        border-radius: 12px;
        margin-bottom: 6px;
        transition: 0.25s ease;
        font-weight: 500;
        color: #0f172a !important;
    }

    section[data-testid="stSidebar"] .stRadio label:hover {
        background: rgba(59,130,246,0.15);
    }

    [data-testid="collapsedControl"] { display: none !important; }
    button[kind="header"]            { display: none !important; }

    .page-header {
        background: white;
        border: 1px solid #dbeafe;
        border-radius: 20px;
        padding: 1.5rem 1.8rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 18px rgba(15,23,42,0.05);
    }

    .stTabs [data-baseweb="tab-list"] { gap: 12px; padding-bottom: 12px; }

    .stTabs [data-baseweb="tab"] {
        background: white !important;
        border: 1px solid #dbeafe !important;
        border-radius: 14px !important;
        padding: 12px 22px !important;
        color: #0f172a !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        transition: all 0.25s ease;
        box-shadow: 0 2px 10px rgba(15,23,42,0.04);
    }

    .stTabs [data-baseweb="tab"]:hover {
        background: #dbeafe !important;
        transform: translateY(-2px);
    }

    .stTabs [aria-selected="true"] {
        background: #3b82f6 !important;
        border-color: #3b82f6 !important;
        box-shadow: 0 6px 18px rgba(59,130,246,0.22);
    }

    .stTabs [aria-selected="true"] p { color: white !important; }

    input, textarea { color: #0f172a !important; }

    label { color: #0f172a !important; font-weight: 600; }

    .stButton > button {
        background: linear-gradient(135deg, #3b82f6, #2563eb);
        color: white !important;
        border: none;
        border-radius: 12px;
        padding: 0.6rem 1.2rem;
        font-weight: 600;
        transition: 0.25s ease;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 18px rgba(37,99,235,0.25);
    }

    .kpi-card {
        background: white;
        padding: 20px;
        border-radius: 20px;
        box-shadow: 0 4px 18px rgba(15,23,42,0.06);
        border: 1px solid #e2e8f0;
        transition: 0.25s ease;
    }

    .kpi-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 10px 24px rgba(15,23,42,0.10);
    }

    /* ── TABLE: NO CONTAINER, BARE TABLE ONLY ──────────────────── */
    /* Strip all wrapper styling so only the raw table is visible.  */

    [data-testid="stDataFrame"] {
        width: 100% !important;
        background: transparent !important;
        border: none !important;
        border-radius: 0 !important;
        box-shadow: none !important;
        padding: 0 !important;
    }

    [data-testid="stDataFrame"] > div {
        width: 100% !important;
        background: transparent !important;
        border: none !important;
        border-radius: 0 !important;
        box-shadow: none !important;
        padding: 0 !important;
    }

    [data-testid="stDataFrame"] iframe {
        width: 100% !important;
        min-width: 0 !important;
    }

    .stDataFrame {
        background: transparent !important;
        border: none !important;
        border-radius: 0 !important;
        box-shadow: none !important;
        padding: 0 !important;
        width: 100% !important;
        overflow-x: auto;
    }
    /* ────────────────────────────────────────────────────────────── */

    /* Plotly charts — styled via wrapper, no internal padding */
    .js-plotly-plot .plotly {
        border-radius: 14px;
        overflow: hidden;
    }

    [data-testid="stPlotlyChart"] > div {
        background: white;
        border-radius: 18px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 18px rgba(15,23,42,0.05);
        overflow: hidden;
    }

    div[data-testid="metric-container"] {
        background: white;
        border-radius: 18px;
        padding: 16px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 14px rgba(15,23,42,0.05);
    }

    div[data-testid="metric-container"] label          { color: #475569 !important; font-weight: 600; }
    div[data-testid="metric-container"] [data-testid="metric-value"] { color: #0f172a !important; }

    ::-webkit-scrollbar               { width: 8px; height: 8px; }
    ::-webkit-scrollbar-track         { background: #e2e8f0; }
    ::-webkit-scrollbar-thumb         { background: #94a3b8; border-radius: 10px; }
    ::-webkit-scrollbar-thumb:hover   { background: #64748b; }

    footer { visibility: hidden; }
    header { background: transparent !important; }

    </style>
    <style>

    /* REMOVE TOP SPACE */
    .block-container {
        padding-top: 0.8rem !important;
        margin-top: 0rem !important;
    }

    /* REMOVE HEADER GAP */
    header[data-testid="stHeader"] {
        height: 0rem !important;
        background: transparent !important;
    }

    /* REMOVE EXTRA SPACE ABOVE TITLE */
    div[data-testid="stVerticalBlock"] > div:first-child {
        padding-top: 0rem !important;
        margin-top: 0rem !important;
    }

    </style>
    """, unsafe_allow_html=True)


def sidebar_brand():
    with st.sidebar:
        st.markdown("""
            <div style="
                padding:1.25rem 0.5rem 1rem;
                border-bottom:1px solid #93c5fd;
                margin-bottom:1rem;
            ">
                <div style="display:flex;align-items:center;gap:0.6rem;">
                    <div style="font-size:1.6rem;">🚚</div>
                    <div>
                        <div style="font-size:0.95rem;font-weight:700;color:#0f172a;line-height:1.2;">
                            APL Logistics
                        </div>
                        <div style="font-size:0.7rem;color:#475569;font-weight:500;">
                            Supply Chain Analytics
                        </div>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)


def page_header(title, subtitle_or_icon="", icon=None):
    if icon is None:
        actual_icon     = subtitle_or_icon
        actual_subtitle = ""
    else:
        actual_icon     = icon
        actual_subtitle = subtitle_or_icon

    st.markdown(f"""
        <div style="padding:1.5rem 0 1rem;border-bottom:2px solid #dbeafe;margin-bottom:1.5rem;">
            <div style="display:flex;align-items:center;gap:0.75rem;margin-bottom:0.3rem;">
                <span style="font-size:1.75rem;">{actual_icon}</span>
                <h1 style="margin:0;font-size:1.35rem;font-weight:700;color:#0f172a;line-height:1.3;">
                    {title}
                </h1>
            </div>
            {"" if not actual_subtitle else
             f'<p style="margin:0;font-size:0.82rem;color:#64748b;padding-left:2.5rem;font-weight:500;">{actual_subtitle}</p>'}
        </div>
    """, unsafe_allow_html=True)


def section_header(title):
    st.markdown(f"""
        <div style="margin:1.75rem 0 0.75rem;padding-bottom:0.4rem;border-bottom:1px solid #dbeafe;">
            <span style="font-size:0.82rem;font-weight:700;color:#475569;
                         text-transform:uppercase;letter-spacing:0.08em;">
                {title}
            </span>
        </div>
    """, unsafe_allow_html=True)


def kpi_card(col, title, value, icon="📊", color="#3b82f6"):
    with col:
        st.markdown(f"""
            <div style="
                background:#ffffff;
                border:1px solid #e2e8f0;
                border-top:3px solid {color};
                border-radius:16px;
                padding:0.85rem 0.95rem;
                margin-bottom:0.45rem;
                min-height:110px;
                box-shadow:0 2px 10px rgba(15,23,42,0.05);
                display:flex;
                justify-content:space-between;
                align-items:flex-start;
                overflow:hidden;
            ">
                <!-- LEFT -->
                <div style="
                    flex:1;
                    min-width:0;
                    padding-right:0.65rem;
                ">
                    <!-- TITLE -->
                    <div style="
                        font-size:0.68rem;
                        font-weight:700;
                        color:#64748b;
                        text-transform:uppercase;
                        letter-spacing:1px;
                        margin-bottom:0.55rem;
                        line-height:1.35;
                    ">
                        {title}
                    </div>
                    <!-- VALUE -->
                    <div style="
                        font-size:2rem;
                        font-weight:800;
                        color:#0f172a;
                        line-height:1.05;
                        white-space:nowrap;
                        overflow:hidden;
                        text-overflow:ellipsis;
                    ">
                        {value}
                    </div>
                </div>
                <!-- ICON -->
                <div style="
                    width:48px;
                    min-width:48px;
                    height:48px;
                    border-radius:14px;
                    background:{color}15;
                    display:flex;
                    align-items:center;
                    justify-content:center;
                    font-size:1.45rem;
                    flex-shrink:0;
                ">
                    {icon}
                </div>
            </div>
        """, unsafe_allow_html=True)


def chart_label(title, subtitle=""):
    st.markdown(f"""
        <div style="margin-bottom:0.5rem;">
            <div style="font-size:0.88rem;font-weight:700;color:#1e293b;">{title}</div>
            {"" if not subtitle else
             f'<div style="font-size:0.75rem;color:#64748b;margin-top:3px;font-weight:400;">{subtitle}</div>'}
        </div>
    """, unsafe_allow_html=True)


def insight_card(text, kind="info"):
    palette = {
        "success": ("#f0fdf4", "#166534", "#22c55e"),
        "warning": ("#fffbeb", "#78350f", "#f59e0b"),
        "error":   ("#fef2f2", "#7f1d1d", "#ef4444"),
        "info":    ("#eff6ff", "#1e3a5f", "#3b82f6"),
    }
    bg, txt, border = palette.get(kind, palette["info"])
    st.markdown(f"""
        <div style="
            background:{bg};
            border-left:4px solid {border};
            border-radius:8px;
            padding:0.75rem 1rem;
            margin:0.5rem 0;
            font-size:0.83rem;
            color:{txt};
            line-height:1.6;
            font-weight:500;
        ">{text}</div>
    """, unsafe_allow_html=True)


def show_table(df, height=None, column_config=None):
    """
    Drop-in replacement for st.dataframe() that always stretches
    to fill the container width and respects optional height/column_config.
    Use this everywhere instead of calling st.dataframe() directly.

    Examples
    --------
    show_table(df)
    show_table(df, height=400)
    show_table(df, column_config={"Delay Gap": st.column_config.NumberColumn(format="%d days")})
    """
    kwargs = dict(use_container_width=True)
    if height is not None:
        kwargs["height"] = height
    if column_config is not None:
        kwargs["column_config"] = column_config
    st.dataframe(df, **kwargs)


def apply_plot_layout(fig, height=340):
    fig.update_layout(
        height=height,
        autosize=True,

        paper_bgcolor=PAPER_BG,
        plot_bgcolor=PLOT_BG,

        margin=dict(l=60, r=30, t=50, b=60),

        font=dict(family="Inter, sans-serif", color=FONT_CLR, size=11),

        legend=dict(
            bgcolor="rgba(255,255,255,0.95)",
            bordercolor="#e2e8f0",
            borderwidth=1,
            font=dict(color="#334155", size=10),
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),

        hoverlabel=dict(
            bgcolor="white",
            bordercolor="#e2e8f0",
            font=dict(color="#0f172a", size=12)
        ),
    )

    fig.update_xaxes(
        gridcolor=GRID_CLR,
        linecolor="#cbd5e1",
        linewidth=1,
        tickfont=dict(color=FONT_CLR, size=10),
        title_font=dict(color=FONT_CLR, size=11),
        automargin=True,
        title_standoff=18,
        zeroline=False,
    )

    fig.update_yaxes(
        gridcolor=GRID_CLR,
        linecolor="#cbd5e1",
        linewidth=1,
        tickfont=dict(color=FONT_CLR, size=10),
        title_font=dict(color=FONT_CLR, size=11),
        automargin=True,
        title_standoff=18,
        zeroline=False,
    )

    for trace in fig.data:
        try:
            if hasattr(trace, "marker") and hasattr(trace.marker, "line"):
                trace.marker.line.width = 0
        except Exception:
            pass

    return fig


def footer():
    st.markdown("""
        <div style="
            margin-top:3rem;
            padding-top:1rem;
            border-top:1px solid #e2e8f0;
            text-align:center;
            font-size:0.72rem;
            color:#94a3b8;
        ">
            APL Logistics · Global Supply Chain Analytics Platform · 2024
        </div>
    """, unsafe_allow_html=True)
