import tweepy
import os

# Load Twitter API keys from environment variables
consumer_key = os.getenv("X_CONSUMER_KEY")
consumer_secret = os.getenv("X_CONSUMER_SECRET")
access_token = os.getenv("X_ACCESS_TOKEN")
access_secret = os.getenv("X_ACCESS_SECRET")

# Authenticate using OAuth 1.0a
auth = tweepy.OAuth1UserHandler(consumer_key, consumer_secret, access_token, access_secret)
api = tweepy.API(auth)

# Example tweet
tweet_text = "मैंने OAuth1.0a से ट्वीट कर दिया 😎🇮🇳"
api.update_status(status=tweet_text)
print("✅ ट्वीट सफलतापूर्वक किया गया")