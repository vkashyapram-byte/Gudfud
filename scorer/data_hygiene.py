import re

def parse_nutrient_value(val_str):
    if not isinstance(val_str, str):
        return float(val_str) if val_str is not None else None
    
    # Strip any spaces
    val_str = val_str.strip().lower()
    
    # Check if there is a number
    match = re.search(r'([\d.]+)', val_str)
    if not match:
        return None
    
    val = float(match.group(1))
    
    # If the bug "114G" is present for sodium, we need to handle it in the normalizer
    # For general parsing, just return the value and the unit found (if any)
    unit_match = re.search(r'([a-z]+)', val_str)
    unit = unit_match.group(1) if unit_match else None
    
    return val, unit

def normalize_nutrients(raw_nutrients):
    """
    raw_nutrients is a dict with keys like 'energy', 'sodium', 'fat', 'saturated_fat', 'carbohydrate', 'sugars', 'protein', 'fibre'
    Output is a dict with all values in g/100g (except sodium in mg/100g and energy in kcal/100g).
    """
    normalized = {}
    
    for key, val in raw_nutrients.items():
        if val is None:
            normalized[key] = None
            continue
            
        parsed = parse_nutrient_value(str(val))
        if not parsed:
            normalized[key] = None
            continue
            
        num, unit = parsed
        
        if key == 'sodium':
            # Handle the "G" bug. If sodium is > 40 (since 40g = 40,000mg which is absurdly high for 100g),
            # and the unit was 'g', it was likely a typo for mg or already mg but tagged as G.
            # If the unit is 'g' and value is < 40, it's 40g = 40000mg.
            if unit == 'g':
                if num > 40:
                    # It's actually mg, they just typed G
                    normalized[key] = num
                else:
                    normalized[key] = num * 1000.0
            else:
                normalized[key] = num
        elif key == 'energy':
            # typically kcal
            normalized[key] = num
        else:
            # Everything else should be g
            if unit == 'mg':
                normalized[key] = num / 1000.0
            else:
                normalized[key] = num
                
    return normalized

def run_sanity_checks(nutrients):
    """
    Returns (is_valid, reasons)
    """
    reasons = []
    
    if nutrients.get('saturated_fat') is not None and nutrients.get('fat') is not None:
        if nutrients['saturated_fat'] > nutrients['fat'] + 0.1: # 0.1g tolerance for rounding
            reasons.append("Saturated fat > total fat")
            
    if nutrients.get('sugars') is not None and nutrients.get('carbohydrate') is not None:
        if nutrients['sugars'] > nutrients['carbohydrate'] + 0.1:
            reasons.append("Sugars > carbohydrates")
            
    if nutrients.get('sodium') is not None:
        if nutrients['sodium'] > 40000:
            reasons.append("Sodium > 40,000 mg/100g")
            
    # Macro sum check
    macros = [nutrients.get('fat', 0) or 0, 
              nutrients.get('carbohydrate', 0) or 0, 
              nutrients.get('protein', 0) or 0]
    
    if sum(macros) > 105: # Allow slight rounding errors over 100g
        reasons.append(f"Macro sum ({sum(macros)}) > 100g")
        
    # Atwater energy check
    if all(nutrients.get(k) is not None for k in ['energy', 'fat', 'carbohydrate', 'protein']):
        est_energy = (nutrients['fat'] * 9) + (nutrients['carbohydrate'] * 4) + (nutrients['protein'] * 4)
        actual = nutrients['energy']
        if actual > 0 and est_energy > 0:
            ratio = actual / est_energy
            if ratio < 0.75 or ratio > 1.25:
                reasons.append(f"Energy {actual} kcal deviates >25% from Atwater estimate {est_energy:.1f} kcal")
                
    return len(reasons) == 0, reasons
