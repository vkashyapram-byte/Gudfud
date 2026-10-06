import yaml
import csv
import re
import os

_ingredient_dict_cache = None
def load_ingredient_dict():
    global _ingredient_dict_cache
    if _ingredient_dict_cache is None:
        path = os.path.join(os.path.dirname(__file__), '..', 'config', 'ingredient_dictionary_india.yaml')
        with open(path, 'r') as f:
            _ingredient_dict_cache = yaml.safe_load(f)
    return _ingredient_dict_cache

_additives_dict_cache = None
def load_additives_dict():
    global _additives_dict_cache
    if _additives_dict_cache is None:
        path = os.path.join(os.path.dirname(__file__), '..', 'config', 'additives_india.csv')
        additives = {}
        with open(path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                additives[row['ins_code'].strip().lower()] = {
                    'tier': int(row['tier']),
                    'evidence': row['evidence']
                }
        _additives_dict_cache = additives
    return _additives_dict_cache

def canonicalize_node(node, ing_dict):
    """
    Recursively maps nodes to canonical ids and groups.
    """
    node_name_lower = node.name.lower().strip()
    # Direct alias match
    if node_name_lower in ing_dict.get('aliases', {}):
        node.canonical_id = ing_dict['aliases'][node_name_lower]
        node.group = ing_dict.get('groups', {}).get(node.canonical_id)
    else:
        # Fallback keyword match
        for alias, can_id in ing_dict.get('aliases', {}).items():
            if alias in node_name_lower:
                node.canonical_id = can_id
                node.group = ing_dict.get('groups', {}).get(can_id)
                break
                
    for child in node.children:
        canonicalize_node(child, ing_dict)

def estimate_percentages(nodes, parent_pct=100.0):
    """
    Basic heuristic to estimate percentage if missing.
    Ensures monotonic decrease.
    """
    # First pass: set declared
    for node in nodes:
        if node.declared_pct is not None:
            node.estimated_pct = node.declared_pct
            node.estimate_method = 'declared'
            
    # Simple fallback: if no declared, distribute evenly
    missing_count = sum(1 for n in nodes if n.estimated_pct is None)
    if missing_count > 0:
        allocated = sum(n.estimated_pct for n in nodes if n.estimated_pct is not None)
        remaining = max(0, parent_pct - allocated)
        even_split = remaining / missing_count
        
        # enforce monotonic (very naive version: just give them all the same)
        for node in nodes:
            if node.estimated_pct is None:
                node.estimated_pct = even_split
                node.estimate_method = 'even_split'
                
    # Recursive for children
    for node in nodes:
        if node.children:
            estimate_percentages(node.children, parent_pct=node.estimated_pct or 0)

def score_ingredients(nodes, nova_class=None):
    ing_dict = load_ingredient_dict()
    additives_dict = load_additives_dict()
    
    # 1. Canonicalize and Estimate
    for node in nodes:
        canonicalize_node(node, ing_dict)
    estimate_percentages(nodes)
    
    score = 100
    reasons = []
    red_flag = False
    
    # Track items
    added_sugars = set()
    total_added_sugar_pct = 0
    fat_quality_penalty = 0
    additive_tiers_sum = 0
    additives_seen = set()
    has_artificial_flavour = False
    
    def traverse(node):
        nonlocal total_added_sugar_pct, fat_quality_penalty, additive_tiers_sum, has_artificial_flavour, red_flag
        
        if node.group == 'added_sugar':
            added_sugars.add(node.canonical_id)
            total_added_sugar_pct += (node.estimated_pct or 0)
            
        if node.group == 'hydrogenated_fat':
            fat_quality_penalty += (node.estimated_pct or 0) * 1.5 # 1.5 multiplier
        elif node.group == 'refined_oil':
            fat_quality_penalty += (node.estimated_pct or 0) * 0.5
            
        if node.group == 'flavour_artificial':
            has_artificial_flavour = True
            
        # Additives
        for code in node.ins_codes:
            code_lower = code.lower().replace(' ', '')
            if code_lower not in additives_seen:
                additives_seen.add(code_lower)
                # Check tier
                info = additives_dict.get(code_lower)
                if info:
                    tier = info['tier']
                    additive_tiers_sum += tier * 2 # 2 points per tier level
                    if tier == 3:
                        red_flag = True
                        reasons.append({"factor": "additives", "source": info['evidence'], "points": -25})
                else:
                    # Missing in dict -> assumed safe GMP for now (Tier 0)
                    pass
                    
        for child in node.children:
            traverse(child)

    for node in nodes:
        traverse(node)
        
    # Processing Level (NOVA)
    if nova_class == 4:
        score -= 35
        reasons.append({"factor": "nova_4", "points": -35})
    elif nova_class == 3:
        score -= 15
        reasons.append({"factor": "nova_3", "points": -15})
    elif nova_class == 2:
        score -= 5
        reasons.append({"factor": "nova_2", "points": -5})
        
    # Added Sugars
    if total_added_sugar_pct > 0:
        sugar_penalty = total_added_sugar_pct * 0.5 + len(added_sugars) * 2
        score -= sugar_penalty
        reasons.append({"factor": "added_sugar", "points": -sugar_penalty})
        
    # Fat Quality
    if fat_quality_penalty > 0:
        score -= fat_quality_penalty
        reasons.append({"factor": "fat_quality", "points": -fat_quality_penalty})
        
    # Refined Base
    if nodes and nodes[0].group == 'refined_grain':
        score -= 10
        reasons.append({"factor": "refined_base", "points": -10})
    if nodes and nodes[0].group in ['whole_grain', 'nut_legume_millet']:
        if (nodes[0].estimated_pct or 0) >= 20:
            score += 5
            reasons.append({"factor": "whole_food_base", "points": 5})
            
    # Flavours
    if has_artificial_flavour:
        score -= 5
        reasons.append({"factor": "artificial_flavour", "points": -5})
        
    # Additives
    additive_penalty = min(25, additive_tiers_sum)
    if additive_penalty > 0:
        score -= additive_penalty
        reasons.append({"factor": "additives", "points": -additive_penalty})
        
    # Clip
    score = max(0, min(100, score))
    
    return {
        "ingredient_score": round(score, 1),
        "red_flag": red_flag,
        "reasons": reasons
    }
