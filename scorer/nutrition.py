import yaml
import os

# Load INR tables
config_dir = os.path.join(os.path.dirname(__file__), '..', 'config')
with open(os.path.join(config_dir, 'inr_tables.yaml')) as f:
    INR_TABLES = yaml.safe_load(f)
with open(os.path.join(config_dir, 'hfss_thresholds.yaml')) as f:
    HFSS_THRESHOLDS = yaml.safe_load(f)

def get_points_discrete(val, category_type, nutrient):
    """
    Returns discrete points based on the INR tables.
    category_type is 'solid' or 'liquid'.
    nutrient is e.g. 'energy', 'sat_fat', 'sugars', 'sodium', 'fv', 'nlm', 'fibre', 'protein'
    """
    if val is None:
        return 0
    
    table = INR_TABLES[category_type]
    
    # We iterate backwards from max points to 0. 
    # The highest point row where val > x_gt is the points awarded.
    # If val doesn't exceed any x_gt, we check if it is <= x_lte for 0 points (it always is, but safe to check).
    for row in reversed(table):
        pts = row['points']
        if pts > 0:
            key = f"{nutrient}_gt"
            if key in row and val > row[key]:
                return pts
        else:
            # points = 0
            key = f"{nutrient}_lte"
            if key in row and val <= row[key]:
                return 0
    return 0

def get_points_continuous(val, category_type, nutrient):
    """
    Linear interpolation between discrete steps for smoother gradients.
    """
    if val is None:
        return 0.0
        
    table = INR_TABLES[category_type]
    
    lower_pts = 0
    upper_pts = None
    lower_bound = 0.0
    upper_bound = None
    
    # Find the bounds
    # Find the bounds
    bounds = []
    # Collect all bounds in order of points
    for i, row in enumerate(table):
        pts = row['points']
        if pts == 0:
            key = f"{nutrient}_lte"
            if key in row:
                bounds.append((0, row[key]))
        else:
            key = f"{nutrient}_gt"
            if key in row:
                # The gt threshold of points N is the max value for points N-1
                bounds.append((pts - 1, row[key]))
                
    if not bounds:
        return 0.0
        
    if val <= bounds[0][1]:
        return float(bounds[0][0])
        
    for i in range(len(bounds) - 1):
        lower_pts, lower_bound = bounds[i]
        upper_pts, upper_bound = bounds[i+1]
        
        if lower_bound < val <= upper_bound:
            if upper_bound == lower_bound:
                return float(upper_pts) # Or lower_pts, they are the same value but maybe a jump
            fraction = (val - lower_bound) / (upper_bound - lower_bound)
            return float(lower_pts) + fraction
            
    # If it exceeded the last bound
    return float(bounds[-1][0] + 1)

def evaluate_hfss(nutrients):
    """
    Returns boolean indicating if product is HFSS.
    Nutrients dictionary expects energy in kcal, sugar in g, sat_fat in g, sodium in mg.
    """
    flags = []
    energy = nutrients.get('energy', 0) or 0
    
    if energy > 0:
        sugar = nutrients.get('sugars', 0) or 0
        sat_fat = nutrients.get('saturated_fat', 0) or 0
        sodium = nutrients.get('sodium', 0) or 0
        
        sugar_energy_pct = (sugar * 4 / energy) * 100
        sat_fat_energy_pct = (sat_fat * 9 / energy) * 100
        sodium_mg_per_kcal = sodium / energy
        
        if sugar_energy_pct >= HFSS_THRESHOLDS['hfss_thresholds']['sugar_energy_pct_min']:
            flags.append('high_sugar')
        if sat_fat_energy_pct >= HFSS_THRESHOLDS['hfss_thresholds']['sat_fat_energy_pct_min']:
            flags.append('high_sat_fat')
        if sodium_mg_per_kcal >= HFSS_THRESHOLDS['hfss_thresholds']['sodium_mg_per_kcal_min']:
            flags.append('high_sodium')
            
    return len(flags) > 0, flags

def calculate_nutrition_score(category_1, energy_kj, sugars_g, sat_fat_g, sodium_mg, fv_nlm_pct, fibre_g, protein_g):
    cat = 'solid' if category_1.lower() == 'solid' else 'liquid'
    
    a_points = 0.0
    a_points += get_points_continuous(energy_kj, cat, 'energy')
    a_points += get_points_continuous(sugars_g, cat, 'sugars')
    a_points += get_points_continuous(sat_fat_g, cat, 'sat_fat')
    a_points += get_points_continuous(sodium_mg, cat, 'sodium')
    
    c_points = 0.0
    fv_points = get_points_continuous(fv_nlm_pct, cat, 'fv') # assume fv covers nlm too for simplicity
    c_points += fv_points
    c_points += get_points_continuous(fibre_g, cat, 'fibre')
    
    # Protein scoring rule: if A points >= 11 and FV points < 5, protein points are ignored
    protein_pts = get_points_continuous(protein_g, cat, 'protein')
    if a_points >= 11 and fv_points < 5:
        # ignore protein
        pass
    else:
        c_points += protein_pts
        
    final_score = a_points - c_points
    return final_score
