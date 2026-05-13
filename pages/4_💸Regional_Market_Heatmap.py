import streamlit as st
import plotly.express as px
import pandas as pd
from data_manager import apply_filters, init_data, preprocess
from style import (inject_css, sidebar_brand, page_header, section_header,
                   kpi_card, chart_label, insight_card, apply_plot_layout, footer, COLORS)
from utils import calculate_kpis

st.set_page_config(
    page_title="Regional & Market Heatmap | APL Logistics",
    layout="wide",
    page_icon="💸"
)
inject_css()
sidebar_brand()

df = apply_filters()
page_header("Regional & Market Heatmap", "Sales and delay risk across regions and markets", "💸")

if df is None:
    st.warning("Please upload a dataset from the Home page.")
    st.stop()

if df.empty:
    st.warning("No data matches the current filters.")
    st.stop()

df = preprocess(df)

total_markets = df['Market'].nunique()        if 'Market'       in df.columns else 0
total_regions = df['Order Region'].nunique()  if 'Order Region' in df.columns else 0
avg_delay     = df['Delay Gap'].mean()        if 'Delay Gap'    in df.columns else 0
total_sales   = df['Sales'].sum()             if 'Sales'        in df.columns else 0

c1, c2, c3, c4 = st.columns(4)
kpi_card(c1, "Markets Covered", f"{total_markets}",      icon="🌍", color=COLORS["blue"])
kpi_card(c2, "Regions",         f"{total_regions}",      icon="🗺️", color=COLORS["purple"])
kpi_card(c3, "Avg Delay Gap",   f"{avg_delay:.1f} Days", icon="⏱️", color=COLORS["amber"])
kpi_card(c4, "Total Sales",     f"${total_sales:,.0f}",  icon="💰", color=COLORS["green"])

section_header("Regional Logistics Performance")

region_df = None
if 'Order Region' in df.columns:
    region_df = (
        df.groupby('Order Region')
        .agg(
            Orders=('Order Region', 'count'),
            Sales=('Sales', 'sum'),
            Profit=('Profit Per Order', 'sum'),
            Avg_Delay=('Delay Gap', 'mean'),
            Delay_Risk=('Delayed', 'mean'),
            Efficiency=('Shipping Efficiency %', 'mean')
        )
        .reset_index()
    )
    region_df['Avg_Delay']   = region_df['Avg_Delay'].round(1)
    region_df['Delay_Risk']  = (region_df['Delay_Risk'] * 100).round(1)
    region_df['Efficiency']  = region_df['Efficiency'].round(1)
    region_df.columns = ['Region', 'Orders', 'Sales', 'Profit', 'Avg Delay (Days)', 'Delay Risk (%)', 'Efficiency (%)']

    st.dataframe(
        region_df.style
        .background_gradient(subset=['Delay Risk (%)'], cmap='Reds')
        .background_gradient(subset=['Efficiency (%)'], cmap='Greens')
        .format({
            'Sales':          '${:,.0f}',
            'Profit':         '${:,.0f}',
            'Delay Risk (%)': '{:.1f}%',
            'Efficiency (%)': '{:.1f}%'
        }),
        use_container_width=True,
        height=320
    )

# =========================================================
# MARKET SALES HEATMAP
# =========================================================

section_header("Market Sales Heatmap")

if 'Market' in df.columns and 'Order Region' in df.columns:

    market_sales = (
        df.groupby(['Market', 'Order Region'])['Sales']
        .sum()
        .reset_index()
    )

    fig1 = px.density_heatmap(
        market_sales,
        x='Market',
        y='Order Region',
        z='Sales',
        color_continuous_scale='Blues',
        text_auto=".2s"
    )

    fig1.update_layout(
        xaxis_title="Market",
        yaxis_title="Region",
        coloraxis_colorbar_title="Sales",
        title=None
    )

    fig1.update_xaxes(
        tickangle=-15
    )

    apply_plot_layout(fig1, 430)

    st.plotly_chart(
        fig1,
        use_container_width=True,
        config={
            "displayModeBar": False
        }
    )

# =========================================================
# REGIONAL DELAY RISK HEATMAP
# =========================================================

section_header("Regional Delay Risk Heatmap")

if 'Market' in df.columns and 'Order Region' in df.columns and 'Delayed' in df.columns:

    risk_heatmap = (
        df.groupby(['Market', 'Order Region'])['Delayed']
        .mean()
        .reset_index()
    )

    risk_heatmap['Delayed'] = (
        risk_heatmap['Delayed'] * 100
    ).round(1)

    fig2 = px.density_heatmap(
        risk_heatmap,
        x='Market',
        y='Order Region',
        z='Delayed',
        color_continuous_scale='Reds',
        text_auto=".1f"
    )

    fig2.update_layout(
        xaxis_title="Market",
        yaxis_title="Region",
        coloraxis_colorbar_title="Risk %",
        title=None
    )

    fig2.update_xaxes(
        tickangle=-15
    )

    apply_plot_layout(fig2, 430)

    st.plotly_chart(
        fig2,
        use_container_width=True,
        config={
            "displayModeBar": False
        }
    )

