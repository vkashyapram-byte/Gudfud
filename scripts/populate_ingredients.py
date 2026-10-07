import os
import sys
from sqlalchemy.orm import Session

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database import SessionLocal
from src import models

def create_ingredient(db, slug, name, ins, e_num, type_, function, summary, gras):
    existing = db.query(models.Ingredient).filter(models.Ingredient.slug == slug).first()
    if existing:
        return
    
    ing = models.Ingredient(
        slug=slug,
        canonical_name=name,
        INS_number=ins,
        E_number=e_num,
        ingredient_type=type_,
        technical_function=function,
        public_summary=summary,
        status="active",
        is_generally_safe=gras
    )
    db.add(ing)

def run():
    db = SessionLocal()
    try:
        ingredients_data = [
            ("aspartame", "Aspartame", "951", "E951", "Artificial Sweetener", "Sweetener", "An artificial non-saccharide sweetener used as a sugar substitute in some foods and beverages.", True),
            ("sucralose", "Sucralose", "955", "E955", "Artificial Sweetener", "Sweetener", "A zero-calorie artificial sweetener made from sugar. Commonly found in diet drinks.", True),
            ("msg", "Monosodium Glutamate", "621", "E621", "Flavor Enhancer", "Flavor Enhancer", "Used to enhance the savory, umami flavor of foods. FDA considers it generally recognized as safe.", True),
            ("carmine", "Carmine", "120", "E120", "Colorant", "Food Color", "A red food color extracted from the crushed shells of cochineal insects.", True),
            ("titanium-dioxide", "Titanium Dioxide", "171", "E171", "Colorant", "Food Color", "Used to make foods white and bright. Banned in the EU as a food additive due to genotoxicity concerns.", False),
            ("sodium-benzoate", "Sodium Benzoate", "211", "E211", "Preservative", "Preservative", "A common preservative in acidic foods such as salad dressings, carbonated drinks, and condiments.", True),
            ("high-fructose-corn-syrup", "High Fructose Corn Syrup", None, None, "Sweetener", "Sweetener", "A sweetener made from corn starch. Strongly associated with obesity and metabolic syndrome.", True),
            ("carrageenan", "Carrageenan", "407", "E407", "Thickener", "Thickener / Stabilizer", "Extracted from red edible seaweeds. Used to thicken and stabilize foods like almond milk and yogurt. Controversial due to potential gastrointestinal inflammation.", True),
            ("xanthan-gum", "Xanthan Gum", "415", "E415", "Thickener", "Thickener / Stabilizer", "A popular food additive used as a thickener or stabilizer. Produced by bacterial fermentation.", True),
            ("soy-lecithin", "Soy Lecithin", "322", "E322(i)", "Emulsifier", "Emulsifier", "Extracted from soybeans, used to mix ingredients that typically separate, like oil and water.", True),
            ("red-40", "Red 40 (Allura Red AC)", "129", "E129", "Colorant", "Food Color", "An artificial red dye. Some studies suggest a link to hyperactivity in children.", True),
            ("yellow-5", "Yellow 5 (Tartrazine)", "102", "E102", "Colorant", "Food Color", "An artificial yellow dye. Can cause allergic reactions in a small portion of the population.", True),
            ("maltodextrin", "Maltodextrin", None, None, "Carbohydrate", "Thickener / Filler", "A highly processed carbohydrate derived from starch, often used as a filler or thickener. High glycemic index.", True),
            ("potassium-sorbate", "Potassium Sorbate", "202", "E202", "Preservative", "Preservative", "Used to suppress mold and yeast growth in foods like cheese, wine, and baked goods.", True),
            ("citric-acid", "Citric Acid", "330", "E330", "Acid", "Acidity Regulator / Preservative", "Naturally occurs in citrus fruits, but commercially produced via mold fermentation. Used for tartness and preservation.", True),
            ("bht", "Butylated Hydroxytoluene (BHT)", "321", "E321", "Preservative", "Antioxidant", "A synthetic antioxidant used to prevent oils from going rancid. Banned in some countries due to potential health concerns.", False),
            ("bha", "Butylated Hydroxyanisole (BHA)", "320", "E320", "Preservative", "Antioxidant", "Used alongside BHT to preserve fats. Reasonably anticipated to be a human carcinogen by the NIH.", False),
            ("guar-gum", "Guar Gum", "412", "E412", "Thickener", "Thickener / Stabilizer", "Made from guar beans. High in soluble fiber and used extensively in gluten-free baking.", True),
            ("erythritol", "Erythritol", "968", "E968", "Sweetener", "Sweetener", "A sugar alcohol used as a low-calorie sweetener. Recently linked to potential cardiovascular risks in high amounts.", True),
            ("stevia", "Stevia Extract", "960", "E960", "Natural Sweetener", "Sweetener", "A natural, zero-calorie sweetener derived from the leaves of the Stevia rebaudiana plant.", True)
        ]
        
        for ing_data in ingredients_data:
            create_ingredient(db, *ing_data)
            
        db.commit()
        print("Successfully populated 20 common ingredients.")
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    run()
