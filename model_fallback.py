from utils import log_event
from generators.grok_generator import generate_with_grok
from generators.chatgpt_generator import generate_with_chatgpt
from generators.sarvam_generator import generate_with_sarvam

def generate_tweet_with_fallback(topic):
    tweet = None

    try:
        tweet = generate_with_grok(topic)
        if tweet:
            log_event("Model: Grok", "Used successfully")
            return tweet
        else:
            log_event("Model: Grok", "Returned empty")
    except Exception as e:
        log_event("Model: Grok", f"Error - {e}")

    try:
        tweet = generate_with_chatgpt(topic)
        if tweet:
            log_event("Model: ChatGPT", "Used as fallback")
            return tweet
        else:
            log_event("Model: ChatGPT", "Returned empty")
    except Exception as e:
        log_event("Model: ChatGPT", f"Error - {e}")

    try:
        tweet = generate_with_sarvam(topic)
        if tweet:
            log_event("Model: Sarvam", "Used as final fallback")
            return tweet
        else:
            log_event("Model: Sarvam", "Returned empty")
    except Exception as e:
        log_event("Model: Sarvam", f"Error - {e}")

    return None