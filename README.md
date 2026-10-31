# SellCraft — Business Intelligence and Analytics System for E-Commerce Management Decision-Making

### Management Information Systems (MIS) Course Project
**Student:** Rishav  
**Registration Number:** RA2311003010921  
**Institution:** SRM Institute of Science and Technology, Kattankulathur  
**Department:** Computing Technologies  
**UI/UX Design Reference:** [SellCraft E-Commerce Dashboard (Behance Case Study 241220463)](https://www.behance.net/gallery/241220463/E-Commerce-Dashboard-UI-UX-Design)  

---

## 1. Executive Summary

This system delivers a production-grade **Business Intelligence (BI) Decision-Support Platform** engineered specifically to replicate the **SellCraft Behance Case Study** design ([Behance Case Study 241220463](https://www.behance.net/gallery/241220463/E-Commerce-Dashboard-UI-UX-Design)):
- **Ultra-Sleek Top Navigation Bar:** Slim, compact header with `SellCraft` brand logo, active rounded black pill on selected tab, clean grey inactive tabs, Settings button (`⚙️ Settings`), and interactive action buttons (`💬` AI Assistant, `🔔` Notifications, `👤` Profile). No tabs or elements overflow outside screen boundaries.
- **Dedicated Interactive Pages (All Buttons & Tabs Fully Functional):**
  1. **Overview:** The executive BI command center featuring:
     - *Total Sales Card:* Large `$148.3k+`, green comparison pill (`+8.9% +$30,456 This Month`), smooth sparkline with `-17.4%` badge, and three sub-cards: `Total Orders` (with `↗`), `Total Cancel Orders` (with `↗`), and `Total Units Sold` (with `↗`).
     - *Sales Heatmap:* 4x5 hourly-weekly matrix with purple gradient shades and textured striped cells.
     - *Top Countries by Order:* Flag badges and purple progress bars for UK, Germany, Portugal, France, and US.
     - *Top Selling Product Table:* Multi-column ledger with product icons, SKU codes, order volume, unit prices, and status badges (`● Available` / `● Out Of Stock`).
     - *Analyses Multi-Line Spline Chart:* Multi-curve smooth area chart with Plotly curves for Total Order (purple), Total Activity (coral), Cancel Order (amber), and interactive hover tooltips.
  2. **Product (Catalog & Inventory):** Active SKU catalog with search, category filtering, stock availability filter, summary KPI boxes, stock status pills, and an interactive "➕ Add New Product" modal that saves directly to SQLite!
  3. **Order (Fulfillment & Ledger):** Complete transactional ledger with status filtering (`Completed`, `Pending`, `Cancelled`, `Returned`), Order ID search, live order status updater that persists to SQLite in real time, and instant CSV export!
  4. **Customer Data (LTV & VIP Cohorts):** Customer intelligence metrics (Total Customers, 96.2% Repeat Rate, $950.49 Average LTV), VIP Customer Leaderboard with RFM tiers (`VIP Platinum`, `Gold Tier`, `Silver Member`), and horizontal buyer spend distribution chart.
  5. **Checkout (Interactive POS Simulator):** Live point-of-sale simulator allowing selecting products, setting quantities, applying promo codes (`SELLCRAFT10`, `SRM20`), previewing real-time itemized bills, and placing live orders that write to SQLite and update the overview dashboard live!
  6. **Document (MIS Academic Report):** Full academic report tailored for SRM Institute of Science and Technology (Student: Rishav, Reg. No: RA2311003010921) across 6 comprehensive sections with mathematical formulas, ETL architecture, and database dictionary.
  7. **Settings:** Store currency formatting ($ USD, € EUR, £ GBP, ₹ INR), theme accents, SQLite database diagnostics (row count, file size, integrity check), and a 1-click button to reset the database to baseline demo data.
  8. **AI Assistant & Alerts Popovers:** Interactive query assistant for instant store analysis and live operational store alerts.

---

## 2. Technology Stack

- **Frontend & App Framework:** Streamlit (v1.66+) with pure custom CSS component injection
- **Data Analytics & ETL:** Python 3, Pandas, NumPy
- **Interactive Visualizations:** Plotly Graph Objects (v7.1+)
- **Structured Storage & Persistence:** SQLite (`ecommerce_bi.db`)
- **Unit Testing Framework:** Python `unittest`

---

## 3. Project File Structure

```
F:\MIS PROJ\
│
├── app.py                         # Primary Streamlit application entry point
├── requirements.txt               # Application dependencies
├── README.md                      # Complete system documentation
├── ecommerce_bi.db                # SQLite persistence database
├── dashboard_full_page.png        # Captured application screenshot (UI validation)
│
├── data/
│   └── ecommerce_demo_data.csv    # 750 realistic demonstration transactions (Appendix A compliant)
│
├── src/
│   ├── __init__.py
│   ├── config.py                  # Theme colors, palette, column schemas, KPI definitions
│   ├── data_engine.py             # CSV loading, validation, cleaning, SQLite ingestion
│   ├── analytics.py               # KPI calculation formulas, PoP growth, trends, decision rules
│   ├── visualizations.py          # Plotly Analyses chart and sparkline
│   ├── components.py              # Custom HTML/CSS component generators (cards, nav, tables)
│   ├── pages.py                   # Dedicated modular views for all application tabs
│   └── generate_data.py           # Synthetic demonstration data generator
│
└── tests/
    └── test_analytics.py          # Automated unit test suite (KPI arithmetic, filters, edge cases)
```
```

---

## 4. Setup & Launch Instructions (Windows)

### Step 1: Open Terminal / PowerShell in Project Directory
```powershell
cd "F:\MIS PROJ"
```

### Step 2: Install Required Dependencies
```powershell
pip install -r requirements.txt
```

### Step 3: Run the Automated Unit Tests
```powershell
python "F:\MIS PROJ\tests\test_analytics.py"
```
*Expected output: `Ran 6 tests in 0.063s. OK`*

### Step 4: Launch the Dashboard Application
```powershell
streamlit run app.py
```
*Or:*
```powershell
python -m streamlit run app.py
```

### Step 5: Access the Dashboard
Open your web browser and navigate to:
```
http://localhost:8501
```

---

## 5. Automated Unit Test Verification

```
......
----------------------------------------------------------------------
Ran 6 tests in 0.063s

OK
```

All 6 unit tests pass:
1. `test_schema_validation`: Validates required column detection on valid schema.
2. `test_missing_required_column`: Validates rejection and non-crashing alert when column missing.
3. `test_kpi_arithmetic`: Validates Net Sales, Eligible Orders, AOV, and Margins against exact known arithmetic.
4. `test_zero_denominator_guard`: Tests empty records and zero-division edge cases safely.
5. `test_category_aggregation_sum`: Verifies category breakdown sum equals total net sales (100% share).
6. `test_cost_missing_handling`: Confirms profit and margin gracefully set to None when cost data omitted.
