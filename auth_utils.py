import os
import time
import requests
from urllib.parse import urlencode
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
REFRESH_TOKEN = os.getenv("REFRESH_TOKEN")
TOKEN_EXPIRES_AT = float(os.getenv("TOKEN_EXPIRES_AT", 0))

TOKEN_URL = "https://api.twitter.com/2/oauth2/token"
TWEET_URL = "https://api.twitter.com/2/tweets"

def save_env_var(key, value):
    with open(".env", "r") as file:
        lines = file.readlines()

    with open(".env", "w") as file:
        found = False
        for line in lines:
            if line.startswith(f"{key}="):
                file.write(f"{key}={value}\n")
                found = True
            else:
                file.write(line)
        if not found:
            file.write(f"{key}={value}\n")

def refresh_access_token():
    print("🔁 Access token expired. Refreshing...")

    data = {
        "grant_type": "refresh_token",
        "refresh_token": REFRESH_TOKEN,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
    }

    response = requests.post(TOKEN_URL, data=urlencode(data), headers=headers)
    if response.status_code != 200:
        raise Exception(f"Token refresh failed: {response.status_code} - {response.text}")

    tokens = response.json()
    access_token = tokens["access_token"]
    refresh_token = tokens.get("refresh_token", REFRESH_TOKEN)
    expires_in = tokens.get("expires_in", 7200)
    expires_at = time.time() + expires_in - 60

    save_env_var("ACCESS_TOKEN", access_token)
    save_env_var("REFRESH_TOKEN", refresh_token)
    save_env_var("TOKEN_EXPIRES_AT", str(expires_at))

    print("✅ Token refreshed successfully.")
    return access_token

def get_valid_access_token():
    global ACCESS_TOKEN
    if time.time() >= TOKEN_EXPIRES_AT:
        ACCESS_TOKEN = refresh_access_token()
    return ACCESS_TOKEN

def post_tweet_oauth2(tweet_text):
    access_token = get_valid_access_token()

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    payload = {
        "text": tweet_text
    }

    response = requests.post(TWEET_URL, json=payload, headers=headers)
    if response.status_code != 201:
        raise Exception(f"Tweet failed: {response.status_code} - {response.text}")

    print("🚀 Tweet posted successfully via OAuth2!")