"""
Configuration module for E-Commerce MIS BI Dashboard.
Defines UI palette for the custom SellCraft design system, KPI definitions, and application settings.
"""

from typing import Dict, List

# Visual Design Theme - SellCraft Custom Design System
THEME = {
    "bg_outer": "#F2F4F7",           # Clean modern light grey dashboard backdrop
    "bg_card": "#FFFFFF",            # Crisp white card surface
    "text_primary": "#111827",       # Bold near-black typography
    "text_secondary": "#6B7280",     # Subtle grey supporting text
    "text_muted": "#9CA3AF",         # Light placeholder/border grey
    "border_color": "#E5E7EB",       # Clean light card borders
    
    # SellCraft Accent Palette
    "accent_purple": "#6366F1",      # Signature vibrant indigo/purple
    "accent_purple_light": "#EEF2FF",
    "accent_purple_deep": "#4F46E5",
    
    "accent_coral": "#F43F5E",       # Coral red for cancel/alert
    "accent_coral_light": "#FFF1F2",
    
    "accent_green": "#10B981",       # Emerald green for positive growth & available status
    "accent_green_light": "#ECFDF5",
    
    "accent_amber": "#F59E0B",       # Golden amber for secondary metrics
    "accent_amber_light": "#FEF3C7",
    
    # Status badges
    "status_available_bg": "#D1FAE5",
    "status_available_text": "#065F46",
    "status_outofstock_bg": "#FEE2E2",
    "status_outofstock_text": "#991B1B",
}

# Required and optional dataset columns matching Appendix A
REQUIRED_COLUMNS: List[str] = [
    "order_id",
    "order_date",
    "quantity",
    "unit_price"
]

RECOMMENDED_COLUMNS: List[str] = [
    "product_id",
    "product_name",
    "category",
    "order_status"
]

OPTIONAL_COLUMNS: List[str] = [
    "customer_id",
    "region",
    "discount",
    "unit_cost"
]

VALID_STATUSES = ["Delivered", "Completed", "Processing", "Pending", "Cancelled", "Returned"]

KPI_DEFINITIONS = {
    "gross_sales": "Gross Line Sales = quantity * unit_price (prior to discount).",
    "net_sales": "Net Sales = Gross Line Sales - Discount. Excludes cancelled orders from completed revenue.",
    "eligible_orders": "Total distinct order IDs excluding cancelled/void transactions.",
    "aov": "Average Order Value = Total Net Sales / Distinct Eligible Orders.",
    "units_sold": "Total sum of quantities sold for non-cancelled orders.",
    "return_rate": "Return Rate (%) = (Returned Orders / Total Orders) * 100.",
    "profit": "Gross Profit = Net Sales - COGS (quantity * unit_cost), calculated when cost data is available.",
    "margin": "Profit Margin (%) = (Gross Profit / Net Sales) * 100."
}
