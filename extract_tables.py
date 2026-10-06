import re
import json

lines = open('fssai_draft.txt').read().split('\n')

solid_table = []
liquid_table = []
points_star = []

in_solid = False
in_liquid = False
in_stars = False

for line in lines:
    line = line.strip()
    if 'Table 2. INR Baseline points' in line:
        in_solid = True
        in_liquid = False
        continue
    if 'Table 3. INR Baseline points for Category-II' in line:
        in_solid = False
        in_liquid = True
        continue
    if 'Table 4.' in line:
        in_liquid = False
    
    if in_solid:
        # Match solid table rows
        m = re.match(r'^(\d+)\s+(?:≤|>)(\d+(?:\.\d+)?)\s+(?:≤|>)(\d+(?:\.\d+)?)\s+(?:≤|>)(\d+(?:\.\d+)?)\s+(?:≤|>)(\d+(?:\.\d+)?)\s+(?:≤|>)?(\d+(?:\.\d+)?)\s+(?:≤|>)?(\d+(?:\.\d+)?)\s+(?:≤|>)?(\d+(?:\.\d+)?)\s+(?:≤|>)?(\d+(?:\.\d+)?)$', line)
        if m:
            pts = int(m.group(1))
            energy = float(m.group(2))
            sat_fat = float(m.group(3))
            sugars = float(m.group(4))
            sodium = float(m.group(5))
            fv = float(m.group(6))
            nlm = float(m.group(7))
            fibre = float(m.group(8))
            protein = float(m.group(9))
            
            # The table is lower-bound except for 0 which is upper bound.
            # But wait, looking at the table:
            # 0: <=80
            # 1: >80
            # 2: >160
            # It means points=1 if >80 and <=160.
            # Actually, we can just store the bounds. For score N (N>0), the threshold is > X. So if value > X, it gets at least N points. We take the max N.
            
            solid_table.append({
                "points": pts,
                "energy_gt": energy if pts > 0 else 0,
                "sat_fat_gt": sat_fat if pts > 0 else 0,
                "sugars_gt": sugars if pts > 0 else 0,
                "sodium_gt": sodium if pts > 0 else 0,
                "fv_gt": fv if pts > 0 else 0,
                "nlm_gt": nlm if pts > 0 else 0,
                "fibre_gt": fibre if pts > 0 else 0,
                "protein_gt": protein if pts > 0 else 0
            })
        else:
            # Try to match incomplete rows (pts 11 to 25)
            # 11   >12 >46.2 >990      >30
            # Some columns are empty
            parts = line.split()
            if len(parts) >= 1 and parts[0].isdigit():
                pts = int(parts[0])
                if pts >= 11:
                    # Let's just manually fill these since there are only a few and regex is hard when columns are missing
                    pass

print("Extracted solid table rows:", len(solid_table))
