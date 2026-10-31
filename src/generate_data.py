"""
Script to generate realistic demonstration dataset for E-Commerce MIS BI System.
Outputs data/ecommerce_demo_data.csv adhering to Appendix A of MIS project report.
"""

import os
import random
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

def generate_demo_dataset(output_path: str, num_records: int = 750, seed: int = 42):
    random.seed(seed)
    np.random.seed(seed)

    products = [
        {"id": "PRD-E101", "name": "AcousticPro Wireless Headphones", "category": "Audio", "price": 189.0, "cost": 92.0},
        {"id": "PRD-E102", "name": "UltraView 34-inch Curved Monitor", "category": "Electronics", "price": 499.0, "cost": 295.0},
        {"id": "PRD-E103", "name": "KeyCraft RGB Mechanical Keyboard", "category": "Electronics", "price": 129.0, "cost": 58.0},
        {"id": "PRD-H201", "name": "ErgoPeak Executive Mesh Chair", "category": "Home & Office", "price": 329.0, "cost": 175.0},
        {"id": "PRD-H202", "name": "AromaMist Ultrasonic Diffuser", "category": "Home & Office", "price": 49.0, "cost": 18.0},
        {"id": "PRD-H203", "name": "Artisan Ceramic Pour-Over Kettle", "category": "Home & Office", "price": 68.0, "cost": 26.0},
        {"id": "PRD-A301", "name": "Nomad Vintage Leather Backpack", "category": "Accessories", "price": 149.0, "cost": 65.0},
        {"id": "PRD-A302", "name": "Titanium Polarized Sunglasses", "category": "Accessories", "price": 119.0, "cost": 42.0},
        {"id": "PRD-A303", "name": "HydroShield Insulated Flask 1L", "category": "Accessories", "price": 38.0, "cost": 14.0},
        {"id": "PRD-C401", "name": "EcoThread Organic Heavy Hoodie", "category": "Apparel", "price": 85.0, "cost": 32.0},
        {"id": "PRD-C402", "name": "Merino Wool Thermal Crewneck", "category": "Apparel", "price": 95.0, "cost": 41.0},
        {"id": "PRD-W501", "name": "PulseTrack Smart GPS Watch", "category": "Wearables", "price": 229.0, "cost": 110.0},
    ]

    customers = [f"CUST-{random.randint(1000, 9999)}" for _ in range(160)]
    regions = ["North America", "Europe", "Asia-Pacific", "Latin America"]
    region_weights = [0.45, 0.30, 0.18, 0.07]
    statuses = ["Delivered", "Completed", "Processing", "Pending", "Returned", "Cancelled"]
    status_weights = [0.58, 0.22, 0.08, 0.05, 0.04, 0.03]

    start_date = datetime(2025, 10, 1)
    end_date = datetime(2026, 10, 25)
    total_days = (end_date - start_date).days

    records = []
    order_seq = 10001

    for _ in range(num_records):
        order_seq += 1
        order_id = f"ORD-2026-{order_seq}"
        
        # Biased date distribution to simulate business growth over the year
        day_offset = int(np.random.beta(a=2.0, b=1.5) * total_days)
        order_date = start_date + timedelta(days=day_offset, hours=random.randint(8, 22), minutes=random.randint(0, 59))
        
        prod = random.choice(products)
        customer_id = random.choice(customers)
        region = random.choices(regions, weights=region_weights)[0]
        status = random.choices(statuses, weights=status_weights)[0]
        
        # Quantity
        qty = random.choices([1, 2, 3, 4], weights=[0.72, 0.20, 0.06, 0.02])[0]
        unit_price = prod["price"]
        unit_cost = prod["cost"]
        
        # Line discount (occasional promotion 0%, 5%, 10%, 15%)
        disc_pct = random.choices([0.0, 0.05, 0.10, 0.15], weights=[0.60, 0.20, 0.15, 0.05])[0]
        discount = round(unit_price * qty * disc_pct, 2)
        
        records.append({
            "order_id": order_id,
            "order_date": order_date.strftime("%Y-%m-%d %H:%M:%S"),
            "customer_id": customer_id,
            "product_id": prod["id"],
            "product_name": prod["name"],
            "category": prod["category"],
            "quantity": qty,
            "unit_price": unit_price,
            "discount": discount,
            "unit_cost": unit_cost,
            "order_status": status,
            "region": region
        })

    # Sort chronologically
    records.sort(key=lambda x: x["order_date"])

    df = pd.DataFrame(records)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Generated {len(df)} records at {output_path}")

if __name__ == "__main__":
    out_file = r"F:\MIS PROJ\data\ecommerce_demo_data.csv"
    generate_demo_dataset(out_file)

