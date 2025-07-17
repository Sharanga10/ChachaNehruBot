import os
import requests

def fetch_news_hindi():
    API_KEY = os.getenv("NEWS_API_KEY")
    url = "https://newsapi.org/v2/everything"
    params = {
        'q': 'भारत OR इंडिया',
        'language': 'hi',
        'pageSize': 5,
        'sortBy': 'publishedAt',
        'apiKey': API_KEY
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        articles = response.json().get('articles', [])
        print("📰 हिंदी न्यूज़:")
        for i, article in enumerate(articles, 1):
            print(f"\n{i}. {article['title']}")
            print(f"➡️ {article.get('url')}")
    except Exception as e:
        print(f"❌ Hindi news fetch error: {e}")

if __name__ == "__main__":
    fetch_news_hindi()