import os
import sys
import uuid
import csv
import re
from datetime import datetime, timezone
import urllib.parse
from duckduckgo_search import DDGS

# Ensure src is in the python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from src.models import (
    Brand, Category, Market, Product, ProductVariant, 
    LabelVersion, Rating, MethodologyVersion, NutritionFacts,
    Ingredient, LabelIngredient
)

raw_url = os.getenv("DATABASE_URL", "postgresql://postgres:postgrespassword@localhost:5432/gudfud")
if raw_url.startswith("postgres://"):
    raw_url = raw_url.replace("postgres://", "postgresql://", 1)

parsed = urllib.parse.urlparse(raw_url)
if parsed.query:
    qs = urllib.parse.parse_qsl(parsed.query)
    qs = [(k, v) for k, v in qs if k != 'pgbouncer']
    parsed = parsed._replace(query=urllib.parse.urlencode(qs))
    DATABASE_URL = urllib.parse.urlunparse(parsed)
else:
    DATABASE_URL = raw_url

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

def extract_percent(text):
    match = re.search(r'\((\d+(?:\.\d+)?)\s*%\)', text)
    if match:
        return float(match.group(1))
    return None

def clean_ingredient_text(text):
    # Remove the percentage from the name
    return re.sub(r'\(\d+(?:\.\d+)?\s*%\)', '', text).strip()

def seed_canonical_ingredients(session):
    sugar, _ = get_or_create(session, Ingredient, defaults={
        "canonical_name": "Sugar",
        "ingredient_type": "sweetener",
    }, slug="sugar")
    
    wheat_flour, _ = get_or_create(session, Ingredient, defaults={
        "canonical_name": "Refined Wheat Flour (Maida)",
        "ingredient_type": "flour",
    }, slug="refined-wheat-flour")
    
    palm_oil, _ = get_or_create(session, Ingredient, defaults={
        "canonical_name": "Palm Oil",
        "ingredient_type": "oil",
    }, slug="palm-oil")
    
    session.flush()
    return {
        "sugar": sugar,
        "refined wheat flour": wheat_flour,
        "wheat flour": wheat_flour,
        "maida": wheat_flour,
        "palm oil": palm_oil,
        "edible vegetable oil": palm_oil,
        "edible vegetable fat": palm_oil
    }

def get_image_url(query):
    try:
        ddgs = DDGS()
        results = ddgs.images(query, max_results=1)
        if results:
            return results[0].get('image')
    except Exception as e:
        pass
    return None

def parse_float(val):
    if not val:
        return None
    try:
        # Strip all non-numeric characters except period
        clean_val = re.sub(r'[^\d.]', '', str(val))
        return float(clean_val) if clean_val else None
    except ValueError:
        return None

