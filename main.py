# main.py (Chacha Nehru Bot — Final Stable Version)

import os
import json
import time
import random
import logging
import requests
import pandas as pd
import nltk
from transformers import pipeline
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from openai import OpenAI
import tweepy
from sarvam_utils import generate_with_sarvam

# Debug Mode to verify secrets
DEBUG_MODE = True
if DEBUG_MODE:
    print("🔐 Debugging GitHub Secrets:")
    keys = ["X_CONSUMER_KEY", "X_CONSUMER_SECRET", "X_ACCESS_TOKEN", "X_ACCESS_SECRET", "XAI_API_KEY", "NEWS_API_KEY", "GOOGLE_API_KEY", "SARVAM_API_KEY"]
    for key in keys:
        print(f"{key}:", "✅" if os.environ.get(key) else "❌ MISSING")

# Load API Keys
X_CONSUMER_KEY = os.environ["X_CONSUMER_KEY"]
X_CONSUMER_SECRET = os.environ["X_CONSUMER_SECRET"]
X_ACCESS_TOKEN = os.environ["X_ACCESS_TOKEN"]
X_ACCESS_SECRET = os.environ["X_ACCESS_SECRET"]
XAI_API_KEY = os.environ["XAI_API_KEY"]
NEWS_API_KEY = os.environ["NEWS_API_KEY"]
GOOGLE_API_KEY = os.environ["GOOGLE_API_KEY"]
SARVAM_API_KEY = os.environ.get("SARVAM_API_KEY")

# Load Model Config
with open("model_config.json", "r") as f:
    model_config = json.load(f)
PRIMARY_MODEL = model_config["primary"]
BACKUP_MODEL = model_config["backup"]

# Logging Setup
logging.basicConfig(filename='bot_logs.txt', level=logging.INFO, format='%(asctime)s - %(message)s')
logs = {'content': [], 'audit': [], 'post': [], 'rpe': []}

# X Client
auth = tweepy.OAuth1UserHandler(X_CONSUMER_KEY, X_CONSUMER_SECRET, X_ACCESS_TOKEN, X_ACCESS_SECRET)
api = tweepy.API(auth)

# XAI Client
xai_client = OpenAI(api_key=XAI_API_KEY, base_url="https://api.x.ai/v1")

# NLP Setup
nltk.download('punkt')
fact_checker = pipeline("text-classification", model="roberta-large-mnli")
sentiment_analyzer = SentimentIntensityAnalyzer()

# Load Shlokas
with open('shlokas.json', 'r') as f:
    shlokas = json.load(f)

dialects = ['pure_hindi', 'bhojpuri', 'marathi', 'gujarati']

def fetch_news():
    url = f"https://newsapi.org/v2/top-headlines?country=in&category=science&apiKey={NEWS_API_KEY}"
    response = requests.get(url)
    articles = response.json().get('articles', [])[:5]
    logging.info(f"Fetched {len(articles)} news items")
    return articles

def google_fact_check(query):
    url = f"https://factchecktools.googleapis.com/v1alpha1/claims:search?query={query}&key={GOOGLE_API_KEY}&languageCode=hi"
    response = requests.get(url)
    if response.status_code == 200:
        claims = response.json().get('claims', [])
        for claim in claims:
            rating = claim.get('claimReview', [{}])[0].get('textualRating', '').lower()
            if 'false' in rating or 'misleading' in rating:
                return False, rating
        return True, "No issues"
    return False, "API error"

