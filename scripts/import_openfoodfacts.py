import os
import sys
import uuid
import json
import urllib.request
import urllib.parse
import re
from datetime import datetime, timezone

# Ensure src is in the python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from src.models import (
    Brand, Category, Market, Product, ProductVariant, 
    LabelVersion, Rating, MethodologyVersion, NutritionFacts
)

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is required")

if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)

def get_or_create(session, model, defaults=None, **kwargs):
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance, False
    params = dict((k, v) for k, v in kwargs.items())
    params.update(defaults or {})
    instance = model(**params)
    session.add(instance)
    session.flush()
    return instance, True

def slugify(text: str) -> str:
    text = text.lower()
    return re.sub(r'[^a-z0-9]+', '-', text).strip('-')

def fetch_openfoodfacts_products():
    search_terms = ["maggi", "haldiram", "britannia", "parle", "amul", "kurkure", "lays", "aashirvaad", "mtr", "sunfeast"]
    products = []
    
    for term in search_terms:
        # Fetch highly popular products matching staple Indian terms to ensure high-quality verifiable data
        url = f"https://world.openfoodfacts.org/api/v2/search?search_terms={urllib.parse.quote(term)}&countries_tags=en:india&fields=code,brands,product_name,ingredients_text,nutriments,categories_tags,image_url&page_size=3&sort_by=popularity"
        req = urllib.request.Request(url, headers={'User-Agent': 'GudFud-Data-Importer/1.0'})
        import ssl
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        try:
            with urllib.request.urlopen(req, context=ctx) as response:
                data = json.loads(response.read().decode('utf-8'))
                products.extend(data.get('products', []))
        except Exception as e:
            print(f"Warning: Failed to fetch '{term}' - {e}")
            
    return products[:20]  # Return up to 20 Indian products

def import_data():
    print("Fetching verifiable real-world products from Open Food Facts...")
    products_data = fetch_openfoodfacts_products()
    
    with Session(engine) as session:
        try:
            now = datetime.now(timezone.utc)
            
            market_in, _ = get_or_create(session, Market, defaults={"name": "India"}, country_code="IN")
            methodology, _ = get_or_create(
                session, MethodologyVersion, 
                defaults={
                    "name": "OFF Automated Nutrition Scoring", 
                    "rules": {"base": 100}, 
                    "effective_from": now,
                    "reviewer": "System Admin"
                }, 
                version="v2.0"
            )

            inserted_count = 0
            for item in products_data:
                gtin = item.get("code")
                if not gtin:
                    continue
                
                # Idempotency check
                existing_variant = session.query(ProductVariant).filter_by(gtin=gtin).first()
                if existing_variant:
                    print(f"Skipping {gtin} - already exists in database.")
                    continue
                
                brand_name = item.get("brands", "").split(",")[0].strip() or "Generic Brand"
                brand_slug = slugify(brand_name) or f"brand-{uuid.uuid4().hex[:8]}"
                
                cat_tags = item.get("categories_tags", [])
                cat_name = "General Food"
                if cat_tags:
                    cat_name = cat_tags[0].split(":")[-1].replace("-", " ").title()
                cat_slug = slugify(cat_name) or f"cat-{uuid.uuid4().hex[:8]}"
                
                product_name = item.get("product_name", "").strip() or "Unnamed Product"
                product_slug = slugify(f"{brand_name} {product_name} {gtin}")
                
                ingredients = item.get("ingredients_text", "Ingredients not provided by manufacturer.")
                nutriments = item.get("nutriments", {})

                image_url = item.get("image_url")
                
                brand, _ = get_or_create(session, Brand, defaults={"name": brand_name}, slug=brand_slug)
                category, _ = get_or_create(session, Category, defaults={"name": cat_name}, slug=cat_slug)
                
                product, _ = get_or_create(
                    session, Product,
                    defaults={"brand_id": brand.id, "category_id": category.id, "canonical_name": product_name},
                    slug=product_slug
                )
                
                variant = ProductVariant(
                    product_id=product.id,
                    market_id=market_in.id,
                    gtin=gtin
                )
                session.add(variant)
                session.flush()
                
                label = LabelVersion(
                    variant_id=variant.id,
                    version_no=1,
                    ingredients_raw=ingredients,
                    label_image_id=image_url,
                    captured_at=now,
                    review_status="published"  # Strict auto-publish parameter
                )
                session.add(label)
                session.flush()

                nutrition = NutritionFacts(
                    label_version_id=label.id,
                    basis_quantity=100,
                    basis_unit="g",
                    energy=nutriments.get("energy-kcal_100g"),
                    fat=nutriments.get("fat_100g"),
                    saturated_fat=nutriments.get("saturated-fat_100g"),
                    carbohydrate=nutriments.get("carbohydrates_100g"),
                    sugars=nutriments.get("sugars_100g"),
                    protein=nutriments.get("proteins_100g"),
                    sodium=nutriments.get("sodium_100g")
                )
                session.add(nutrition)
                
                # Objective scoring metric logic per PRD
                nutrition_score = 60
                if nutriments.get("sugars_100g", 0) > 10: nutrition_score -= 10
                if nutriments.get("saturated-fat_100g", 0) > 5: nutrition_score -= 10
                if nutriments.get("sodium_100g", 0) > 1: nutrition_score -= 10
                nutrition_score = max(0, nutrition_score)

                ingredient_score = 25  # Baseline for MVP
                context_score = 15     # Baseline for MVP
                
                score = nutrition_score + ingredient_score + context_score
                
                if score >= 80: band = "Favorable"
                elif score >= 60: band = "Mostly favorable"
                elif score >= 40: band = "Mixed"
                elif score >= 20: band = "Less favorable"
                else: band = "Least favorable"
                
                rating = Rating(
                    label_version_id=label.id,
                    methodology_version_id=methodology.id,
                    total_score=score,
                    nutrition_score=nutrition_score,
                    ingredient_score=ingredient_score,
                    context_score=context_score,
                    band=band,
                    confidence_grade="C",  # Provisional, per PRD for automated imports
                    explanation={"summary": "Automated scoring based on 100g nutritional profile from Open Food Facts."},
                    calculated_at=now
                )
                session.add(rating)
                inserted_count += 1
                
            session.commit()
            print(f"Success! Imported and published {inserted_count} new staple products.")
        except Exception as e:
            session.rollback()
            print(f"Error during import. Rolled back transaction safely: {e}")
            raise e

if __name__ == "__main__":
    import_data()
