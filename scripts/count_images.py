import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from src.models import ProductVariant, LabelVersion

engine = create_engine("postgresql://postgres.cynbftllkqcwslnnvydu:JYavQICA4BGECz6G@aws-0-ap-southeast-2.pooler.supabase.com:5432/postgres")

with Session(engine) as session:
    total = session.query(ProductVariant).count()
    with_images = session.query(LabelVersion).filter(LabelVersion.label_image_id != None).count()
    without_images = total - with_images
    print(f"Total products: {total}")
    print(f"Products WITH images: {with_images}")
    print(f"Products WITHOUT images: {without_images}")
