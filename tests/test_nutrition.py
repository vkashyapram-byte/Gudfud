import os
import sys
import yaml

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from scorer.nutrition import get_points_discrete, get_points_continuous, evaluate_hfss, INR_TABLES

def test_inr_table_discrete_solid():
    # Test every single row of the solid table boundaries to ensure they return the correct points
    table = INR_TABLES['solid']
    
    for row in table:
        pts = row['points']
        if pts == 0:
            for nut in ['energy', 'sat_fat', 'sugars', 'sodium', 'fv', 'nlm', 'fibre', 'protein']:
                key = f"{nut}_lte"
                if key in row:
                    val = row[key]
                    assert get_points_discrete(val, 'solid', nut) == 0
                    assert get_points_discrete(val - 0.01, 'solid', nut) == 0
        else:
            for nut in ['energy', 'sat_fat', 'sugars', 'sodium', 'fv', 'nlm', 'fibre', 'protein']:
                key = f"{nut}_gt"
                if key in row:
                    val = row[key]
                    # Since it is 'greater than', the value exactly at the boundary should yield the LOWER points.
                    # Wait, if row points is 1, and >80, then 80 gives 0 points. 80.01 gives 1 point.
                    assert get_points_discrete(val + 0.01, 'solid', nut) == pts
                    # 80 should give pts-1.
                    assert get_points_discrete(val, 'solid', nut) == pts - 1

def test_inr_table_continuous_solid():
    # Test continuous interpolation
    # Energy: 0 <=80, 1 >80, 2 >160.
    # At 80, should be 0. At 160, should be 1.0. At 120, should be 0.5.
    # Wait, if discrete 1 is >80 and 2 is >160.
    # The interval between 80 and 160 is where it linearly transitions from 0 to 1? Or 1 to 2?
    # In Health Star Rating, points are given for ranges. A continuous function smooths this.
    # My continuous function maps val 80 -> 0, 160 -> 1.0, 120 -> 0.5. Let's check:
    print("Energy 80:", get_points_continuous(80, 'solid', 'energy'))
    print("Energy 160:", get_points_continuous(160, 'solid', 'energy'))
    print("Energy 120:", get_points_continuous(120, 'solid', 'energy'))
    
    # Sat fat: 0 <=1.0, 1 >1.0, 2 >2.0
    assert get_points_continuous(1.0, 'solid', 'sat_fat') == 0.0
    assert get_points_continuous(2.0, 'solid', 'sat_fat') == 1.0
    assert get_points_continuous(1.5, 'solid', 'sat_fat') == 0.5

def test_hfss():
    # Sugar HFSS threshold: sugar*4 / energy >= 0.1
    # Example: energy 100 kcal. Sugar 2.5g -> 10 kcal -> 10% -> HFSS
    is_hfss, flags = evaluate_hfss({'energy': 100, 'sugars': 2.5})
    assert is_hfss
    assert 'high_sugar' in flags
    
    is_hfss, flags = evaluate_hfss({'energy': 100, 'sugars': 2.4})
    assert not is_hfss
    assert 'high_sugar' not in flags
    
    # Sat fat threshold: sat_fat*9 / energy >= 0.1
    is_hfss, flags = evaluate_hfss({'energy': 90, 'saturated_fat': 1.0}) # 9/90 = 10%
    assert is_hfss
    assert 'high_sat_fat' in flags
    
    # Sodium threshold: sodium >= 1 * energy
    is_hfss, flags = evaluate_hfss({'energy': 100, 'sodium': 100})
    assert is_hfss
    assert 'high_sodium' in flags

if __name__ == "__main__":
    test_inr_table_discrete_solid()
    test_inr_table_continuous_solid()
    test_hfss()
    print("All nutrition tests passed!")
