import tweepy
import os

# Load from .env if needed
from dotenv import load_dotenv
load_dotenv()

# Get access token (OAuth 2.0 User token, not bearer)
ACCESS_TOKEN = os.getenv("X_ACCESS_TOKEN")

# Initialize Tweepy Client
client = tweepy.Client(access_token=ACCESS_TOKEN)

# Your tweet content
tweet_text = "चाचा नेहरू बॉट अब X API v2 से ट्वीट कर रहा है 🚀🇮🇳"

try:
    response = client.create_tweet(text=tweet_text)
    print("✅ ट्वीट सफलतापूर्वक किया गया: ", response.data)
except tweepy.TweepyException as e:
    print("❌ एरर आया:", e)