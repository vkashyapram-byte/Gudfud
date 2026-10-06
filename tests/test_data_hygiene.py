import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from scorer.data_hygiene import normalize_nutrients, run_sanity_checks

def test_data_hygiene():
    # Test normalization
    raw = {
        'sodium': '114G',
        'energy': '500 kcal',
        'fat': '20g',
        'saturated_fat': '5 g',
        'carbohydrate': '60',
        'sugars': '20',
        'protein': '10'
    }
    
    norm = normalize_nutrients(raw)
    assert norm['sodium'] == 114.0 # Should recognize 114 > 40 rule for sodium mg bug
    assert norm['energy'] == 500.0
    assert norm['fat'] == 20.0
    
    # Test sanity checks pass
    valid, reasons = run_sanity_checks(norm)
    assert valid, f"Expected valid, got invalid with reasons {reasons}"
    
    # Test sanity checks fail
    bad = {
        'sodium': 50000,
        'energy': 100,
        'fat': 30,
        'saturated_fat': 40,
        'carbohydrate': 40,
        'sugars': 50,
        'protein': 40
    }
    valid, reasons = run_sanity_checks(bad)
    assert not valid
    assert "Saturated fat > total fat" in reasons
    assert "Sugars > carbohydrates" in reasons
    assert "Sodium > 40,000 mg/100g" in reasons
    assert any("Macro sum" in r for r in reasons)
    assert any("Atwater" in r for r in reasons)
    
    print("All data hygiene tests passed!")

if __name__ == "__main__":
    test_data_hygiene()
