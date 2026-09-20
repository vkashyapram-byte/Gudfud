import os
from urllib.parse import urlparse, urlencode, parse_qsl, urlunparse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

raw_url = os.getenv("DATABASE_URL", "postgresql://postgres:postgrespassword@localhost:5432/gudfud")

# psycopg2 does not support the 'pgbouncer' query parameter, so strip it out if present
parsed = urlparse(raw_url)
if parsed.query:
    qs = parse_qsl(parsed.query)
    qs = [(k, v) for k, v in qs if k != 'pgbouncer']
    parsed = parsed._replace(query=urlencode(qs))
    SQLALCHEMY_DATABASE_URL = urlunparse(parsed)
else:
    SQLALCHEMY_DATABASE_URL = raw_url

if SQLALCHEMY_DATABASE_URL.startswith("postgres://"):
    SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
