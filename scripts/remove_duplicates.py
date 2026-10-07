import os
from sqlalchemy import create_engine, text

DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://postgres.cynbftllkqcwslnnvydu:JYavQICA4BGECz6G@aws-0-ap-southeast-2.pooler.supabase.com:6543/postgres")
engine = create_engine(DATABASE_URL)

def remove_duplicates():
    query = text("""
        DELETE FROM rating 
        WHERE id IN (
            SELECT id 
            FROM (
                SELECT id, row_number() over (partition by label_version_id order by calculated_at desc) as rn
                FROM rating
            ) t
            WHERE rn > 1
        );
    """)
    with engine.connect() as conn:
        result = conn.execute(query)
        conn.commit()
        print(f"Deleted {result.rowcount} duplicate rating rows.")

if __name__ == "__main__":
    remove_duplicates()
