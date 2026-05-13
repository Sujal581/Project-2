import streamlit as st
import plotly.express as px
import pandas as pd
from data_manager import apply_filters, init_data, preprocess
from style import (inject_css, sidebar_brand, page_header, section_header,
                   kpi_card, chart_label, insight_card, apply_plot_layout, footer, COLORS)
from utils import calculate_kpis

st.set_page_config(
    page_title="Delay Risk Analysis | APL Logistics",
    layout="wide",
    page_icon="📊"
)
inject_css()
sidebar_brand()

df = apply_filters()
page_header("Delay Risk Analysis", "High-level & Low-level Risk from all over the regions", "🕑")

if df is None:
    st.warning("Please upload a dataset from the Home page.")
    st.stop()

if df.empty:
    st.warning("No data matches the current filters.")
    st.stop()

df = preprocess(df)

section_header("Delay Risk Analysis")

high_risk = (
    df['High Risk Shipment'].eq('High Risk').sum()
    if 'High Risk Shipment' in df.columns else 0
)
low_risk = (
    df['High Risk Shipment'].eq('Low Risk').sum()
    if 'High Risk Shipment' in df.columns else 0
)
risk_pct = (high_risk / len(df)) * 100 if len(df) > 0 else 0
avg_delay_gap = df['Delay Gap'].mean() if 'Delay Gap' in df.columns else 0

c1, c2, c3, c4 = st.columns(4)
kpi_card(c1, "High Risk Shipments", f"{high_risk:,}",           icon="⚠️", color=COLORS["red"])
kpi_card(c2, "Low Risk Shipments",  f"{low_risk:,}",            icon="✅", color=COLORS["green"])
kpi_card(c3, "Risk Percentage",     f"{risk_pct:.1f}%",         icon="📊", color=COLORS["amber"])
kpi_card(c4, "Avg Delay Gap",       f"{avg_delay_gap:.1f} Days",icon="⏱️", color=COLORS["cyan"])

cl, cr = st.columns([2, 3])

with cl:
    chart_label("Shipment Risk Split", "High vs Low delivery risk")
    risk_df = pd.DataFrame({
        "Risk Level": ["High Risk", "Low Risk"],
        "Shipments":  [high_risk, low_risk]
    })
    fig1 = px.pie(
        risk_df, names='Risk Level', values='Shipments', hole=0.58,
        color_discrete_sequence=[COLORS["red"], COLORS["green"]]
    )
    fig1.update_traces(textinfo='percent+label')
    apply_plot_layout(fig1, 320)
    st.plotly_chart(fig1, use_container_width=True)

with cr:
    chart_label("Delay Gap Distribution", "Shipping delay spread analysis")
    if 'Delay Gap' in df.columns:
        fig2 = px.histogram(df, x='Delay Gap', nbins=30,
                            color_discrete_sequence=[COLORS["amber"]])
        fig2.update_traces(marker_line_width=1, marker_line_color="#0f172a")
        apply_plot_layout(fig2, 320)
        st.plotly_chart(fig2, use_container_width=True)

section_header("Delay Risk by Ship Mode")

if 'Ship Mode' in df.columns:
    ship_risk = (
        df.groupby('Ship Mode')
        .agg(
            Shipments=('Ship Mode', 'count'),
            Avg_Delay=('Delay Gap', 'mean'),
            Risk_Rate=('Delayed', 'mean')
        )
        .reset_index()
    )
    ship_risk['Avg_Delay']  = ship_risk['Avg_Delay'].round(1)
    ship_risk['Risk_Rate']  = (ship_risk['Risk_Rate'] * 100).round(1)
    ship_risk.columns = ['Ship Mode', 'Shipments', 'Avg Delay (Days)', 'Delay Risk %']

    st.dataframe(
        ship_risk.style
        .background_gradient(subset=['Avg Delay (Days)'], cmap='OrRd')
        .background_gradient(subset=['Delay Risk %'],    cmap='Reds')
        .format({'Avg Delay (Days)': '{:.1f}', 'Delay Risk %': '{:.1f}%'}),
        use_container_width=True,
        height=250
    )

section_header("Regional Delay Risk Analysis")

if 'Order Region' in df.columns:
    region_risk = (
        df.groupby('Order Region')
        .agg(
            Shipments=('Order Region', 'count'),
            Avg_Delay=('Delay Gap', 'mean'),
            Risk_Rate=('Delayed', 'mean')
        )
        .reset_index()
    )
    region_risk['Avg_Delay'] = region_risk['Avg_Delay'].round(1)
    region_risk['Risk_Rate'] = (region_risk['Risk_Rate'] * 100).round(1)

    sorted_df = region_risk.sort_values('Risk_Rate', ascending=False)

    fig3 = px.bar(
        sorted_df,
        x='Order Region',
        y='Risk_Rate',
        color='Risk_Rate',
        color_continuous_scale='Reds',
        range_color=[0, sorted_df['Risk_Rate'].max() or 100],  # never goes negative
    )

    fig3.update_layout(
        yaxis_title="Delay Risk %",
        xaxis_title="",
        yaxis=dict(range=[0, max(sorted_df['Risk_Rate'].max() * 1.15, 5)]),
        coloraxis_colorbar=dict(
            title="Risk %",
            tickformat=".0f",
            ticksuffix="%",
        ),
    )

    fig3 = apply_plot_layout(fig3, 380)  # assign the return value

    fig3.update_xaxes(tickangle=-40)     # angled labels so regions don't overlap

    st.plotly_chart(fig3, use_container_width=True)

section_header("High Risk Shipment Records")

risk_cols = [col for col in [
    'Order Region', 'Order Country', 'Ship Mode', 'Real Shipping Days',
    'Scheduled Shipping Days', 'Delay Gap', 'Delivery Status', 'High Risk Shipment'
] if col in df.columns]

if 'High Risk Shipment' in df.columns:
    high_risk_df = df[df['High Risk Shipment'] == 'High Risk'][risk_cols].head(100)
    st.dataframe(high_risk_df, use_container_width=True, height=320)
    
section_header("Risk Insights & Recommendations")

if 'Ship Mode' in df.columns and 'ship_risk' in dir():
    highest_risk_mode = ship_risk.sort_values('Delay Risk %', ascending=False).iloc[0]
    insight_card(
        f"⚠️ Highest delay risk observed in <strong>{highest_risk_mode['Ship Mode']}</strong> "
        f"shipping mode with a delay risk of <strong>{highest_risk_mode['Delay Risk %']:.1f}%</strong>.",
        "warning"
    )

if risk_pct > 30:
    insight_card(
        f"🔴 Overall high-risk shipment percentage is <strong>{risk_pct:.1f}%</strong>. "
        f"Operational improvements and route optimization are recommended.",
        "error"
    )
else:
    insight_card(
        f"✅ Overall shipment risk remains controlled at <strong>{risk_pct:.1f}%</strong>.",
        "success"
    )

if avg_delay_gap > 2:
    insight_card(
        f"📦 Average shipment delay gap is <strong>{avg_delay_gap:.1f} days</strong>, "
        f"indicating possible logistics bottlenecks.",
        "info"
    )

footer()
