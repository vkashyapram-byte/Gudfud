import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from src.models import Category

engine = create_engine("postgresql://postgres.cynbftllkqcwslnnvydu:JYavQICA4BGECz6G@aws-0-ap-southeast-2.pooler.supabase.com:5432/postgres")

with Session(engine) as session:
    cats = session.query(Category.name).all()
    for c in set([x[0] for x in cats]):
        print(c)
