# ✅ post_to_twitter.py (OAuth2 User Context Method)

import os
import tweepy
from dotenv import load_dotenv

load_dotenv()

def post_to_twitter(text):
    try:
        consumer_key = os.getenv("X_CONSUMER_KEY")
        consumer_secret = os.getenv("X_CONSUMER_SECRET")
        access_token = os.getenv("X_ACCESS_TOKEN")
        access_token_secret = os.getenv("X_ACCESS_TOKEN_SECRET")

        if not all([consumer_key, consumer_secret, access_token, access_token_secret]):
            raise Exception("Missing Twitter API credentials.")

        auth = tweepy.OAuth1UserHandler(
            consumer_key,
            consumer_secret,
            access_token,
            access_token_secret
        )

        api = tweepy.API(auth)
        response = api.update_status(status=text)

        print("✅ Tweet posted successfully:", response.id)
        return True

    except Exception as e:
        print("❌ Failed to post tweet:", str(e))
        return False