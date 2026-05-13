import streamlit as st
import plotly.express as px
import pandas as pd
from data_manager import apply_filters, init_data, preprocess
from style import (inject_css, sidebar_brand, page_header, section_header,
                   kpi_card, chart_label, insight_card, apply_plot_layout, footer, COLORS)
from utils import calculate_kpis

st.set_page_config(
    page_title="Delivery Performance Overview | APL Logistics",
    layout="wide",
    page_icon="📊",
)
inject_css()
sidebar_brand()

df = apply_filters()
page_header("Delivery Performance Overview", "Delivery performance across all routes and regions", "📦")

if df is None:
    st.warning("Please upload a dataset from the Home page.")
    st.stop()

if df.empty:
    st.warning("No data matches the current filters.")
    st.stop()

df = preprocess(df)

if "Delayed" not in df.columns:
    if "Late_delivery_risk" in df.columns:
        df["Delayed"] = df["Late_delivery_risk"]
    else:
        df["Delayed"] = 0

if "Real Shipping Days" not in df.columns:
    df["Real Shipping Days"] = 0

if "Scheduled Shipping Days" not in df.columns:
    df["Scheduled Shipping Days"] = 0

# Convert delayed to boolean
df["Delayed"] = df["Delayed"].astype(bool)


kpis = calculate_kpis(df)

total_orders = kpis.get('Total Orders', 0)
on_time_pct  = kpis.get('On-Time %', 0)
delay_gap    = kpis.get('Average Delay Gap', 0)
risk_pct     = kpis.get('Late Delivery Risk %', 0)
sales        = kpis.get('Total Sales', 0)
profit       = kpis.get('Total Profit', 0)

routes = df['Order Region'].nunique() if 'Order Region' in df.columns else 0

c1, c2, c3, c4  = st.columns(4)

kpi_card(c1, "Total Orders",       f"{total_orders:,}",       icon="📦", color=COLORS["blue"])
kpi_card(c2, "On-Time Delivery",   f"{on_time_pct:.1f}%",     icon="✅", color=COLORS["green"])
kpi_card(c3, "Avg Delay Gap",      f"{delay_gap:.1f} Days",   icon="⏱️", color=COLORS["cyan"])
kpi_card(c4, "Late Delivery Risk", f"{risk_pct:.1f}%",        icon="⚠️", color=COLORS["amber"])

c5,c6 = st.columns(2,gap="medium")
kpi_card(c5, "Total Sales",        f"${sales:,.0f}",          icon="💰", color=COLORS["purple"])
kpi_card(c6, "Regions Covered",    f"{routes}",               icon="🌍", color=COLORS["pink"])

section_header("Delivery Performance Overview")

cl, cr = st.columns([3, 2])

with cl:
    chart_label("Delivery Performance Distribution", "Comparison of shipment delivery outcomes")
    if 'Delivery Performance' in df.columns:
        perf = df['Delivery Performance'].value_counts().reset_index()
        perf.columns = ['Status', 'Orders']
        fig = px.bar(
            perf, x='Status', y='Orders', color='Status',
            color_discrete_sequence=[COLORS["green"], COLORS["amber"], COLORS["red"]]
        )
        apply_plot_layout(fig, 320)
        st.plotly_chart(fig, use_container_width=True)

with cr:
    chart_label("Delayed vs Non-Delayed Orders", "Overall shipment risk split")
    if 'Delayed' in df.columns:
        pie_df = pd.DataFrame({
            "Status": ["On-Time", "Delayed"],
            "Count":  [df['Delayed'].eq(False).sum(), df['Delayed'].sum()]
        })
        fig2 = px.pie(
            pie_df, names='Status', values='Count', hole=0.55,
            color_discrete_sequence=[COLORS["green"], COLORS["red"]]
        )
        fig2.update_traces(textinfo='percent+label')
        apply_plot_layout(fig2, 320)
        st.plotly_chart(fig2, use_container_width=True)

section_header("Shipping Time Analysis")

cl2, cr2 = st.columns(2)