# =========================================================
# SALES & PROFIT BY MARKET
# =========================================================

section_header("Sales & Profit by Market")

market_sales_chart  = None
market_profit_chart = None

if 'Market' in df.columns:

    cl, cr = st.columns(2)

    # -----------------------------------------------------
    # SALES CHART
    # -----------------------------------------------------

    with cl:

        chart_label(
            "Total Sales by Market",
            "Revenue contribution across markets"
        )

        market_sales_chart = (
            df.groupby('Market')['Sales']
            .sum()
            .reset_index()
        )

        fig3 = px.bar(
            market_sales_chart.sort_values(
                'Sales',
                ascending=False
            ),
            x='Market',
            y='Sales',
            color='Sales',
            color_continuous_scale='Blues',
            text_auto='.2s'
        )

        fig3.update_traces(
            textposition='outside',
            cliponaxis=False
        )

        fig3.update_layout(
            xaxis_title="",
            yaxis_title="Sales",
            coloraxis_showscale=False,
            uniformtext_minsize=8,
            uniformtext_mode='hide'
        )

        fig3.update_xaxes(
            tickangle=-15
        )

        apply_plot_layout(fig3, 370)

        st.plotly_chart(
            fig3,
            use_container_width=True,
            config={
                "displayModeBar": False
            }
        )

    # -----------------------------------------------------
    # PROFIT CHART
    # -----------------------------------------------------

    with cr:

        chart_label(
            "Total Profit by Market",
            "Profitability comparison"
        )

        market_profit_chart = (
            df.groupby('Market')['Profit Per Order']
            .sum()
            .reset_index()
        )

        fig4 = px.bar(
            market_profit_chart.sort_values(
                'Profit Per Order',
                ascending=False
            ),
            x='Market',
            y='Profit Per Order',
            color='Profit Per Order',
            color_continuous_scale='Greens',
            text_auto='.2s'
        )

        fig4.update_traces(
            textposition='outside',
            cliponaxis=False
        )

        fig4.update_layout(
            xaxis_title="",
            yaxis_title="Profit",
            coloraxis_showscale=False,
            uniformtext_minsize=8,
            uniformtext_mode='hide'
        )

        fig4.update_xaxes(
            tickangle=-15
        )

        apply_plot_layout(fig4, 370)

        st.plotly_chart(
            fig4,
            use_container_width=True,
            config={
                "displayModeBar": False
            }
        )

# =========================================================
# REGIONAL SHIPPING EFFICIENCY
# =========================================================

section_header("Regional Shipping Efficiency")

if 'Order Region' in df.columns and 'Shipping Efficiency %' in df.columns:

    efficiency_df = (
        df.groupby('Order Region')['Shipping Efficiency %']
        .mean()
        .reset_index()
    )

    efficiency_df['Shipping Efficiency %'] = (
        efficiency_df['Shipping Efficiency %']
        .round(1)
    )

    fig5 = px.bar(
        efficiency_df.sort_values(
            'Shipping Efficiency %',
            ascending=False
        ),
        x='Order Region',
        y='Shipping Efficiency %',
        color='Shipping Efficiency %',
        color_continuous_scale='Greens',
        text_auto='.1f'
    )

    fig5.update_traces(
        textposition='outside',
        cliponaxis=False
    )

    fig5.update_layout(
        xaxis_title="",
        yaxis_title="Efficiency (%)",
        coloraxis_showscale=False
    )

    fig5.update_xaxes(
        tickangle=-20
    )

    apply_plot_layout(fig5, 390)

    st.plotly_chart(
        fig5,
        use_container_width=True,
        config={
            "displayModeBar": False
        }
    )

# =========================================================
# REGIONAL INSIGHTS
# =========================================================

section_header("Regional Insights")

if region_df is not None:

    best_region = (
        region_df.sort_values(
            'Efficiency (%)',
            ascending=False
        ).iloc[0]
    )

    worst_region = (
        region_df.sort_values(
            'Delay Risk (%)',
            ascending=False
        ).iloc[0]
    )

    insight_card(
        f"""
        🏆 Best logistics region:
        <strong>{best_region['Region']}</strong>
        achieved a shipping efficiency of
        <strong>{best_region['Efficiency (%)']:.1f}%</strong>.
        """,
        "success"
    )

    insight_card(
        f"""
        ⚠️ Highest delay risk observed in
        <strong>{worst_region['Region']}</strong>
        with a delay risk of
        <strong>{worst_region['Delay Risk (%)']:.1f}%</strong>.
        """,
        "warning"
    )

if market_sales_chart is not None and len(market_sales_chart) > 0:

    best_market = (
        market_sales_chart.sort_values(
            'Sales',
            ascending=False
        ).iloc[0]
    )

    insight_card(
        f"""
        💰 Highest revenue generated from
        <strong>{best_market['Market']}</strong>
        market with total sales of
        <strong>${best_market['Sales']:,.0f}</strong>.
        """,
        "info"
    )

footer()