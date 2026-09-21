from duckduckgo_search import DDGS

try:
    with DDGS() as ddgs:
        results = list(ddgs.images("PARLE HIDE & SEEK", max_results=1))
        if results:
            print("Found image:", results[0].get("image"))
        else:
            print("No image found.")
except Exception as e:
    print("Error:", e)
