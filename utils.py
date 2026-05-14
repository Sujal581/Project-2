import pandas as pd
import numpy as np


def clean_data(df):
    df = df.copy()
    df = df.drop_duplicates()
    df = df.dropna(how="all")

    df.columns = df.columns.astype(str).str.strip()
    
    rename_map = {

        "Days for shipping (real)": "Real Shipping Days",
        "Days for shipment (scheduled)": "Scheduled Shipping Days",
        "Benefit per order": "Benefit Per Order",
        "Sales per customer": "Sales Per Customer",
        "Shipping Mode": "Ship Mode",
        "Order Item Total": "Order Total",
        "Order Item Quantity": "Order Quantity",
        "Order Item Product Price": "Product Price",
        "Order Profit Per Order": "Profit Per Order",
        "Late_delivery_risk": "Late Delivery Risk",
        "Customer Fname": "Customer First Name",
        "Customer Lname": "Customer Last Name"
    }

    df = df.rename(columns=rename_map)
    df = df.loc[:, ~df.columns.duplicated()]

    text_columns = [
        'Ship Mode', 'Order Region', 'Market', 'Order Country',
        'Order State', 'Order City', 'Customer Segment',
        'Category Name', 'Department Name', 'Delivery Status', 'Product Name'
    ]
    for col in text_columns:
        if col in df.columns:
            try:
                df[col] = df[col].fillna("Unknown").astype(str).str.strip()
            except:
                pass

    numeric_cols = [
        'Real Shipping Days', 'Scheduled Shipping Days', 'Sales',
        'Order Quantity', 'Order Total', 'Product Price', 'Profit Per Order',
        'Benefit Per Order', 'Sales Per Customer', 'Latitude', 'Longitude'
    ]
    for col in numeric_cols:
        if col in df.columns:
            try:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            except:
                pass

    if 'Real Shipping Days' in df.columns and 'Scheduled Shipping Days' in df.columns:
        try:
            df = df[
                (df['Real Shipping Days'] >= 0) &
                (df['Scheduled Shipping Days'] >= 0)
            ]
        except:
            pass

    fill_text_cols = ['Ship Mode', 'Order Region', 'Market', 'Customer Segment']
    for col in fill_text_cols:
        if col in df.columns:
            try:
                df[col] = df[col].fillna("Unknown")
            except:
                pass

    date_cols = ["Order Date", "Shipping Date"]
    for col in date_cols:
        if col in df.columns:
            try:
                df[col] = pd.to_datetime(df[col], errors="coerce")
            except:
                pass

    df = df.reset_index(drop=True)
    return df


def feature_engineering(df, save=False, path="cleaned_data.csv"):
    df = df.copy()
    df = df.drop_duplicates()
    df.columns = df.columns.astype(str).str.strip()

    if 'Real Shipping Days' in df.columns and 'Scheduled Shipping Days' in df.columns:
        try:
            df['Delay Gap'] = df['Real Shipping Days'] - df['Scheduled Shipping Days']
        except:
            pass

    if 'Delay Gap' in df.columns:
        try:
            def classify_delivery(x):
                if pd.isna(x):
                    return "Unknown"
                if x > 0:
                    return "Delayed"
                elif x < 0:
                    return "Early"
                return "On-Time"
            df['Delivery Performance'] = df['Delay Gap'].apply(classify_delivery)
        except:
            pass

    if 'Delay Gap' in df.columns:
        try:
            df['Delayed'] = df['Delay Gap'] > 0
        except:
            pass

    if 'Real Shipping Days' in df.columns and 'Scheduled Shipping Days' in df.columns:
        try:
            df['Shipping Efficiency %'] = np.where(
                df['Real Shipping Days'] > 0,
                (df['Scheduled Shipping Days'] / df['Real Shipping Days']) * 100,
                0
            )
        except:
            pass

    if 'Late Delivery Risk' in df.columns:
        try:
            df['High Risk Shipment'] = np.where(
                df['Late Delivery Risk'] == 1, "High Risk", "Low Risk"
            )
        except:
            pass

    if 'Profit Per Order' in df.columns:
        try:
            df['Profit Category'] = pd.cut(
                df['Profit Per Order'],
                bins=[-999999, 0, 100, 500, 999999],
                labels=['Loss', 'Low Profit', 'Medium Profit', 'High Profit']
            )
        except:
            pass

    if 'Sales' in df.columns:
        try:
            df['Sales Category'] = pd.cut(
                df['Sales'],
                bins=[0, 100, 500, 1000, 999999],
                labels=['Low Sales', 'Medium Sales', 'High Sales', 'Very High Sales']
            )
        except:
            pass

    if 'Order Total' in df.columns:
        try:
            df['Order Value Category'] = pd.cut(
                df['Order Total'],
                bins=[0, 100, 500, 1000, 999999],
                labels=['Small Order', 'Medium Order', 'Large Order', 'Enterprise Order']
            )
        except:
            pass

    return df


def calculate_kpis(df):
    kpis = {}

    try:
        kpis['Total Orders'] = len(df)
    except:
        kpis['Total Orders'] = 0

    if 'Delayed' in df.columns:
        try:
            kpis['Delayed Orders'] = int(df['Delayed'].fillna(False).sum())
        except:
            kpis['Delayed Orders'] = 0

    if 'Delivery Performance' in df.columns:
        try:
            on_time_orders = len(df[df['Delivery Performance'] == 'On-Time'])
            total_orders = len(df)
            kpis['On-Time %'] = round((on_time_orders / total_orders) * 100, 2) if total_orders > 0 else 0
        except:
            kpis['On-Time %'] = 0

    if 'Delay Gap' in df.columns:
        try:
            kpis['Average Delay Gap'] = round(df['Delay Gap'].mean(), 2)
        except:
            kpis['Average Delay Gap'] = 0

    if 'Late Delivery Risk' in df.columns:
        try:
            kpis['Late Delivery Risk %'] = round(
                pd.to_numeric(df['Late Delivery Risk'], errors='coerce').mean() * 100, 2
            )
        except:
            kpis['Late Delivery Risk %'] = 0

    if 'Sales' in df.columns:
        try:
            kpis['Total Sales'] = round(
                pd.to_numeric(df['Sales'], errors='coerce').sum(), 2
            )
        except:
            kpis['Total Sales'] = 0

    if 'Profit Per Order' in df.columns:
        try:
            kpis['Total Profit'] = round(
                pd.to_numeric(df['Profit Per Order'], errors='coerce').sum(), 2
            )
        except:
            kpis['Total Profit'] = 0

    return kpis
