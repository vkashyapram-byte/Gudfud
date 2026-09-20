with open('scripts/bulk_import_products.py', 'r') as f:
    content = f.read()

# Remove the auth header injection
import re
content = re.sub(r'    import base64.*?    req\.add_header\("Authorization", f"Basic \{base64string\}"\)', '', content, flags=re.DOTALL)

with open('scripts/bulk_import_products.py', 'w') as f:
    f.write(content)

print("Auth removed!")
