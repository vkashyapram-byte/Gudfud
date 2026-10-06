import os
import sys
import time
import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

# Ensure src is in the python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.models import ProductVariant, LabelVersion, Product, Brand

DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://postgres.cynbftllkqcwslnnvydu:JYavQICA4BGECz6G@aws-0-ap-southeast-2.pooler.supabase.com:6543/postgres")
engine = create_engine(DATABASE_URL)

session_req = requests.Session()
session_req.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
})

import urllib.parse
from bs4 import BeautifulSoup
import re

def get_image_url(product_name, brand_name):
    # Enforce strictly Indian grocery results
    query = f"{brand_name} {product_name} India grocery OR bigbasket OR jiomart".strip()
    url = f"https://www.bing.com/images/async?q={urllib.parse.quote(query)}&first=0&count=1"
    
    try:
        response = session_req.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        for a in soup.find_all('a', class_='iusc'):
            m = re.search(r'"murl":"(.*?)"', a.get('m', ''))
            if m:
                return m.group(1)
    except Exception as e:
        print(f"Error fetching image for {query}: {e}")
    return None

def fetch_images():
    print("Starting image fetch from Open Food Facts...")
    with Session(engine) as session:
        # Get labels without images
        labels_without_images = session.query(LabelVersion).filter(
            (LabelVersion.label_image_id == None) | 
            (LabelVersion.label_image_id == "") |
            (LabelVersion.label_image_id.like("%wikipedia.org%"))
        ).all()
        
        print(f"Found {len(labels_without_images)} products missing images.")
        
        updated_count = 0
        for i, label in enumerate(labels_without_images):
            # Join variant -> product -> brand
            variant = session.query(ProductVariant).filter(ProductVariant.id == label.variant_id).first()
            if not variant: continue
            product = session.query(Product).filter(Product.id == variant.product_id).first()
            if not product: continue
            brand = session.query(Brand).filter(Brand.id == product.brand_id).first()
            
            brand_name = brand.name if brand else ""
            product_name = product.canonical_name
            
            print(f"[{i+1}/{len(labels_without_images)}] Fetching image for: {brand_name} {product_name}")
            
            image_url = get_image_url(product_name, brand_name)
            if image_url:
                label.label_image_id = image_url
                updated_count += 1
                print(f"  -> Found: {image_url}")
            else:
                print(f"  -> No image found")
                
            # Commit periodically
            if (i + 1) % 20 == 0:
                session.commit()
                
            # Rate limiting
            time.sleep(1)
            
        session.commit()
        print(f"Finished! Successfully added images to {updated_count} products.")

if __name__ == "__main__":
    fetch_images()
