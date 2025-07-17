# main.py

import os, json, time, random, logging
import requests, pandas as pd, nltk
from transformers.pipelines import pipeline
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from openai import OpenAI
import tweepy
from dotenv import load_dotenv
from content_generator import generate_content
from audit_engine import audit_content
from datetime import datetime

# Load environment
load_dotenv()

# Debug keys check
if os.getenv("DEBUG_MODE") == "true":
    print("🔐 Debugging Keys:")
    for key in ["X_CONSUMER_KEY", "X_CONSUMER_SECRET", "X_ACCESS_TOKEN", "X_ACCESS_SECRET", "XAI_API_KEY", "NEWS_API_KEY", "GOOGLE_API_KEY", "SARVAM_API_KEY"]:
        print(f"{key}: ✅" if os.getenv(key) else "❌ MISSING")

# Twitter Auth
auth = tweepy.OAuth1UserHandler(
    os.environ["X_CONSUMER_KEY"],
    os.environ["X_CONSUMER_SECRET"],
    os.environ["X_ACCESS_TOKEN"],
    os.environ["X_ACCESS_SECRET"]
)
api = tweepy.API(auth)

# Logs setup
logging.basicConfig(filename='bot_logs.txt', level=logging.INFO, format='%(asctime)s - %(message)s')
logs = {'post': [], 'rpe': []}

# Load config files
with open("feature_flags.json") as f: feature_flags = json.load(f)
with open("model_config.json") as f: model_config = json.load(f)
with open("banned_keywords.json") as f: banned_keywords = json.load(f)
with open("dialect_config.json") as f: dialects_json = json.load(f)
dialects = dialects_json.get("enabled_dialects", [])  # updated to match your config structure
with open("tweet_schedule.json") as f: schedule_config = json.load(f)
with open("refinement_config.json") as f: refine_config = json.load(f)
with open("shlokas.json") as f: shlokas = json.load(f)

# NLP setup
nltk.download('punkt')
sentiment_analyzer = SentimentIntensityAnalyzer()
fact_checker = pipeline("text-classification", model="roberta-large-mnli")

# Tracking
tweet_count = {"grok-4": 0, "chatgpt": 0, "sarvam": 0}

def fetch_news():
    url = f"https://newsapi.org/v2/top-headlines?country=in&apiKey={os.environ['NEWS_API_KEY']}"
    try:
        r = requests.get(url)
        return r.json().get('articles', [])[:10]
    except Exception as e:
        print(f"Error fetching news: {e}")
        return []

def save_to_dataset(prompt, tweet, metadata):
    with open("dataset.jsonl", "a") as f:
        json.dump({"prompt": prompt, "output": tweet, "metadata": metadata}, f)
        f.write('\n')
    logs['rpe'].append({"prompt": prompt, "tweet": tweet})

def update_dashboard():
    df = pd.DataFrame(logs['post'])
    df.to_csv('post_log.csv', mode='a', index=False)
    logging.info("Dashboard updated")

def post_tweet(text):
    try:
        tweet = api.update_status(text)
        logs['post'].append({
            "id": tweet.id,
            "text": text,
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        print(f"Tweet posted: {text[:50]}...")  # debug print
        return True
    except Exception as e:
        logging.error(f"Tweet failed: {e}")
        print(f"Tweet failed: {e}")  # debug print
        return False

def run_bot():
    posts_today = []
    quota = {"grok-4": 20, "chatgpt": 20, "sarvam": 10}
    models = list(quota.keys())

    print("Starting run_bot()...")  # debug

    # Add shlokas
    if feature_flags.get("enable_shlokas"):
        print("Shlokas enabled, generating shlokas...")
        for timing in ["morning", "evening"]:
            candidates = [s for s in shlokas if timing in s.get('theme', '')]
            print(f"Found {len(candidates)} shlokas for {timing}")
            if not candidates:
                logging.warning(f"No shlokas found for timing: {timing}")
                continue
            shloka = random.choice(candidates)
            prompt = f"{timing.title()} shloka: {shloka.get('sanskrit', '')} — {shloka.get('hindi', '')}"
            model = random.choice(models)
            print(f"Generating shloka tweet with model {model} and prompt: {prompt[:60]}...")
            result = generate_content(prompt, model)
            if result and result.get("text"):
                passed, reason = audit_content(result['text'], shloka.get('hindi', ''), "India positive")
                if passed:
                    posts_today.append(result['text'])
                    tweet_count[model] += 1
                    save_to_dataset(prompt, result['text'], {"type": "shloka", "dialect": "pure_hindi"})
                    print(f"Shloka tweet passed audit and queued for posting.")
                else:
                    logging.warning(f"⚠️ {timing.title()} shloka failed audit: {reason}")
                    print(f"Shloka tweet failed audit: {reason}")
            else:
                logging.warning(f"⚠️ {timing.title()} shloka generation failed.")
                print(f"Shloka generation failed for {timing}")

    # Add News
    if feature_flags.get("enable_news_tweets"):
        print("News tweets enabled, fetching news...")
        news_articles = fetch_news()
        print(f"Fetched {len(news_articles)} news articles.")
        for article in news_articles:
            model = random.choices(models, weights=[quota[m] - tweet_count[m] for m in models])[0]
            dialect = random.choice(dialects) if dialects else "pure_hindi"
            prompt = f"Generate tweet on: {article.get('title', '')} — dialect: {dialect}"
            print(f"Generating news tweet with model {model} and prompt: {prompt[:60]}...")
            result = generate_content(prompt, model)
            if result and result.get("text"):
                passed, reason = audit_content(result['text'], article.get('description', ''), article.get('title', ''))
                if passed:
                    posts_today.append(result['text'])
                    tweet_count[model] += 1
                    save_to_dataset(prompt, result['text'], {"type": "news", "dialect": dialect})
                    print(f"News tweet passed audit and queued for posting.")
                else:
                    logging.warning(f"⚠️ News tweet rejected: {reason}")
                    print(f"News tweet rejected by audit: {reason}")
            else:
                print("News tweet generation failed.")

    # Post tweets
    print(f"Total tweets to post: {len(posts_today)}")
    for post in posts_today:
        if post_tweet(post):
            delay = schedule_config.get("delay_between_tweets_sec", 2700)
            print(f"Sleeping for {delay} seconds before next tweet...")
            time.sleep(delay)

    update_dashboard()
    print("run_bot() completed.")

if __name__ == "__main__":
    run_bot()