"""
Custom UI Components for SellCraft E-Commerce Dashboard.
Faithfully recreates the exact Behance SellCraft design system across all pages:
- Overview (Executive BI Dashboard)
- Product (Catalog & Inventory Management)
- Order (Fulfillment & Transaction Ledger)
- Customer Data (LTV & VIP Cohorts)
- Checkout (Interactive POS Simulator)
- Document (MIS Project Report & Academic Audit)
- Settings (Configuration & SQLite Management)
- Chat (AI MIS Assistant)
- Alerts (Store Notifications)
- Profile (SRM IST Academic Profile)
"""

from typing import Dict, Any, List, Optional
import pandas as pd
from src.config import THEME, KPI_DEFINITIONS

def get_custom_css() -> str:
    """
    CSS stylesheet injected into Streamlit to replicate the exact Behance SellCraft aesthetic.
    Guarantees slim navbar, sleek padding, and no overflow outside margins.
    """
    return f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Inter:wght@400;500;600;700&display=swap');

        /* Global Reset */
        *, *::before, *::after {{
            box-sizing: border-box !important;
        }}

        .stApp {{
            background-color: {THEME["bg_outer"]} !important;
            font-family: 'Plus Jakarta Sans', 'Inter', -apple-system, sans-serif !important;
            color: {THEME["text_primary"]} !important;
            overflow-x: hidden !important;
        }}

        /* Completely remove thick top header gap */
        header[data-testid="stHeader"], [data-testid="stAppHeader"], div[data-testid="stToolbar"] {{
            display: none !important;
            height: 0px !important;
            min-height: 0px !important;
        }}
        .main {{
            padding-top: 0px !important;
        }}
        .main .block-container {{
            background-color: {THEME["bg_card"]} !important;
            border-radius: 24px !important;
            border: 1px solid {THEME["border_color"]} !important;
            box-shadow: 0 4px 25px rgba(0, 0, 0, 0.03) !important;
            padding: 12px 28px 28px 28px !important;
            margin: 8px auto 20px auto !important;
            max-width: 1420px !important;
            width: 96% !important;
        }}

        footer {{
            visibility: hidden;
            display: none;
        }}
        #MainMenu {{
            visibility: hidden;
        }}

        /* Ultra-sleek SellCraft Navbar */
        .sc-navbar {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 2px 0 12px 0;
            border-bottom: 1px solid #F1F3F7;
            margin-bottom: 18px;
            height: 48px;
        }}

        .sc-brand {{
            font-size: 22px;
            font-weight: 800;
            color: #111827;
            text-decoration: none;
            letter-spacing: -0.6px;
            display: flex;
            align-items: center;
            line-height: 1;
        }}
        .sc-brand:hover {{
            color: #000000;
        }}

        .sc-nav-center {{
            display: flex;
            align-items: center;
            gap: 6px;
        }}

        .sc-nav-link {{
            text-decoration: none;
            font-size: 13.5px;
            font-weight: 500;
            color: #6B7280;
            padding: 6px 16px;
            border-radius: 20px;
            transition: all 0.15s ease-in-out;
            line-height: 1.2;
            white-space: nowrap;
        }}
        .sc-nav-link:hover {{
            color: #111827;
            background-color: #F3F4F6;
        }}
        .sc-nav-link.sc-active {{
            background-color: #111827 !important;
            color: #FFFFFF !important;
            font-weight: 700 !important;
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
        }}

        .sc-nav-right {{
            display: flex;
            align-items: center;
            gap: 8px;
        }}

        .sc-settings-btn {{
            display: flex;
            align-items: center;
            gap: 6px;
            text-decoration: none;
            font-size: 12.5px;
            font-weight: 600;
            color: #374151;
            background: #FFFFFF;
            border: 1px solid #E5E7EB;
            border-radius: 20px;
            padding: 5px 13px;
            transition: all 0.15s ease;
            line-height: 1;
        }}
        .sc-settings-btn:hover {{
            background: #F9FAFB;
            border-color: #D1D5DB;
            color: #111827;
        }}
        .sc-settings-btn.sc-active-btn {{
            background: #111827;
            color: #FFFFFF;
            border-color: #111827;
        }}

        .sc-icon-btn {{
            display: flex;
            align-items: center;
            justify-content: center;
            width: 32px;
            height: 32px;
            border-radius: 50%;
            background: #FFFFFF;
            border: 1px solid #E5E7EB;
            text-decoration: none;
            font-size: 13px;
            transition: all 0.15s ease;
        }}
        .sc-icon-btn:hover {{
            background: #F3F4F6;
            border-color: #D1D5DB;
        }}
        .sc-icon-btn.sc-active-icon {{
            background: #EDE9FE;
            border-color: #7C3AED;
        }}

        .sc-profile-btn {{
            display: flex;
            align-items: center;
            justify-content: center;
            width: 32px;
            height: 32px;
            border-radius: 50%;
            background: #111827;
            color: #FFFFFF;
            border: 1px solid #111827;
            text-decoration: none;
            font-size: 13px;
            transition: all 0.15s ease;
        }}
        .sc-profile-btn:hover {{
            opacity: 0.9;
            transform: scale(1.05);
        }}
        .sc-profile-btn.sc-active-profile {{
            box-shadow: 0 0 0 2px #7C3AED;
        }}

        /* Page Headers */
        .sc-page-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 16px;
        }}
        .sc-page-title {{
            font-size: 20px;
            font-weight: 800;
            color: #111827;
            margin: 0;
            letter-spacing: -0.5px;
        }}
        .sc-page-subtitle {{
            font-size: 12.5px;
            color: #6B7280;
            margin-top: 3px;
            margin-bottom: 0;
        }}

        /* Common Card Shell */
        .sc-card {{
            background: #FFFFFF;
            border: 1px solid {THEME["border_color"]};
            border-radius: 20px;
            padding: 20px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.02);
            height: 100%;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }}
        .sc-card-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
        }}
        .sc-card-title {{
            font-size: 15px;
            font-weight: 700;
            color: {THEME["text_primary"]};
            display: flex;
            align-items: center;
            gap: 8px;
            margin: 0;
        }}
        .sc-dots-btn {{
            color: #9CA3AF;
            font-size: 16px;
            cursor: pointer;
            line-height: 1;
        }}

        /* Total Sales Hero Card */
        .sc-total-sales-val {{
            font-size: 32px;
            font-weight: 800;
            letter-spacing: -1px;
            color: {THEME["text_primary"]};
            line-height: 1.1;
            margin-bottom: 8px;
        }}
        .sc-badge-green {{
            background: #D1FAE5;
            color: #065F46;
            font-size: 11.5px;
            font-weight: 700;
            padding: 3px 9px;
            border-radius: 12px;
            display: inline-block;
        }}
        .sc-badge-red {{
            background: #FEE2E2;
            color: #991B1B;
            font-size: 11.5px;
            font-weight: 700;
            padding: 3px 9px;
            border-radius: 12px;
            display: inline-block;
        }}
        .sc-badge-purple {{
            background: #EDE9FE;
            color: #6D28D9;
            font-size: 11.5px;
            font-weight: 700;
            padding: 3px 9px;
            border-radius: 12px;
            display: inline-block;
        }}
        .sc-badge-amber {{
            background: #FEF3C7;
            color: #92400E;
            font-size: 11.5px;
            font-weight: 700;
            padding: 3px 9px;
            border-radius: 12px;
            display: inline-block;
        }}

        /* Sub Metric Cards Triplet */
        .sc-sub-grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 12px;
            margin-top: 14px;
        }}
        .sc-sub-card {{
            background: #F9FAFB;
            border: 1px solid #F3F4F6;
            border-radius: 16px;
            padding: 14px;
            position: relative;
        }}
        .sc-sub-label {{
            font-size: 12px;
            color: {THEME["text_secondary"]};
            font-weight: 600;
            margin-bottom: 6px;
        }}
        .sc-sub-val {{
            font-size: 20px;
            font-weight: 800;
            color: {THEME["text_primary"]};
            letter-spacing: -0.5px;
            margin-bottom: 8px;
        }}
        .sc-sub-arrow {{
            width: 22px;
            height: 22px;
            background: #111827;
            color: #FFFFFF;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 11px;
            position: absolute;
            bottom: 12px;
            right: 12px;
        }}

        /* 4-KPI Row Grid */
        .sc-kpi-grid-4 {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 16px;
            margin-bottom: 20px;
        }}
        .sc-kpi-box {{
            background: #FFFFFF;
            border: 1px solid {THEME["border_color"]};
            border-radius: 18px;
            padding: 16px 20px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.02);
        }}
        .sc-kpi-box-title {{
            font-size: 12.5px;
            color: #6B7280;
            font-weight: 600;
            margin-bottom: 8px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }}
        .sc-kpi-box-val {{
            font-size: 24px;
            font-weight: 800;
            color: #111827;
            letter-spacing: -0.5px;
            margin-bottom: 6px;
        }}

        /* Sales Heatmap */
        .sc-heatmap-table {{
            width: 100%;
            border-collapse: separate;
            border-spacing: 5px;
            margin-top: 8px;
        }}
        .sc-heatmap-time {{
            font-size: 11px;
            color: #9CA3AF;
            font-weight: 600;
            text-align: right;
            padding-right: 6px;
        }}
        .sc-heatmap-colhdr {{
            font-size: 11px;
            color: #9CA3AF;
            font-weight: 600;
            text-align: center;
            padding-bottom: 4px;
        }}
        .sc-hm-cell {{
            height: 26px;
            border-radius: 6px;
            transition: transform 0.1s ease;
        }}
        .sc-hm-l1 {{ background: #EDE9FE; }}
        .sc-hm-l2 {{ background: #DDD6FE; }}
        .sc-hm-l3 {{ background: #A78BFA; }}
        .sc-hm-l4 {{ background: #7C3AED; }}
        .sc-hm-stripes {{
            background: repeating-linear-gradient(45deg, #A78BFA, #A78BFA 4px, #C4B5FD 4px, #C4B5FD 8px);
        }}

        /* Country Progress Rows */
        .sc-country-row {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 8px 0;
            font-size: 13px;
        }}
        .sc-c-info {{
            display: flex;
            align-items: center;
            gap: 10px;
            width: 38%;
            font-weight: 600;
            color: {THEME["text_primary"]};
        }}
        .sc-bar-wrap {{
            flex-grow: 1;
            height: 7px;
            background: #F3F4F6;
            border-radius: 10px;
            overflow: hidden;
            margin: 0 12px;
        }}
        .sc-bar-fill {{
            height: 100%;
            background: #8B5CF6;
            border-radius: 10px;
        }}
        .sc-c-pct {{
            font-weight: 700;
            color: {THEME["text_secondary"]};
            width: 32px;
            text-align: right;
            font-size: 12px;
        }}

        /* Product & Order Tables */
        .sc-product-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 13px;
        }}
        .sc-product-table th {{
            text-align: left;
            padding: 10px 12px;
            font-size: 11.5px;
            color: {THEME["text_secondary"]};
            font-weight: 600;
            border-bottom: 1px solid #F1F3F7;
        }}
        .sc-product-table td {{
            padding: 12px;
            border-bottom: 1px solid #F9FAFB;
            vertical-align: middle;
        }}
        .sc-prod-detail {{
            display: flex;
            align-items: center;
            gap: 12px;
        }}
        .sc-prod-img {{
            width: 36px;
            height: 36px;
            border-radius: 10px;
            background: #F3F4F6;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 18px;
            flex-shrink: 0;
        }}
        .sc-status-pill {{
            font-size: 11px;
            font-weight: 700;
            padding: 4px 10px;
            border-radius: 14px;
            display: inline-flex;
            align-items: center;
            gap: 5px;
        }}
        .sc-status-available {{
            background: {THEME["status_available_bg"]};
            color: {THEME["status_available_text"]};
        }}
        .sc-status-outofstock {{
            background: {THEME["status_outofstock_bg"]};
            color: {THEME["status_outofstock_text"]};
        }}
        .sc-status-pending {{
            background: #FEF3C7;
            color: #92400E;
        }}
        .sc-status-delivered {{
            background: #D1FAE5;
            color: #065F46;
        }}
        .sc-status-cancelled {{
            background: #FEE2E2;
            color: #991B1B;
        }}

        /* Form elements & Cards */
        .sc-input-box {{
            background: #F9FAFB;
            border: 1px solid #E5E7EB;
            border-radius: 12px;
            padding: 10px 14px;
            font-size: 13.5px;
            color: #111827;
            width: 100%;
            outline: none;
        }}
        .sc-btn-primary {{
            background: #111827;
            color: #FFFFFF;
            border: none;
            border-radius: 20px;
            padding: 10px 20px;
            font-size: 13.5px;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.15s ease;
            text-align: center;
            display: inline-block;
            text-decoration: none;
        }}
        .sc-btn-primary:hover {{
            background: #000000;
            transform: translateY(-1px);
        }}
        .sc-btn-secondary {{
            background: #FFFFFF;
            color: #374151;
            border: 1px solid #E5E7EB;
            border-radius: 20px;
            padding: 8px 16px;
            font-size: 13px;
            font-weight: 600;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
        }}
        .sc-btn-secondary:hover {{
            background: #F9FAFB;
            border-color: #D1D5DB;
        }}

        /* Container wrappers for charts */
        div[data-testid="stVerticalBlockBorderWrapper"] > div {{
            background: #FFFFFF !important;
            border: 1px solid {THEME["border_color"]} !important;
            border-radius: 20px !important;
            padding: 18px 20px !important;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.02) !important;
        }}
    </style>
    """

def render_sellcraft_navbar(active_page: str = "Overview") -> str:
    """
    Renders the exact SellCraft slim top navbar.
    Clicking tabs or buttons updates URL query params and switches page instantly.
    """
    tabs = ["Overview", "Product", "Order", "Customer Data", "Checkout", "Document"]
    tabs_html = ""
    for t in tabs:
        is_active = (t == active_page)
        cls = "sc-nav-link sc-active" if is_active else "sc-nav-link"
        tabs_html += f'<a href="?tab={t}" target="_self" class="{cls}">{t}</a>'

    settings_cls = "sc-settings-btn sc-active-btn" if active_page == "Settings" else "sc-settings-btn"
    chat_cls = "sc-icon-btn sc-active-icon" if active_page == "Chat" else "sc-icon-btn"
    alerts_cls = "sc-icon-btn sc-active-icon" if active_page == "Alerts" else "sc-icon-btn"
    profile_cls = "sc-profile-btn sc-active-profile" if active_page == "Profile" else "sc-profile-btn"

    return f"""
    <div class="sc-navbar">
        <a href="?tab=Overview" target="_self" class="sc-brand">SellCraft</a>
        <div class="sc-nav-center">
            {tabs_html}
        </div>
        <div class="sc-nav-right">
            <a href="?tab=Settings" target="_self" class="{settings_cls}">
                <span>⚙️</span> Settings
            </a>
            <a href="?tab=Chat" target="_self" class="{chat_cls}" title="AI MIS Assistant">💬</a>
            <a href="?tab=Alerts" target="_self" class="{alerts_cls}" title="Store Notifications">🔔</a>
            <a href="?tab=Profile" target="_self" class="{profile_cls}" title="Rishav (SRM IST)">👤</a>
        </div>
    </div>
    """

def render_total_sales_card(kpis: Dict[str, Any]) -> str:
    """
    Renders the SellCraft Total Sales card with the 3 sub-cards underneath:
    Total Orders, Total Cancel Orders, Total Units Sold.
    """
    sales_k = f"${kpis['total_net_sales']/1000:,.1f}k+" if kpis['total_net_sales'] >= 1000 else f"${kpis['total_net_sales']:,.2f}"

    return f"""<div class="sc-card">
<div>
<div class="sc-card-header">
<div class="sc-card-title">🛒 Total Sales</div>
<span class="sc-dots-btn">⋮</span>
</div>
<div style="display: flex; justify-content: space-between; align-items: flex-end;">
<div>
<div class="sc-total-sales-val">{sales_k}</div>
<span class="sc-badge-green">+8.9% +$30,456 This Month</span>
</div>
<div style="text-align: right;">
<svg width="120" height="42" viewBox="0 0 120 42" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M2 35 C 20 30, 30 18, 50 24 C 70 30, 80 12, 105 16 L 118 8" stroke="#D1D5DB" stroke-width="2.5" stroke-linecap="round"/>
<circle cx="118" cy="8" r="4" fill="#111827" stroke="#FFFFFF" stroke-width="2"/>
</svg>
<div style="margin-top: 2px;"><span style="background:#111827; color:#FFFFFF; font-size:10px; font-weight:700; padding:2px 6px; border-radius:10px;">-17.4%</span></div>
</div>
</div>
</div>

<div class="sc-sub-grid">
<!-- Sub Card 1: Total Orders -->
<div class="sc-sub-card">
<div class="sc-sub-label">Total Orders</div>
<div class="sc-sub-val">{kpis['eligible_orders']:,}</div>
<span class="sc-badge-green">+14.9% 12k</span>
<div class="sc-sub-arrow">↗</div>
</div>

<!-- Sub Card 2: Total Cancel Orders -->
<div class="sc-sub-card">
<div class="sc-sub-label">Total Cancel Orders</div>
<div class="sc-sub-val">{int(kpis['total_orders'] - kpis['eligible_orders']):,}</div>
<span class="sc-badge-red">-14.9% -370</span>
<div class="sc-sub-arrow">↗</div>
</div>

<!-- Sub Card 3: Total Visitors / Units Sold -->
<div class="sc-sub-card">
<div class="sc-sub-label">Total Units Sold</div>
<div class="sc-sub-val">{kpis['units_sold']:,}</div>
<span class="sc-badge-green">+14.9% +32k</span>
<div class="sc-sub-arrow">↗</div>
</div>
</div>
</div>"""

def render_sales_heatmap() -> str:
    """
    Renders the SellCraft Sales Heatmap card with the purple grid texture and legend.
    """
    return f"""<div class="sc-card">
<div>
<div class="sc-card-header">
<div class="sc-card-title">📊 Sales Heatmap</div>
<span class="sc-dots-btn">⋮</span>
</div>

<table class="sc-heatmap-table">
<thead>
<tr>
<th style="width: 32px;"></th>
<th class="sc-heatmap-colhdr">Mon</th>
<th class="sc-heatmap-colhdr">Tue</th>
<th class="sc-heatmap-colhdr">Wed</th>
<th class="sc-heatmap-colhdr">Thu</th>
<th class="sc-heatmap-colhdr">Fri</th>
</tr>
</thead>
<tbody>
<tr>
<td class="sc-heatmap-time">5am</td>
<td><div class="sc-hm-cell sc-hm-l3"></div></td>
<td><div class="sc-hm-cell sc-hm-l1"></div></td>
<td><div class="sc-hm-cell sc-hm-stripes"></div></td>
<td><div class="sc-hm-cell sc-hm-l4"></div></td>
<td><div class="sc-hm-cell sc-hm-l2"></div></td>
</tr>
<tr>
<td class="sc-heatmap-time">7am</td>
<td><div class="sc-hm-cell sc-hm-l4"></div></td>
<td><div class="sc-hm-cell sc-hm-l3"></div></td>
<td><div class="sc-hm-cell sc-hm-l1"></div></td>
<td><div class="sc-hm-cell sc-hm-stripes"></div></td>
<td><div class="sc-hm-cell sc-hm-l3"></div></td>
</tr>
<tr>
<td class="sc-heatmap-time">9am</td>
<td><div class="sc-hm-cell sc-hm-l1"></div></td>
<td><div class="sc-hm-cell sc-hm-stripes"></div></td>
<td><div class="sc-hm-cell sc-hm-l4"></div></td>
<td><div class="sc-hm-cell sc-hm-l2"></div></td>
<td><div class="sc-hm-cell sc-hm-l4"></div></td>
</tr>
<tr>
<td class="sc-heatmap-time">11am</td>
<td><div class="sc-hm-cell sc-hm-l2"></div></td>
<td><div class="sc-hm-cell sc-hm-l4"></div></td>
<td><div class="sc-hm-cell sc-hm-l3"></div></td>
<td><div class="sc-hm-cell sc-hm-l1"></div></td>
<td><div class="sc-hm-cell sc-hm-stripes"></div></td>
</tr>
</tbody>
</table>
</div>

<div style="display:flex; justify-content:space-between; align-items:center; margin-top:14px; font-size:11px; color:#6B7280; font-weight:600;">
<span><span style="color:#7C3AED;">●</span> 3,000&gt;</span>
<span><span style="color:#A78BFA;">●</span> 1,000&gt;</span>
<span><span style="color:#DDD6FE;">●</span> 500&gt;</span>
<span><span style="color:#EDE9FE;">●</span> 100&gt;</span>
</div>
</div>"""

def render_top_countries() -> str:
    """
    Renders the SellCraft Top Countries By Order card with flags and progress bars.
    """
    countries = [
        {"name": "United Kingdom", "flag": "🇬🇧", "pct": 26, "val": "26%"},
        {"name": "Germany", "flag": "🇩🇪", "pct": 17, "val": "17%"},
        {"name": "Portugal", "flag": "🇵🇹", "pct": 12, "val": "12%"},
        {"name": "France", "flag": "🇫🇷", "pct": 20, "val": "20%"},
        {"name": "United States", "flag": "🇺🇸", "pct": 25, "val": "25%"},
    ]

    rows = ""
    for c in countries:
        rows += f"""<div class="sc-country-row">
<div class="sc-c-info">
<span style="font-size: 16px; line-height: 1;">{c['flag']}</span>
<span style="font-size: 13px;">{c['name']}</span>
</div>
<div class="sc-bar-wrap">
<div class="sc-bar-fill" style="width: {c['pct']}%;"></div>
</div>
<div class="sc-c-pct">{c['val']}</div>
</div>"""

    return f"""<div class="sc-card">
<div>
<div class="sc-card-header">
<div class="sc-card-title">📍 Top Countries By Order</div>
<span class="sc-dots-btn">⋮</span>
</div>
<div style="margin-bottom: 8px;">
<span class="sc-badge-green">+8.9% 7,346 Active Order</span>
</div>
<div style="margin-top: 6px;">
{rows}
</div>
</div>
</div>"""

def render_top_selling_product_table(top_df: pd.DataFrame) -> str:
    """
    Renders the bottom-left SellCraft Top Selling Product data table.
    """
    if len(top_df) == 0:
        return "<div class='sc-card'><p>No product performance records.</p></div>"

    icons = {
        "Audio": "🎧",
        "Electronics": "🖥️",
        "Home & Office": "🪑",
        "Accessories": "🎒",
        "Apparel": "👕",
        "Wearables": "⌚"
    }

    rows = ""
    for idx, row in top_df.head(4).iterrows():
        icon = icons.get(row['category'], "📦")
        sub_id = f"#{457200 + idx * 31}KH"
        price = f"${row['net_sales'] / max(1, row['units_sold']):,.0f}"
        status_cls = "sc-status-available" if idx % 2 == 0 else "sc-status-outofstock"
        status_text = "● Available" if idx % 2 == 0 else "● Out Of Stock"

        rows += f"""<tr>
<td><input type="checkbox" {'checked' if idx == 0 else ''} style="cursor: pointer; accent-color: #111827;"></td>
<td>
<div class="sc-prod-detail">
<div class="sc-prod-img">{icon}</div>
<div>
<div style="font-weight: 700; color: #111827; font-size: 13.5px;">{row['product_name']}</div>
<div style="font-size: 11px; color: #9CA3AF;">{sub_id}</div>
</div>
</div>
</td>
<td>
<div style="font-weight: 700; color: #111827;">{row['orders_count'] * 25:,}</div>
<div style="font-size: 11px; color: #9CA3AF;">{row['units_sold']} this month</div>
</td>
<td style="font-weight: 700; color: #111827;">{price}</td>
<td><span class="sc-status-pill {status_cls}">{status_text}</span></td>
</tr>"""

    return f"""<div class="sc-card">
<div>
<div class="sc-card-header">
<div class="sc-card-title">✨ Top Selling Product</div>
<span class="sc-dots-btn">⋮</span>
</div>
<div style="overflow-x: auto;">
<table class="sc-product-table">
<thead>
<tr>
<th style="width: 24px;">#</th>
<th>Product Details</th>
<th>Total Order</th>
<th>Price</th>
<th>Status</th>
</tr>
</thead>
<tbody>
{rows}
</tbody>
</table>
</div>
</div>
</div>"""
