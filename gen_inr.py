import yaml

def generate_solid():
    rows = []
    # Points 0 to 25
    energy = [80, 80, 160, 240, 320, 400, 480, 560, 640, 720, 800] + [None]*15
    satfat = [1.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 34, 36, 38, 40]
    sugars = [4.2, 4.2, 8.4, 12.6, 16.8, 21.0, 25.2, 29.4, 33.6, 37.8, 42.0, 46.2, 50.4, 54.6, 58.8, 63.0, 67.2, 71.4, 75.6, 79.8, 84.0] + [None]*5
    sodium = [90, 90, 180, 270, 360, 450, 540, 630, 720, 810, 900, 990, 1080, 1170, 1260, 1350, 1440, 1530, 1620, 1710, 1800, 1890, 1980, 2070, 2160, 2250]
    
    fv = [10, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55] + [None]*15
    nlm = [10, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55] + [None]*15
    fibre = [3, 3, 6, 9, 12, 15, 18, 21, 24, 27, 30] + [None]*15
    protein = [1.5, 1.5, 2.0, 2.5, 3.0, 5.0, 7.0, 10.0, 15.0, 20.0, 25.0, 30.0, 35.0, 40.0, 45.0, 50.0] + [None]*10
    
    for i in range(26):
        row = {"points": i}
        if i == 0:
            if energy[0] is not None: row["energy_lte"] = energy[0]
            if satfat[0] is not None: row["sat_fat_lte"] = satfat[0]
            if sugars[0] is not None: row["sugars_lte"] = sugars[0]
            if sodium[0] is not None: row["sodium_lte"] = sodium[0]
            if fv[0] is not None: row["fv_lte"] = fv[0]
            if nlm[0] is not None: row["nlm_lte"] = nlm[0]
            if fibre[0] is not None: row["fibre_lte"] = fibre[0]
            if protein[0] is not None: row["protein_lte"] = protein[0]
        else:
            if i < len(energy) and energy[i] is not None: row["energy_gt"] = energy[i]
            if i < len(satfat) and satfat[i] is not None: row["sat_fat_gt"] = satfat[i]
            if i < len(sugars) and sugars[i] is not None: row["sugars_gt"] = sugars[i]
            if i < len(sodium) and sodium[i] is not None: row["sodium_gt"] = sodium[i]
            if i < len(fv) and fv[i] is not None: row["fv_gt"] = fv[i]
            if i < len(nlm) and nlm[i] is not None: row["nlm_gt"] = nlm[i]
            if i < len(fibre) and fibre[i] is not None: row["fibre_gt"] = fibre[i]
            if i < len(protein) and protein[i] is not None: row["protein_gt"] = protein[i]
        rows.append(row)
    return rows

def generate_liquid():
    rows = []
    # Points 0 to 15
    energy = [6, 6, 12, 18, 24, 30, 36, 42, 48, 54, 60] + [None]*5
    sugars = [0.1, 0.1, 1.6, 3.1, 4.6, 6.1, 7.6, 9.1, 10.6, 12.1, 13.6] + [None]*5
    fv = [5, 5, 10, 15, 20, 25, 30, 35, 40, 45, 55] + [None]*5
    protein = [1.5, 1.5, 2.0, 2.5, 3.0, 5.0, 7.0, 10.0, 15.0, 20.0, 25.0, 30.0, 35.0, 40.0, 45.0, 50.0]
    
    for i in range(16):
        row = {"points": i}
        if i == 0:
            if energy[0] is not None: row["energy_lte"] = energy[0]
            if sugars[0] is not None: row["sugars_lte"] = sugars[0]
            if fv[0] is not None: row["fv_lte"] = fv[0]
            if protein[0] is not None: row["protein_lte"] = protein[0]
        else:
            if i < len(energy) and energy[i] is not None: row["energy_gt"] = energy[i]
            if i < len(sugars) and sugars[i] is not None: row["sugars_gt"] = sugars[i]
            if i < len(fv) and fv[i] is not None: row["fv_gt"] = fv[i]
            if i < len(protein) and protein[i] is not None: row["protein_gt"] = protein[i]
        rows.append(row)
    return rows

data = {
    "solid": generate_solid(),
    "liquid": generate_liquid()
}

with open('config/inr_tables.yaml', 'w') as f:
    yaml.dump(data, f, sort_keys=False)
print("config/inr_tables.yaml generated")
