import requests

def get_wiki_image(query):
    url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "prop": "pageimages",
        "format": "json",
        "piprop": "original",
        "titles": query,
        "redirects": 1
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    try:
        data = requests.get(url, params=params, headers=headers).json()
        pages = data["query"]["pages"]
        for page_id, page_info in pages.items():
            if "original" in page_info:
                return page_info["original"]["source"]
    except Exception as e:
        print("Error:", e)
    return None

print("Chocolate:", get_wiki_image("Chocolate_bar"))
print("Biscuit:", get_wiki_image("Biscuit"))
print("Chips:", get_wiki_image("Potato_chip"))
