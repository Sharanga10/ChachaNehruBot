import os
import requests

def fetch_news():
    API_KEY = os.getenv("NEWS_API_KEY")
    url = "https://newsapi.org/v2/everything"
    params = {
        'q': 'India',
        'language': 'en',
        'pageSize': 5,
        'sortBy': 'publishedAt',
        'apiKey': API_KEY
    }

    try:
        r = requests.get(url, params=params)
        print("🔗 API Call URL:", r.url)
        print("📦 Raw JSON Response:", r.json())
        articles = r.json().get('articles', [])
        print(f"\n✅ Fetched {len(articles)} articles:\n")
        for i, article in enumerate(articles):
            print(f"{i+1}. {article['title']}")
    except Exception as e:
        print(f"❌ Error: {e}")

fetch_news()