import streamlit as st
import plotly.express as px
import pandas as pd
from data_manager import apply_filters, init_data,preprocess
from style import (inject_css, sidebar_brand, page_header, section_header,
                   kpi_card, chart_label, insight_card, apply_plot_layout, footer, COLORS)
from utils import calculate_kpis
st.set_page_config(
    page_title="Shipping Mode Comparison | APL Logistics",
    layout="wide",
    page_icon="🚛"
)
inject_css()
sidebar_brand()


df = apply_filters()
page_header("Shipping Mode Comparison", "Comparison of shipping from all over the region", "🚛")

if df is None:
    st.warning("Please upload a dataset from the Home page.")
    st.stop()

if df.empty:
    st.warning("No data matches the current filters.")
    st.stop()

df = preprocess(df)

total_modes = df['Ship Mode'].nunique() if 'Ship Mode' in df.columns else 0
avg_shipping_days = df['Real Shipping Days'].mean() if 'Real Shipping Days' in df.columns else 0
delay_rate = df['Delayed'].mean() * 100 if 'Delayed' in df.columns else 0
avg_efficiency = df['Shipping Efficiency %'].mean() if 'Shipping Efficiency %' in df.columns else 0

c1, c2, c3, c4 = st.columns(4)
kpi_card(c1, "Shipping Modes",   f"{total_modes}",           icon="🚚", color=COLORS["blue"])
kpi_card(c2, "Avg Shipping Days",f"{avg_shipping_days:.1f}", icon="⏱️", color=COLORS["cyan"])
kpi_card(c3, "Delay Rate",       f"{delay_rate:.1f}%",       icon="⚠️", color=COLORS["amber"])
kpi_card(c4, "Avg Efficiency",   f"{avg_efficiency:.1f}%",   icon="📦", color=COLORS["green"])

section_header("Shipping Mode Performance Summary")

ship_mode_df = None
if 'Ship Mode' in df.columns:
    ship_mode_df = (
        df.groupby('Ship Mode')
        .agg(
            Total_Orders=('Ship Mode', 'count'),
            Avg_Real_Shipping=('Real Shipping Days', 'mean'),
            Avg_Scheduled_Shipping=('Scheduled Shipping Days', 'mean'),
            Avg_Delay=('Delay Gap', 'mean'),
            Delay_Rate=('Delayed', 'mean'),
            Avg_Efficiency=('Shipping Efficiency %', 'mean'),
            Total_Sales=('Sales', 'sum'),
            Total_Profit=('Profit Per Order', 'sum')
        )
        .reset_index()
    )
    ship_mode_df['Avg_Real_Shipping']      = ship_mode_df['Avg_Real_Shipping'].round(1)
    ship_mode_df['Avg_Scheduled_Shipping'] = ship_mode_df['Avg_Scheduled_Shipping'].round(1)
    ship_mode_df['Avg_Delay']              = ship_mode_df['Avg_Delay'].round(1)
    ship_mode_df['Delay_Rate']             = (ship_mode_df['Delay_Rate'] * 100).round(1)
    ship_mode_df['Avg_Efficiency']         = ship_mode_df['Avg_Efficiency'].round(1)
    ship_mode_df['Total_Sales']            = ship_mode_df['Total_Sales'].round(0)
    ship_mode_df['Total_Profit']           = ship_mode_df['Total_Profit'].round(0)
    ship_mode_df.columns = [
        'Ship Mode', 'Orders', 'Real Shipping Days', 'Scheduled Shipping Days',
        'Avg Delay Gap', 'Delay Rate (%)', 'Efficiency (%)', 'Total Sales', 'Total Profit'
    ]

    st.dataframe(
        ship_mode_df.style
        .background_gradient(subset=['Delay Rate (%)'], cmap='Reds')
        .background_gradient(subset=['Efficiency (%)'], cmap='Greens')
        .format({
            'Delay Rate (%)': '{:.1f}%',
            'Efficiency (%)': '{:.1f}%',
            'Total Sales':    '${:,.0f}',
            'Total Profit':   '${:,.0f}'
        }),
        use_container_width=True,
        height=320
    )

