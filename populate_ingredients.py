import requests
import urllib.parse
import re
import time
from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql://postgres:postgrespassword@localhost:5432/gudfud"
engine = create_engine(DATABASE_URL)

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
    except Exception as e:
        pass
    return None

def get_wiki_summary(name):
    # Try exact match first
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
    except Exception as e:
        print(f"Error Wiki exact for {name}: {e}")
        
    # Try search
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
    except Exception as e:
        pass
        
    return None

def main():
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT i.id, i.canonical_name, count(li.id) as freq 
            FROM ingredient i 
            LEFT JOIN label_ingredient li ON i.id = li.ingredient_id
            GROUP BY i.id 
            ORDER BY freq DESC 
            LIMIT 50
        """))
        items = result.fetchall()
        
    print(f"Processing {len(items)} items...")
    updates = []
    
    for item_id, name, freq in items:
        # print(f"Processing {name}...")
        image_url = get_image_from_bing(name)
        summary = get_wiki_summary(name)
        
        if not summary:
            summary = "No verified summary currently available for this ingredient."
            
        print(f"{name}: Img={'Yes' if image_url else 'No'}, Sum={len(summary)} chars")
        
        summary_escaped = summary.replace("'", "''")
        image_val = f"'{image_url}'" if image_url else "NULL"
        
        updates.append(f"UPDATE ingredient SET public_summary = '{summary_escaped}', image_url = {image_val} WHERE id = '{item_id}';")
        time.sleep(0.5)
        
    with open('ingredient_updates.sql', 'w') as f:
        f.write("\n".join(updates))
        
    print(f"Wrote {len(updates)} statements to ingredient_updates.sql")

if __name__ == "__main__":
    main()
