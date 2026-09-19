import os
import sys

# Ensure serverless environment uses our pre-seeded local database
os.environ["DATABASE_URL"] = "sqlite:///prod.db"

# Fix python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + '/..'))

from src.main import app
