import random
from models.grok import generate_tweet_grok
from models.chatgpt import generate_tweet_chatgpt
from models.sarvam import generate_tweet_sarvam
from banned_words import is_banned
from utils import log_event
from datetime import datetime

# Ordered list of models for fallback
FALLBACK_MODELS = ["grok", "chatgpt", "sarvam"]

def generate_tweet_with_fallback(topic: str, tone: str = "emotional", language: str = "hi", mode: str = "DAY") -> tuple:
    """
    Generate tweet using fallback logic: Grok → ChatGPT → Sarvam.
    Reject banned content. Return tweet and metadata.
    """
    for model in FALLBACK_MODELS:
        try:
            if model == "grok":
                tweet = generate_tweet_grok(topic, tone=tone, language=language, mode=mode)
            elif model == "chatgpt":
                tweet = generate_tweet_chatgpt(topic, tone=tone, language=language, mode=mode)
            elif model == "sarvam":
                tweet = generate_tweet_sarvam(topic, tone=tone, language=language, mode=mode)
            else:
                continue

            if tweet and not is_banned(tweet):
                log_event("content_generator", f"{model} used successfully")
                metadata = {
                    "model": model,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "mode": mode,
                }
                return tweet, metadata
            else:
                log_event("content_generator", f"{model} output rejected (banned or empty)")

        except Exception as e:
            log_event("content_generator", f"{model} failed: {str(e)}")

    log_event("content_generator", "All models failed. Returning fallback message.")
    fallback_tweet = "आज कुछ तकनीकी दिक्कत है, पर चाचा नेहरू कल फिर लौटेंगे। 🚫🤖"
    metadata = {
        "model": "none",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "mode": mode,
    }
    return fallback_tweet, metadata