def import_csv_data():
    print("Starting CSV import...")
    now = datetime.now(timezone.utc)
    
    with open('products.csv', mode='r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        
    with Session(engine) as session:
        try:
            canonical_map = seed_canonical_ingredients(session)
            market_in, _ = get_or_create(session, Market, defaults={"name": "India"}, country_code="IN")
            methodology, _ = get_or_create(
                session, MethodologyVersion, 
                defaults={
                    "name": "Automated Nutrition Scoring", 
                    "rules": {"base": 100}, 
                    "effective_from": now,
                    "reviewer": "System Admin"
                }, 
                version="v2.0"
            )

            inserted_count = 0
            for idx, row in enumerate(rows):
                product_name = row.get("Item name", "").strip()
                brand_name = row.get("Brand_Name", "").strip()
                if not product_name:
                    continue

                gtin = f"CSV-{idx}-{slugify(brand_name)}-{slugify(product_name)}"[:100]
                
                existing_variant = session.query(ProductVariant).filter_by(gtin=gtin).first()
                if existing_variant:
                    continue

                print(f"[{idx+1}/{len(rows)}] Processing {product_name}...")

                brand_slug = slugify(brand_name) or f"brand-{uuid.uuid4().hex[:8]}"
                cat_name = row.get("Category", "").strip() or "General Food"
                cat_slug = slugify(cat_name) or f"cat-{uuid.uuid4().hex[:8]}"
                product_slug = slugify(f"{brand_name} {product_name}")[:100] or f"prod-{uuid.uuid4().hex[:8]}"
                
                brand, _ = get_or_create(session, Brand, defaults={"name": brand_name}, slug=brand_slug)
                category, _ = get_or_create(session, Category, defaults={"name": cat_name}, slug=cat_slug)
                
                product, created = get_or_create(
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

                # Get Image
                image_url = get_image_url(f"{brand_name} {product_name} product packaging india")
                
                ingredients_text = row.get("Ingredients", "")
                
                label = LabelVersion(
                    variant_id=variant.id,
                    version_no=1,
                    ingredients_raw=ingredients_text,
                    label_image_id=image_url,
                    captured_at=now,
                    review_status="published"
                )
                session.add(label)
                session.flush()

                raw_ings = [i.strip() for i in ingredients_text.replace("(", ",").replace(")", ",").replace(".", "").split(",")]
                parsed_ings = [(i, extract_percent(i)) for i in raw_ings if i and len(i) >= 2]

                seen_mapped = set()
                seen_texts = set()
                unique_ings = []
                
                for raw_ing_text, percent in parsed_ings:
                    lower_ing = raw_ing_text.lower().strip()
                    mapped_ing_id = None
                    for keyword, can_ing in canonical_map.items():
                        if keyword in lower_ing:
                            mapped_ing_id = can_ing.id
                            break
                            
                    if mapped_ing_id and mapped_ing_id in seen_mapped:
                        continue
                    if lower_ing in seen_texts:
                        continue
                        
                    if mapped_ing_id:
                        seen_mapped.add(mapped_ing_id)
                    seen_texts.add(lower_ing)
                    
                    clean_name = clean_ingredient_text(raw_ing_text)[:255]
                    unique_ings.append((clean_name, percent, mapped_ing_id))

                position = 1
                for clean_name, percent, mapped_ing_id in unique_ings:
                    li = LabelIngredient(
                        label_version_id=label.id,
                        ingredient_id=mapped_ing_id,
                        label_text=clean_name,
                        position=position,
                        declared_percent=percent
                    )
                    session.add(li)
                    position += 1

                basis_qty = parse_float(row.get("Serving_Size_g", 100))

                nutrition = NutritionFacts(
                    label_version_id=label.id,
                    basis_quantity=basis_qty if basis_qty else 100,
                    basis_unit="g",
                    energy=parse_float(row.get("Calories_kcal")),
                    fat=parse_float(row.get("Total_Fat_g")),
                    saturated_fat=parse_float(row.get("Saturated_Fat_g")),
                    trans_fat=parse_float(row.get("Trans_Fat_g")),
                    carbohydrate=parse_float(row.get("Carbohydrates_g")),
                    sugars=parse_float(row.get("Sugar_g")),
                    protein=parse_float(row.get("Proteins_g")),
                    sodium=parse_float(row.get("Sodium_mg")),
                    fibre=parse_float(row.get("Dietary_Fiber_g"))
                )
                session.add(nutrition)
                
                nutrition_score = 60
                sugars = parse_float(row.get("Sugar_g")) or 0
                sat_fat = parse_float(row.get("Saturated_Fat_g")) or 0
                sodium = parse_float(row.get("Sodium_mg")) or 0
                
                if sugars > 10: nutrition_score -= 10
                if sat_fat > 5: nutrition_score -= 10
                if sodium > 100: nutrition_score -= 10
                nutrition_score = max(0, nutrition_score)

                ingredient_score = 25
                context_score = 15
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
                    confidence_grade="C",
                    explanation={"summary": "Automated scoring based on provided CSV data."},
                    calculated_at=now
                )
                session.add(rating)
                
                if idx % 50 == 0:
                    session.commit()
                    
                inserted_count += 1
                
            session.commit()
            print(f"Success! Imported {inserted_count} products.")
        except Exception as e:
            session.rollback()
            print(f"Error during import: {e}")
            raise e

if __name__ == "__main__":
    import_csv_data()
