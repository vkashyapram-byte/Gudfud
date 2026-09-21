import requests

url = "https://world.openfoodfacts.org/cgi/search.pl"
params = {
    "search_terms": "parle hide seek",
    "search_simple": "1",
    "action": "process",
    "json": "1",
    "page_size": "1"
}
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}
try:
    response = requests.get(url, params=params, headers=headers, timeout=10)
    print("Status:", response.status_code)
    data = response.json()
    if data.get("products"):
        print("Image:", data["products"][0].get("image_front_url"))
    else:
        print("No products")
except Exception as e:
    print("Error:", e)
