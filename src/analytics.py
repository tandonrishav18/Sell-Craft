"""
Analytics and KPI Engine for E-Commerce MIS BI System.
Implements exact KPI arithmetic, time-series aggregations, period-over-period comparisons,
customer analytics, product inventory tracking, and checkout order creation.
"""

from typing import Dict, Any, Optional, Tuple, List
from datetime import datetime
import pandas as pd
import numpy as np

def filter_dataset(
    df: pd.DataFrame,
    start_date: Optional[pd.Timestamp] = None,
    end_date: Optional[pd.Timestamp] = None,
    categories: Optional[List[str]] = None,
    regions: Optional[List[str]] = None,
    statuses: Optional[List[str]] = None
) -> pd.DataFrame:
    """
    Applies multi-dimensional filters to the dataset.
    """
    filtered = df.copy()

    if start_date is not None:
        filtered = filtered[filtered['order_date'] >= pd.to_datetime(start_date)]
    if end_date is not None:
        filtered = filtered[filtered['order_date'] <= pd.to_datetime(end_date)]

    if categories and "All" not in categories:
        filtered = filtered[filtered['category'].isin(categories)]

    if regions and "All" not in regions:
        filtered = filtered[filtered['region'].isin(regions)]

    if statuses and "All" not in statuses:
        filtered = filtered[filtered['order_status'].isin(statuses)]

    return filtered

def calculate_kpis(current_df: pd.DataFrame, previous_df: Optional[pd.DataFrame] = None) -> Dict[str, Any]:
    """
    Calculates executive KPIs according to MIS Project Report specifications:
    - Total Gross Sales
    - Total Net Sales (excluding cancelled transactions)
    - Distinct Eligible Orders
    - Average Order Value (AOV)
    - Units Sold
    - Return Rate (%)
    - Gross Profit and Profit Margin (%)
    - Period-over-Period trend percentages when previous_df is supplied
    """
    if len(current_df) == 0:
        return {
            "total_net_sales": 0.0,
            "total_gross_sales": 0.0,
            "total_orders": 0,
            "eligible_orders": 0,
            "aov": 0.0,
            "units_sold": 0,
            "return_rate": 0.0,
            "total_profit": None,
            "profit_margin": None,
            "growth_sales": None,
            "growth_orders": None,
            "growth_aov": None,
            "growth_units": None,
            "has_cost_data": False
        }

    non_cancelled = current_df[~current_df['order_status'].isin(['Cancelled', 'Void'])]
    total_distinct_orders = current_df['order_id'].nunique()
    eligible_distinct_orders = non_cancelled['order_id'].nunique()

    total_gross = float(non_cancelled['gross_sales'].sum())
    total_net = float(non_cancelled['net_sales'].sum())
    units_sold = int(non_cancelled['quantity'].sum())

    aov = (total_net / eligible_distinct_orders) if eligible_distinct_orders > 0 else 0.0

    returned_orders = current_df[current_df['order_status'] == 'Returned']['order_id'].nunique()
    return_rate = (returned_orders / total_distinct_orders * 100.0) if total_distinct_orders > 0 else 0.0

    has_cost = 'cogs' in current_df.columns and non_cancelled['cogs'].notnull().any()
    if has_cost:
        valid_profit_rows = non_cancelled.dropna(subset=['gross_profit'])
        if len(valid_profit_rows) > 0:
            total_profit = float(valid_profit_rows['gross_profit'].sum())
            valid_net = float(valid_profit_rows['net_sales'].sum())
            profit_margin = (total_profit / valid_net * 100.0) if valid_net > 0 else 0.0
        else:
            total_profit = None
            profit_margin = None
            has_cost = False
    else:
        total_profit = None
        profit_margin = None

    growth_sales = None
    growth_orders = None
    growth_aov = None
    growth_units = None

    if previous_df is not None and len(previous_df) > 0:
        prev_kpis = calculate_kpis(previous_df, None)
        if prev_kpis['total_net_sales'] > 0:
            growth_sales = ((total_net - prev_kpis['total_net_sales']) / prev_kpis['total_net_sales']) * 100.0
        if prev_kpis['eligible_orders'] > 0:
            growth_orders = ((eligible_distinct_orders - prev_kpis['eligible_orders']) / prev_kpis['eligible_orders']) * 100.0
        if prev_kpis['aov'] > 0:
            growth_aov = ((aov - prev_kpis['aov']) / prev_kpis['aov']) * 100.0
        if prev_kpis['units_sold'] > 0:
            growth_units = ((units_sold - prev_kpis['units_sold']) / prev_kpis['units_sold']) * 100.0

    return {
        "total_net_sales": total_net,
        "total_gross_sales": total_gross,
        "total_orders": total_distinct_orders,
        "eligible_orders": eligible_distinct_orders,
        "aov": aov,
        "units_sold": units_sold,
        "return_rate": return_rate,
        "total_profit": total_profit,
        "profit_margin": profit_margin,
        "growth_sales": growth_sales,
        "growth_orders": growth_orders,
        "growth_aov": growth_aov,
        "growth_units": growth_units,
        "has_cost_data": has_cost
    }

