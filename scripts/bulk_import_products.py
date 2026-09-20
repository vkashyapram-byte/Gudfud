import os
import sys
import uuid
import json
import urllib.request
import urllib.parse
import re
import time
from datetime import datetime, timezone

# Ensure src is in the python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from src.models import (
    Brand, Category, Market, Product, ProductVariant, 
    LabelVersion, Rating, MethodologyVersion, NutritionFacts, LabelIngredient
)
from scripts.import_openfoodfacts import seed_canonical_ingredients

def flatten_ingredients(ing_list):
    flat = []
    for i in ing_list:
        text = i.get("text", "").strip()
        percent = i.get("percent") or i.get("percent_estimate")
        if text and text.lower() not in ('eii', 'e', 'ii', 'mm', '68%'):
            flat.append((text, percent))
        if "ingredients" in i:
            flat.extend(flatten_ingredients(i["ingredients"]))
    return flat

raw_url = os.getenv("DATABASE_URL")
if not raw_url:
    raise ValueError("DATABASE_URL environment variable is required")
if raw_url.startswith("postgres://"):
    raw_url = raw_url.replace("postgres://", "postgresql://", 1)

engine = create_engine(raw_url)

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

PDF_PRODUCTS = [
    "Aachi Biryani Masala", "Aachi Chicken 65 Masala", "Aachi Chicken Masala", "Aachi Chilli Powder", "Aachi Coriander Powder", "Aachi Fish Fry Masala", "Aachi Garam Masala", "Aachi Meat Masala", "Aachi Mutton Masala", "Aachi Pav Bhaji Masala", "Aachi Pepper Powder", "Aachi Rasam Powder", "Aachi Sambar Powder", "Aachi Turmeric Powder", "Aarey Milk", "Aashirvaad Atta", "Aashirvaad Besan", "Aashirvaad Coriander Powder", "Aashirvaad Garam Masala", "Aashirvaad Maida", "Aashirvaad Multigrain Atta", "Aashirvaad Multi Millet Mix", "Aashirvaad Red Chilli Powder", "Aashirvaad Salt", "Aashirvaad Select Sharbati Atta", "Aashirvaad Shudh Chakki Atta", "Aashirvaad Sooji", "Aashirvaad Sugar Release Control Atta", "Aashirvaad Svasti Ghee", "Aashirvaad Turmeric Powder", "Aavin Butter", "Aavin Buttermilk", "Aavin Curd", "Aavin Flavoured Milk", "Aavin Ghee", "Aavin Ice Cream", "Aavin Milk", "Aavin Paneer", "Act II Butter Delite Popcorn", "Act II Golden Sizzle Popcorn", "Act II Instant Popcorn", "Ahmad Tea Earl Grey", "Ahmad Tea English Breakfast", "Ahmad Tea London Afternoon", "Akshayakalpa Organic Butter", "Akshayakalpa Organic Buttermilk", "Akshayakalpa Organic Curd", "Akshayakalpa Organic Ghee", "Akshayakalpa Organic Milk", "Akshayakalpa Organic Paneer", "Alpenliebe Candy", "Alpenliebe Eclairs", "Alpenliebe Gold", "Alpenliebe Juzt Jelly", "Alpenliebe Lollipop", "Alpino Chocolate Peanut Butter", "Alpino High Protein Peanut Butter", "Alpino Natural Peanut Butter", "Alpino Peanut Butter", "American Garden Mayonnaise", "American Garden Peanut Butter", "Amul Amrakhand", "Amul Buffalo Milk", "Amul Butter", "Amul Cassata Ice Cream", "Amul Cheese Cubes", "Amul Cheese Slices", "Amul Cheese Spread", "Amul Chocobar", "Amul Cow Milk", "Amul Dahi", "Amul Dark Chocolate", "Amul Fresh Cream", "Amul Fruit & Nut Chocolate", "Amul Full Cream Milk Powder", "Amul Ghee", "Amul Gold Milk", "Amul Gulab Jamun (Canned)", "Amul Ice Cream", "Amul Kool Cafe", "Amul Kool Elaichi", "Amul Kool Kesar", "Amul Kool Koko", "Amul Kulfi", "Amul Lassi", "Amul Masti Buttermilk", "Amul Masti Spiced Buttermilk", "Amul Milk Chocolate", "Amul Mishti Doi", "Amul Mithai Mate", "Amul Mozzarella Cheese", "Amul Paneer", "Amul Pizza Cheese", "Amul Processed Cheese", "Amul Rasgulla (Canned)", "Amul Sagar Skimmed Milk Powder", "Amul Shakti Milk", "Amul Shrikhand", "Amul Slim n Trim Milk", "Amulspray Infant Milk Food", "Amul Taaza Milk", "Amul Tricone Ice Cream", "Amul Vanilla Magic Ice Cream", "Amulya Dairy Whitener", "Annapurna Atta", "Annapurna Salt", "Anveshan A2 Desi Cow Ghee", "Anveshan Cold Pressed Groundnut Oil", "Anveshan Honey", "Apis Honey", "Appy", "Appy Fizz", "Aquafina Packaged Drinking Water", "Arokya Milk", "Arun Ice Cream",
    "Bagrry's Corn Flakes", "Bagrry's Crunchy Muesli", "Bagrry's Instant Oats", "Bagrry's Rolled Oats", "Bagrry's White Oats", "Balaji Chataka Pataka Wafers", "Balaji Crunchem Masala Munch", "Balaji Masala Masti Wafers", "Balaji Ratlami Sev", "Balaji Sev Murmura", "Balaji Simply Salted Wafers", "Balaji Tomato Twist Wafers", "Bambino Macaroni", "Bambino Roasted Vermicelli", "Bambino Spaghetti", "Bambino Vermicelli", "Barilla Farfalle", "Barilla Fusilli", "Barilla Pasta Sauce Basilico", "Barilla Penne Rigate", "Barilla Pesto Genovese", "Barilla Spaghetti", "Bertolli Extra Light Olive Oil", "Bertolli Extra Virgin Olive Oil", "Bikaji Aloo Bhujia", "Bikaji Bhujia", "Bikaji Gulab Jamun (Canned)", "Bikaji Moong Dal", "Bikaji Papad", "Bikaji Rasgulla (Canned)", "Bikaji Soan Papdi", "Bikanervala Aloo Bhujia", "Bikanervala Kaju Katli", "Bikanervala Rasgulla (Canned)", "Bikanervala Soan Papdi", "Bikano Aloo Bhujia", "Bikano Gulab Jamun (Canned)", "Bikano Rasgulla (Canned)", "Bikano Soan Papdi", "Bindu Jeera Masala Soda", "Bingo Mad Angles", "Bingo Mad Angles Achaari Masti", "Bingo Mad Angles Tomato Madness", "Bingo Original Style Chips", "Bingo Tedhe Medhe", "Bingo Yumitos", "Bisleri Club Soda", "Bisleri Limonata", "Bisleri Packaged Drinking Water", "Bisleri Spyci", "Bisleri Vedica Natural Mountain Water", "Blue Tokai Attikan Estate Coffee", "Blue Tokai Cold Brew Coffee", "Blue Tokai Instant Coffee", "Blue Tokai Monsoon Malabar Coffee", "Blue Tokai Vienna Roast Coffee", "B Natural Apple Juice", "B Natural Guava Juice", "B Natural Mango Juice", "B Natural Mixed Fruit Juice", "Boost Health Drink", "Borges Extra Virgin Olive Oil", "Borges Pure Olive Oil", "Bovonto", "Bragg Apple Cider Vinegar", "Britannia 50-50 Maska Chaska", "Britannia 50-50 Sweet & Salty", "Britannia Bourbon", "Britannia Cheese Cubes", "Britannia Cheese Slices", "Britannia Cheese Spread", "Britannia Croissant", "Britannia Gobbles Cake", "Britannia Good Day Butter Cookies", "Britannia Good Day Cashew Cookies", "Britannia Good Day Choco Chip Cookies", "Britannia Good Day Pista Badam Cookies", "Britannia Jim Jam", "Britannia Little Hearts", "Britannia Marie Gold", "Britannia Milk Bikis", "Britannia Nutri Choice Digestive", "Britannia Nutri Choice Oats Cookies", "Britannia Pure Magic", "Britannia Sandwich Bread", "Britannia Tiger Krunch Chocochips", "Britannia Toastea Premium Bake Rusk", "Britannia Treat Jim Jam", "Britannia Winkin' Cow", "Brooke Bond 3 Roses", "Brooke Bond Red Label", "Brooke Bond Red Label Natural Care", "Brooke Bond Taaza", "Brooke Bond Taj Mahal", "Bru Gold Instant Coffee", "Bru Green Label Coffee", "Bru Instant Coffee", "Bubbaloo Bubble Gum"
]

