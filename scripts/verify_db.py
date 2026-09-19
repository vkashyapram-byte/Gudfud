#!/usr/bin/env python3
import os
import sys
from sqlalchemy import create_engine, text

def main():
    # Load .env into os.environ if it exists
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, val = line.split('=', 1)
                    if key.strip() not in os.environ:
                        os.environ[key.strip()] = val.strip()

    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        print("FAIL: DATABASE_URL environment variable is not set.")
        sys.exit(1)

    print(f"Connecting to database via DATABASE_URL...")
    
    try:
        engine = create_engine(database_url)
        with engine.connect() as conn:
            # Check all core tables using actual database schema names
            expected_tables = [
                'brand', 'category', 'product', 'product_variant', 
                'label_version', 'nutrition_facts', 'ingredient', 
                'rating', 'outbox_event', 'audit_log'
            ]
            
            missing_tables = []
            for table in expected_tables:
                result = conn.execute(text(
                    "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = :table_name)"
                ), {"table_name": table}).scalar()
                
                if not result:
                    missing_tables.append(table)
            
            if missing_tables:
                print(f"FAIL: The following required tables are missing: {', '.join(missing_tables)}")
                sys.exit(1)
            else:
                print("PASS: All required tables exist.")

            # Query product variants count and list
            products = conn.execute(text(
                """
                SELECT p.canonical_name, pv.gtin 
                FROM product_variant pv
                JOIN product p ON p.id = pv.product_id
                """
            )).fetchall()
            
            count = len(products)
            if count == 0:
                print("FAIL: Product count is 0. Data seed was not applied properly.")
                sys.exit(1)
                
            print(f"PASS: Found {count} imported product variants.")
            print("IMPORTED PRODUCTS:")
            for p in products:
                print(f"- GTIN: {p.gtin} | Name: {p.canonical_name}")

    except Exception as e:
        print(f"FAIL: Database connection or query failed. Error: {e}")
        sys.exit(1)

    print("VERIFICATION COMPLETE: ALL PASS.")
    sys.exit(0)

if __name__ == "__main__":
    main()
