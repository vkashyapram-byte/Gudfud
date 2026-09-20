import json

with open('scripts/bulk_import_products.py', 'r') as f:
    content = f.read()

# Replace the fetch_product function to add basic auth
fetch_code = """
def fetch_product(term):
    url = f"https://world.openfoodfacts.org/api/v2/search?search_terms={urllib.parse.quote(term)}&countries_tags=en:india&fields=code,brands,product_name,ingredients_text,ingredients,nutriments,categories_tags,image_url&page_size=1"
    req = urllib.request.Request(url, headers={'User-Agent': 'GudFud-Data-Importer/1.0'})
    
    # Add Basic Auth
    import base64
    auth_string = "kashiii:Sudopassword"
    base64string = base64.b64encode(auth_string.encode('utf-8')).decode('utf-8')
    req.add_header("Authorization", f"Basic {base64string}")
    
    import ssl
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    try:
        with urllib.request.urlopen(req, context=ctx) as response:
            data = json.loads(response.read().decode('utf-8'))
            return data.get('products', [])
    except urllib.error.HTTPError as e:
        if e.code == 503:
            print(f"503 Service Unavailable for '{term}'. OFF API rate limited.")
            return None
        print(f"HTTPError {e.code} for '{term}'")
        return None
    except Exception as e:
        print(f"Warning: Failed to fetch '{term}' - {e}")
        return None
"""

import re
content = re.sub(r'def fetch_product\(term\):.*?return None\n', fetch_code.strip() + '\n\n', content, flags=re.DOTALL)

# Add the JSON loading logic
main_code = """
def import_bulk_products():
    import json
    import os
    all_products = list(PDF_PRODUCTS)
    try:
        if os.path.exists('products_c_to_z.json'):
            with open('products_c_to_z.json', 'r') as f:
                c_z = json.load(f)
                all_products.extend(c_z)
    except Exception as e:
        print(f"Error loading C-Z products: {e}")
        
    print(f"Starting bulk import for {len(all_products)} products...")
"""

content = re.sub(r'def import_bulk_products\(\):\n    print\(f"Starting bulk import for \{len\(PDF_PRODUCTS\)\} products\.\.\."\)', main_code.strip(), content)

content = content.replace("for i, search_term in enumerate(PDF_PRODUCTS):", "for i, search_term in enumerate(all_products):")

with open('scripts/bulk_import_products.py', 'w') as f:
    f.write(content)

print("Patched script!")