with cl2:
    chart_label("Real Shipping Days", "Actual delivery duration distribution")
    if 'Real Shipping Days' in df.columns:
        fig3 = px.histogram(df, x='Real Shipping Days', nbins=25,
                            color_discrete_sequence=[COLORS["blue"]])
        apply_plot_layout(fig3, 300)
        st.plotly_chart(fig3, use_container_width=True)

with cr2:
    chart_label("Scheduled vs Real Shipping Days", "Efficiency comparison")
    if 'Scheduled Shipping Days' in df.columns and 'Real Shipping Days' in df.columns:
        fig4 = px.scatter(
            df, x='Scheduled Shipping Days', y='Real Shipping Days',
            color='Delivery Performance', opacity=0.7
        )
        apply_plot_layout(fig4, 300)
        st.plotly_chart(fig4, use_container_width=True)

section_header("Regional Logistics Performance")

if 'Order Region' in df.columns:
    region_df = (
        df.groupby('Order Region')
        .agg(
            Orders=('Order Region', 'count'),
            Avg_Real_Shipping=('Real Shipping Days', 'mean'),
            Delay_Risk=('Delayed', 'mean')
        )
        .reset_index()
    )
    region_df['Avg_Real_Shipping'] = region_df['Avg_Real_Shipping'].round(1)
    region_df['Delay_Risk'] = (region_df['Delay_Risk'] * 100).round(1)
    region_df.columns = ['Region', 'Orders', 'Avg Shipping Days', 'Delay Risk %']

    st.dataframe(
        region_df.style
        .background_gradient(subset=['Avg Shipping Days'], cmap='YlOrRd')
        .background_gradient(subset=['Delay Risk %'], cmap='Reds')
        .format({'Avg Shipping Days': '{:.1f}', 'Delay Risk %': '{:.1f}%'}),
        use_container_width=True,
        height=320
    )

section_header("Transportation Mode Analysis")

if 'Ship Mode' in df.columns:
    ship_df = (
        df.groupby('Ship Mode')
        .agg(
            Orders=('Ship Mode', 'count'),
            Avg_Shipping=('Real Shipping Days', 'mean'),
            Delay_Risk=('Delayed', 'mean')
        )
        .reset_index()
    )
    ship_df['Avg_Shipping'] = ship_df['Avg_Shipping'].round(1)
    ship_df['Delay_Risk']   = (ship_df['Delay_Risk'] * 100).round(1)
    ship_df.columns = ['Ship Mode', 'Orders', 'Avg Shipping Days', 'Delay Risk %']

    st.dataframe(
        ship_df.style
        .background_gradient(subset=['Avg Shipping Days'], cmap='Blues')
        .format({'Avg Shipping Days': '{:.1f}', 'Delay Risk %': '{:.1f}%'}),
        use_container_width=True,
        height=240
    )

section_header("Operational Insights")

if 'Order Region' in df.columns and 'region_df' in dir():
    best_region  = region_df.nsmallest(1, 'Avg Shipping Days').iloc[0]
    worst_region = region_df.nlargest(1, 'Avg Shipping Days').iloc[0]

    insight_card(
        f"🏆 Best logistics region: <strong>{best_region['Region']}</strong> "
        f"with an average shipping time of <strong>{best_region['Avg Shipping Days']:.1f} days</strong>.",
        "success"
    )
    insight_card(
        f"⚠️ Slowest performing region: <strong>{worst_region['Region']}</strong> "
        f"with an average shipping duration of <strong>{worst_region['Avg Shipping Days']:.1f} days</strong>.",
        "warning"
    )

if risk_pct > 30:
    insight_card(
        f"🔴 High delivery risk detected with <strong>{risk_pct:.1f}%</strong> "
        f"late delivery risk across shipments.",
        "error"
    )
else:
    insight_card(
        f"✅ Delivery risk remains stable at <strong>{risk_pct:.1f}%</strong>, "
        f"indicating efficient logistics performance.",
        "info"
    )

footer()
