import streamlit as st
import pandas as pd
import io
import csv
from utils import clean_data, feature_engineering, calculate_kpis


COLUMN_MAPPING = {
    'Days for shipping (real)': 'Real Shipping Days',
    'Days for shipment (scheduled)': 'Scheduled Shipping Days',
    'Late_delivery_risk': 'Late Delivery Risk',
    'Shipping Mode': 'Ship Mode',
    'Sales per customer': 'Sales Per Customer',
    'Benefit per order': 'Benefit Per Order',
    'Customer Fname': 'Customer First Name',
    'Customer Lname': 'Customer Last Name',
    'Order Item Quantity': 'Order Quantity',
    'Order Item Total': 'Order Total',
    'Order Profit Per Order': 'Profit Per Order'
}


def safe_read_csv(raw_bytes):

    encodings = [
        "utf-8-sig",
        "utf-8",
        "cp1252",
        "utf-16",
        "latin1"
    ]

    for enc in encodings:
        try:
            return pd.read_csv(
                io.BytesIO(raw_bytes),
                encoding=enc,
                engine="python",
                on_bad_lines="skip"
            )

        except UnicodeDecodeError:
            continue

        except Exception:
            continue

    try:
        text = raw_bytes.decode("latin1", errors="replace")

        return pd.read_csv(
            io.StringIO(text),
            engine="python",
            on_bad_lines="skip"
        )

    except Exception:
        return None
    return None

@st.cache_data(show_spinner=False)
def _parse_csv(raw_bytes: bytes) -> pd.DataFrame:
    df = safe_read_csv(raw_bytes)

    df.dropna(how="all", inplace=True)
    df.dropna(axis=1, how="all", inplace=True)

    df.columns = df.columns.astype(str).str.strip()

    df.rename(columns=COLUMN_MAPPING, inplace=True)

    categorical_cols = [
        'Ship Mode', 'Order Region', 'Market', 'Customer Segment',
        'Order Country', 'Order State', 'Order City', 'Category Name',
        'Department Name', 'Delivery Status'
    ]
    for col in categorical_cols:
        if col in df.columns:
            try:
                df[col] = df[col].astype(str).astype("category")
            except:
                pass

    date_cols = ["Order Date", "Shipping Date"]
    for col in date_cols:
        if col in df.columns:
            try:
                df[col] = pd.to_datetime(df[col], errors="coerce")
            except:
                pass

    try:
        df = clean_data(df)
    except Exception as e:
        st.warning(f"clean_data() failed: {e}")

    try:
        df = feature_engineering(df)
    except Exception as e:
        st.warning(f"feature_engineering() failed: {e}")

    df.drop_duplicates(inplace=True)
    df.reset_index(drop=True, inplace=True)

    return df

@st.cache_data
def preprocess(df):
    df= clean_data(df)
    df=feature_engineering(df)
    return df

def upload_screen():
    st.markdown("""
        <div style="
            background:#111827;
            border:1px dashed #374151;
            border-radius:18px;
            padding:3rem;
            text-align:center;
            max-width:520px;
            margin:3rem auto;
        ">
            <div style="font-size:3rem;margin-bottom:1rem;">🚚</div>
            <div style="font-size:1.1rem;font-weight:700;color:#f8fafc;margin-bottom:0.4rem;">
                Upload Logistics Dataset
            </div>
            <div style="font-size:0.85rem;color:#94a3b8;">
                Upload CSV file to unlock all analytics dashboards
            </div>
        </div>
    """, unsafe_allow_html=True)

    uploaded = st.file_uploader("Upload CSV", type=["csv"])

    if uploaded is not None:
        raw_bytes = uploaded.getvalue()
        df = safe_read_csv(raw_bytes)
        if df is not None:
            df = clean_data(df)
            df = feature_engineering(df)
            kpis = calculate_kpis(df)

            st.success("Data Loaded Successfully")
            st.dataframe(df.head())

        else:
            st.error("Could not parse CSV")

    st.stop()


def init_data():
    return st.session_state.get("master_df", None)


def apply_filters():
    df = st.session_state.get("master_df", None)

    if df is None:
        return None

    with st.sidebar:
        st.markdown("""
            <div style="
                font-size:0.75rem;
                font-weight:700;
                color:#64748b;
                text-transform:uppercase;
                letter-spacing:0.08em;
                margin-bottom:0.7rem;
            ">
                🔍 Global Filters
            </div>
        """, unsafe_allow_html=True)

        defaults = {"region": "All", "market": "All", "mode": "All", "segment": "All", "delay": 5}

        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value

        if "Order Region" in df.columns:
            regions = ["All"] + sorted(df["Order Region"].dropna().astype(str).unique().tolist())
            st.selectbox("🌍 Order Region", regions, key="region")

        if "Market" in df.columns:
            markets = ["All"] + sorted(df["Market"].dropna().astype(str).unique().tolist())
            st.selectbox("📦 Market", markets, key="market")

        if "Ship Mode" in df.columns:
            modes = ["All"] + sorted(df["Ship Mode"].dropna().astype(str).unique().tolist())
            st.selectbox("🚚 Ship Mode", modes, key="mode")

        if "Customer Segment" in df.columns:
            segments = ["All"] + sorted(df["Customer Segment"].dropna().astype(str).unique().tolist())
            st.selectbox("👥 Customer Segment", segments, key="segment")

        st.slider("⏱ Delay Threshold", 1, 15, key="delay")

        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("🔄 Reset Filters", use_container_width=True):
            for key in defaults.keys():
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

        if st.button("📤 Upload New CSV", use_container_width=True):
            st.cache_data.clear()
            keys = list(st.session_state.keys())
            for key in keys:
                del st.session_state[key]
            st.rerun()

    filtered = df.copy()

    if "Order Region" in filtered.columns and st.session_state.region != "All":
        filtered = filtered[filtered["Order Region"] == st.session_state.region]

    if "Market" in filtered.columns and st.session_state.market != "All":
        filtered = filtered[filtered["Market"] == st.session_state.market]

    if "Ship Mode" in filtered.columns and st.session_state.mode != "All":
        filtered = filtered[filtered["Ship Mode"] == st.session_state.mode]

    if "Customer Segment" in filtered.columns and st.session_state.segment != "All":
        filtered = filtered[filtered["Customer Segment"] == st.session_state.segment]

    if "Delay Gap" in filtered.columns:
        filtered["Delayed"] = filtered["Delay Gap"] > st.session_state.delay

    return filtered


def clear_cache():
    st.cache_data.clear()
    keys = list(st.session_state.keys())
    for key in keys:
        del st.session_state[key]
    st.success("Cache cleared")
    st.rerun()
