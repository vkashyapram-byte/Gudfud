import os
import sys

# Ensure src is in the python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from src.models import (
    Brand, Category, Market, Product, ProductVariant, 
    LabelVersion, Rating, MethodologyVersion, NutritionFacts,
    LabelIngredient, IngredientAlias, IngredientEvidence,
    EvidenceSource, RegulatoryStatus, VariantSource,
    Alternative
)

DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)

def clear_db():
    print("Clearing the database...")
    with Session(engine) as session:
        session.query(Alternative).delete()
        session.query(VariantSource).delete()
        session.query(LabelIngredient).delete()
        session.query(Rating).delete()
        session.query(NutritionFacts).delete()
        session.query(LabelVersion).delete()
        session.query(ProductVariant).delete()
        session.query(Product).delete()
        session.query(Brand).delete()
        session.query(Category).delete()
        # Not deleting MethodologyVersion to keep it
        session.commit()
    print("Database cleared successfully.")

if __name__ == "__main__":
    clear_db()
