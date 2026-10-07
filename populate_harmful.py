import asyncio
from sqlalchemy import create_engine, text
import uuid

DATABASE_URL = "postgresql://postgres:postgrespassword@localhost:5432/gudfud"
engine = create_engine(DATABASE_URL)

HARMFUL_INGREDIENTS = {
    "aspartame": {
        "summary": "Aspartame is an artificial non-saccharide sweetener used as a sugar substitute. While approved by many agencies, the WHO's IARC classified aspartame as 'possibly carcinogenic to humans' (Group 2B) in 2023, though the JECFA reaffirmed acceptable daily intake levels.",
        "effect": "Possible Carcinogen",
        "grade": "warning"
    },
    "sucralose": {
        "summary": "Sucralose is an artificial sweetener. Recent studies suggest it may alter gut microbiome composition and negatively affect glucose tolerance. Some evidence points to it causing DNA damage in high concentrations.",
        "effect": "Gut Microbiome Disruption",
        "grade": "warning"
    },
    "high-fructose-corn-syrup": {
        "summary": "High Fructose Corn Syrup (HFCS) is a liquid sweetener. Its high consumption is strongly linked to obesity, insulin resistance, type 2 diabetes, and non-alcoholic fatty liver disease (NAFLD).",
        "effect": "Metabolic Disruption",
        "grade": "harmful"
    },
    "carrageenan": {
        "summary": "Carrageenan is an extract from red seaweed used as a thickener. Degraded carrageenan can cause gastrointestinal inflammation and intestinal lesions. Even food-grade carrageenan is suspected by some researchers to trigger inflammation.",
        "effect": "Gastrointestinal Inflammation",
        "grade": "warning"
    },
    "bha": {
        "summary": "Butylated Hydroxyanisole (BHA) is a synthetic antioxidant used as a preservative. The National Institutes of Health (NIH) considers BHA 'reasonably anticipated to be a human carcinogen' based on animal studies.",
        "effect": "Endocrine Disruptor / Possible Carcinogen",
        "grade": "harmful"
    },
    "bht": {
        "summary": "Butylated Hydroxytoluene (BHT) is a preservative structurally similar to BHA. Animal studies indicate potential liver enlargement and carcinogenic effects at high doses.",
        "effect": "Potential Organ Toxicity",
        "grade": "warning"
    },
    "red-40-allura-red-ac": {
        "summary": "Red 40 is a synthetic food dye. It has been associated with hypersensitivity reactions and increased hyperactivity in children. Some European countries require warning labels on foods containing it.",
        "effect": "Hyperactivity in Children",
        "grade": "warning"
    },
    "yellow-5-tartrazine": {
        "summary": "Yellow 5 (Tartrazine) is a synthetic lemon yellow azo dye. It is known to cause allergic reactions, asthma, and skin rashes in a small percentage of the population, and is linked to hyperactivity in children.",
        "effect": "Allergic Reactions / Hyperactivity",
        "grade": "warning"
    },
    "titanium-dioxide": {
        "summary": "Titanium Dioxide is a white pigment used to enhance color. In 2021, the European Food Safety Authority (EFSA) declared it can no longer be considered safe as a food additive due to concerns over genotoxicity (DNA damage).",
        "effect": "Genotoxicity",
        "grade": "harmful"
    },
    "sodium-benzoate": {
        "summary": "Sodium Benzoate is a preservative. When combined with ascorbic acid (Vitamin C), it can form benzene, a known carcinogen. It may also exacerbate hyperactivity in children.",
        "effect": "Benzene Formation Risk",
        "grade": "warning"
    }
}

def main():
    updates = []
    
    with engine.connect() as conn:
        for slug, info in HARMFUL_INGREDIENTS.items():
            # Check if it exists
            res = conn.execute(text(f"SELECT id FROM ingredient WHERE slug = '{slug}'"))
            row = res.fetchone()
            if row:
                ing_id = row[0]
                # Update the ingredient
                summary_escaped = info['summary'].replace("'", "''")
                updates.append(f"UPDATE ingredient SET is_generally_safe = false, public_summary = '{summary_escaped}' WHERE id = '{ing_id}';")
                
                # Delete existing evidence
                updates.append(f"DELETE FROM ingredient_evidence WHERE ingredient_id = '{ing_id}';")
                
                # Insert evidence
                ev_id = str(uuid.uuid4())
                updates.append(f"""
                INSERT INTO ingredient_evidence (id, ingredient_id, effect_type, evidence_grade, summary, created_at, updated_at) 
                VALUES ('{ev_id}', '{ing_id}', '{info['effect']}', '{info['grade']}', '{summary_escaped}', NOW(), NOW());
                """)
                
    with open('harmful_updates.sql', 'w') as f:
        f.write("\n".join(updates))
        
    print(f"Generated harmful_updates.sql with {len(updates)} statements.")

if __name__ == "__main__":
    main()
