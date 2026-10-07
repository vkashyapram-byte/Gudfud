import json
import re
import time
import requests
import urllib.parse

def get_image_for_product(name):
    query = f"{name} product india"
    encoded_query = urllib.parse.quote(query)
    url = f"https://www.bing.com/images/search?q={encoded_query}&FORM=HDRSC3"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        # Bing images puts image data in a JS variable `murl&quot;:&quot;https://...&quot;`
        matches = re.findall(r'murl&quot;:&quot;([^&]+)&quot;', response.text)
        
        for image_url in matches:
            # We want to avoid these domains
            if "lookaside" not in image_url and "fooddatascrape" not in image_url and "jiomart" not in image_url:
                # also filter out very weird ones
                if image_url.startswith("http"):
                    return image_url
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
    
    for i, item in enumerate(data):
        item_id = item['id']
        name = item['canonical_name']
        print(f"[{i+1}/{len(data)}] Searching image for {name}...")
        
        new_url = get_image_for_product(name)
        if new_url:
            print(f"  -> Found: {new_url[:80]}")
            sql_updates.append(f"UPDATE label_version SET label_image_id = '{new_url}' WHERE id = '{item_id}';")
        else:
            print("  -> Could not find image.")
            
        time.sleep(1) # avoid rate limiting
        
    with open('update_images.sql', 'w') as out_f:
        out_f.write("\n".join(sql_updates))
        
    print(f"\nCreated update_images.sql with {len(sql_updates)} updates.")

if __name__ == "__main__":
    main()
