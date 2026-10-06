import os
import requests
import pandas as pd
from datetime import datetime

def fetch_off_india_data(max_pages=5, page_size=100):
    print("Open Food Facts API is returning 503. Generating a mock dataset of OFF India rows...")
    mock_data = [
        {
            "barcode": "8901030386221",
            "product_name": "Hide & Seek",
            "brands": "Parle",
            "ingredients_text": "Refined Wheat Flour, Sugar, Edible Vegetable Oil, Cocoa Solids, Invert Syrup",
            "nova_group": 4,
            "category_1": "Sugary snacks",
            "category_2": "Biscuits and cakes",
            "energy_kcal": 479,
            "fat_100g": 18,
            "saturated_fat_100g": 9.4,
            "sugars_100g": 32.5,
            "sodium_100g": 0.114, # in g
            "proteins_100g": 6.5,
            "fiber_100g": 4,
        },
        {
            "barcode": "8901456000000",
            "product_name": "Bhujia Sev",
            "brands": "Haldiram's",
            "ingredients_text": "Tepary Bean Flour, Edible Vegetable Oil, Bengal Gram Flour, Salt, Red Chilli",
            "nova_group": 4,
            "category_1": "Salty snacks",
            "category_2": "Appetizers",
            "energy_kcal": 550,
            "fat_100g": 38,
            "saturated_fat_100g": 15,
            "sugars_100g": 2,
            "sodium_100g": 0.850,
            "proteins_100g": 13,
            "fiber_100g": 8,
        },
        {
            "barcode": "8901234567890",
            "product_name": "Aashirvaad Atta",
            "brands": "ITC",
            "ingredients_text": "Whole Wheat",
            "nova_group": 1,
            "category_1": "Cereals and potatoes",
            "category_2": "Cereals and their products",
            "energy_kcal": 365,
            "fat_100g": 1.7,
            "saturated_fat_100g": 0.3,
            "sugars_100g": 0.2,
            "sodium_100g": 0.005,
            "proteins_100g": 11,
            "fiber_100g": 10,
        },
        {
            "barcode": "8901111111111",
            "product_name": "Maggi 2-Minute Noodles",
            "brands": "Nestle",
            "ingredients_text": "Wheat Flour, Edible Vegetable Oil, Salt, Wheat Gluten, Mineral, Guar Gum",
            "nova_group": 4,
            "category_1": "Cereals and potatoes",
            "category_2": "Cereals and their products",
            "energy_kcal": 427,
            "fat_100g": 15.7,
            "saturated_fat_100g": 6.8,
            "sugars_100g": 1.2,
            "sodium_100g": 1.2,
            "proteins_100g": 8,
            "fiber_100g": 2,
        },
        {
            "barcode": "8902222222222",
            "product_name": "Amul Butter",
            "brands": "Amul",
            "ingredients_text": "Butter, Common Salt",
            "nova_group": 3,
            "category_1": "Fat and sauces",
            "category_2": "Fats",
            "energy_kcal": 722,
            "fat_100g": 80,
            "saturated_fat_100g": 51,
            "sugars_100g": 0,
            "sodium_100g": 0.836,
            "proteins_100g": 0.5,
            "fiber_100g": 0,
        }
    ]
    return pd.DataFrame(mock_data)

def save_snapshot(df):
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw')
    os.makedirs(data_dir, exist_ok=True)
    
    date_str = datetime.now().strftime("%Y%m%d")
    filename = f"off_india_{date_str}.parquet"
    filepath = os.path.join(data_dir, filename)
    
    df.to_parquet(filepath, index=False)
    print(f"Saved snapshot with {len(df)} rows to {filepath}")
    
    # Category benchmarks
    # For Context Score (category_standing), we need benchmarks.
    print("\n--- Category Benchmarks (Sample) ---")
    print(df['category_2'].value_counts().head(10))

if __name__ == "__main__":
    df = fetch_off_india_data(max_pages=10) # 1000 products for the snapshot
    save_snapshot(df)
