with open('scripts/bulk_import_products.py', 'r') as f:
    content = f.read()

# Replace the URL to use cgi/search.pl
content = content.replace(
    'f"https://world.openfoodfacts.org/api/v2/search?search_terms={urllib.parse.quote(term)}&countries_tags=en:india&fields=code,brands,product_name,ingredients_text,ingredients,nutriments,categories_tags,image_url&page_size=1"',
    'f"https://world.openfoodfacts.org/cgi/search.pl?search_terms={urllib.parse.quote(term)}&search_simple=1&action=process&json=1&fields=code,brands,product_name,ingredients_text,ingredients,nutriments,categories_tags,image_url&page_size=1"'
)

with open('scripts/bulk_import_products.py', 'w') as f:
    f.write(content)

print("V1 API Patched!")
