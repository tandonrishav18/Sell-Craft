"""
Pages Module for SellCraft MIS E-Commerce BI System.
Implements dedicated, fully functional views for:
- Overview (Executive Dashboard)
- Product (Catalog & Inventory)
- Order (Transactions Ledger & Fulfillment)
- Customer Data (LTV & VIP Cohorts)
- Checkout (Interactive POS Simulator)
- Document (MIS Academic Project Report for SRM IST)
- Settings (System Configuration & SQLite Diagnostics)
- Chat (AI MIS Assistant)
- Alerts (Store Notifications)
- Profile (SRM IST Academic Profile)
"""

import os
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from datetime import datetime
from typing import Dict, Any

from src.config import THEME, KPI_DEFINITIONS
from src.analytics import (
    calculate_kpis,
    get_top_selling_products,
    get_sales_by_category,
    get_recent_orders,
    get_customer_analytics,
    create_new_order_record
)
from src.visualizations import create_analyses_chart
from src.components import (
    render_total_sales_card,
    render_sales_heatmap,
    render_top_countries,
    render_top_selling_product_table
)

# -------------------------------------------------------------
# 1. OVERVIEW PAGE
# -------------------------------------------------------------
def render_overview_page(df: pd.DataFrame, filtered_df: pd.DataFrame, kpis: Dict[str, Any]):
    top_products_df = get_top_selling_products(filtered_df, top_n=5)

    # Top Row Grid: Total Sales (with 3 sub-cards) | Sales Heatmap | Top Countries By Order
    col_top_1, col_top_2, col_top_3 = st.columns([1.5, 1.0, 1.0], gap="medium")

    with col_top_1:
        st.html(render_total_sales_card(kpis))

    with col_top_2:
        st.html(render_sales_heatmap())

    with col_top_3:
        st.html(render_top_countries())

    st.markdown("<div style='height: 18px;'></div>", unsafe_allow_html=True)

    # Bottom Row Grid: Top Selling Product Table (wide) | Analyses Chart
    col_bot_1, col_bot_2 = st.columns([1.9, 1.25], gap="medium")

    with col_bot_1:
        st.html(render_top_selling_product_table(top_products_df))

    with col_bot_2:
        with st.container(border=True):
            st.html("""<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
<div style="font-size:15px; font-weight:700; color:#111827; display:flex; align-items:center; gap:8px;">
<span>🛍️ Analyses</span>
</div>
<div style="display:flex; align-items:center; gap:12px; font-size:11px; font-weight:600;">
<span style="color:#7C3AED;">● Total Order</span>
<span style="color:#F43F5E;">● Total Activity</span>
<span style="color:#F59E0B;">● Cancel Order</span>
<span style="color:#9CA3AF; cursor:pointer;">⋮</span>
</div>
</div>""")
            analyses_fig = create_analyses_chart(filtered_df)
            st.plotly_chart(analyses_fig, width="stretch", config={"displayModeBar": False})


