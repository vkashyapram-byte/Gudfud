import os
import sys

# Removed SQLite override to use actual Postgres DATABASE_URL from Vercel config
# Fix python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.main import app
