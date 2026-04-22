import requests

def web_search(query: str):
    try:
        # simple DuckDuckGo search (no API key needed)
        url = f"https://duckduckgo.com/?q={query}&format=json"
        response = requests.get(url)

        if response.status_code != 200:
            return "❌ Failed to fetch search results"

        return response.text[:1000]  # limit size

    except Exception as e:
        return f"❌ Search error: {str(e)}"