def get_top_selling_products(df: pd.DataFrame, top_n: int = 5) -> pd.DataFrame:
    """
    Ranks products by total net sales. Includes units sold and order count.
    """
    if len(df) == 0:
        return pd.DataFrame(columns=['product_name', 'category', 'net_sales', 'units_sold', 'orders_count'])

    non_cancelled = df[~df['order_status'].isin(['Cancelled', 'Void'])]

    grouped = non_cancelled.groupby(['product_name', 'category']).agg({
        'net_sales': 'sum',
        'quantity': 'sum',
        'order_id': 'nunique'
    }).reset_index()

    grouped.rename(columns={
        'quantity': 'units_sold',
        'order_id': 'orders_count'
    }, inplace=True)

    grouped = grouped.sort_values(by='net_sales', ascending=False).reset_index(drop=True)
    return grouped.head(top_n)

def get_sales_by_category(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregates net sales and order volume across categories.
    """
    if len(df) == 0:
        return pd.DataFrame(columns=['category', 'net_sales', 'percentage_share', 'units_sold'])

    non_cancelled = df[~df['order_status'].isin(['Cancelled', 'Void'])]
    total_revenue = non_cancelled['net_sales'].sum()

    grouped = non_cancelled.groupby('category').agg({
        'net_sales': 'sum',
        'quantity': 'sum'
    }).reset_index()

    grouped.rename(columns={'quantity': 'units_sold'}, inplace=True)
    grouped['percentage_share'] = (grouped['net_sales'] / total_revenue * 100.0) if total_revenue > 0 else 0.0
    grouped = grouped.sort_values(by='net_sales', ascending=False).reset_index(drop=True)
    return grouped

def get_recent_orders(df: pd.DataFrame, limit: int = 8) -> pd.DataFrame:
    """
    Returns recent transaction records sorted by order_date descending.
    """
    if len(df) == 0:
        return pd.DataFrame(columns=['order_id', 'customer_id', 'product_name', 'net_sales', 'order_status', 'order_date'])

    cols = ['order_id', 'customer_id', 'product_name', 'net_sales', 'order_status', 'order_date']
    available_cols = [c for c in cols if c in df.columns]
    return df.sort_values(by='order_date', ascending=False)[available_cols].head(limit)

def get_sales_trend(df: pd.DataFrame, freq: str = "W") -> pd.DataFrame:
    """
    Aggregates sales performance by frequency:
    'D' (Daily), 'W' (Weekly), 'M' (Monthly), 'Q' (Quarterly).
    """
    if len(df) == 0:
        return pd.DataFrame(columns=['period', 'net_sales', 'eligible_orders', 'units_sold'])

    non_cancelled = df[~df['order_status'].isin(['Cancelled', 'Void'])].copy()
    if len(non_cancelled) == 0:
        return pd.DataFrame(columns=['period', 'net_sales', 'eligible_orders', 'units_sold'])

    temp = non_cancelled.set_index('order_date').sort_index()
    trend = temp.resample(freq).agg({
        'net_sales': 'sum',
        'order_id': 'nunique',
        'quantity': 'sum'
    }).reset_index()

    trend.rename(columns={
        'order_date': 'period',
        'order_id': 'eligible_orders',
        'quantity': 'units_sold'
    }, inplace=True)
    return trend

def get_customer_analytics(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Computes customer-level analytics for the Customer Data tab:
    - Unique customer count
    - Average Customer Lifetime Value (LTV)
    - Repeat purchase rate
    - Top VIP customer leaderboard
    """
    if len(df) == 0 or 'customer_id' not in df.columns:
        return {
            "total_customers": 0,
            "repeat_rate": 0.0,
            "avg_ltv": 0.0,
            "top_customers": pd.DataFrame()
        }

    non_cancelled = df[~df['order_status'].isin(['Cancelled', 'Void'])]
    cust_group = non_cancelled.groupby('customer_id').agg({
        'order_id': 'nunique',
        'net_sales': 'sum',
        'quantity': 'sum',
        'category': lambda x: x.mode()[0] if len(x) > 0 else "General",
        'region': lambda x: x.mode()[0] if len(x) > 0 else "Global"
    }).reset_index()

    cust_group.rename(columns={
        'order_id': 'orders_count',
        'net_sales': 'total_spent',
        'quantity': 'units_purchased',
        'category': 'favorite_category'
    }, inplace=True)

    total_customers = len(cust_group)
    repeat_customers = (cust_group['orders_count'] > 1).sum()
    repeat_rate = (repeat_customers / total_customers * 100.0) if total_customers > 0 else 0.0
    avg_ltv = float(cust_group['total_spent'].mean()) if total_customers > 0 else 0.0

    # Assign tiers
    def get_tier(spent):
        if spent >= 1500:
            return "VIP Platinum"
        elif spent >= 800:
            return "Gold Tier"
        else:
            return "Silver Member"

    cust_group['tier'] = cust_group['total_spent'].apply(get_tier)
    top_customers = cust_group.sort_values(by='total_spent', ascending=False).reset_index(drop=True)

    return {
        "total_customers": total_customers,
        "repeat_rate": repeat_rate,
        "avg_ltv": avg_ltv,
        "top_customers": top_customers
    }

def create_new_order_record(
    df: pd.DataFrame,
    customer_id: str,
    product_name: str,
    category: str,
    quantity: int,
    unit_price: float,
    discount_pct: float,
    region: str,
    status: str = "Completed"
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Appends a new order from the Checkout simulator into the dataframe.
    """
    order_seq = len(df) + 10001
    order_id = f"ORD-2026-{order_seq}"
    now = datetime.now()
    
    qty = max(1, int(quantity))
    price = max(0.0, float(unit_price))
    discount = round(price * qty * (discount_pct / 100.0), 2)
    gross_sales = price * qty
    net_sales = max(0.0, gross_sales - discount)
    unit_cost = round(price * 0.55, 2)
    cogs = unit_cost * qty
    profit = net_sales - cogs

    new_row = {
        "order_id": order_id,
        "order_date": now,
        "customer_id": customer_id.strip() or "CUST-NEW",
        "product_id": f"PRD-{hash(product_name) % 1000}",
        "product_name": product_name.strip(),
        "category": category.strip(),
        "quantity": qty,
        "unit_price": price,
        "discount": discount,
        "unit_cost": unit_cost,
        "order_status": status,
        "region": region,
        "gross_sales": gross_sales,
        "net_sales": net_sales,
        "cogs": cogs,
        "gross_profit": profit,
        "year_month": now.strftime("%Y-%m"),
        "date_only": now.date()
    }

    new_df = pd.concat([pd.DataFrame([new_row]), df], ignore_index=True)
    return new_df, new_row
