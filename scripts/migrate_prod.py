import os
import urllib.parse
from sqlalchemy import create_engine, text

raw_url = os.getenv("DATABASE_URL")
if raw_url.startswith("postgres://"):
    raw_url = raw_url.replace("postgres://", "postgresql://", 1)

# Ensure pgbouncer param is removed for SQLAlchemy
parsed = urllib.parse.urlparse(raw_url)
if parsed.query:
    qs = urllib.parse.parse_qsl(parsed.query)
    qs = [(k, v) for k, v in qs if k != 'pgbouncer']
    parsed = parsed._replace(query=urllib.parse.urlencode(qs))
    DATABASE_URL = urllib.parse.urlunparse(parsed)
else:
    DATABASE_URL = raw_url

print(f"Connecting to {DATABASE_URL}")
engine = create_engine(DATABASE_URL)

with engine.connect() as conn:
    print("Creating extension pg_trgm...")
    conn.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm;"))
    conn.commit()
    
    print("Adding declared_percent column...")
    conn.execute(text("ALTER TABLE label_ingredient ADD COLUMN IF NOT EXISTS declared_percent NUMERIC;"))
    conn.commit()
    
    print("Truncating tables...")
    conn.execute(text("TRUNCATE TABLE label_ingredient, ingredient_evidence, nutrition_facts, rating, label_version, product_variant, product, category, brand, ingredient, market RESTART IDENTITY CASCADE;"))
    conn.commit()
    
    print("Migration & Truncation complete.")
