import streamlit as st
import io
import pandas as pd
from style import (inject_css, sidebar_brand, page_header, section_header,
                   kpi_card, chart_label, insight_card, apply_plot_layout, footer, COLORS)
from utils import clean_data, feature_engineering
from data_manager import init_data, apply_filters

st.set_page_config(
    page_icon="📈",
    page_title="APL Logistics",
    layout="wide",
    initial_sidebar_state="expanded"
)
inject_css()
sidebar_brand()

page_header(
    "Global Supply Chain Analytics: Delivery Performance, Delay Risk & Logistics Efficiency Dashboard",
    "Real-time logistics intelligence and supply chain monitoring",
    "🌍"
)

c1, c2, c3, c4 = st.columns(4)
kpi_card(c1, "Shipments Delivered", "10M+",   icon="🚚", color="#3b82f6")
kpi_card(c2, "Warehouses",          "500+",   icon="🏭", color="#22c55e")
kpi_card(c3, "Countries Served",    "60+",    icon="🌍", color="#f59e0b")
kpi_card(c4, "Supply Chain Clients","1,000+", icon="📦", color="#a855f7")

section_header("Data Setup")

if "master_df" in st.session_state:
    df = st.session_state.master_df
    insight_card(
        f"✅ <strong>{len(df):,} global shipments</strong> loaded · {df.shape[1]} columns · "
        "Use the sidebar to navigate analytics pages.",
        "success"
    )
    if st.button("↑ Upload Different CSV"):
        del st.session_state.master_df
        st.rerun()
else:
    st.markdown("""
        <div style="background:#ffffff;border:1px dashed #334155;border-radius:14px;
                    padding:2.5rem;text-align:center;margin-bottom:1rem;">
            <div style="font-size:2rem;margin-bottom:0.6rem;">📂</div>
            <div style="font-size:1rem;font-weight:700;color:#0f172a;margin-bottom:0.35rem;">
                Upload Your Global Shipping Data
            </div>
            <div style="font-size:0.82rem;color:#0f172a;">
                Upload <strong style="color:#475569;">APL_Logistics.csv</strong> to unlock all analytics pages.
            </div>
        </div>
    """, unsafe_allow_html=True)

uploaded = st.file_uploader(
    "Upload CSV",
    type=["csv"],
    label_visibility="collapsed"
)
if uploaded:
    try:
        raw_bytes = uploaded.getvalue()
        df = None
        # Fast encodings first
        fast_encodings = [
            "utf-8",
            "utf-8-sig",
            "cp1252",
            "latin1"
        ]
        for enc in fast_encodings:
            try:
                df = pd.read_csv(
                    io.BytesIO(raw_bytes),
                    encoding=enc,
                    engine="c",   # MUCH faster
                    low_memory=False
                )
                break
            except Exception:
                continue
        # Fallback only if all fail
        if df is None:
            try:
                df = pd.read_csv(
                    io.BytesIO(raw_bytes),
                    encoding="latin1",
                    engine="python",
                    on_bad_lines="skip"
                )
            except Exception:
                pass
        if df is None:
            st.error("Could not parse CSV")
        else:
            df = clean_data(df)
            df = feature_engineering(df)
            st.session_state.master_df = df
            st.success("CSV Loaded Successfully")
    except Exception as e:
        st.error(f"Could not parse CSV: {e}")

section_header("About APL Logistics")
tab1, tab2, tab3, tab4 = st.tabs([
    "🌍 Company Overview",
    "🚚 Logistics Services",
    "📊 Operations Insights",
    "🏭 Distribution Network"
])