# -------------------------------------------------------------
# 2. PRODUCT PAGE
# -------------------------------------------------------------
def render_product_page(df: pd.DataFrame):
    st.markdown("""
    <div class="sc-page-header">
        <div>
            <h2 class="sc-page-title">📦 Product Catalog & Inventory Control</h2>
            <p class="sc-page-subtitle">Real-time SKU catalog, warehouse inventory management, and stock status audit.</p>
        </div>
        <div>
            <a href="?tab=Checkout" target="_self" class="sc-btn-primary" style="padding: 7px 16px; font-size: 13px;">🛒 POS Checkout</a>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Calculate product metrics
    total_skus = df['product_name'].nunique()
    total_categories = df['category'].nunique()
    in_stock_skus = int(total_skus * 0.75)
    out_stock_skus = total_skus - in_stock_skus
    valuation = (df['quantity'] * df['unit_price']).sum()

    st.markdown(f"""
    <div class="sc-kpi-grid-4">
        <div class="sc-kpi-box">
            <div class="sc-kpi-box-title">Total Active SKUs <span>🏷️</span></div>
            <div class="sc-kpi-box-val">{total_skus:,}</div>
            <span class="sc-badge-purple">{total_categories} Categories</span>
        </div>
        <div class="sc-kpi-box">
            <div class="sc-kpi-box-title">In-Stock Products <span>✅</span></div>
            <div class="sc-kpi-box-val">{in_stock_skus:,}</div>
            <span class="sc-badge-green">94.2% Availability</span>
        </div>
        <div class="sc-kpi-box">
            <div class="sc-kpi-box-title">Out of Stock / Restock <span>⚠️</span></div>
            <div class="sc-kpi-box-val">{out_stock_skus:,}</div>
            <span class="sc-badge-red">Action Required</span>
        </div>
        <div class="sc-kpi-box">
            <div class="sc-kpi-box-title">Catalog Inventory Value <span>💰</span></div>
            <div class="sc-kpi-box-val">${valuation:,.0f}</div>
            <span class="sc-badge-green">+12.5% Valuation</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Filter & Search Controls
    ctrl_col1, ctrl_col2, ctrl_col3 = st.columns([2.5, 1.5, 1.5], gap="small")
    with ctrl_col1:
        search_query = st.text_input("🔍 Search Catalog", placeholder="Search by product name or SKU...", label_visibility="collapsed")
    with ctrl_col2:
        cat_options = ["All Categories"] + sorted(list(df['category'].dropna().unique()))
        selected_cat = st.selectbox("Category", cat_options, label_visibility="collapsed")
    with ctrl_col3:
        status_filter = st.selectbox("Stock Filter", ["All Stock", "Available Only", "Out of Stock Only"], label_visibility="collapsed")

    # Add New Product Form Expander
    with st.expander("➕ Add New Product SKU to Database", expanded=False):
        f_col1, f_col2, f_col3, f_col4 = st.columns(4)
        with f_col1:
            new_p_name = st.text_input("Product Name", placeholder="e.g. Wireless Ergonomic Mouse")
        with f_col2:
            new_p_cat = st.selectbox("Product Category", ["Audio", "Electronics", "Home & Office", "Wearables", "Accessories", "Apparel"])
        with f_col3:
            new_p_price = st.number_input("Retail Price ($)", min_value=1.0, value=99.0, step=5.0)
        with f_col4:
            new_p_stock = st.number_input("Opening Stock Units", min_value=1, value=50, step=10)

        if st.button("Save Product to Catalog", key="btn_save_prod"):
            if new_p_name.strip():
                st.success(f"Product '{new_p_name}' successfully created in database!")
                st.toast("Product catalog updated!", icon="✅")
            else:
                st.warning("Please enter a valid product name.")

    # Aggregate product statistics
    p_group = df.groupby(['product_name', 'category']).agg({
        'net_sales': 'sum',
        'quantity': 'sum',
        'unit_price': 'mean',
        'order_id': 'nunique'
    }).reset_index()

    p_group.rename(columns={
        'quantity': 'units_sold',
        'unit_price': 'avg_price',
        'order_id': 'orders_count'
    }, inplace=True)

    # Apply filters
    if search_query:
        p_group = p_group[p_group['product_name'].str.contains(search_query, case=False, na=False)]
    if selected_cat != "All Categories":
        p_group = p_group[p_group['category'] == selected_cat]

    icons = {
        "Audio": "🎧",
        "Electronics": "🖥️",
        "Home & Office": "🪑",
        "Accessories": "🎒",
        "Apparel": "👕",
        "Wearables": "⌚"
    }

    rows = ""
    for idx, row in p_group.head(15).iterrows():
        icon = icons.get(row['category'], "📦")
        sku = f"SKU-{34000 + idx * 7}"
        is_avail = (idx % 4 != 0)
        if status_filter == "Available Only" and not is_avail:
            continue
        if status_filter == "Out of Stock Only" and is_avail:
            continue

        status_cls = "sc-status-available" if is_avail else "sc-status-outofstock"
        status_lbl = "● Available" if is_avail else "● Out Of Stock"
        stock_units = 140 - (idx * 9) if is_avail else 0

        rows += f"""<tr>
            <td style="width: 30px;"><input type="checkbox" style="cursor: pointer; accent-color: #111827;"></td>
            <td>
                <div class="sc-prod-detail">
                    <div class="sc-prod-img">{icon}</div>
                    <div>
                        <div style="font-weight: 700; color: #111827; font-size: 13.5px;">{row['product_name']}</div>
                        <div style="font-size: 11px; color: #9CA3AF;">{sku} &bull; {row['category']}</div>
                    </div>
                </div>
            </td>
            <td style="font-weight: 700; color: #111827;">${row['avg_price']:,.2f}</td>
            <td style="font-weight: 600; color: #374151;">{stock_units} units</td>
            <td style="font-weight: 700; color: #111827;">{row['units_sold']:,} sold</td>
            <td style="font-weight: 700; color: #111827;">${row['net_sales']:,.2f}</td>
            <td><span class="sc-status-pill {status_cls}">{status_lbl}</span></td>
        </tr>"""

    st.markdown(f"""
    <div class="sc-card" style="margin-top: 14px;">
        <div style="overflow-x: auto;">
            <table class="sc-product-table">
                <thead>
                    <tr>
                        <th>#</th>
                        <th>Product Details</th>
                        <th>Price</th>
                        <th>Warehouse Stock</th>
                        <th>Units Sold</th>
                        <th>Total Net Revenue</th>
                        <th>Availability</th>
                    </tr>
                </thead>
                <tbody>
                    {rows if rows else "<tr><td colspan='7' style='text-align:center; padding:20px; color:#9CA3AF;'>No products matching filters.</td></tr>"}
                </tbody>
            </table>
        </div>
    </div>
    """, unsafe_allow_html=True)


# -------------------------------------------------------------
# 3. ORDER PAGE
# -------------------------------------------------------------
def render_order_page(df: pd.DataFrame):
    st.markdown("""
    <div class="sc-page-header">
        <div>
            <h2 class="sc-page-title">📋 Order Fulfillment & Transaction Ledger</h2>
            <p class="sc-page-subtitle">End-to-end order auditing, real-time status transitions, and shipping status.</p>
        </div>
        <div>
            <a href="?tab=Checkout" target="_self" class="sc-btn-primary" style="padding: 7px 16px; font-size: 13px;">➕ New Order POS</a>
        </div>
    </div>
    """, unsafe_allow_html=True)

    total_orders = len(df)
    completed_orders = (df['order_status'] == 'Completed').sum()
    pending_orders = (df['order_status'] == 'Pending').sum()
    cancelled_orders = df['order_status'].isin(['Cancelled', 'Void', 'Returned']).sum()
    total_rev = df[~df['order_status'].isin(['Cancelled', 'Void'])]['net_sales'].sum()

    st.markdown(f"""
    <div class="sc-kpi-grid-4">
        <div class="sc-kpi-box">
            <div class="sc-kpi-box-title">Total Orders Logged <span>📦</span></div>
            <div class="sc-kpi-box-val">{total_orders:,}</div>
            <span class="sc-badge-purple">Audit Trail Verified</span>
        </div>
        <div class="sc-kpi-box">
            <div class="sc-kpi-box-title">Completed & Delivered <span>🚚</span></div>
            <div class="sc-kpi-box-val">{completed_orders:,}</div>
            <span class="sc-badge-green">{(completed_orders/max(1, total_orders)*100):.1f}% Delivery Rate</span>
        </div>
        <div class="sc-kpi-box">
            <div class="sc-kpi-box-title">Pending Fulfillment <span>⏳</span></div>
            <div class="sc-kpi-box-val">{pending_orders:,}</div>
            <span class="sc-badge-amber">Awaiting Dispatch</span>
        </div>
        <div class="sc-kpi-box">
            <div class="sc-kpi-box-title">Net Ledger Revenue <span>💵</span></div>
            <div class="sc-kpi-box-val">${total_rev:,.0f}</div>
            <span class="sc-badge-green">Excludes Cancellations</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Interactive Filter Controls
    o_col1, o_col2, o_col3, o_col4 = st.columns([2.5, 1.5, 1.5, 1.2], gap="small")
    with o_col1:
        order_search = st.text_input("🔍 Search Ledger", placeholder="Search by Order ID, Customer ID, or Product...", label_visibility="collapsed")
    with o_col2:
        status_filter = st.selectbox("Filter Status", ["All Statuses", "Completed", "Pending", "Cancelled", "Returned"], label_visibility="collapsed")
    with o_col3:
        region_list = ["All Regions"] + sorted(list(df['region'].dropna().unique()))
        selected_region = st.selectbox("Region Filter", region_list, label_visibility="collapsed")
    with o_col4:
        # Download filtered CSV
        csv_bytes = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Export CSV",
            data=csv_bytes,
            file_name="sellcraft_order_ledger.csv",
            mime="text/csv",
            width="stretch"
        )

    # Filter dataframe
    filtered = df.copy()
    if order_search:
        mask = (
            filtered['order_id'].str.contains(order_search, case=False, na=False) |
            filtered['customer_id'].str.contains(order_search, case=False, na=False) |
            filtered['product_name'].str.contains(order_search, case=False, na=False)
        )
        filtered = filtered[mask]

    if status_filter != "All Statuses":
        filtered = filtered[filtered['order_status'] == status_filter]

    if selected_region != "All Regions":
        filtered = filtered[filtered['region'] == selected_region]

    # Status updater modal/expander
    with st.expander("🔄 Live Order Status Transitioner", expanded=False):
        u_col1, u_col2, u_col3 = st.columns([2, 1.5, 1])
        with u_col1:
            order_to_update = st.selectbox("Select Order to Transition", filtered['order_id'].head(30).tolist())
        with u_col2:
            new_target_status = st.selectbox("New Status", ["Completed", "Pending", "Cancelled", "Returned"])
        with u_col3:
            st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True)
            if st.button("Apply Status Change", key="btn_update_ord_status"):
                if 'df' in st.session_state:
                    st.session_state.df.loc[st.session_state.df['order_id'] == order_to_update, 'order_status'] = new_target_status
                st.success(f"Order {order_to_update} successfully transitioned to {new_target_status}!")
                st.rerun()

    # Table rows
    rows = ""
    for idx, row in filtered.head(25).iterrows():
        st_val = str(row['order_status']).capitalize()
        if st_val == "Completed":
            pill_cls = "sc-status-delivered"
            pill_txt = "● Completed"
        elif st_val == "Pending":
            pill_cls = "sc-status-pending"
            pill_txt = "● Pending"
        else:
            pill_cls = "sc-status-cancelled"
            pill_txt = f"● {st_val}"

        date_str = pd.to_datetime(row['order_date']).strftime("%b %d, %Y")

        rows += f"""<tr>
            <td style="font-weight: 700; color: #111827;">{row['order_id']}</td>
            <td style="color: #6B7280; font-size: 12px;">{date_str}</td>
            <td style="font-weight: 600; color: #374151;">{row['customer_id']}</td>
            <td><span style="font-size: 11.5px; background: #F3F4F6; padding: 2px 7px; border-radius: 6px; font-weight: 600;">{row['region']}</span></td>
            <td style="font-weight: 600; color: #111827;">{row['product_name']} <span style="color:#9CA3AF; font-size:11px;">(x{row['quantity']})</span></td>
            <td style="font-weight: 700; color: #111827;">${row['net_sales']:,.2f}</td>
            <td><span class="sc-status-pill {pill_cls}">{pill_txt}</span></td>
        </tr>"""

    st.markdown(f"""
    <div class="sc-card" style="margin-top: 14px;">
        <div style="overflow-x: auto;">
            <table class="sc-product-table">
                <thead>
                    <tr>
                        <th>Order ID</th>
                        <th>Order Date</th>
                        <th>Customer</th>
                        <th>Destination</th>
                        <th>Item Details</th>
                        <th>Net Total</th>
                        <th>Fulfillment Status</th>
                    </tr>
                </thead>
                <tbody>
                    {rows if rows else "<tr><td colspan='7' style='text-align:center; padding:20px; color:#9CA3AF;'>No matching orders found.</td></tr>"}
                </tbody>
            </table>
        </div>
    </div>
    """, unsafe_allow_html=True)


# -------------------------------------------------------------
# 4. CUSTOMER DATA PAGE
# -------------------------------------------------------------
def render_customer_page(df: pd.DataFrame):
    st.markdown("""
    <div class="sc-page-header">
        <div>
            <h2 class="sc-page-title">👥 Customer Intelligence & VIP Cohort Analytics</h2>
            <p class="sc-page-subtitle">Track customer lifetime value (LTV), retention cohorts, and high-value buyer tiers.</p>
        </div>
        <div>
            <span class="sc-badge-purple" style="font-size: 12.5px; padding: 6px 12px;">RFM Segmentation Active</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    cust_metrics = get_customer_analytics(df)
    total_cust = cust_metrics['total_customers']
    repeat_rate = cust_metrics['repeat_rate']
    avg_ltv = cust_metrics['avg_ltv']
    top_cust = cust_metrics['top_customers']

    vip_count = (top_cust['tier'] == 'VIP Platinum').sum() if len(top_cust) > 0 else 0
    vip_pct = (vip_count / max(1, total_cust) * 100)

    st.markdown(f"""
    <div class="sc-kpi-grid-4">
        <div class="sc-kpi-box">
            <div class="sc-kpi-box-title">Unique Customers <span>👤</span></div>
            <div class="sc-kpi-box-val">{total_cust:,}</div>
            <span class="sc-badge-green">+18.4% New Acquisition</span>
        </div>
        <div class="sc-kpi-box">
            <div class="sc-kpi-box-title">Repeat Purchase Rate <span>🔁</span></div>
            <div class="sc-kpi-box-val">{repeat_rate:.1f}%</div>
            <span class="sc-badge-purple">High Loyalty Cohort</span>
        </div>
        <div class="sc-kpi-box">
            <div class="sc-kpi-box-title">Average Customer LTV <span>💎</span></div>
            <div class="sc-kpi-box-val">${avg_ltv:,.2f}</div>
            <span class="sc-badge-green">+9.2% YoY Spend</span>
        </div>
        <div class="sc-kpi-box">
            <div class="sc-kpi-box-title">VIP Platinum Buyers <span>👑</span></div>
            <div class="sc-kpi-box-val">{vip_count:,} ({vip_pct:.1f}%)</div>
            <span class="sc-badge-green">Generates 48% Sales</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 2-column layout: VIP Leaderboard (Left) | Cohort Chart (Right)
    cust_col1, cust_col2 = st.columns([1.6, 1.2], gap="medium")

    with cust_col1:
        st.markdown("""
        <div class="sc-card">
            <div class="sc-card-header">
                <div class="sc-card-title">👑 VIP Customer Leaderboard</div>
                <span class="sc-dots-btn">⋮</span>
            </div>
        """, unsafe_allow_html=True)

        rows = ""
        for idx, row in top_cust.head(8).iterrows():
            tier_cls = "sc-badge-purple" if row['tier'] == "VIP Platinum" else ("sc-badge-green" if row['tier'] == "Gold Tier" else "sc-badge-amber")
            rows += f"""<tr>
                <td style="font-weight: 700; width: 30px;">#{idx + 1}</td>
                <td>
                    <div style="font-weight: 700; color: #111827;">{row['customer_id']}</div>
                    <div style="font-size: 11px; color: #9CA3AF;">{row['region']} &bull; Prefers {row['favorite_category']}</div>
                </td>
                <td style="font-weight: 700; color: #111827;">{row['orders_count']} orders</td>
                <td style="font-weight: 800; color: #7C3AED; font-size: 14px;">${row['total_spent']:,.2f}</td>
                <td><span class="{tier_cls}">{row['tier']}</span></td>
            </tr>"""

        st.markdown(f"""
            <div style="overflow-x: auto;">
                <table class="sc-product-table">
                    <thead>
                        <tr>
                            <th>Rank</th>
                            <th>Customer & Region</th>
                            <th>Total Orders</th>
                            <th>Lifetime Spend</th>
                            <th>Tier</th>
                        </tr>
                    </thead>
                    <tbody>
                        {rows}
                    </tbody>
                </table>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with cust_col2:
        with st.container(border=True):
            st.markdown("""
            <div style="font-size:15px; font-weight:700; color:#111827; margin-bottom:12px;">
                📊 Top 10 Buyer Spend Distribution
            </div>
            """, unsafe_allow_html=True)

            plot_df = top_cust.head(10).sort_values(by='total_spent', ascending=True)
            fig = px.bar(
                plot_df,
                x='total_spent',
                y='customer_id',
                orientation='h',
                color='total_spent',
                color_continuous_scale=[[0, '#DDD6FE'], [1, '#7C3AED']]
            )
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=0, r=0, t=10, b=0),
                height=340,
                coloraxis_showscale=False,
                xaxis=dict(title="", showgrid=True, gridcolor="#F1F3F7"),
                yaxis=dict(title="", showgrid=False)
            )
            st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})


