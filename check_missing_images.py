from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql://postgres:postgrespassword@localhost:5432/gudfud"
engine = create_engine(DATABASE_URL)

def main():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT count(*) FROM ingredient WHERE image_url IS NULL"))
        print(f"Missing images: {result.fetchone()[0]}")
        
        result2 = conn.execute(text("SELECT canonical_name FROM ingredient WHERE image_url IS NULL LIMIT 20"))
        print("Some missing ingredients:")
        for row in result2:
            print(f"- {row[0]}")

if __name__ == "__main__":
    main()
