import tweepy
import requests
from transformers import pipeline
import nltk
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from openai import OpenAI
import json
import time
import random
import logging
import pandas as pd
import os

# Setup Logging
logging.basicConfig(filename='bot_logs.txt', level=logging.INFO, format='%(asctime)s - %(message)s')
logs = {'content': [], 'audit': [], 'post': [], 'rpe': []}

# API Credentials from GitHub Secrets
X_CONSUMER_KEY = os.environ['X_CONSUMER_KEY']
X_CONSUMER_SECRET = os.environ['X_CONSUMER_SECRET']
X_ACCESS_TOKEN = os.environ['X_ACCESS_TOKEN']
X_ACCESS_SECRET = os.environ['X_ACCESS_SECRET']
XAI_API_KEY = os.environ['XAI_API_KEY']
NEWS_API_KEY = os.environ['NEWS_API_KEY']
GOOGLE_API_KEY = os.environ['GOOGLE_API_KEY']

# Clients
auth = tweepy.OAuth1UserHandler(X_CONSUMER_KEY, X_CONSUMER_SECRET, X_ACCESS_TOKEN, X_ACCESS_SECRET)
api = tweepy.API(auth)
xai_client = OpenAI(api_key=XAI_API_KEY, base_url="https://api.x.ai/v1")

# Audits
nltk.download('punkt')
fact_checker = pipeline("text-classification", model="roberta-large-mnli")
sentiment_analyzer = SentimentIntensityAnalyzer()

# Shlokas
with open('shlokas.json', 'r') as f:
    shlokas = json.load(f)

# Dialects
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
    # Grammar: Complete sentences
    sentences = nltk.sent_tokenize(text)
    if any(len(s.split()) < 4 or not any(verb in s for verb in ['है', 'था', 'कर']) for s in sentences):
        return False, "Incomplete sentence"

    # Positivity
    sentiment = sentiment_analyzer.polarity_scores(text)
    if sentiment['compound'] < 0.9:
        return False, "Not positive enough"

    # Fact Consistency
    entailment = fact_checker(f"{premise} [SEP] {text}")[0]
    if entailment['label'] == 'CONTRADICTION' or entailment['score'] < 0.8:
        return False, "Factual issue"

    # Google Fact Check
    fact_valid, fact_reason = google_fact_check(query)
    if not fact_valid:
        return False, fact_reason

    # Restrictions
    restricted = ['congress', 'tmc', 'rld', 'mns', 'abuse', 'crime', 'rape', 'murder']
    if any(word in text.lower() for word in restricted):
        return False, "Restricted content"

    return True, "Passed"

def generate_content(prompt):
    response = xai_client.chat.completions.create(
        model="grok-4",
        messages=[
            {"role": "system", "content": "You are Chacha Nehru bot: Positive, nationalist, respectful, humorous with mild sarcasm, promote India/policies/science/culture, 90% simple Hindi, dialects, no opposition, complete sentences. Return JSON: {'text': content, 'inferred_prompt': inferred}."},
            {"role": "user", "content": prompt}
        ]
    )
    result = json.loads(response.choices[0].message.content)
    logging.info(f"Generated: {result['text']}, Inferred: {result['inferred_prompt']}")
    return result

def reverse_prompt(tweet):
    response = xai_client.chat.completions.create(
        model="grok-4",
        messages=[
            {"role": "system", "content": "Infer original prompt for this Chacha Nehru bot tweet: Ensure nationalist, respectful, simple Hindi/dialect, no opposition."},
            {"role": "user", "content": tweet}
        ]
    )
    return response.choices[0].message.content

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
    prompt = f"Generate morning post with shloka: {shloka['sanskrit']} अनुवाद: {shloka['hindi']}. Tie to positive India theme, nationalist, respectful, pure_hindi."
    result = generate_content(prompt)
    passed, reason = audit_content(result['text'], shloka['hindi'], "India positive")
    logs['audit'].append({"text": result['text'], "passed": passed, "reason": reason})
    if passed:
        posts_today.append(result)
        save_to_dataset(result['inferred_prompt'], result['text'], {"date": time.strftime("%Y-%m-%d"), "type": "shloka", "dialect": "pure_hindi"})

    # News Reactions (10–15 posts)
    for article in news:
        dialect = random.choice(dialects)
        prompt = f"Generate parody tweet on '{article['title']}', {dialect}, positive India/policy/science/culture, humorous, respectful, nationalist, no opposition, complete sentences."
        result = generate_content(prompt)
        passed, reason = audit_content(result['text'], article['description'], article['title'])
        logs['audit'].append({"text": result['text'], "passed": passed, "reason": reason})
        if passed:
            posts_today.append(result)
            save_to_dataset(result['inferred_prompt'], result['text'], {"date": time.strftime("%Y-%m-%d"), "dialect": dialect})
        else:
            result = generate_content(prompt + f" Fix: {reason}")
            passed, reason = audit_content(result['text'], article['description'], article['title'])
            if passed:
                posts_today.append(result)
                save_to_dataset(result['inferred_prompt'], result['text'], {"date": time.strftime("%Y-%m-%d"), "dialect": dialect})

    # Evening Shloka
    shloka = random.choice([s for s in shlokas if 'evening' in s['theme']])
    prompt = f"Generate evening post with shloka: {shloka['sanskrit']} अनुवाद: {shloka['hindi']}. Tie to positive India theme, nationalist, respectful, pure_hindi."
    result = generate_content(prompt)
    passed, reason = audit_content(result['text'], shloka['hindi'], "India positive")
    logs['audit'].append({"text": result['text'], "passed": passed, "reason": reason})
    if passed:
        posts_today.append(result)
        save_to_dataset(result['inferred_prompt'], result['text'], {"date": time.strftime("%Y-%m-%d"), "type": "shloka", "dialect": "pure_hindi"})

    # Post (cap at 15/day for X API limits)
    for i, post in enumerate(posts_today[:15]):
        try:
            tweet = api.update_status(post['text'])
            logs['post'].append({"id": tweet.id, "text": post['text'], "time": time.strftime("%Y-%m-%d %H:%M:%S")})
            logging.info(f"Posted tweet ID {tweet.id}")
            time.sleep(2700)  # 45 mins spacing
        except Exception as e:
            logging.error(f"Post error: {e}")

    update_dashboard()

if __name__ == "__main__":
    main()