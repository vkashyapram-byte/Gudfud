import os
import sys
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.models import (
    LabelVersion, NutritionFacts, ProductVariant, Product, Category, Rating, MethodologyVersion
)
from scorer.engine import calculate_overall_score

DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://postgres.cynbftllkqcwslnnvydu:JYavQICA4BGECz6G@aws-0-ap-southeast-2.pooler.supabase.com:6543/postgres")
engine = create_engine(DATABASE_URL)

def get_or_create_methodology(session: Session) -> str:
    """Ensure we have a methodology version for GudFud v1.0"""
    meth = session.query(MethodologyVersion).filter_by(version="1.0.0").first()
    if not meth:
        meth = MethodologyVersion(
            version="1.0.0",
            name="GudFud Baseline Engine",
            rules={"engine": "1.0", "description": "Phase 5 Baseline"},
            effective_from=datetime.now(),
            reviewer="system"
        )
        session.add(meth)
        session.commit()
    return meth.id

def score_all_products():
    print("Starting scoring engine batch run...")
    with Session(engine) as session:
        meth_id = get_or_create_methodology(session)
        
        print("Fetching all labels with relations...")
        query = (
            session.query(LabelVersion, NutritionFacts, Category)
            .outerjoin(NutritionFacts, NutritionFacts.label_version_id == LabelVersion.id)
            .join(ProductVariant, ProductVariant.id == LabelVersion.variant_id)
            .join(Product, Product.id == ProductVariant.product_id)
            .join(Category, Category.id == Product.category_id)
        )
        
        results = query.all()
        print(f"Found {len(results)} label versions to score.")
        
        processed = 0
        for i, (label, nutri, category) in enumerate(results):
            if i % 10 == 0:
                print(f"Processing label {i+1}...")
            
            # Build product_dict for the engine
            product_dict = {
                'energy_kcal': float(nutri.energy) if nutri and nutri.energy is not None else 0.0,
                'sodium_g': float(nutri.sodium) if nutri and nutri.sodium is not None else 0.0,
                'fat_g': float(nutri.fat) if nutri and nutri.fat is not None else 0.0,
                'sat_fat_g': float(nutri.saturated_fat) if nutri and nutri.saturated_fat is not None else 0.0,
                'sugars_g': float(nutri.sugars) if nutri and nutri.sugars is not None else 0.0,
                'protein_g': float(nutri.protein) if nutri and nutri.protein is not None else 0.0,
                'carbohydrate_g': float(nutri.carbohydrate) if nutri and nutri.carbohydrate is not None else 0.0,
                'fiber_g': float(nutri.fibre) if nutri and nutri.fibre is not None else 0.0,
                'ingredients': label.ingredients_raw or "",
                'nova': 4, # Defaulting to 4 unless mapped
                'category_1': category.name if category else 'Solid'
            }
            
            try:
                result = calculate_overall_score(product_dict)
                
                # Upsert rating
                existing_rating = session.query(Rating).filter_by(
                    label_version_id=label.id, 
                    methodology_version_id=meth_id
                ).first()
                
                if existing_rating:
                    existing_rating.total_score = int(result['overall_score'])
                    existing_rating.band = result['overall_label']
                    existing_rating.nutrition_score = int(result['nutrition_score'])
                    existing_rating.ingredient_score = int(result['ingredient_score'])
                    existing_rating.context_score = int(result['context_score'])
                    existing_rating.confidence_grade = result['confidence']
                    existing_rating.explanation = result['reasons']
                    existing_rating.calculated_at = datetime.now()
                else:
                    new_rating = Rating(
                        label_version_id=label.id,
                        methodology_version_id=meth_id,
                        total_score=int(result['overall_score']),
                        band=result['overall_label'],
                        nutrition_score=int(result['nutrition_score']),
                        ingredient_score=int(result['ingredient_score']),
                        context_score=int(result['context_score']),
                        confidence_grade=result['confidence'],
                        explanation=result['reasons'],
                        calculated_at=datetime.now()
                    )
                    session.add(new_rating)
                
                processed += 1
                
            except Exception as e:
                print(f"Failed to score product variant {label.variant_id}: {e}")
                
            if processed % 100 == 0:
                session.commit()
                print(f"Committed {processed} ratings...")
                
        session.commit()
        print(f"Done! Successfully scored and saved ratings for {processed} products.")

if __name__ == "__main__":
    score_all_products()
