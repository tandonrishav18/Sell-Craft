"""
Data Engine Module for E-Commerce MIS BI System.
Handles CSV loading, strict schema validation, cleaning, missing-value imputation,
and SQLite persistence.
"""

import os
import sqlite3
from typing import Tuple, List, Optional
import pandas as pd
import numpy as np

from src.config import REQUIRED_COLUMNS, RECOMMENDED_COLUMNS, OPTIONAL_COLUMNS

class DataValidationError(Exception):
    """Custom exception raised when uploaded data fails schema or integrity constraints."""
    pass

def load_csv(file_or_path) -> pd.DataFrame:
    """
    Safely load CSV data with multiple encoding fallbacks and robust error handling.
    """
    try:
        if isinstance(file_or_path, str):
            if not os.path.exists(file_or_path):
                raise FileNotFoundError(f"File not found: {file_or_path}")
            df = pd.read_csv(file_or_path, encoding='utf-8')
        else:
            df = pd.read_csv(file_or_path, encoding='utf-8')
    except UnicodeDecodeError:
        if isinstance(file_or_path, str):
            df = pd.read_csv(file_or_path, encoding='latin1')
        else:
            file_or_path.seek(0)
            df = pd.read_csv(file_or_path, encoding='latin1')
    except Exception as e:
        raise DataValidationError(f"Failed to read CSV file: {str(e)}")

    return df

def validate_schema(df: pd.DataFrame) -> Tuple[bool, List[str], List[str], List[str]]:
    """
    Validates dataframe columns against required, recommended, and optional schemas.
    Returns:
        is_valid: bool
        missing_required: list of required columns not present
        missing_recommended: list of recommended columns not present
        warnings: list of validation messages
    """
    cols = set(df.columns.str.lower().str.strip())
    missing_required = [col for col in REQUIRED_COLUMNS if col.lower() not in cols]
    missing_recommended = [col for col in RECOMMENDED_COLUMNS if col.lower() not in cols]
    warnings = []

    if missing_required:
        warnings.append(f"Missing mandatory columns: {', '.join(missing_required)}")

    if missing_recommended:
        warnings.append(f"Missing recommended columns for full analysis: {', '.join(missing_recommended)}")

    if len(df) == 0:
        warnings.append("Dataset is empty (0 records).")

    is_valid = len(missing_required) == 0 and len(df) > 0
    return is_valid, missing_required, missing_recommended, warnings

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans raw dataframe:
    - Normalizes column names
    - Converts dates with error coercion
    - Validates and sanitizes numeric values
    - Imputes missing categories and statuses
    - Calculates gross_sales, net_sales, cogs, profit
    """
    cleaned = df.copy()
    # Normalize headers: lower case, strip whitespace, replace spaces with underscores
    cleaned.columns = cleaned.columns.str.strip().str.lower().str.replace(' ', '_')

    # Parse order_date
    if 'order_date' in cleaned.columns:
        cleaned['order_date'] = pd.to_datetime(cleaned['order_date'], errors='coerce')
        # Drop rows where date is NaT
        cleaned = cleaned.dropna(subset=['order_date'])

    # Ensure order_id is string
    if 'order_id' in cleaned.columns:
        cleaned['order_id'] = cleaned['order_id'].astype(str).str.strip()
    else:
        cleaned['order_id'] = [f"ORD-{i+1}" for i in range(len(cleaned))]

    # Numeric validations
    cleaned['quantity'] = pd.to_numeric(cleaned['quantity'], errors='coerce').fillna(1)
    cleaned['quantity'] = cleaned['quantity'].apply(lambda x: max(1, int(round(x))))

    cleaned['unit_price'] = pd.to_numeric(cleaned['unit_price'], errors='coerce').fillna(0.0)
    cleaned['unit_price'] = cleaned['unit_price'].apply(lambda x: max(0.0, float(x)))

    if 'discount' in cleaned.columns:
        cleaned['discount'] = pd.to_numeric(cleaned['discount'], errors='coerce').fillna(0.0)
        cleaned['discount'] = cleaned['discount'].apply(lambda x: max(0.0, float(x)))
    else:
        cleaned['discount'] = 0.0

    # Categorical handling
    if 'category' not in cleaned.columns:
        cleaned['category'] = "General"
    else:
        cleaned['category'] = cleaned['category'].fillna("Uncategorized").astype(str).str.strip()

    if 'product_name' not in cleaned.columns:
        if 'product_id' in cleaned.columns:
            cleaned['product_name'] = cleaned['product_id'].astype(str)
        else:
            cleaned['product_name'] = "Standard Item"
    else:
        cleaned['product_name'] = cleaned['product_name'].fillna("Unnamed Product").astype(str).str.strip()

    if 'order_status' not in cleaned.columns:
        cleaned['order_status'] = "Completed"
    else:
        cleaned['order_status'] = cleaned['order_status'].fillna("Completed").astype(str).str.strip().str.capitalize()

    if 'customer_id' not in cleaned.columns:
        cleaned['customer_id'] = "ANON-GUEST"
    else:
        cleaned['customer_id'] = cleaned['customer_id'].fillna("ANON-GUEST").astype(str).str.strip()

    if 'region' not in cleaned.columns:
        cleaned['region'] = "Global"
    else:
        cleaned['region'] = cleaned['region'].fillna("Other").astype(str).str.strip()

    # Financial metric calculations per MIS Report definitions
    cleaned['gross_sales'] = cleaned['quantity'] * cleaned['unit_price']
    # Net sales cannot be negative
    cleaned['net_sales'] = (cleaned['gross_sales'] - cleaned['discount']).clip(lower=0.0)

    # Unit cost and Profitability
    if 'unit_cost' in cleaned.columns:
        cleaned['unit_cost'] = pd.to_numeric(cleaned['unit_cost'], errors='coerce')
        # Compute cogs only where unit_cost is not null and positive
        cleaned['cogs'] = cleaned['quantity'] * cleaned['unit_cost']
        cleaned['gross_profit'] = cleaned['net_sales'] - cleaned['cogs']
    else:
        cleaned['unit_cost'] = np.nan
        cleaned['cogs'] = np.nan
        cleaned['gross_profit'] = np.nan

    # Add helper date parts for analytics
    cleaned['year_month'] = cleaned['order_date'].dt.to_period('M').astype(str)
    cleaned['date_only'] = cleaned['order_date'].dt.date

    return cleaned

def persist_to_sqlite(df: pd.DataFrame, db_path: str = "ecommerce_bi.db", table_name: str = "orders"):
    """
    Persists cleaned records to SQLite for structured querying and MIS audit compliance.
    """
    conn = sqlite3.connect(db_path)
    # Convert dates to string for sqlite compatibility
    export_df = df.copy()
    if 'order_date' in export_df.columns:
        export_df['order_date'] = export_df['order_date'].astype(str)
    export_df.to_sql(table_name, conn, if_exists='replace', index=False)
    conn.commit()
    conn.close()

