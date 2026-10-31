"""
Automated Unit Tests for E-Commerce MIS BI Analytics Engine.
Verifies KPI arithmetic, schema integrity, zero denominator guards,
cancellation handling, and category aggregation per the MIS Project Report Testing Plan.
"""

import unittest
import os
import sys
from datetime import datetime

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd
import numpy as np

from src.data_engine import validate_schema, clean_data, DataValidationError
from src.analytics import calculate_kpis, get_sales_by_category, get_top_selling_products, get_sales_trend

class TestMISAnalytics(unittest.TestCase):

    def setUp(self):
        # Deterministic sample dataset with known ground truth
        self.sample_data = pd.DataFrame([
            {
                "order_id": "ORD-001",
                "order_date": "2026-01-10 10:00:00",
                "customer_id": "C-101",
                "product_name": "Pro Headphones",
                "category": "Audio",
                "quantity": 2,
                "unit_price": 100.0,
                "discount": 20.0,
                "unit_cost": 50.0,
                "order_status": "Delivered",
                "region": "North America"
            },
            {
                "order_id": "ORD-002",
                "order_date": "2026-01-11 11:30:00",
                "customer_id": "C-102",
                "product_name": "Ergo Mouse",
                "category": "Electronics",
                "quantity": 1,
                "unit_price": 60.0,
                "discount": 0.0,
                "unit_cost": 30.0,
                "order_status": "Completed",
                "region": "Europe"
            },
            {
                "order_id": "ORD-003",
                "order_date": "2026-01-12 14:15:00",
                "customer_id": "C-103",
                "product_name": "Mechanical Keyboard",
                "category": "Electronics",
                "quantity": 1,
                "unit_price": 150.0,
                "discount": 10.0,
                "unit_cost": 70.0,
                "order_status": "Returned",
                "region": "North America"
            },
            {
                "order_id": "ORD-004",
                "order_date": "2026-01-13 16:00:00",
                "customer_id": "C-104",
                "product_name": "Desk Lamp",
                "category": "Home & Office",
                "quantity": 3,
                "unit_price": 40.0,
                "discount": 0.0,
                "unit_cost": 20.0,
                "order_status": "Cancelled",
                "region": "Asia-Pacific"
            }
        ])
        self.cleaned_df = clean_data(self.sample_data)

    def test_schema_validation(self):
        """Test valid dataset schema detection."""
        is_valid, missing_req, missing_rec, warnings = validate_schema(self.sample_data)
        self.assertTrue(is_valid)
        self.assertEqual(len(missing_req), 0)

    def test_missing_required_column(self):
        """Test schema rejection when mandatory column is absent."""
        corrupt_data = self.sample_data.drop(columns=['unit_price'])
        is_valid, missing_req, missing_rec, warnings = validate_schema(corrupt_data)
        self.assertFalse(is_valid)
        self.assertIn('unit_price', missing_req)

    def test_kpi_arithmetic(self):
        """
        Verify exact arithmetic against manual calculations:
        ORD-001: Delivered, Gross = 2*100 = 200, Net = 200-20 = 180, COGS = 2*50 = 100, Profit = 80
        ORD-002: Completed, Gross = 1*60 = 60, Net = 60-0 = 60, COGS = 1*30 = 30, Profit = 30
        ORD-003: Returned, Gross = 1*150 = 150, Net = 150-10 = 140, COGS = 70, Profit = 70
        ORD-004: Cancelled -> Excluded from Net Sales and Eligible Orders
        
        Eligible orders = 3 (ORD-001, ORD-002, ORD-003)
        Total Net Sales = 180 + 60 + 140 = $380.0
        AOV = 380.0 / 3 = $126.6667
        Units Sold = 2 + 1 + 1 = 4
        Total Distinct Orders = 4
        Returned Orders = 1 (ORD-003) -> Return Rate = 1/4 * 100 = 25.0%
        Total Profit = 80 + 30 + 70 = $180.0
        Profit Margin = 180 / 380 * 100 = 47.368%
        """
        kpis = calculate_kpis(self.cleaned_df)
        self.assertEqual(kpis['eligible_orders'], 3)
        self.assertEqual(kpis['total_orders'], 4)
        self.assertAlmostEqual(kpis['total_net_sales'], 380.0, places=2)
        self.assertAlmostEqual(kpis['aov'], 126.67, places=2)
        self.assertEqual(kpis['units_sold'], 4)
        self.assertAlmostEqual(kpis['return_rate'], 25.0, places=2)
        self.assertAlmostEqual(kpis['total_profit'], 180.0, places=2)
        self.assertAlmostEqual(kpis['profit_margin'], 47.37, places=2)

    def test_zero_denominator_guard(self):
        """Test that empty dataframes gracefully return zeros without division by zero."""
        empty_df = pd.DataFrame(columns=self.cleaned_df.columns)
        kpis = calculate_kpis(empty_df)
        self.assertEqual(kpis['eligible_orders'], 0)
        self.assertEqual(kpis['total_net_sales'], 0.0)
        self.assertEqual(kpis['aov'], 0.0)
        self.assertEqual(kpis['return_rate'], 0.0)
        self.assertIsNone(kpis['total_profit'])

    def test_category_aggregation_sum(self):
        """Verify that category breakdown sum equals total net sales."""
        cat_df = get_sales_by_category(self.cleaned_df)
        kpis = calculate_kpis(self.cleaned_df)
        self.assertAlmostEqual(cat_df['net_sales'].sum(), kpis['total_net_sales'], places=2)
        self.assertAlmostEqual(cat_df['percentage_share'].sum(), 100.0, places=2)

    def test_cost_missing_handling(self):
        """Test dataset without unit_cost safely sets profit and margin to None."""
        data_no_cost = self.sample_data.drop(columns=['unit_cost'])
        cleaned_no_cost = clean_data(data_no_cost)
        kpis = calculate_kpis(cleaned_no_cost)
        self.assertFalse(kpis['has_cost_data'])
        self.assertIsNone(kpis['total_profit'])
        self.assertIsNone(kpis['profit_margin'])

if __name__ == "__main__":
    unittest.main()