section_header("Shipping Mode Visual Analysis")

if ship_mode_df is not None:
    cl, cr = st.columns(2)

    with cl:
        chart_label("Delay Rate by Ship Mode", "Transportation risk comparison")
        fig1 = px.bar(
            ship_mode_df.sort_values('Delay Rate (%)', ascending=False),
            x='Ship Mode', y='Delay Rate (%)',
            color='Delay Rate (%)', color_continuous_scale='Reds'
        )
        fig1.update_layout(xaxis_title="", yaxis_title="Delay Rate (%)")
        apply_plot_layout(fig1, 320)
        st.plotly_chart(fig1, use_container_width=True)

    with cr:
        chart_label("Shipping Efficiency Comparison", "Operational efficiency across ship modes")
        fig2 = px.bar(
            ship_mode_df.sort_values('Efficiency (%)', ascending=False),
            x='Ship Mode', y='Efficiency (%)',
            color='Efficiency (%)', color_continuous_scale='Greens'
        )
        fig2.update_layout(xaxis_title="", yaxis_title="Efficiency (%)")
        apply_plot_layout(fig2, 320)
        st.plotly_chart(fig2, use_container_width=True)

section_header("Shipping Duration Analysis")

cl2, cr2 = st.columns(2)

with cl2:
    chart_label("Real Shipping Days", "Actual delivery duration by ship mode")
    if 'Ship Mode' in df.columns and 'Real Shipping Days' in df.columns:
        fig3 = px.box(df, x='Ship Mode', y='Real Shipping Days', color='Ship Mode')
        apply_plot_layout(fig3, 320)
        st.plotly_chart(fig3, use_container_width=True)

with cr2:
    chart_label("Scheduled vs Real Shipping", "Delivery timeline comparison")
    if 'Scheduled Shipping Days' in df.columns and 'Real Shipping Days' in df.columns:
        fig4 = px.scatter(
            df, x='Scheduled Shipping Days', y='Real Shipping Days',
            color='Ship Mode', opacity=0.7
        )
        apply_plot_layout(fig4, 320)
        st.plotly_chart(fig4, use_container_width=True)

section_header("Sales & Profit by Ship Mode")

if ship_mode_df is not None:
    cl3, cr3 = st.columns(2)

    with cl3:
        chart_label("Total Sales", "Revenue contribution by ship mode")
        fig5 = px.pie(ship_mode_df, names='Ship Mode', values='Total Sales', hole=0.55)
        apply_plot_layout(fig5, 320)
        st.plotly_chart(fig5, use_container_width=True)

    with cr3:
        chart_label("Total Profit", "Profitability comparison")
        fig6 = px.bar(
            ship_mode_df.sort_values('Total Profit', ascending=False),
            x='Ship Mode', y='Total Profit',
            color='Total Profit', color_continuous_scale='Blues'
        )
        fig6.update_layout(xaxis_title="", yaxis_title="Profit")
        apply_plot_layout(fig6, 320)
        st.plotly_chart(fig6, use_container_width=True)

section_header("Business Insights")

if ship_mode_df is not None:
    best_efficiency = ship_mode_df.sort_values('Efficiency (%)', ascending=False).iloc[0]
    highest_delay   = ship_mode_df.sort_values('Delay Rate (%)', ascending=False).iloc[0]
    highest_profit  = ship_mode_df.sort_values('Total Profit',   ascending=False).iloc[0]

    insight_card(
        f"🏆 Most efficient shipping mode: <strong>{best_efficiency['Ship Mode']}</strong> "
        f"with an average efficiency of <strong>{best_efficiency['Efficiency (%)']:.1f}%</strong>.",
        "success"
    )
    insight_card(
        f"⚠️ Highest delay risk observed in <strong>{highest_delay['Ship Mode']}</strong> "
        f"with a delay rate of <strong>{highest_delay['Delay Rate (%)']:.1f}%</strong>.",
        "warning"
    )
    insight_card(
        f"💰 Highest profit generated through <strong>{highest_profit['Ship Mode']}</strong> "
        f"with total profit of <strong>${highest_profit['Total Profit']:,.0f}</strong>.",
        "info"
    )

footer()
