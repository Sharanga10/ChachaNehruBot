import os
import requests
from dotenv import load_dotenv

load_dotenv()  # Load .env file variables

BEARER_TOKEN = os.getenv("BEARER_TOKEN")

def create_headers():
    return {"Authorization": f"Bearer {BEARER_TOKEN}", "Content-Type": "application/json"}

def post_tweet(text):
    url = "https://api.twitter.com/2/tweets"
    payload = {"text": text}
    headers = create_headers()
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 201:
        print("✅ Tweet posted successfully!")
    else:
        print(f"❌ Failed to post tweet: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    if not BEARER_TOKEN:
        print("❌ Error: BEARER_TOKEN missing in .env")
    else:
        post_tweet("Testing Tweet from Chacha Nehru Bot using OAuth2 💥")