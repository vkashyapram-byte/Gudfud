import asyncio
from sqlalchemy import select, create_engine
from sqlalchemy.orm import Session
from src.models import LabelVersion

DATABASE_URL = "postgresql://postgres:postgrespassword@localhost:5432/gudfud"
engine = create_engine(DATABASE_URL)

def main():
    with Session(engine) as session:
        stmt = select(LabelVersion.ingredients_raw)
        raw_ingredients_lists = session.execute(stmt).scalars().all()
        
        print(f"Found {len(raw_ingredients_lists)} LabelVersions.")
        
        # Count how many are non-null
        non_null = [i for i in raw_ingredients_lists if i]
        print(f"Found {len(non_null)} non-null ingredients_raw.")
        if len(non_null) > 0:
            print("Sample:")
            print(non_null[0][:200])

if __name__ == "__main__":
    main()
