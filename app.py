"""
Business Intelligence and Analytics System for E-Commerce Management Decision-Making
MIS Course Project - SRM Institute of Science and Technology
Student: Rishav (RA2311003010921)

UI Architecture: Custom Modern E-Commerce BI Dashboard (SellCraft)
Primary Entry Point: streamlit run app.py
"""

import os
import sys
from datetime import datetime, timedelta
import pandas as pd
import streamlit as st

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from src.config import THEME, KPI_DEFINITIONS, REQUIRED_COLUMNS
from src.data_engine import load_csv, validate_schema, clean_data, persist_to_sqlite
from src.analytics import filter_dataset, calculate_kpis
from src.components import get_custom_css, render_sellcraft_navbar
from src.pages import (
    render_overview_page,
    render_product_page,
    render_order_page,
    render_customer_page,
    render_checkout_page,
    render_document_page,
    render_settings_page,
    render_chat_page,
    render_alerts_page,
    render_profile_page
)

# 1. Page Configuration
st.set_page_config(
    page_title="SellCraft | E-Commerce BI Dashboard",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Inject custom SellCraft CSS
st.html(get_custom_css())

# 2. Navigation State (Synced via URL query params & session state)
current_tab = st.query_params.get("tab", "Overview")
st.session_state.active_tab = current_tab

# 3. Data Initialization & Caching in Session State
demo_file_path = os.path.join(CURRENT_DIR, "data", "ecommerce_demo_data.csv")
db_path = os.path.join(CURRENT_DIR, "ecommerce_bi.db")

# Sidebar Configuration (Discreet MIS Controls)
st.sidebar.markdown(
    """
    <div style="padding: 10px 0 16px 0; border-bottom: 1px solid #E5E7EB; margin-bottom: 16px;">
        <div style="font-size:18px; font-weight:800; color:#111827;">SellCraft BI Engine</div>
        <div style="font-size:11.5px; color:#6B7280; margin-top:4px;">
            <b>MIS Project</b> &bull; SRM IST<br>
            Student: Rishav [RA2311003010921]
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

st.sidebar.markdown("### 📂 Data Ingestion")
data_source = st.sidebar.radio(
    "Data Source",
    ["Demonstration Dataset", "Upload Custom CSV"],
    index=0
)

uploaded_file = None
if data_source == "Upload Custom CSV":
    uploaded_file = st.sidebar.file_uploader(
        "Upload Orders CSV",
        type=["csv"],
        help="Upload CSV with order_id, order_date, quantity, unit_price."
    )

if "df" not in st.session_state or uploaded_file is not None:
    try:
        if uploaded_file is not None:
            raw_df = load_csv(uploaded_file)
        elif os.path.exists(demo_file_path):
            raw_df = load_csv(demo_file_path)
        else:
            st.error("Demonstration dataset missing.")
            st.stop()
        
        # Validate & Clean Data
        is_valid, missing_req, missing_rec, warnings = validate_schema(raw_df)
        if not is_valid:
            st.sidebar.error(f"Missing mandatory columns: {', '.join(missing_req)}")
            st.stop()

        cleaned = clean_data(raw_df)
        st.session_state.df = cleaned

        # Persist to SQLite
        try:
            persist_to_sqlite(cleaned, db_path)
        except Exception:
            pass

    except Exception as e:
        st.error(f"Error loading CSV: {e}")
        st.stop()

df = st.session_state.df

# Sidebar Filters
st.sidebar.markdown("---")
st.sidebar.markdown("### 🔍 Dashboard Filters")

min_date = df['order_date'].min().date()
max_date = df['order_date'].max().date()

date_range = st.sidebar.date_input(
    "Date Window",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

start_date, end_date = None, None
if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date = pd.to_datetime(date_range[0])
    end_date = pd.to_datetime(date_range[1]) + timedelta(days=1) - timedelta(seconds=1)

categories_list = sorted(list(df['category'].dropna().unique()))
selected_categories = st.sidebar.multiselect("Category", options=["All"] + categories_list, default=["All"])

filtered_df = filter_dataset(df, start_date=start_date, end_date=end_date, categories=selected_categories)

# Analytics Calculations
kpis = calculate_kpis(filtered_df)

# Sidebar Export
st.sidebar.markdown("---")
csv_data = filtered_df.to_csv(index=False).encode('utf-8')
st.sidebar.download_button(
    label="Export Filtered CSV",
    data=csv_data,
    file_name="sellcraft_filtered_orders.csv",
    mime="text/csv",
    width="stretch"
)

# 4. Main Canvas Rendering - Top Navigation Header (Sleek, slim, not thick)
st.html(render_sellcraft_navbar(active_page=current_tab))

# 5. Dedicated Page Routing
if current_tab == "Overview":
    render_overview_page(df=df, filtered_df=filtered_df, kpis=kpis)

elif current_tab == "Product":
    render_product_page(df=df)

elif current_tab == "Order":
    render_order_page(df=df)

elif current_tab == "Customer Data":
    render_customer_page(df=df)

elif current_tab == "Checkout":
    render_checkout_page(df=df)

elif current_tab == "Document":
    render_document_page()

elif current_tab == "Settings":
    render_settings_page(df=df)

elif current_tab == "Chat":
    render_chat_page(df=df, kpis=kpis)

elif current_tab == "Alerts":
    render_alerts_page(df=df)

elif current_tab == "Profile":
    render_profile_page()

else:
    render_overview_page(df=df, filtered_df=filtered_df, kpis=kpis)
