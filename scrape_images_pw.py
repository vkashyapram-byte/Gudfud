import json
import re
import time
import urllib.parse
from playwright.sync_api import sync_playwright

def get_image_for_product(page, name):
    query = f"{name} product india"
    encoded_query = urllib.parse.quote(query)
    url = f"https://www.google.com/search?q={encoded_query}&tbm=isch"
    
    try:
        page.goto(url, wait_until="networkidle")
        
        # In Google Images, images are inside img tags with 'src' starting with 'http' or data:image
        # Wait a bit for images to load
        time.sleep(1)
        
        images = page.locator("img").all()
        for img in images:
            src = img.get_attribute("src")
            if src and src.startswith("http"):
                # Avoid google branding
                if "google" not in src and "gstatic" not in src:
                    return src
                    
        # fallback
        for img in images:
            src = img.get_attribute("src")
            if src and src.startswith("http"):
                if "gstatic" not in src:
                    return src

    except Exception as e:
        print(f"Error searching for {name}: {e}")
        
    return None

def main():
    with open('/Users/kashii/.gemini/antigravity-ide/brain/e9415697-9e83-4999-8f41-9a28b9b10e88/.system_generated/steps/721/output.txt', 'r') as f:
        content = f.read()

    try:
        data_wrapper = json.loads(content)
        content_str = data_wrapper.get("result", "")
    except Exception:
        content_str = content

    match = re.search(r'<untrusted-data-[^>]+>\n(.*)\n</untrusted-data-[^>]+>', content_str, re.DOTALL)
    if not match:
        print("Could not find JSON array")
        return
        
    json_str = match.group(1).strip()
    data = json.loads(json_str)
    
    print(f"Found {len(data)} items to process.")
    sql_updates = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        for i, item in enumerate(data):
            item_id = item['id']
            name = item['canonical_name']
            print(f"[{i+1}/{len(data)}] Searching image for {name}...")
            
            new_url = get_image_for_product(page, name)
            if new_url:
                print(f"  -> Found: {new_url[:60]}...")
                sql_updates.append(f"UPDATE label_version SET label_image_id = '{new_url}' WHERE id = '{item_id}';")
            else:
                print("  -> Could not find image.")
                
            time.sleep(0.5) # avoid rate limiting
            
            # just save it periodically so we don't lose it
            if i % 10 == 0:
                with open('update_images.sql', 'w') as out_f:
                    out_f.write("\n".join(sql_updates))
                    
        browser.close()
        
    with open('update_images.sql', 'w') as out_f:
        out_f.write("\n".join(sql_updates))
        
    print(f"\nCreated update_images.sql with {len(sql_updates)} updates.")

if __name__ == "__main__":
    main()
