import json
import re
import urllib.parse
import requests
import concurrent.futures

HEADERS = {
    "User-Agent": "GUDFUD/1.0 (kashii@example.com) Mozilla/5.0"
}

def get_image_from_bing(name):
    query = f"{name} ingredient food"
    encoded_query = urllib.parse.quote(query)
    url = f"https://www.bing.com/images/search?q={encoded_query}&FORM=HDRSC3"
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        matches = re.findall(r'murl&quot;:&quot;([^&]+)&quot;', response.text)
        for image_url in matches:
            if "lookaside" not in image_url and "fooddatascrape" not in image_url and image_url.startswith("http"):
                return image_url
    except Exception:
        pass
    return None

def get_wiki_summary(name):
    query = urllib.parse.quote(name)
    url = f"https://en.wikipedia.org/w/api.php?action=query&prop=extracts&exintro&explaintext&titles={query}&format=json"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10).json()
        pages = resp.get("query", {}).get("pages", {})
        for k, v in pages.items():
            if k != "-1" and "extract" in v:
                ext = v["extract"].strip()
                if ext:
                    return ext
    except:
        pass
        
    try:
        search_url = f"https://en.wikipedia.org/w/api.php?action=opensearch&search={query}&limit=1&format=json"
        s_resp = requests.get(search_url, headers=HEADERS, timeout=10).json()
        if len(s_resp) > 1 and s_resp[1]:
            closest_title = s_resp[1][0]
            url2 = f"https://en.wikipedia.org/w/api.php?action=query&prop=extracts&exintro&explaintext&titles={urllib.parse.quote(closest_title)}&format=json"
            resp2 = requests.get(url2, headers=HEADERS, timeout=10).json()
            pages = resp2.get("query", {}).get("pages", {})
            for k, v in pages.items():
                if k != "-1" and "extract" in v:
                    return v["extract"].strip()
    except:
        pass
    return None

def process_item(item):
    name = item["canonical_name"]
    slug = item["slug"]
    
    image_url = get_image_from_bing(name)
    summary = get_wiki_summary(name)
    
    if not summary:
        summary = "No verified summary currently available for this ingredient."
        
    summary_escaped = summary.replace("'", "''")
    image_val = f"'{image_url}'" if image_url else "NULL"
    
    sql = f"UPDATE ingredient SET public_summary = '{summary_escaped}', image_url = {image_val} WHERE slug = '{slug}';"
    return (name, image_url is not None, len(summary), sql)

def main():
    with open('supa_ingredients.txt', 'r') as f:
        content = f.read()
        
    match = re.search(r'\{\s*"boundary.*?("rows":\s*\[.*\]).*\}', content, re.DOTALL)
    if not match:
        start = content.find('"rows":')
        end = content.rfind('],') + 1
        json_str = "{" + content[start:end] + "}"
    else:
        json_str = "{" + match.group(1) + "}"
        
    data = json.loads(json_str)
    items = data["rows"]
    
    # Process remaining 150 items
    items = items[150:300]
    print(f"Processing next {len(items)} items concurrently...")
    
    sqls = []
    success = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        results = executor.map(process_item, items)
        for res in results:
            name, has_img, sum_len, sql = res
            sqls.append(sql)
            if has_img:
                success += 1
            print(f"{name}: Img={'Yes' if has_img else 'No'}, Sum={sum_len} chars")
            
    with open('update_supa2.sql', 'w') as f:
        f.write("\n".join(sqls))
        
    print(f"Done. {success} images found. Generated update_supa2.sql")

if __name__ == "__main__":
    main()
