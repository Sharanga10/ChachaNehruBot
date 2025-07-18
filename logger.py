import csv
import os
from datetime import datetime

POST_LOG_FILE = "post_log.csv"
EVENT_LOG_FILE = "event_log.txt"

def log_post(tweet_text: str, model_used: str, topic: str, metadata: dict, response: dict):
    """
    Logs a tweet to the post_log.csv file.
    """
    row = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "text": tweet_text,
        "model": model_used,
        "topic": topic,
        "metadata": str(metadata),
        "status": response.get("status", "unknown"),
        "tweet_id": response.get("tweet_id", ""),
        "error": response.get("error", "")
    }

    file_exists = os.path.isfile(POST_LOG_FILE)
    with open(POST_LOG_FILE, mode="a", newline="", encoding="utf-8") as csvfile:
        fieldnames = list(row.keys())
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)

def log_event(message: str):
    """
    Logs any event to a plain text file.
    """
    with open(EVENT_LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}\n")