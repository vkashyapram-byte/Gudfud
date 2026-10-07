import asyncio
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

DATABASE_URL = "postgresql://postgres:postgrespassword@localhost:5432/gudfud"
engine = create_engine(DATABASE_URL)

def main():
    with engine.connect() as conn:
        try:
            conn.execute(text("ALTER TABLE ingredient ADD COLUMN image_url character varying;"))
            conn.commit()
            print("Local alter successful.")
        except Exception as e:
            print(f"Error (maybe already exists): {e}")

if __name__ == "__main__":
    main()
