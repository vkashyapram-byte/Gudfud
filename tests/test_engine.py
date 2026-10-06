import json
from scorer.engine import calculate_overall_score

def test_engine_hide_and_seek():
    # Construct a raw product dict representing a product like Hide & Seek
    raw_product = {
        "barcode": "8901030386221",
        "product_name": "Hide & Seek",
        "brands": "Parle",
        "ingredients": "Refined Wheat Flour, Sugar (20%), Edible Vegetable Oil, Cocoa Solids, Invert Syrup",
        "nova": 4,
        "energy_kcal": 479,
        "fat_g": 18,
        "sat_fat_g": 9.4,
        "sugars_g": 32.5,
        "sodium_g": 0.114,
        "protein_g": 6.5,
        "fiber_g": 4,
        "fruit_veg_nut_millet_pct": 0,
        "category_1": "Solid"
    }
    
    result = calculate_overall_score(raw_product)
    
    print(json.dumps(result, indent=2))
    
    # Assertions based on Section 1 of the spec
    assert "overall_label" in result
    assert "overall_score" in result
    assert "nutrition_score" in result
    assert "ingredient_score" in result
    assert "context_score" in result
    assert "reasons" in result
    
    assert result["overall_score"] <= 100
    assert result["overall_score"] >= 0

if __name__ == '__main__':
    test_engine_hide_and_seek()
    print("Engine tests passed!")
