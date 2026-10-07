import asyncio
from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql://postgres:postgrespassword@localhost:5432/gudfud"
engine = create_engine(DATABASE_URL)

def main():
    with engine.connect() as conn:
        result = conn.execute(text("""
        SELECT i.canonical_name, i.slug, count(li.id) as freq 
        FROM ingredient i 
        JOIN label_ingredient li ON i.id = li.ingredient_id
        GROUP BY i.id 
        ORDER BY freq DESC 
        LIMIT 20;
        """))
        for row in result:
            print(f"{row[0]} ({row[1]}): {row[2]}")

if __name__ == "__main__":
    main()
