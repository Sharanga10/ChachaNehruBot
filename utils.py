import json
import os
import csv
from datetime import datetime

def save_metadata(metadata):
    with open("post_log.csv", "a") as f:
        writer = csv.writer(f)
        writer.writerow([datetime.now().isoformat(), metadata.get("mode"), metadata.get("model"), metadata.get("length")])

def log_post(tweet, metadata):
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "tweet": tweet,
        "model": metadata.get("model"),
        "mode": metadata.get("mode")
    }
    with open("event_log.json", "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

def log_event(source: str, message: str):
    """General purpose event logger."""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "source": source,
        "message": message
    }
    with open("events.log", "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

def load_banned_keywords():
    try:
        with open("banned_keywords.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def load_feature_flags():
    try:
        with open("feature_flags.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def get_model_name():
    try:
        with open("model_config.json", "r", encoding="utf-8") as f:
            return json.load(f).get("model_name", "unknown")
    except Exception:
        return "unknown"

def get_scheduler_config():
    try:
        with open("scheduler_config.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def trim_tweet(tweet: str, max_length: int = 280) -> str:
    """Trim tweet to max_length, adding ellipsis if needed."""
    if len(tweet) <= max_length:
        return tweet
    return tweet[:max_length - 3] + "..."

def log_generated_tweet(tweet: str, metadata: dict):
    """Log generated tweet and metadata for debugging or audit."""
    with open("generated_tweets.log", "a", encoding="utf-8") as f:
        log_entry = f"{datetime.now().isoformat()} | {metadata.get('model', 'unknown')} | {tweet}\n"
        f.write(log_entry)