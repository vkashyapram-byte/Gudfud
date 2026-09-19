#!/usr/bin/env python3
import subprocess
import os
import sys
import urllib.request
import json
from sqlalchemy import create_engine, text

def check_git_state():
    print("Checking Git State...")
    try:
        # Check for uncommitted changes
        status = subprocess.check_output(['git', 'status', '--porcelain']).decode('utf-8').strip()
        if status:
            print("FAIL: Uncommitted changes detected in git.")
            return False
        
        # Check for detached head or ahead of remote
        branch_info = subprocess.check_output(['git', 'branch', '-v']).decode('utf-8')
        if '* (HEAD detached' in branch_info or 'ahead' in branch_info:
            print("FAIL: Git head is detached or branch is ahead of remote.")
            return False
            
        print("PASS: Git state is clean.")
        return True
    except subprocess.CalledProcessError:
        print("FAIL: Failed to execute git commands.")
        return False

def check_database_state():
    print("Checking Database State...")
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        print("FAIL: DATABASE_URL environment variable is not set.")
        return False
        
    try:
        engine = create_engine(db_url)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT count(*) FROM product_variant"))
            count = result.scalar()
            if count > 0:
                print(f"PASS: Database seed data persisted ({count} product variants found).")
                return True
            else:
                print("FAIL: No seed data found in product_variant table.")
                return False
    except Exception as e:
        print(f"FAIL: Database connection or query failed. Error: {str(e)}")
        return False

def check_environment_binding():
    print("Checking Environment Binding...")
    # Attempt to read .env file directly since os.environ might not have it if not exported
    env_vars = {}
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, val = line.split('=', 1)
                    env_vars[key.strip()] = val.strip()
    
    api_url = env_vars.get("NEXT_PUBLIC_API_URL") or os.environ.get("NEXT_PUBLIC_API_URL")
    
    if not api_url:
        print("FAIL: NEXT_PUBLIC_API_URL is not set.")
        return False

    forbidden_domains = ['localhost', '127.0.0.1', 'supabase.co', 'vercel.app']
    if any(domain in api_url for domain in forbidden_domains):
        print(f"FAIL: NEXT_PUBLIC_API_URL ({api_url}) contains a forbidden domain.")
        return False
        
    if 'onrender.com' not in api_url:
        print(f"FAIL: NEXT_PUBLIC_API_URL ({api_url}) is not a Render URL.")
        return False

    print(f"PASS: Environment binding correct ({api_url}).")
    return True

def check_live_api_ping():
    print("Checking Live API Ping...")
    env_vars = {}
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key, val = line.strip().split('=', 1)
                    env_vars[key.strip()] = val.strip()
                    
    api_url = env_vars.get("NEXT_PUBLIC_API_URL") or os.environ.get("NEXT_PUBLIC_API_URL")
    if not api_url:
        print("FAIL: NEXT_PUBLIC_API_URL is not available for ping.")
        return False

    endpoint = f"{api_url.rstrip('/')}/v1/catalogue"
    try:
        import ssl
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        
        req = urllib.request.Request(endpoint, headers={'User-Agent': 'AuditScript/1.0'})
        with urllib.request.urlopen(req, timeout=10, context=ctx) as response:
            if response.status != 200:
                print(f"FAIL: HTTP GET returned status {response.status}.")
                return False
            data = json.loads(response.read().decode('utf-8'))
            items = data.get('items', [])
            if not items:
                print("FAIL: HTTP GET successful but items array is empty.")
                return False
                
            print("PASS: Live API ping successful with non-empty items.")
            return True
    except Exception as e:
        print(f"FAIL: HTTP GET failed. Error: {str(e)}")
        return False

def main():
    print("--- GUD FUD SYSTEM AUDIT ---")
    
    # Load .env into os.environ
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, val = line.split('=', 1)
                    if key.strip() not in os.environ:
                        os.environ[key.strip()] = val.strip()

    checks = [
        check_git_state(),
        check_database_state(),
        check_environment_binding(),
        check_live_api_ping()
    ]
    
    print("--- AUDIT RESULTS ---")
    if all(checks):
        print("PASS: All checks succeeded.")
        sys.exit(0)
    else:
        print("FAIL: One or more checks failed.")
        sys.exit(1)

if __name__ == "__main__":
    main()