def audit_content(text, premise, query):
    sentences = nltk.sent_tokenize(text)
    if any(len(s.split()) < 4 or not any(verb in s for verb in ['है', 'था', 'कर']) for s in sentences):
        return False, "Incomplete sentence"

    sentiment = sentiment_analyzer.polarity_scores(text)
    if sentiment['compound'] < 0.9:
        return False, "Not positive enough"

    entailment = fact_checker(f"{premise} [SEP] {text}")[0]
    if entailment['label'] == 'CONTRADICTION' or entailment['score'] < 0.8:
        return False, "Factual issue"

    fact_valid, fact_reason = google_fact_check(query)
    if not fact_valid:
        return False, fact_reason

    restricted = ['congress', 'tmc', 'rld', 'mns', 'abuse', 'crime', 'rape', 'murder']
    if any(word in text.lower() for word in restricted):
        return False, "Restricted content"

    return True, "Passed"

def generate_content(prompt):
    try:
        if PRIMARY_MODEL == "grok":
            response = xai_client.chat.completions.create(
                model="grok-4",
                messages=[
                    {"role": "system", "content": "You are Chacha Nehru bot. Return JSON: {'text': content, 'inferred_prompt': inferred}."},
                    {"role": "user", "content": prompt}
                ]
            )
            return json.loads(response.choices[0].message.content)
        elif PRIMARY_MODEL == "sarvam":
            return generate_with_sarvam(prompt, SARVAM_API_KEY)
    except Exception as e:
        logging.warning(f"Primary failed: {e}")
        if BACKUP_MODEL == "sarvam":
            return generate_with_sarvam(prompt, SARVAM_API_KEY)
        elif BACKUP_MODEL == "grok":
            response = xai_client.chat.completions.create(
                model="grok-4",
                messages=[
                    {"role": "system", "content": "You are Chacha Nehru bot. Return JSON: {'text': content, 'inferred_prompt': inferred}."},
                    {"role": "user", "content": prompt}
                ]
            )
            return json.loads(response.choices[0].message.content)

def save_to_dataset(prompt, tweet, metadata):
    with open('dataset.jsonl', 'a') as f:
        json.dump({"prompt": prompt, "output": tweet, "metadata": metadata}, f)
        f.write('\n')
    logs['rpe'].append({"prompt": prompt, "tweet": tweet})

def update_dashboard():
    df = pd.DataFrame(logs['post'])
    df.to_csv('post_log.csv', mode='a', index=False)
    logging.info("Dashboard updated")

def main():
    news = fetch_news()
    posts_today = []

    # Morning Shloka
    shloka = random.choice([s for s in shlokas if 'morning' in s['theme']])
    prompt = f"Morning shloka: {shloka['sanskrit']} — {shloka['hindi']}"
    result = generate_content(prompt)
    passed, reason = audit_content(result['text'], shloka['hindi'], "India positive")
    if passed:
        posts_today.append(result)
        save_to_dataset(result['inferred_prompt'], result['text'], {"type": "shloka", "dialect": "pure_hindi"})

    # News Posts
    for article in news:
        dialect = random.choice(dialects)
        prompt = f"Generate tweet on: {article['title']} — dialect: {dialect}"
        result = generate_content(prompt)
        passed, reason = audit_content(result['text'], article['description'], article['title'])
        if passed:
            posts_today.append(result)
            save_to_dataset(result['inferred_prompt'], result['text'], {"dialect": dialect})

    # Evening Shloka
    shloka = random.choice([s for s in shlokas if 'evening' in s['theme']])
    prompt = f"Evening shloka: {shloka['sanskrit']} — {shloka['hindi']}"
    result = generate_content(prompt)
    passed, reason = audit_content(result['text'], shloka['hindi'], "India positive")
    if passed:
        posts_today.append(result)
        save_to_dataset(result['inferred_prompt'], result['text'], {"type": "shloka", "dialect": "pure_hindi"})

    # Post to X
    for post in posts_today[:15]:
        try:
            tweet = api.update_status(post['text'])
            logs['post'].append({"id": tweet.id, "text": post['text'], "time": time.strftime("%Y-%m-%d %H:%M:%S")})
            time.sleep(2700)  # 45 mins
        except Exception as e:
            logging.error(f"Post error: {e}")

    update_dashboard()

if __name__ == "__main__":
    main()
