from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql://postgres:postgrespassword@localhost:5432/gudfud"
engine = create_engine(DATABASE_URL)

def main():
    with engine.connect() as conn:
        with open('ingredient_updates.sql', 'r') as f:
            sql = f.read()
            for stmt in sql.split(';'):
                stmt = stmt.strip()
                if stmt:
                    try:
                        conn.execute(text(stmt))
                    except Exception as e:
                        print(f"Error executing: {stmt[:50]}... -> {e}")
            conn.commit()
    print("Local updates applied successfully.")

if __name__ == "__main__":
    main()
