import asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

DATABASE_URL = "postgresql://postgres:postgrespassword@localhost:5432/gudfud"
engine = create_engine(DATABASE_URL)

def main():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'ingredient'"))
        for row in result:
            print(row)

if __name__ == "__main__":
    from sqlalchemy import text
    main()
