from duckduckgo_search import DDGS
from itertools import islice

def get_image(name):
    try:
        results = DDGS().images(f"{name} ingredient food", max_results=1)
        if results:
            return results[0]['image']
    except Exception as e:
        pass
    return None

if __name__ == "__main__":
    print(get_image("Sugar"))
