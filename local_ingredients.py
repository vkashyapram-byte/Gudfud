import asyncio
from sqlalchemy import select, create_engine, text
from sqlalchemy.orm import Session

DATABASE_URL = "postgresql://postgres:postgrespassword@localhost:5432/gudfud"
engine = create_engine(DATABASE_URL)

def main():
    with Session(engine) as session:
        # Insert unique ingredients
        session.execute(text("""
        INSERT INTO ingredient (id, slug, canonical_name, ingredient_type, public_summary, status)
        SELECT 
            gen_random_uuid(),
            trim(BOTH '-' FROM regexp_replace(lower(trim(label_text)), '[^a-z0-9]+', '-', 'g')),
            trim(label_text),
            'Unknown',
            'Information for ' || trim(label_text) || ' will be populated later.',
            'active'
        FROM (SELECT DISTINCT label_text FROM label_ingredient WHERE label_text IS NOT NULL AND trim(label_text) != '') AS unique_labels
        ON CONFLICT (slug) DO NOTHING;
        """))
        
        # Link them
        session.execute(text("""
        UPDATE label_ingredient
        SET ingredient_id = i.id
        FROM ingredient i
        WHERE trim(BOTH '-' FROM regexp_replace(lower(trim(label_ingredient.label_text)), '[^a-z0-9]+', '-', 'g')) = i.slug
        AND label_ingredient.ingredient_id IS NULL;
        """))
        
        session.commit()
        print("Updated local database.")

if __name__ == "__main__":
    main()
