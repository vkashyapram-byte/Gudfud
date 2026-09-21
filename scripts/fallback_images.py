import os
import sys
import requests
from datetime import datetime, timezone
import uuid

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from src.models import Category, Product, ProductVariant, LabelVersion

WIKI_PAGES = {
    "JUICE": "Juice",
    "WAFFLE": "Waffle",
    "SNACKS": "Snack",
    "WAFER": "Wafer",
    "CHOCOLATE": "Chocolate_bar",
    "CAKE": "Cake",
    "BISCUIT": "Biscuit"
}

def get_wiki_image(query):
    url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "prop": "pageimages",
        "format": "json",
        "piprop": "original",
        "titles": query,
        "redirects": 1
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    try:
        data = requests.get(url, params=params, headers=headers).json()
        pages = data["query"]["pages"]
        for page_id, page_info in pages.items():
            if "original" in page_info:
                return page_info["original"]["source"]
    except Exception as e:
        print(f"Error fetching wiki image for {query}:", e)
    return None

def set_fallback_images():
    print("Assigning fallback images for products without images...")
    DATABASE_URL = os.environ.get("DATABASE_URL")
    if not DATABASE_URL:
        DATABASE_URL = "postgresql://postgres.cynbftllkqcwslnnvydu:JYavQICA4BGECz6G@aws-0-ap-southeast-2.pooler.supabase.com:5432/postgres"
    engine = create_engine(DATABASE_URL)
    
    # Pre-fetch and cache wiki images
    category_images = {}
    for cat_name, wiki_query in WIKI_PAGES.items():
        img_url = get_wiki_image(wiki_query)
        if img_url:
            category_images[cat_name] = img_url
            print(f"Loaded fallback for {cat_name}: {img_url}")

    with Session(engine) as session:
        # Find all label versions with missing images
        missing_labels = session.query(LabelVersion).filter(LabelVersion.label_image_id == None).all()
        
        print(f"Found {len(missing_labels)} labels missing images.")
        updated = 0
        
        for label in missing_labels:
            variant = session.query(ProductVariant).filter(ProductVariant.id == label.variant_id).first()
            if not variant: continue
            product = session.query(Product).filter(Product.id == variant.product_id).first()
            if not product: continue
            category = session.query(Category).filter(Category.id == product.category_id).first()
            if not category: continue
            
            cat_name = category.name.strip().upper()
            fallback_url = category_images.get(cat_name)
            
            if fallback_url:
                label.label_image_id = fallback_url
                updated += 1
                
        session.commit()
        print(f"Successfully added fallback images to {updated} products!")

if __name__ == "__main__":
    set_fallback_images()
