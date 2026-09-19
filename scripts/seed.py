import os
import sys
import uuid
from datetime import datetime, timezone
import json

# Ensure src is in the python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from src.models import (
    Brand, Category, Market, Product, ProductVariant, 
    LabelVersion, Rating, MethodologyVersion
)

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is required")

# Handle typical postgresql:// to postgresql+psycopg2:// translation if needed for SQLAlchemy
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)

def get_or_create(session, model, defaults=None, **kwargs):
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance, False
    else:
        params = dict((k, v) for k, v in kwargs.items())
        params.update(defaults or {})
        instance = model(**params)
        session.add(instance)
        session.flush()
        return instance, True

def seed_data():
    with Session(engine) as session:
        try:
            now = datetime.now(timezone.utc)
            
            # 1. Base Reference Data
            market_us, _ = get_or_create(session, Market, defaults={"name": "United States"}, country_code="US")
            
            methodology, _ = get_or_create(
                session, MethodologyVersion, 
                defaults={
                    "name": "Standard Nutrition Scoring", 
                    "rules": {"base": 100}, 
                    "effective_from": now,
                    "reviewer": "System Admin"
                }, 
                version="v1.0"
            )

            # 2. Categories
            cat_grains, _ = get_or_create(session, Category, defaults={"name": "Grains & Cereals"}, slug="grains-cereals")
            cat_dairy, _ = get_or_create(session, Category, defaults={"name": "Dairy"}, slug="dairy")
            cat_bakery, _ = get_or_create(session, Category, defaults={"name": "Bakery"}, slug="bakery")

            # 3. Brands
            brand_quaker, _ = get_or_create(session, Brand, defaults={"name": "Quaker"}, slug="quaker")
            brand_horizon, _ = get_or_create(session, Brand, defaults={"name": "Horizon Organic"}, slug="horizon-organic")
            brand_natures, _ = get_or_create(session, Brand, defaults={"name": "Nature's Own"}, slug="natures-own")

            # 4. Products & Hierarchies
            
            # Product 1: Rolled Oats
            p1, _ = get_or_create(
                session, Product,
                defaults={"brand_id": brand_quaker.id, "category_id": cat_grains.id, "canonical_name": "Old Fashioned Rolled Oats"},
                slug="quaker-old-fashioned-rolled-oats"
            )
            v1, _ = get_or_create(
                session, ProductVariant,
                defaults={"market_id": market_us.id, "gtin": "030000010402"},
                product_id=p1.id
            )
            l1, _ = get_or_create(
                session, LabelVersion,
                defaults={
                    "ingredients_raw": "Whole Grain Rolled Oats",
                    "captured_at": now,
                    "review_status": "published"
                },
                variant_id=v1.id, version_no=1
            )
            get_or_create(
                session, Rating,
                defaults={
                    "total_score": 95,
                    "band": "A",
                    "confidence_grade": "High",
                    "explanation": {"summary": "Single ingredient whole grain."},
                    "calculated_at": now
                },
                label_version_id=l1.id, methodology_version_id=methodology.id
            )

            # Product 2: Whole Milk
            p2, _ = get_or_create(
                session, Product,
                defaults={"brand_id": brand_horizon.id, "category_id": cat_dairy.id, "canonical_name": "Organic Whole Milk"},
                slug="horizon-organic-whole-milk"
            )
            v2, _ = get_or_create(
                session, ProductVariant,
                defaults={"market_id": market_us.id, "gtin": "742365264450"},
                product_id=p2.id
            )
            l2, _ = get_or_create(
                session, LabelVersion,
                defaults={
                    "ingredients_raw": "Organic Grade A Milk, Vitamin D3",
                    "captured_at": now,
                    "review_status": "published"
                },
                variant_id=v2.id, version_no=1
            )
            get_or_create(
                session, Rating,
                defaults={
                    "total_score": 85,
                    "band": "B",
                    "confidence_grade": "High",
                    "explanation": {"summary": "Standard organic dairy product fortified with Vitamin D3."},
                    "calculated_at": now
                },
                label_version_id=l2.id, methodology_version_id=methodology.id
            )

            # Product 3: Whole Wheat Bread
            p3, _ = get_or_create(
                session, Product,
                defaults={"brand_id": brand_natures.id, "category_id": cat_bakery.id, "canonical_name": "100% Whole Wheat Bread"},
                slug="natures-own-100-whole-wheat-bread"
            )
            v3, _ = get_or_create(
                session, ProductVariant,
                defaults={"market_id": market_us.id, "gtin": "072250037068"},
                product_id=p3.id
            )
            l3, _ = get_or_create(
                session, LabelVersion,
                defaults={
                    "ingredients_raw": "Whole Wheat Flour, Water, Yeast, Brown Sugar, Wheat Gluten, Contains 2% or less of each of the following: Salt, Dough Conditioners, Soybean Oil, Vinegar, Cultured Wheat Flour, Ascorbic Acid, Enzymes.",
                    "captured_at": now,
                    "review_status": "published"
                },
                variant_id=v3.id, version_no=1
            )
            get_or_create(
                session, Rating,
                defaults={
                    "total_score": 75,
                    "band": "C",
                    "confidence_grade": "Medium",
                    "explanation": {"summary": "Contains added sugars and dough conditioners."},
                    "calculated_at": now
                },
                label_version_id=l3.id, methodology_version_id=methodology.id
            )

            session.commit()
            print("Successfully seeded the database.")

        except Exception as e:
            session.rollback()
            print(f"Error during seeding: {e}")
            raise e

if __name__ == "__main__":
    seed_data()
