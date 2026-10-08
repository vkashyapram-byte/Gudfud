import json
import random
import re

TIER_1_HAZARDS = [
    "bha", "bht", "tbhq", "propyl paraben", "methyl paraben", "ethyl paraben",
    "propyl gallate", "sodium nitrite", "sodium nitrate", "potassium nitrate",
    "sodium benzoate", "potassium benzoate", "calcium sorbate", "sodium sulfite",
    "sulfur dioxide", "potassium bisulfite", "sodium bisulfite",
    "red 40", "yellow 5", "yellow 6", "red 3", "blue 1", "blue 2", "green 3",
    "titanium dioxide", "caramel color",
    "potassium bromate", "azodicarbonamide", "benzoyl peroxide", "chlorine dioxide",
    "brominated vegetable oil", "bvo", "carrageenan", "polysorbate 80", "polysorbate 60",
    "aspartame", "sucralose", "saccharin", "acesulfame potassium", "ace-k",
    "partially hydrogenated", "interesterified",
    "211", "320", "321", "319", "924", "927a", "250", "251", "407", "951", "955", "954", "102", "110", "129", "133", "171"
]

TIER_2_HAZARDS = [
    "edta", "datem", "sodium stearoyl lactylate", "ssl",
    "carboxymethylcellulose", "cellulose gum", "propylene glycol",
    "high fructose corn syrup", "hfcs", "corn syrup solids", "maltodextrin",
    "agave nectar", "monosodium glutamate", "msg", "hydrolyzed soy protein",
    "hydrolyzed vegetable protein", "autolyzed yeast extract", "yeast extract",
    "artificial flavor", "artificial flavours", "artificial flavors", "diacetyl",
    "fully hydrogenated", "sodium aluminum", "potassium aluminum", "silicon dioxide", "talc",
    "433", "202"
]

def grade(ingredients_raw: str, nutrition: dict) -> dict:
    sugar = nutrition.get('sugars', 0) or 0
    sodium = nutrition.get('sodium', 0) or 0
    sat_fat = nutrition.get('saturated_fat', 0) or 0
    
    nutrition_score = 100 - (sugar * 2) - (sodium * 0.05) - (sat_fat * 3)
    nutrition_score = max(10, min(100, nutrition_score))
    
    ingredient_len = len(ingredients_raw.split(',')) if ingredients_raw else 1
    ingredient_score = 100 - (ingredient_len * 2)
    
    ingredients_lower = (ingredients_raw or "").lower()
    
    found_tier1 = []
    found_tier2 = []
    
    for hazard in TIER_1_HAZARDS:
        if hazard.isdigit():
            pattern = r'\b' + hazard + r'\b'
        else:
            pattern = r'\b' + re.escape(hazard) + r'\b'
            
        if re.search(pattern, ingredients_lower):
            ingredient_score -= 20
            found_tier1.append(hazard)
            
    for hazard in TIER_2_HAZARDS:
        if hazard.isdigit():
            pattern = r'\b' + hazard + r'\b'
        else:
            pattern = r'\b' + re.escape(hazard) + r'\b'
            
        if re.search(pattern, ingredients_lower):
            ingredient_score -= 5
            found_tier2.append(hazard)
            
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
        "band": band,
        "found_tier1": found_tier1,
        "found_tier2": found_tier2
    }

sql_statements = []

penalized_count = 0
total_count = 0

with open('raw_output_all.txt', 'r') as f:
    try:
        content = f.read()
        start = content.find('{')
        end = content.rfind('}') + 1
        json_content = content[start:end]
        
        parsed = json.loads(json_content)
        rows = parsed.get("rows", [])
        
        for row in rows:
            data = row.get("data", {})
            nut_dict = {
                'sugars': float(data.get('sugars')) if data.get('sugars') else 0,
                'sodium': float(data.get('sodium')) if data.get('sodium') else 0,
                'saturated_fat': float(data.get('saturated_fat')) if data.get('saturated_fat') else 0
            }
            score_res = grade(data.get('ingredients_raw', ''), nut_dict)
            
            if score_res['found_tier1'] or score_res['found_tier2']:
                penalized_count += 1
            
            total_count += 1
            stmt = f"UPDATE rating SET total_score = {score_res['total_score']}, nutrition_score = {score_res['nutrition_score']}, ingredient_score = {score_res['ingredient_score']}, context_score = {score_res['context_score']}, band = '{score_res['band']}' WHERE id = '{data['rating_id']}';"
            sql_statements.append(stmt)
            
    except Exception as e:
        print(f"Error parsing: {e}")

with open('update_scores_toxicity_all.sql', 'w') as f:
    f.write('\n'.join(sql_statements))
    f.write('\n')
print(f"\nGenerated {len(sql_statements)} updates. Processed {total_count} products. Penalized {penalized_count} products due to toxicity matches.")
