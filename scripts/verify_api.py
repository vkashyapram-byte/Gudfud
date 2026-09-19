#!/usr/bin/env python3
import os
import sys
import json
import time
import urllib.request
import urllib.error
import ssl

def main():
    api_url = os.environ.get("API_URL")
    if not api_url and len(sys.argv) > 1:
        api_url = sys.argv[1]

    if not api_url:
        print("FAIL: API_URL environment variable or command line argument is not set.")
        sys.exit(1)

    api_url = api_url.rstrip("/")
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    print(f"Verifying API: {api_url}")

    # Check 1: GET /v1/catalogue
    catalogue_url = f"{api_url}/v1/catalogue"
    start_time = time.time()
    try:
        req = urllib.request.Request(catalogue_url, headers={'User-Agent': 'VerifyAPI/1.0'})
        with urllib.request.urlopen(req, timeout=15, context=ctx) as response:
            status = response.status
            body = response.read().decode('utf-8')
            elapsed = (time.time() - start_time) * 1000

            if status != 200:
                print(f"FAIL: GET /v1/catalogue returned HTTP {status} in {elapsed:.0f}ms.")
                sys.exit(1)
            
            data = json.loads(body)
            items = data.get("items", [])
            if not items:
                print(f"FAIL: GET /v1/catalogue returned 0 items in {elapsed:.0f}ms.")
                sys.exit(1)
            
            print(f"PASS: GET /v1/catalogue returned HTTP {status} with {len(items)} items in {elapsed:.0f}ms.")
    
    except urllib.error.HTTPError as e:
        elapsed = (time.time() - start_time) * 1000
        print(f"FAIL: GET /v1/catalogue returned HTTP {e.code} in {elapsed:.0f}ms.")
        sys.exit(1)
    except Exception as e:
        elapsed = (time.time() - start_time) * 1000
        print(f"FAIL: GET /v1/catalogue failed in {elapsed:.0f}ms. Error: {e}")
        sys.exit(1)

    # Check 2: POST /v1/admin/worker/process
    worker_url = f"{api_url}/v1/admin/worker/process"
    start_time = time.time()
    try:
        req = urllib.request.Request(worker_url, data=b"", headers={'User-Agent': 'VerifyAPI/1.0'})
        req.get_method = lambda: 'POST'
        with urllib.request.urlopen(req, timeout=15, context=ctx) as response:
            status = response.status
            elapsed = (time.time() - start_time) * 1000
            print(f"FAIL: POST /v1/admin/worker/process unexpectedly returned HTTP {status} in {elapsed:.0f}ms. Route guard missing.")
            sys.exit(1)

    except urllib.error.HTTPError as e:
        elapsed = (time.time() - start_time) * 1000
        if e.code in (401, 403):
            print(f"PASS: POST /v1/admin/worker/process returned HTTP {e.code} in {elapsed:.0f}ms. Route guard active.")
        else:
            print(f"FAIL: POST /v1/admin/worker/process returned HTTP {e.code} in {elapsed:.0f}ms. Expected 401 or 403.")
            sys.exit(1)
    except Exception as e:
        elapsed = (time.time() - start_time) * 1000
        print(f"FAIL: POST /v1/admin/worker/process failed in {elapsed:.0f}ms. Error: {e}")
        sys.exit(1)

    sys.exit(0)

if __name__ == "__main__":
    main()