with tab1:
    cl, cr = st.columns(2)
    with cl:
        st.markdown("""
            <div style="background:#ffffff;border:1px solid #dbeafe;border-radius:12px;padding:1.25rem;">
                <h3 style="margin-top:0!important;">Supply Chain Services</h3>
                <ul style="color:#475569;list-style:none;padding:0;margin:0;">
                    <li style="padding:0.45rem 0;border-bottom:1px solid #e2e8f0;">🚚 Global Freight & Transportation Management</li>
                    <li style="padding:0.45rem 0;border-bottom:1px solid #e2e8f0;">🏭 Warehousing & Distribution Operations</li>
                    <li style="padding:0.45rem 0;border-bottom:1px solid #e2e8f0;">📦 Inventory & Order Fulfillment Solutions</li>
                    <li style="padding:0.45rem 0;border-bottom:1px solid #e2e8f0;">🌍 International Supply Chain & Trade Compliance</li>
                    <li style="padding:0.45rem 0;">📊 Logistics Analytics & Delivery Optimization</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)
    with cr:
        st.markdown("""
            <div style="background:#ffffff;border:1px solid #dbeafe;border-radius:12px;padding:1.25rem;">
                <h3 style="margin-top:0!important;">Global Operations</h3>
                <p style="color:#475569;font-size:0.875rem;">
                    APL Logistics manages large-scale supply chain operations across
                    <strong style="color:black;">60+ countries</strong> with advanced transportation,
                    warehousing, and distribution networks.
                </p>
                <div style="margin-top:0.75rem;padding:0.7rem;background:#f1f5f9;border-radius:8px;border-left:3px solid #3b82f6;">
                    <div style="font-size:0.78rem;color:#3b82f6;font-weight:700;">Real-Time Logistics Visibility</div>
                    <div style="font-size:0.78rem;color:#475569;margin-top:2px;">
                        AI-powered tracking and analytics improve delivery performance and reduce delay risks.
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

with tab2:
    cl, cr = st.columns(2)
    with cl:
        st.markdown("""
            <div style="background:#ffffff;border:1px solid #dbeafe;border-radius:12px;padding:1.25rem;">
                <h3 style="margin-top:0!important;">Global Logistics Services</h3>
                <ul style="color:#475569;list-style:none;padding:0;margin:0;">
                    <li style="padding:0.4rem 0;border-bottom:1px solid #0f172a;">🚚 Freight Forwarding</li>
                    <li style="padding:0.4rem 0;border-bottom:1px solid #0f172a;">📦 Transportation Management</li>
                    <li style="padding:0.4rem 0;border-bottom:1px solid #0f172a;">🏭 Warehousing & Distribution</li>
                    <li style="padding:0.4rem 0;">🌍 International Trade Compliance</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)
    with cr:
        st.markdown("""
            <div style="background:#ffffff;border:1px solid #dbeafe;border-radius:12px;padding:1.25rem;">
                <h3 style="margin-top:0!important;">Supply Chain Capabilities</h3>
                <ul style="color:#475569;list-style:none;padding:0;margin:0;">
                    <li style="padding:0.4rem 0;border-bottom:1px solid #0f172a;">📊 Logistics Analytics & Insights</li>
                    <li style="padding:0.4rem 0;border-bottom:1px solid #0f172a;">⚡ Real-Time Shipment Tracking</li>
                    <li style="padding:0.4rem 0;border-bottom:1px solid #0f172a;">🧠 AI-Based Delay Risk Prediction</li>
                    <li style="padding:0.4rem 0;">🔄 End-to-End Supply Chain Optimization</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)

with tab3:
    cols = st.columns(4)
    for col, (icon, name, desc) in zip(cols, [
        ("🚚", "Delivery Performance", "Track on-time shipment success rates"),
        ("⚠️", "Delay Risk",           "Identify high-risk delivery disruptions"),
        ("📦", "Warehouse Efficiency", "Monitor inventory & fulfillment operations"),
        ("🌍", "Global Operations",    "Analyze international logistics performance"),
    ]):
        with col:
            st.markdown(f"""
                <div style="background:#ffffff;border:1px solid #dbeafe;border-radius:12px;
                            padding:1.1rem;text-align:center;">
                    <div style="font-size:1.8rem;margin-bottom:0.4rem;">{icon}</div>
                    <div style="font-weight:700;color:#0f172a;font-size:0.875rem;">{name}</div>
                    <div style="font-size:0.76rem;color:#475569;margin-top:0.3rem;">{desc}</div>
                </div>
            """, unsafe_allow_html=True)

with tab4:
    st.markdown("""
        <div style="background:#ffffff;border:1px solid #dbeafe;border-radius:12px;padding:1.25rem;">
            <h3 style="margin-top:0!important;">Global Supply Chain & Distribution Network</h3>
            <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:0.75rem;margin-top:0.75rem;">
                <div style="background:#f1f5f9;border-radius:8px;padding:0.75rem;border:1px solid #e2e8f0;">
                    <div style="font-size:0.8rem;font-weight:700;color:#22c55e;">✔ Global Reach</div>
                    <div style="font-size:0.75rem;color:#475569;margin-top:2px;">Operations across 60+ countries worldwide</div>
                </div>
                <div style="background:#f1f5f9;border-radius:8px;padding:0.75rem;border:1px solid #e2e8f0;">
                    <div style="font-size:0.8rem;font-weight:700;color:#22c55e;">✔ Smart Warehousing</div>
                    <div style="font-size:0.75rem;color:#475569;margin-top:2px;">Optimized inventory and fulfillment systems</div>
                </div>
                <div style="background:#f1f5f9;border-radius:8px;padding:0.75rem;border:1px solid #e2e8f0;">
                    <div style="font-size:0.8rem;font-weight:700;color:#22c55e;">✔ Real-Time Logistics</div>
                    <div style="font-size:0.75rem;color:#475569;margin-top:2px;">Advanced tracking and delivery analytics</div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

footer()