def fetch_product(term):
    url = f"https://world.openfoodfacts.org/cgi/search.pl?search_terms={urllib.parse.quote(term)}&search_simple=1&action=process&json=1&fields=code,brands,product_name,ingredients_text,ingredients,nutriments,categories_tags,image_url&page_size=1"
    req = urllib.request.Request(url, headers={'User-Agent': 'GudFud-Data-Importer/1.0'})
    
    # Add Basic Auth

    
    import ssl
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    try:
        with urllib.request.urlopen(req, context=ctx) as response:
            data = json.loads(response.read().decode('utf-8'))
            return data.get('products', [])
    except urllib.error.HTTPError as e:
        if e.code == 503:
            print(f"503 Service Unavailable for '{term}'. OFF API rate limited.")
            return None
        print(f"HTTPError {e.code} for '{term}'")
        return None
    except Exception as e:
        print(f"Warning: Failed to fetch '{term}' - {e}")
        return None

        print(f"HTTPError {e.code} for '{term}'")
        return None
    except Exception as e:
        print(f"Warning: Failed to fetch '{term}' - {e}")
        return None

def import_bulk_products():
    import json
    import os
    all_products = list(PDF_PRODUCTS)
    try:
        if os.path.exists('products_c_to_z.json'):
            with open('products_c_to_z.json', 'r') as f:
                c_z = json.load(f)
                all_products.extend(c_z)
    except Exception as e:
        print(f"Error loading C-Z products: {e}")
        
    print(f"Starting bulk import for {len(all_products)} products...")
    
    with Session(engine) as session:
        canonical_map = seed_canonical_ingredients(session)
        now = datetime.now(timezone.utc)
        market_in, _ = get_or_create(session, Market, defaults={"name": "India"}, country_code="IN")
        methodology, _ = get_or_create(
            session, MethodologyVersion, 
            defaults={"name": "OFF Automated Nutrition Scoring", "rules": {"base": 100}, "effective_from": now, "reviewer": "System Admin"}, 
            version="v2.0"
        )
        
        inserted_count = 0
        skipped_count = 0
        failed_count = 0

        for i, search_term in enumerate(all_products):
            print(f"[{i+1}/{len(PDF_PRODUCTS)}] Searching for: {search_term}...")
            products = fetch_product(search_term)
            
            if products is None:
                print(f" -> API Error/Rate Limited. Pausing before continuing...")
                time.sleep(5)
                failed_count += 1
                continue
            
            if not products:
                print(f" -> Not found on Open Food Facts India.")
                skipped_count += 1
                time.sleep(2)  # Rate limiting
                continue
                
            item = products[0]
            gtin = item.get("code")
            if not gtin:
                print(f" -> Missing barcode.")
                skipped_count += 1
                time.sleep(2)
                continue
            
            # Idempotency check
            existing_variant = session.query(ProductVariant).filter_by(gtin=gtin).first()
            if existing_variant:
                print(f" -> Already exists in database.")
                skipped_count += 1
                time.sleep(2)
                continue
                
            try:
                brand_name = item.get("brands", "").split(",")[0].strip() or "Generic Brand"
                brand_slug = slugify(brand_name) or f"brand-{uuid.uuid4().hex[:8]}"
                
                cat_tags = item.get("categories_tags", [])
                cat_name = "General Food"
                if cat_tags:
                    cat_name = cat_tags[0].split(":")[-1].replace("-", " ").title()
                cat_slug = slugify(cat_name) or f"cat-{uuid.uuid4().hex[:8]}"
                
                product_name = item.get("product_name", "").strip() or search_term
                product_slug = slugify(f"{brand_name} {product_name}")
                
                ingredients_text = item.get("ingredients_text", "Ingredients not provided by manufacturer.")
                structured_ingredients = item.get("ingredients", [])
                nutriments = item.get("nutriments", {})
                image_url = item.get("image_url")
                
                brand, _ = get_or_create(session, Brand, defaults={"name": brand_name}, slug=brand_slug)
                category, _ = get_or_create(session, Category, defaults={"name": cat_name}, slug=cat_slug)
                
                product, created = get_or_create(
                    session, Product,
                    defaults={"brand_id": brand.id, "category_id": category.id, "canonical_name": product_name},
                    slug=product_slug
                )
                
                variant = ProductVariant(product_id=product.id, market_id=market_in.id, gtin=gtin)
                session.add(variant)
                session.flush()
                
                label = LabelVersion(
                    variant_id=variant.id, version_no=1, ingredients_raw=ingredients_text,
                    label_image_id=image_url, captured_at=now, review_status="published"
                )
                session.add(label)
                session.flush()

                parsed_ings = []
                if structured_ingredients:
                    parsed_ings = flatten_ingredients(structured_ingredients)
                elif ingredients_text and ingredients_text != "Ingredients not provided by manufacturer.":
                    raw_ings = [j.strip() for j in ingredients_text.replace("(", ",").replace(")", ",").replace(".", "").split(",")]
                    parsed_ings = [(j, None) for j in raw_ings if j and len(j) >= 2 and not j.endswith('%')]

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
                            
                    if mapped_ing_id and mapped_ing_id in seen_mapped: continue
                    if lower_ing in seen_texts: continue
                        
                    if mapped_ing_id: seen_mapped.add(mapped_ing_id)
                    seen_texts.add(lower_ing)
                    unique_ings.append((raw_ing_text, percent, mapped_ing_id))

                position = 1
                for raw_ing_text, percent, mapped_ing_id in unique_ings:
                    li = LabelIngredient(
                        label_version_id=label.id, ingredient_id=mapped_ing_id,
                        label_text=raw_ing_text[:255], position=position, declared_percent=percent
                    )
                    session.add(li)
                    position += 1

                nutrition = NutritionFacts(
                    label_version_id=label.id, basis_quantity=100, basis_unit="g",
                    energy=nutriments.get("energy-kcal_100g"), fat=nutriments.get("fat_100g"),
                    saturated_fat=nutriments.get("saturated-fat_100g"), carbohydrate=nutriments.get("carbohydrates_100g"),
                    sugars=nutriments.get("sugars_100g"), protein=nutriments.get("proteins_100g"),
                    sodium=nutriments.get("sodium_100g")
                )
                session.add(nutrition)
                
                nutrition_score = 60
                if nutriments.get("sugars_100g", 0) > 10: nutrition_score -= 10
                if nutriments.get("saturated-fat_100g", 0) > 5: nutrition_score -= 10
                if nutriments.get("sodium_100g", 0) > 1: nutrition_score -= 10
                nutrition_score = max(0, nutrition_score)

                score = nutrition_score + 25 + 15
                if score >= 80: band = "Favorable"
                elif score >= 60: band = "Mostly favorable"
                elif score >= 40: band = "Mixed"
                elif score >= 20: band = "Less favorable"
                else: band = "Least favorable"
                
                rating = Rating(
                    label_version_id=label.id, methodology_version_id=methodology.id,
                    total_score=score, nutrition_score=nutrition_score, ingredient_score=25,
                    context_score=15, band=band, confidence_grade="C",
                    explanation={"summary": "Automated scoring based on 100g nutritional profile from Open Food Facts."},
                    calculated_at=now
                )
                session.add(rating)
                
                session.commit()
                print(f" -> Successfully imported {product_name}.")
                inserted_count += 1
            except Exception as e:
                session.rollback()
                print(f" -> Error inserting {search_term}: {e}")
                failed_count += 1
                
            time.sleep(2) # Enforce 2 second rate limit
            
        print(f"\n--- Import Complete ---")
        print(f"Inserted: {inserted_count}")
        print(f"Skipped: {skipped_count}")
        print(f"Failed: {failed_count}")

if __name__ == "__main__":
    import_bulk_products()