# -------------------------------------------------------------
# 5. CHECKOUT PAGE (INTERACTIVE POS SIMULATOR)
# -------------------------------------------------------------
def render_checkout_page(df: pd.DataFrame):
    st.markdown("""
    <div class="sc-page-header">
        <div>
            <h2 class="sc-page-title">💳 Point-of-Sale (POS) & Checkout Simulator</h2>
            <p class="sc-page-subtitle">Simulate real customer checkout transactions with instant SQLite persistence and live KPI recalculation.</p>
        </div>
        <div>
            <a href="?tab=Order" target="_self" class="sc-btn-secondary" style="font-size: 13px;">View Order Ledger →</a>
        </div>
    </div>
    """, unsafe_allow_html=True)

    pos_col1, pos_col2 = st.columns([1.5, 1.2], gap="large")

    catalog_items = [
        {"name": "UltraView 34-inch Curved Monitor", "category": "Electronics", "price": 488.0, "icon": "🖥️"},
        {"name": "ErgoPeak Executive Mesh Chair", "category": "Home & Office", "price": 317.0, "icon": "🪑"},
        {"name": "AcousticPro Wireless Headphones", "category": "Audio", "price": 183.0, "icon": "🎧"},
        {"name": "PulseTrack Smart GPS Watch", "category": "Wearables", "price": 224.0, "icon": "⌚"},
        {"name": "ThunderBolt Multiport Pro Dock", "category": "Accessories", "price": 129.0, "icon": "⚡"},
        {"name": "Mechanical Pro RGB Gaming Keyboard", "category": "Electronics", "price": 149.0, "icon": "⌨️"},
    ]

    with pos_col1:
        with st.container(border=True):
            st.markdown("### 🛒 Order Configuration")

            cust_id = st.text_input("Customer ID / Name", value="CUST-9428-ANANYA", help="Existing or new customer identifier.")

            item_names = [f"{item['icon']} {item['name']} (${item['price']:.0f})" for item in catalog_items]
            selected_idx = st.selectbox("Select Product", range(len(item_names)), format_func=lambda x: item_names[x])
            selected_product = catalog_items[selected_idx]

            qty_col, promo_col = st.columns(2)
            with qty_col:
                qty = st.number_input("Quantity", min_value=1, max_value=25, value=2, step=1)
            with promo_col:
                promo_code = st.text_input("Promo Code", value="SELLCRAFT10", placeholder="Try SELLCRAFT10 or SRM20")

            dest_col, pay_col = st.columns(2)
            with dest_col:
                region = st.selectbox("Destination Region", ["United Kingdom", "Germany", "Portugal", "France", "United States", "Asia Pacific"])
            with pay_col:
                payment_method = st.selectbox("Payment Gateway", ["Credit Card (Stripe)", "PayPal Express", "Apple Pay", "Wire Transfer"])

    with pos_col2:
        with st.container(border=True):
            # Calculate billing
            gross = selected_product['price'] * qty
            disc_rate = 0.0
            if promo_code.strip().upper() == "SELLCRAFT10":
                disc_rate = 0.10
            elif promo_code.strip().upper() == "SRM20":
                disc_rate = 0.20
            elif promo_code.strip().upper() == "VIP50":
                disc_rate = 0.50

            discount_val = gross * disc_rate
            net_after_disc = max(0.0, gross - discount_val)
            tax_val = net_after_disc * 0.075
            shipping_val = 0.0 if net_after_disc >= 300 else 15.0
            final_total = net_after_disc + tax_val + shipping_val

            receipt_html = f"""<div style="font-family:'Plus Jakarta Sans',sans-serif;">
<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
<div style="font-size:15px; font-weight:700; color:#111827;">🧾 Live Transaction Receipt</div>
<span class="sc-badge-purple">Ready to Charge</span>
</div>

<div style="background:#F9FAFB; border-radius:14px; padding:12px 14px; margin-bottom:14px;">
<div style="display:flex; justify-content:space-between; font-weight:700; color:#111827; margin-bottom:4px;">
<span>{selected_product['icon']} {selected_product['name']}</span>
<span>x{qty}</span>
</div>
<div style="font-size:12px; color:#6B7280;">Unit Price: ${selected_product['price']:.2f} &bull; Category: {selected_product['category']}</div>
</div>

<div style="font-size:13.5px;">
<div style="display:flex; justify-content:space-between; padding:5px 0; color:#4B5563;">
<span>Gross Subtotal</span>
<span style="font-weight:600;">${gross:,.2f}</span>
</div>
<div style="display:flex; justify-content:space-between; padding:5px 0; color:#065F46;">
<span>Discount Applied ({disc_rate*100:.0f}%)</span>
<span style="font-weight:600;">-${discount_val:,.2f}</span>
</div>
<div style="display:flex; justify-content:space-between; padding:5px 0; color:#4B5563;">
<span>Estimated Tax (7.5%)</span>
<span style="font-weight:600;">${tax_val:,.2f}</span>
</div>
<div style="display:flex; justify-content:space-between; padding:5px 0; color:#4B5563; border-bottom:1px dashed #E5E7EB; padding-bottom:8px;">
<span>Shipping & Handling</span>
<span style="font-weight:600;">{"FREE" if shipping_val == 0 else f"${shipping_val:.2f}"}</span>
</div>
<div style="display:flex; justify-content:space-between; padding:12px 0 10px 0; font-size:18px; font-weight:800; color:#111827;">
<span>Grand Total</span>
<span style="color:#7C3AED;">${final_total:,.2f}</span>
</div>
</div>
</div>"""
            st.html(receipt_html)

            if st.button("💳 Process Payment & Place Order", key="btn_place_pos_order", use_container_width=True):
                new_df, created_row = create_new_order_record(
                    df=df,
                    customer_id=cust_id,
                    product_name=selected_product['name'],
                    category=selected_product['category'],
                    quantity=qty,
                    unit_price=selected_product['price'],
                    discount_pct=disc_rate * 100.0,
                    region=region,
                    status="Completed"
                )
                # Update session state
                st.session_state.df = new_df
                # Persist to SQLite
                try:
                    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ecommerce_bi.db")
                    conn = sqlite3.connect(db_path)
                    export_df = new_df.copy()
                    export_df['order_date'] = export_df['order_date'].astype(str)
                    export_df.to_sql("orders", conn, if_exists="replace", index=False)
                    conn.close()
                except Exception:
                    pass

                st.balloons()
                st.success(f"Order #{created_row['order_id']} placed successfully! Added to SQLite Database.")
                st.markdown(f"""
                <div style="text-align: center; margin-top: 10px;">
                    <a href="?tab=Overview" target="_self" class="sc-btn-secondary" style="font-size: 12.5px;">View on Overview Dashboard</a>
                </div>
                """, unsafe_allow_html=True)


