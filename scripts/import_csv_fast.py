import os
import sys
import uuid
import csv
import re
from datetime import datetime, timezone
import urllib.parse

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from src.models import (
    Brand, Category, Market, Product, ProductVariant, 
    LabelVersion, Rating, MethodologyVersion, NutritionFacts,
    Ingredient, LabelIngredient
)
from scripts.import_csv import seed_canonical_ingredients, get_or_create, parse_float, clean_ingredient_text, extract_percent, slugify

def import_csv_data():
    print("Starting fast CSV import...")
    now = datetime.now(timezone.utc)
    DATABASE_URL = os.environ.get("DATABASE_URL")
    engine = create_engine(DATABASE_URL)
    
    with open('products.csv', mode='r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        
    with Session(engine) as session:
        canonical_map = seed_canonical_ingredients(session)
        market_in, _ = get_or_create(session, Market, defaults={"name": "India"}, country_code="IN")
        methodology, _ = get_or_create(
            session, MethodologyVersion, 
            defaults={"name": "Automated Nutrition Scoring", "rules": {"base": 100}, "effective_from": now, "reviewer": "System Admin"}, 
            version="v2.0"
        )
        session.flush()

        # FETCH ALL GTINS TO AVOID N+1 SELECTS
        existing_gtins = {v.gtin for v in session.query(ProductVariant.gtin).all()}
        print(f"Found {len(existing_gtins)} existing variants in DB.")

        inserted_count = 0
        for idx, row in enumerate(rows):
            product_name = row.get("Item name", "").strip()
            brand_name = row.get("Brand_Name", "").strip()
            if not product_name: continue

            gtin = f"CSV-{idx}-{slugify(brand_name)}-{slugify(product_name)}"[:100]
            if gtin in existing_gtins:
                continue

            print(f"[{idx+1}/{len(rows)}] Processing {product_name}...")
            brand_slug = slugify(brand_name) or f"brand-{uuid.uuid4().hex[:8]}"
            cat_name = row.get("Category", "").strip() or "General Food"
            cat_slug = slugify(cat_name) or f"cat-{uuid.uuid4().hex[:8]}"
            product_slug = slugify(f"{brand_name} {product_name}")[:100] or f"prod-{uuid.uuid4().hex[:8]}"
            
            brand, _ = get_or_create(session, Brand, defaults={"name": brand_name}, slug=brand_slug)
            category, _ = get_or_create(session, Category, defaults={"name": cat_name}, slug=cat_slug)
            product, _ = get_or_create(session, Product, defaults={"brand_id": brand.id, "category_id": category.id, "canonical_name": product_name}, slug=product_slug)
            
            variant = ProductVariant(product_id=product.id, market_id=market_in.id, gtin=gtin)
            session.add(variant)
            session.flush()

            ingredients_text = row.get("Ingredients", "")
            label = LabelVersion(variant_id=variant.id, version_no=1, ingredients_raw=ingredients_text, label_image_id=None, captured_at=now, review_status="published")
            session.add(label)
            session.flush()

            raw_ings = [i.strip() for i in ingredients_text.replace("(", ",").replace(")", ",").replace(".", "").split(",")]
            parsed_ings = [(i, extract_percent(i)) for i in raw_ings if i and len(i) >= 2]
            seen_mapped, seen_texts, unique_ings = set(), set(), []
            for raw_ing_text, percent in parsed_ings:
                lower_ing = raw_ing_text.lower().strip()
                mapped_ing_id = next((can_ing.id for k, can_ing in canonical_map.items() if k in lower_ing), None)
                if mapped_ing_id and mapped_ing_id in seen_mapped: continue
                if lower_ing in seen_texts: continue
                if mapped_ing_id: seen_mapped.add(mapped_ing_id)
                seen_texts.add(lower_ing)
                unique_ings.append((clean_ingredient_text(raw_ing_text)[:255], percent, mapped_ing_id))

            for pos, (clean_name, percent, mapped_ing_id) in enumerate(unique_ings, 1):
                session.add(LabelIngredient(label_version_id=label.id, ingredient_id=mapped_ing_id, label_text=clean_name, position=pos, declared_percent=percent))

            basis_qty = parse_float(row.get("Serving_Size_g", 100)) or 100
            session.add(NutritionFacts(
                label_version_id=label.id, basis_quantity=basis_qty, basis_unit="g",
                energy=parse_float(row.get("Calories_kcal")), fat=parse_float(row.get("Total_Fat_g")),
                saturated_fat=parse_float(row.get("Saturated_Fat_g")), trans_fat=parse_float(row.get("Trans_Fat_g")),
                carbohydrate=parse_float(row.get("Carbohydrates_g")), sugars=parse_float(row.get("Sugar_g")),
                protein=parse_float(row.get("Proteins_g")), sodium=parse_float(row.get("Sodium_mg")), fibre=parse_float(row.get("Dietary_Fiber_g"))
            ))
            
            sugars, sat_fat, sodium = parse_float(row.get("Sugar_g")) or 0, parse_float(row.get("Saturated_Fat_g")) or 0, parse_float(row.get("Sodium_mg")) or 0
            nutrition_score = max(0, 60 - (10 if sugars > 10 else 0) - (10 if sat_fat > 5 else 0) - (10 if sodium > 100 else 0))
            ingredient_score, context_score = 25, 15
            score = nutrition_score + ingredient_score + context_score
            band = "Favorable" if score >= 80 else "Mostly favorable" if score >= 60 else "Mixed" if score >= 40 else "Less favorable" if score >= 20 else "Least favorable"
            
            session.add(Rating(label_version_id=label.id, methodology_version_id=methodology.id, total_score=score, nutrition_score=nutrition_score, ingredient_score=ingredient_score, context_score=context_score, band=band, confidence_grade="C", explanation={"summary": "Automated scoring based on provided CSV data."}, calculated_at=now))
            
            if inserted_count % 50 == 0: session.commit()
            inserted_count += 1
            
        session.commit()
        print(f"Success! Imported {inserted_count} products.")

if __name__ == "__main__": import_csv_data()
