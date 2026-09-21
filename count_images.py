import os
from sqlmodel import Session, create_engine, text

DATABASE_URL = "postgresql://postgres.cynbftllkqcwslnnvydu:JYavQICA4BGECz6G@aws-0-ap-southeast-2.pooler.supabase.com:6543/postgres?pgbouncer=true"
engine = create_engine(DATABASE_URL)

with Session(engine) as session:
    count_all = session.execute(text("SELECT COUNT(*) FROM label_versions")).scalar()
    count_images = session.execute(text("SELECT COUNT(*) FROM label_versions WHERE label_image_id IS NOT NULL")).scalar()
    print(f"Total Labels: {count_all}")
    print(f"Labels with Images: {count_images}")
