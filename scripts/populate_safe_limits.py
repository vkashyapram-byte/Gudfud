import os
import sys
import uuid
from datetime import datetime, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.models import Ingredient, IngredientEvidence, Source

# Setup Database connection
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///prod.db")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def populate_safe_limits():
    """
    Populates base safe consumption limits for specific critical ingredients.
    In a real production environment, this would call the USDA FoodData Central 
    or Open Food Facts API to pull vast taxonomies. Here we seed the baseline 
    WHO/FDA recommended limits for scoring logic.
    """
    db = SessionLocal()

    # Define our foundational limit dictionary based on FDA / WHO
    limits_data = {
        "sodium": {
            "limit": 2300, 
            "unit": "mg", 
            "safe": False, 
            "summary": "Too much sodium can lead to high blood pressure, heart disease, and stroke.",
            "evidence_grade": "High"
        },
        "sugar": {
            "limit": 50, 
            "unit": "g", 
            "safe": False, 
            "summary": "Excessive added sugar is linked to obesity, type 2 diabetes, and heart disease.",
            "evidence_grade": "High"
        },
        "saturated fat": {
            "limit": 20, 
            "unit": "g", 
            "safe": False, 
            "summary": "High saturated fat intake increases LDL cholesterol levels, increasing risk of heart disease.",
            "evidence_grade": "High"
        },
        "ascorbic acid": {
            "limit": 2000, 
            "unit": "mg", 
            "safe": True, 
            "summary": "Vitamin C. Generally recognized as safe. Essential for tissue repair.",
            "evidence_grade": "High"
        }
    }

    try:
        # Create a default source for our WHO/FDA limits
        source = db.query(Source).filter_by(title="FDA / WHO Daily Guidelines").first()
        if not source:
            source = Source(
                title="FDA / WHO Daily Guidelines",
                publisher="WHO",
                source_type="Guideline",
                accessed_at=datetime.now(timezone.utc),
                url="https://www.who.int/news-room/fact-sheets"
            )
            db.add(source)
            db.commit()
            db.refresh(source)

        ingredients = db.query(Ingredient).all()
        updated_count = 0

        for key, data in limits_data.items():
            # Find ingredient by name
            ing = db.query(Ingredient).filter(Ingredient.canonical_name.ilike(f"%{key}%")).first()
            if not ing:
                # Create it
                ing = Ingredient(
                    id=uuid.uuid4(),
                    canonical_name=key.title(),
                    slug=key.replace(" ", "-").lower(),
                    public_summary=data["summary"],
                    status="published"
                )
                db.add(ing)
                db.flush()

            # Update the Ingredient model
            ing.daily_limit_amount = data["limit"]
            ing.daily_limit_unit = data["unit"]
            ing.is_generally_safe = data["safe"]
            
            # Create Educational Evidence
            evidence = db.query(IngredientEvidence).filter_by(ingredient_id=ing.id).first()
            if not evidence:
                evidence = IngredientEvidence(
                    ingredient_id=ing.id,
                    effect_type="General Health",
                    evidence_grade=data["evidence_grade"],
                    summary=data["summary"],
                    review_status="Approved",
                    reviewed_at=datetime.now(timezone.utc)
                )
                db.add(evidence)
            else:
                evidence.summary = data["summary"]

            updated_count += 1
                
        db.commit()
        print(f"✅ Successfully updated {updated_count} ingredients with Safe Consumption Limits and Educational Evidence.")

    except Exception as e:
        print(f"❌ Error populating database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    populate_safe_limits()
