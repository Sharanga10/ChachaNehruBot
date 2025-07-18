# ✅ test_auth.py — OAuth1 User Context test

import os
import tweepy
from dotenv import load_dotenv

load_dotenv()

def test_oauth1_credentials():
    try:
        consumer_key = os.getenv("X_CONSUMER_KEY")
        consumer_secret = os.getenv("X_CONSUMER_SECRET")
        access_token = os.getenv("X_ACCESS_TOKEN")
        access_token_secret = os.getenv("X_ACCESS_TOKEN_SECRET")

        if not all([consumer_key, consumer_secret, access_token, access_token_secret]):
            raise Exception("Missing credentials")

        auth = tweepy.OAuth1UserHandler(
            consumer_key,
            consumer_secret,
            access_token,
            access_token_secret
        )
        api = tweepy.API(auth)

        user = api.verify_credentials()
        if user:
            print(f"✅ Authenticated as @{user.screen_name} (ID: {user.id})")
        else:
            print("❌ Invalid credentials")

    except Exception as e:
        print("❌ Error:", str(e))

if __name__ == "__main__":
    test_oauth1_credentials()