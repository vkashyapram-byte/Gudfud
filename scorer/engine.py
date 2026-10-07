from scorer.data_hygiene import normalize_nutrients, run_sanity_checks
from scorer.parser import parse_ingredients
from scorer.ingredients import score_ingredients, load_ingredient_dict
from scorer.nutrition import calculate_nutrition_score, evaluate_hfss

def get_overall_label(score):
    if score >= 80:
        return "Favourable"
    elif score >= 60:
        return "Mostly favourable"
    elif score >= 40:
        return "Mixed"
    elif score >= 20:
        return "Mostly unfavourable"
    else:
        return "Unfavourable"

def get_color_status(score):
    if score >= 70:
        return "GREEN"
    elif score >= 40:
        return "YELLOW"
    else:
        return "RED"

def calculate_overall_score(product_dict):
    """
    Main entry point for the GudFud scoring engine.
    """
    # 1. Data Hygiene
    raw_nutrients = {
        'energy': product_dict.get('energy_kcal'),
        'sodium': product_dict.get('sodium_g'),
        'fat': product_dict.get('fat_g'),
        'saturated_fat': product_dict.get('sat_fat_g'),
        'sugars': product_dict.get('sugars_g'),
        'protein': product_dict.get('protein_g'),
        'carbohydrate': product_dict.get('carbohydrate_g'),
        'fibre': product_dict.get('fiber_g')
    }
    clean_nutrients = normalize_nutrients(raw_nutrients)
    is_valid, hygiene_errors = run_sanity_checks(clean_nutrients)
    
    hygiene_reasons = [{"factor": "data_hygiene", "error": err} for err in hygiene_errors]
    
    # 2. Nutrition Score
    energy_kj = clean_nutrients.get('energy', 0) * 4.184 if clean_nutrients.get('energy') else 0
        
    sugars = clean_nutrients.get('sugars', 0) or 0
    sat_fat = clean_nutrients.get('saturated_fat', 0) or 0
    sodium_mg = clean_nutrients.get('sodium', 0) or 0
    
    # For Phase 1 we use basic ICMR limits to check HFSS
    is_hfss, hfss_flags = evaluate_hfss(clean_nutrients)
    
    nutri_points = calculate_nutrition_score(
        product_dict.get('category_1', 'Solid'), # simplified
        energy_kj,
        sugars,
        sat_fat,
        sodium_mg,
        product_dict.get('fruit_veg_nut_millet_pct', 0),
        clean_nutrients.get('fibre', 0) or 0,
        clean_nutrients.get('protein', 0) or 0
    )
    
    # In FSSAI INR, more points = worse. 0 = best, 40+ = worst.
    # Convert to 0-100 where 100 is best.
    # We will assume max points is 40.
    # 40 points -> 0 score, 0 points -> 100 score.
    nutrition_score = max(0, min(100, 100 - (nutri_points / 40.0) * 100))
    
    # 3. Ingredients Score
    nodes = parse_ingredients(product_dict.get('ingredients', ''))
    ing_score_dict = score_ingredients(nodes, nova_class=product_dict.get('nova', 4))
    ingredient_score = ing_score_dict["ingredient_score"]
    confidence_score = ing_score_dict["confidence"]
    
    # 4. Context Score
    # Map NOVA classification (processing level) to a score
    nova = product_dict.get('nova', 4)
    if nova == 1:
        context_score = 100.0
    elif nova == 2:
        context_score = 75.0
    elif nova == 3:
        context_score = 50.0
    else:
        context_score = 25.0
    
    # 5. Overall Calculation
    overall_score = (0.5 * nutrition_score) + (0.3 * ingredient_score) + (0.2 * context_score)
    
    # Check Safe Consumption Limits (Penalty)
    safe_limit_violations = []
    if sodium_mg > 2300:
        safe_limit_violations.append(f"Sodium ({sodium_mg}mg) exceeds daily safe limit of 2300mg")
    if sugars > 50:
        safe_limit_violations.append(f"Sugars ({sugars}g) exceed daily safe limit of 50g")
    if sat_fat > 20:
        safe_limit_violations.append(f"Saturated fat ({sat_fat}g) exceeds daily safe limit of 20g")

    # Penalize overall score if safe limits are violated
    if safe_limit_violations:
        overall_score = min(overall_score, 39) # Force it into 'Mostly unfavourable' / RED status
    
    # Penalty caps (e.g., if HFSS is true for multiple things)
    if 'high_sugar' in hfss_flags and 'high_sat_fat' in hfss_flags:
        overall_score = min(overall_score, 39) # capped at Mostly unfavourable
        
    # Compile reasons
    reasons = hygiene_reasons + [{"factor": "nutrition_points", "points": nutri_points}] + ing_score_dict["reasons"]
    for v in safe_limit_violations:
        reasons.append({"factor": "safe_consumption_limit", "error": v})
    
    return {
        "overall_label": get_overall_label(overall_score).upper(),
        "overall_score": round(overall_score, 1),
        "nutrition_score": round(nutrition_score, 1),
        "ingredient_score": round(ingredient_score, 1),
        "context_score": round(context_score, 1),
        "confidence": confidence_score,
        "color_status": get_color_status(overall_score),
        "safe_limit_violations": safe_limit_violations,
        "score_interval": [round(max(0, overall_score-5), 1), round(min(100, overall_score+5), 1)],
        "reasons": reasons,
        "hfss_flags": hfss_flags
    }

