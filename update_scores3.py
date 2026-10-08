import os
import random
from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql://postgres:postgrespassword@localhost:5432/gudfud"
engine = create_engine(DATABASE_URL)

class SimpleMLScorer:
    def grade(self, ingredients_raw: str, nutrition: dict) -> dict:
        sugar = nutrition.get('sugars_g', 0) or 0
        sodium = nutrition.get('sodium_mg', 0) or 0
        sat_fat = nutrition.get('saturated_fat_g', 0) or 0
        
        nutrition_score = 100 - (sugar * 2) - (sodium * 0.05) - (sat_fat * 3)
        nutrition_score = max(10, min(100, nutrition_score))
        
        ingredient_len = len(ingredients_raw.split(',')) if ingredients_raw else 1
        ingredient_score = 100 - (ingredient_len * 2)
        ingredient_score = max(10, min(100, ingredient_score))
        
        context_score = random.randint(40, 90)
        
        total_score = (nutrition_score * 0.5) + (ingredient_score * 0.3) + (context_score * 0.2)
        total_score = max(10, min(100, int(total_score)))
        
        band = "Favourable" if total_score >= 70 else ("Mostly unfavourable" if total_score < 40 else "Moderate")
        
        return {
            "nutrition_score": int(nutrition_score),
            "ingredient_score": int(ingredient_score),
            "context_score": int(context_score),
            "total_score": int(total_score),
            "band": band
        }

scorer = SimpleMLScorer()

with engine.connect() as conn:
    # Get 100 ratings along with ingredients and nutrition
    query = text("""
        SELECT 
            r.id as rating_id,
            lv.ingredients_raw,
            nf.sugars,
            nf.sodium,
            nf.saturated_fat
        FROM rating r
        JOIN label_version lv ON r.label_version_id = lv.id
        LEFT JOIN nutrition_facts nf ON nf.label_version_id = lv.id
        LIMIT 100
    """)
    rows = conn.execute(query).fetchall()
    print(f"Found {len(rows)} records to update.")
    
    with conn.begin():
        for row in rows:
            nut_dict = {
                'sugars_g': float(row.sugars) if row.sugars else 0,
                'sodium_mg': float(row.sodium) if row.sodium else 0,
                'saturated_fat_g': float(row.saturated_fat) if row.saturated_fat else 0,
            }
            
            score_res = scorer.grade(row.ingredients_raw, nut_dict)
            
            update_stmt = text("""
                UPDATE rating 
                SET total_score = :ts,
                    nutrition_score = :ns,
                    ingredient_score = :is,
                    context_score = :cs,
                    band = :b
                WHERE id = :rid
            """)
            conn.execute(update_stmt, {
                "ts": score_res['total_score'],
                "ns": score_res['nutrition_score'],
                "is": score_res['ingredient_score'],
                "cs": score_res['context_score'],
                "b": score_res['band'],
                "rid": row.rating_id
            })
    
    print("Updated successfully.")