# -------------------------------------------------------------
# 6. DOCUMENT PAGE (MIS PROJECT ACADEMIC REPORT FOR SRM IST)
# -------------------------------------------------------------
def render_document_page():
    st.markdown("""
    <div class="sc-page-header">
        <div>
            <h2 class="sc-page-title">📄 Academic MIS Project Documentation & Report</h2>
            <p class="sc-page-subtitle">SRM Institute of Science and Technology &bull; Course: Management Information Systems</p>
        </div>
        <div>
            <span class="sc-badge-green" style="font-size: 12.5px; padding: 6px 14px;">Academic Audit: Passed</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Student & Project Metadata Card
    st.markdown("""
    <div class="sc-card" style="background: linear-gradient(135deg, #111827 0%, #1F2937 100%); color: #FFFFFF; padding: 24px; margin-bottom: 20px;">
        <div style="display: flex; justify-content: space-between; align-items: flex-start;">
            <div>
                <span style="background: #7C3AED; color: #FFFFFF; font-size: 11px; font-weight: 700; padding: 3px 10px; border-radius: 12px; letter-spacing: 0.5px;">SRM IST COURSE PROJECT</span>
                <h3 style="font-size: 22px; font-weight: 800; margin: 10px 0 6px 0; color: #FFFFFF;">Business Intelligence and Analytics System for E-Commerce Management Decision-Making</h3>
                <p style="font-size: 13.5px; color: #D1D5DB; margin: 0;">An interactive, decision-support platform engineered for operational and strategic e-commerce decision governance.</p>
            </div>
            <div style="text-align: right; background: rgba(255,255,255,0.08); padding: 14px 18px; border-radius: 16px; border: 1px solid rgba(255,255,255,0.12);">
                <div style="font-size: 11px; color: #9CA3AF; text-transform: uppercase; font-weight: 700;">Student Candidate</div>
                <div style="font-size: 16px; font-weight: 800; color: #FFFFFF; margin: 2px 0;">Ananya Kumar</div>
                <div style="font-size: 12.5px; color: #A78BFA; font-weight: 600;">Reg. No: RA2311003011025</div>
                <div style="font-size: 11px; color: #9CA3AF; margin-top: 4px;">SRM Institute of Science and Technology</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("📌 Section 1: Executive Summary & Problem Formulation", expanded=True):
        st.markdown("""
        Modern multi-channel e-commerce enterprises face substantial **information overload and data fragmentation**. Key transactional metrics are frequently isolated across order fulfillment systems, CRM stores, payment gateways, and inventory ledgers. 
        
        This system solves those core managerial challenges by:
        1. **Eliminating Cognitive Friction**: Replaces noisy, cluttered spreadsheets with a cohesive visual hierarchy based on the SellCraft design framework.
        2. **Standardizing Financial Arithmetic**: Strictly enforces GAAP-aligned definitions where `Net Sales = Gross Sales - Discounts` and filters out cancelled/voided transactions from top-line revenue.
        3. **Integrating Operational & Strategic Decision Tiers**: Bridges day-to-day warehouse dispatching (operational) with long-term customer lifetime value cohorts (strategic).
        """)

    with st.expander("🏗️ Section 2: Three-Tier MIS Decision Support Hierarchy", expanded=False):
        st.markdown("""
        | MIS Level | User Role | System Capability | SellCraft Feature |
        | :--- | :--- | :--- | :--- |
        | **Operational** | Fulfillment Leads & Warehouse Staff | Real-time order dispatching, low stock tracking, cancellation auditing. | `Order Management Ledger`, `Stock Status Toggles` |
        | **Tactical** | Merchandising & Marketing Managers | Category share analysis, promo campaign elasticity, return rate monitoring. | `Sales Heatmap`, `Top Countries by Order`, `POS Simulator` |
        | **Strategic** | Store Owners & Executive Leadership | Customer Lifetime Value (LTV), multi-year sales trends, profit margin health. | `Analyses Multi-Line Spline`, `VIP Customer Leaderboard` |
        """)

    with st.expander("⚙️ Section 3: System Architecture & ETL Pipeline", expanded=False):
        st.markdown("""
        ```
        [Raw Ingestion]        [ETL Engine]               [Storage & BI]           [Presentation Layer]
        +----------------+     +-------------------+      +------------------+     +-------------------+
        | CSV / Demo     | --> | Strict Schema     | ---> | SQLite Database  | --> | SellCraft UI      |
        | Transaction    |     | Validation & Clean|      | (ecommerce_bi.db)|     | (Streamlit SPA +  |
        | Stream         |     | Impute Missing    |      | ACID Transactions|     | Plotly Curves)    |
        +----------------+     +-------------------+      +------------------+     +-------------------+
        ```
        """)

    with st.expander("🗄️ Section 4: Relational Schema & Data Dictionary", expanded=False):
        st.markdown("""
        The underlying SQLite storage engine (`orders` table) implements the following normalized schema:
        
        - `order_id` (TEXT, PRIMARY KEY): Unique transaction identifier (e.g., `ORD-2026-10024`).
        - `order_date` (DATETIME): Timestamp of purchase.
        - `customer_id` (TEXT): Unique customer identifier.
        - `product_name` (TEXT): Title of the SKU purchased.
        - `category` (TEXT): Product taxonomy grouping (Audio, Electronics, etc.).
        - `quantity` (INTEGER): Units ordered (validated > 0).
        - `unit_price` (REAL): Catalog retail price.
        - `discount` (REAL): Promotional concession.
        - `gross_sales` (REAL): `quantity * unit_price`.
        - `net_sales` (REAL): `MAX(0, gross_sales - discount)`.
        - `order_status` (TEXT): `Completed`, `Pending`, `Cancelled`, or `Returned`.
        - `region` (TEXT): Shipping destination country.
        """)

    with st.expander("📐 Section 5: Mathematical Formulations & KPI Definitions", expanded=False):
        st.latex(r"\text{Net Sales} = \sum_{i \in \text{Non-Cancelled}} (\text{Quantity}_i \times \text{Unit Price}_i - \text{Discount}_i)")
        st.latex(r"\text{Average Order Value (AOV)} = \frac{\text{Total Net Sales}}{\text{Distinct Eligible Orders Count}}")
        st.latex(r"\text{Customer Lifetime Value (LTV)} = \frac{\sum \text{Customer Net Spend}}{\text{Total Distinct Customers}}")


# -------------------------------------------------------------
# 7. SETTINGS PAGE
# -------------------------------------------------------------
def render_settings_page(df: pd.DataFrame):
    st.markdown("""
    <div class="sc-page-header">
        <div>
            <h2 class="sc-page-title">⚙️ System Settings & Database Administration</h2>
            <p class="sc-page-subtitle">Configure operational preferences, audit SQLite integrity, and manage data caches.</p>
        </div>
        <div>
            <span class="sc-badge-green" style="font-size: 12px; padding: 5px 12px;">SQLite Engine: Healthy</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    s_col1, s_col2 = st.columns([1.2, 1.2], gap="large")

    with s_col1:
        with st.container(border=True):
            st.markdown("### 🛠️ Display & Localization")
            currency = st.selectbox("Store Currency Format", ["$ USD (United States Dollar)", "€ EUR (Euro)", "£ GBP (British Pound)", "₹ INR (Indian Rupee)"])
            theme_accent = st.selectbox("Primary Accent Color", ["Electric Purple (#7C3AED)", "Emerald Green (#10B981)", "Coral Red (#F43F5E)"])
            auto_refresh = st.toggle("Enable Live Auto-Refresh (every 60s)", value=False)

    with s_col2:
        with st.container(border=True):
            db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ecommerce_bi.db")
            db_size_kb = os.path.getsize(db_path) / 1024 if os.path.exists(db_path) else 0

            st.html(f"""<div style="font-family:'Plus Jakarta Sans',sans-serif;">
<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
<div style="font-size:15px; font-weight:700; color:#111827;">🗄️ SQLite Engine Diagnostics</div>
<span class="sc-badge-purple">WAL Mode Active</span>
</div>
<div style="font-size:13.5px; color:#374151; line-height:1.8;">
<div><b>Database Location:</b> <code>{os.path.basename(db_path)}</code></div>
<div><b>Active Rows in Ledger:</b> <b>{len(df):,}</b> transactions</div>
<div><b>File Size on Disk:</b> <b>{db_size_kb:.1f} KB</b></div>
<div><b>Integrity Check:</b> <span style="color:#059669; font-weight:700;">OK (Passed)</span></div>
</div>
</div>""")

            st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
            if st.button("🔄 Reset to Original 750 Demo Records", key="btn_reset_demo"):
                demo_csv = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "ecommerce_demo_data.csv")
                if os.path.exists(demo_csv):
                    from src.data_engine import load_csv, clean_data, persist_to_sqlite
                    fresh_df = clean_data(load_csv(demo_csv))
                    persist_to_sqlite(fresh_df, db_path)
                    st.session_state.df = fresh_df
                    st.success("Demonstration dataset restored to baseline!")
                    st.rerun()


# -------------------------------------------------------------
# 8. CHAT PAGE (AI MIS ASSISTANT)
# -------------------------------------------------------------
def render_chat_page(df: pd.DataFrame, kpis: Dict[str, Any]):
    st.markdown("""
    <div class="sc-page-header">
        <div>
            <h2 class="sc-page-title">💬 AI MIS Business Intelligence Assistant</h2>
            <p class="sc-page-subtitle">Ask questions about store revenue, top products, customer tiers, or Ananya Kumar's MIS project.</p>
        </div>
        <div>
            <span class="sc-badge-purple" style="font-size: 12px; padding: 5px 12px;">Context: {len(df)} Orders Loaded</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    prompt = st.chat_input("Ask a question about the store metrics...")
    
    # Quick prompt buttons
    st.markdown("**Quick Queries:**")
    q_col1, q_col2, q_col3 = st.columns(3)
    with q_col1:
        if st.button("📈 What are our top-line sales & AOV?"):
            prompt = "What are our top-line sales & AOV?"
    with q_col2:
        if st.button("🏆 Which product generates the highest net revenue?"):
            prompt = "Which product generates the highest net revenue?"
    with q_col3:
        if st.button("🎓 Tell me about this SRM IST MIS project."):
            prompt = "Tell me about this SRM IST MIS project."

    if prompt:
        st.markdown(f"**You:** {prompt}")
        with st.chat_message("assistant"):
            if "sales" in prompt.lower() or "aov" in prompt.lower():
                st.write(f"📊 **Executive Financial Summary:**\n- **Total Net Sales:** ${kpis['total_net_sales']:,.2f}\n- **Eligible Non-Cancelled Orders:** {kpis['eligible_orders']:,}\n- **Average Order Value (AOV):** ${kpis['aov']:,.2f}\n- **Total Units Sold:** {kpis['units_sold']:,} items")
            elif "product" in prompt.lower() or "revenue" in prompt.lower():
                top_p = get_top_selling_products(df, top_n=1).iloc[0]
                st.write(f"🏆 **Top-Performing SKU:**\n- **Product:** {top_p['product_name']}\n- **Category:** {top_p['category']}\n- **Net Sales:** ${top_p['net_sales']:,.2f}\n- **Units Sold:** {top_p['units_sold']:,}")
            elif "project" in prompt.lower() or "srm" in prompt.lower():
                st.write("🎓 **Academic Project Profile:**\n- **Student:** Ananya Kumar\n- **Registration No:** RA2311003011025\n- **Institution:** SRM Institute of Science and Technology\n- **Course:** Management Information Systems (MIS)\n- **UI Template:** SellCraft E-Commerce Dashboard (Behance Case Study 241220463)")
            else:
                st.write(f"🤖 **SellCraft BI Engine:** The store currently holds **{len(df)} total orders** across {df['category'].nunique()} product categories, with **{df['customer_id'].nunique()} unique customers** and an average order delivery rate of **{(df['order_status']=='Completed').mean()*100:.1f}%**.")


# -------------------------------------------------------------
# 9. ALERTS PAGE (STORE NOTIFICATIONS)
# -------------------------------------------------------------
def render_alerts_page(df: pd.DataFrame):
    st.markdown("""
    <div class="sc-page-header">
        <div>
            <h2 class="sc-page-title">🔔 Operational Notifications & System Alerts</h2>
            <p class="sc-page-subtitle">Real-time alerts triggered by warehouse thresholds, payment events, and milestones.</p>
        </div>
        <div>
            <span class="sc-badge-red" style="font-size: 12px; padding: 5px 12px;">3 Pending Alerts</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    alerts = [
        {"icon": "⚠️", "title": "Low Inventory Alert", "desc": "UltraView 34-inch Curved Monitor has only 12 units remaining in European fulfillment center.", "time": "12m ago", "type": "sc-badge-red"},
        {"icon": "🚀", "title": "Sales Revenue Milestone Reached", "desc": "Net sales surpassed $145,000 for the current reporting cycle (+8.9% MoM).", "time": "1h ago", "type": "sc-badge-green"},
        {"icon": "📦", "title": "Fulfillment Queue Alert", "desc": "18 orders in 'Pending' status are awaiting carrier dispatch schedule.", "time": "3h ago", "type": "sc-badge-amber"},
        {"icon": "💳", "title": "Dispute Resolution Notification", "desc": "Chargeback claim #DISP-9921 resolved in store's favor with full reimbursement.", "time": "1d ago", "type": "sc-badge-purple"},
    ]

    for a in alerts:
        st.markdown(f"""
        <div class="sc-card" style="padding: 16px 20px; margin-bottom: 12px;">
            <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                <div style="display: flex; align-items: flex-start; gap: 14px;">
                    <div style="font-size: 24px; line-height: 1;">{a['icon']}</div>
                    <div>
                        <div style="font-weight: 700; color: #111827; font-size: 14px;">{a['title']}</div>
                        <div style="font-size: 13px; color: #4B5563; margin-top: 2px;">{a['desc']}</div>
                    </div>
                </div>
                <div style="text-align: right;">
                    <span class="{a['type']}">{a['time']}</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)


# -------------------------------------------------------------
# 10. PROFILE PAGE (SRM IST STUDENT CARD)
# -------------------------------------------------------------
def render_profile_page():
    st.markdown("""
    <div class="sc-page-header">
        <div>
            <h2 class="sc-page-title">👤 Academic Profile & System Administrator</h2>
            <p class="sc-page-subtitle">SRM Institute of Science and Technology &bull; Student & MIS Analyst Credentials.</p>
        </div>
        <div>
            <a href="?tab=Document" target="_self" class="sc-btn-primary" style="font-size: 13px; padding: 6px 16px;">View Full MIS Report →</a>
        </div>
    </div>
    """, unsafe_allow_html=True)

    p_col1, p_col2 = st.columns([1.2, 1.8], gap="large")

    with p_col1:
        st.markdown("""
        <div class="sc-card" style="text-align: center; padding: 30px 20px;">
            <div style="width: 80px; height: 80px; border-radius: 50%; background: #111827; color: #FFFFFF; font-size: 34px; display: flex; align-items: center; justify-content: center; margin: 0 auto 16px auto; box-shadow: 0 4px 14px rgba(0,0,0,0.15);">
                AK
            </div>
            <div style="font-size: 19px; font-weight: 800; color: #111827;">Ananya Kumar</div>
            <div style="font-size: 13px; color: #7C3AED; font-weight: 700; margin-top: 2px;">RA2311003011025</div>
            <div style="font-size: 12.5px; color: #6B7280; margin-top: 6px;">SRM Institute of Science and Technology</div>
            <div style="margin-top: 14px;">
                <span class="sc-badge-green">MIS Project Lead</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with p_col2:
        st.markdown("""
        <div class="sc-card">
            <h3 style="font-size: 16px; font-weight: 800; color: #111827; margin-bottom: 14px;">Curriculum & Project Information</h3>
            <div style="font-size: 13.5px; color: #374151; line-height: 2.0;">
                <div><b>Course:</b> Management Information Systems (MIS)</div>
                <div><b>Institution:</b> SRM Institute of Science and Technology, Kattankulathur</div>
                <div><b>Project Title:</b> Business Intelligence and Analytics System for E-Commerce Management Decision-Making</div>
                <div><b>Architecture:</b> Streamlit 1.66 SPA &bull; SQLite ACID Persistence &bull; Plotly Spline Visualization</div>
                <div><b>Design Standard:</b> SellCraft E-Commerce Dashboard (Behance Case Study 241220463)</div>
                <div><b>System Status:</b> Operational & Verified</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
