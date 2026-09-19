import os
import sys

# Ensure src is in the python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from src.models import (
    Rating, NutritionFacts, LabelIngredient, LabelVersion, 
    ProductVariant, Product, Brand, Category
)

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is required")

if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)

def purge():
    with Session(engine) as session:
        print("Purging product data from the database...")
        try:
            # Delete in order of dependencies (children first)
            session.query(Rating).delete()
            session.query(NutritionFacts).delete()
            session.query(LabelIngredient).delete()
            session.query(LabelVersion).delete()
            session.query(ProductVariant).delete()
            session.query(Product).delete()
            session.query(Brand).delete()
            session.query(Category).delete()
            
            session.commit()
            print("Purge complete!")
        except Exception as e:
            session.rollback()
            print(f"Error during purge: {e}")
            raise e

if __name__ == "__main__":
    purge()
