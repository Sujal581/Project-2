import streamlit as st
import pandas as pd
import plotly.express as px

from data_manager import apply_filters, preprocess
from style import (
    inject_css,
    sidebar_brand,
    page_header,
    section_header,
    kpi_card,
    apply_plot_layout,
    footer,
    COLORS
)

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix
)

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Predictive Analysis | APL Logistics",
    layout="wide",
    page_icon="🤖"
)

inject_css()
sidebar_brand()

# =========================================================
# PAGE HEADER
# =========================================================

page_header(
    "Predictive Analysis",
    "AI-powered late delivery risk prediction",
    "🤖"
)

# =========================================================
# LOAD DATA
# =========================================================

df = apply_filters()

if df is None:
    st.warning("Please upload a dataset from the Home page.")
    st.stop()

if df.empty:
    st.warning("No data matches the current filters.")
    st.stop()

# =========================================================
# CACHE PREPROCESSING
# =========================================================

@st.cache_data(show_spinner=False)
def cached_preprocess(data):
    return preprocess(data)

df = cached_preprocess(df)

# =========================================================
# REQUIRED COLUMNS
# =========================================================

required_columns = [
    'Late Delivery Risk',
    'Ship Mode',
    'Order Region',
    'Market',
    'Customer Segment',
    'Real Shipping Days',
    'Scheduled Shipping Days',
    'Sales',
    'Order Quantity'
]

missing_columns = [col for col in required_columns if col not in df.columns]

if missing_columns:
    st.error(f"Missing columns required for modelling: {missing_columns}")
    st.stop()

# =========================================================
# MODEL DATA
# =========================================================

model_df = df[required_columns].dropna()

# =========================================================
# FEATURE PREPARATION
# =========================================================

@st.cache_data(show_spinner=False)
def prepare_features(data):

    X = data[[
        'Ship Mode',
        'Order Region',
        'Market',
        'Customer Segment',
        'Real Shipping Days',
        'Scheduled Shipping Days',
        'Sales',
        'Order Quantity'
    ]]

    X = pd.get_dummies(X, drop_first=True)

    y = data['Late Delivery Risk']

    return X, y

X, y = prepare_features(model_df)

# =========================================================
# TRAIN TEST SPLIT
# =========================================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

# =========================================================
# MODEL TRAINING (CACHED)
# =========================================================

@st.cache_resource(show_spinner=False)
def train_model(X_train, y_train):

    model = RandomForestClassifier(
        n_estimators=80,
        max_depth=10,
        random_state=42,
        n_jobs=-1
    )

    model.fit(X_train, y_train)

    return model

with st.spinner("Training predictive model..."):
    model = train_model(X_train, y_train)

# =========================================================
# PREDICTIONS
# =========================================================

predictions = model.predict(X_test)

accuracy = accuracy_score(y_test, predictions)
precision = precision_score(y_test, predictions)
recall = recall_score(y_test, predictions)
f1 = f1_score(y_test, predictions)

# =========================================================
# METRICS
# =========================================================

section_header("Model Performance Metrics")

c1, c2, c3, c4 = st.columns(4)

kpi_card(
    c1,
    "Accuracy",
    f"{accuracy*100:.2f}%",
    icon="🎯",
    color=COLORS["blue"]
)

kpi_card(
    c2,
    "Precision",
    f"{precision*100:.2f}%",
    icon="📏",
    color=COLORS["green"]
)

kpi_card(
    c3,
    "Recall",
    f"{recall*100:.2f}%",
    icon="🔍",
    color=COLORS["amber"]
)

kpi_card(
    c4,
    "F1 Score",
    f"{f1*100:.2f}%",
    icon="⚖️",
    color=COLORS["purple"]
)

# =========================================================
# FEATURE IMPORTANCE
# =========================================================

section_header("Feature Importance")

@st.cache_data(show_spinner=False)
def get_importance_df(columns, importances):

    importance_df = pd.DataFrame({
        'Feature': columns,
        'Importance': importances
    })

    importance_df = importance_df.sort_values(
        by='Importance',
        ascending=False
    )

    return importance_df

importance_df = get_importance_df(
    X.columns.tolist(),
    model.feature_importances_.tolist()
)

fig = px.bar(
    importance_df.head(15),
    x='Importance',
    y='Feature',
    orientation='h',
    color='Importance',
    color_continuous_scale='Viridis',
    title='Top Features Affecting Delay Risk'
)

apply_plot_layout(fig, 420)

st.plotly_chart(
    fig,
    use_container_width=True,
    config={"displayModeBar": False}
)

# =========================================================
# CONFUSION MATRIX
# =========================================================

section_header("Confusion Matrix")

cm = confusion_matrix(y_test, predictions)

cm_df = pd.DataFrame(
    cm,
    index=['Actual No Risk', 'Actual Risk'],
    columns=['Predicted No Risk', 'Predicted Risk']
)

st.dataframe(
    cm_df,
    use_container_width=True
)

# =========================================================
# PREDICTION UI
# =========================================================

section_header("Predict Shipment Delay Risk")

col1, col2 = st.columns(2)

with col1:

    ship_mode = st.selectbox(
        "Ship Mode",
        sorted(df['Ship Mode'].dropna().unique())
    )

    region = st.selectbox(
        "Order Region",
        sorted(df['Order Region'].dropna().unique())
    )

    market = st.selectbox(
        "Market",
        sorted(df['Market'].dropna().unique())
    )

    segment = st.selectbox(
        "Customer Segment",
        sorted(df['Customer Segment'].dropna().unique())
    )

with col2:

    real_days = st.number_input(
        "Real Shipping Days",
        min_value=0,
        value=5
    )

    scheduled_days = st.number_input(
        "Scheduled Shipping Days",
        min_value=0,
        value=3
    )

    sales = st.number_input(
        "Sales",
        min_value=0.0,
        value=500.0
    )

    quantity = st.number_input(
        "Order Quantity",
        min_value=1,
        value=2
    )

# =========================================================
# PREDICT BUTTON
# =========================================================

if st.button("🚀 Predict Risk"):

    input_df = pd.DataFrame({
        'Ship Mode': [ship_mode],
        'Order Region': [region],
        'Market': [market],
        'Customer Segment': [segment],
        'Real Shipping Days': [real_days],
        'Scheduled Shipping Days': [scheduled_days],
        'Sales': [sales],
        'Order Quantity': [quantity]
    })

    input_encoded = pd.get_dummies(input_df)

    input_encoded = input_encoded.reindex(
        columns=X.columns,
        fill_value=0
    )

    prediction = model.predict(input_encoded)[0]

    probability = model.predict_proba(input_encoded)[0][1]

    if prediction == 1:

        st.error(
            f"⚠️ High Delay Risk ({probability*100:.2f}%)"
        )

    else:

        st.success(
            f"✅ Low Delay Risk ({(1-probability)*100:.2f}%)"
        )

# =========================================================
# FOOTER
# =========================================================

footer()