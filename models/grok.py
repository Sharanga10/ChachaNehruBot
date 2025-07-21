import os
import requests
from models.model_config import get_model_config

def generate_tweet_grok(topic: str, tone: str = "emotional", language: str = "hi", mode: str = "DAY") -> str:
    """
    Generates a tweet using the official Grok API (xAI's chat-completions endpoint).
    
    This function connects to https://api.x.ai/v1/chat/completions using the 
    GROK-compatible model like 'grok-4-0709' and returns a tweet-like response
    based on the provided content idea.

    Environment Variable:
        - XAI_API_KEY : Bearer token for authentication

    Reference: https://x.ai/api
    """
    config = get_model_config("grok")
    api_url = config.get("api_url", "https://api.x.ai/v1/chat/completions")
    api_key = os.getenv("XAI_API_KEY")
    
    if not api_key:
        print("❌ Grok API key not found. Please set XAI_API_KEY in environment.")
        return None

    # Create appropriate prompt based on mode and language
    if language == "hi":
        system_message = "आप एक सहायक असिस्टेंट हैं जो संक्षिप्त, आकर्षक ट्वीट लिखते हैं।"
        user_message = f"""एक भावनात्मक और आकर्षक ट्वीट लिखें:

विषय: {topic}
टोन: {tone}
मोड: {mode}

आवश्यकताएं:
- 280 अक्षरों से कम
- प्राकृतिक और मानवीय लगे
- हैशटैग या इमोजी न हों"""
    else:
        system_message = "You are a helpful assistant that writes concise, engaging tweets."
        user_message = f"""Generate a tweet about: {topic}

Tone: {tone}
Mode: {mode}

Requirements:
- 280 characters or less
- Natural and human-like
- No hashtags or emojis"""

    payload = {
        "model": config.get("model", "grok-4-0709"),
        "messages": [
            {
                "role": "system",
                "content": system_message
            },
            {
                "role": "user",
                "content": user_message
            }
        ],
        "temperature": config.get("temperature", 0.7),
        "max_tokens": config.get("max_tokens", 100)
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(api_url, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        
        tweet = response.json()["choices"][0]["message"]["content"].strip()
        
        # Ensure tweet is within character limit
        if len(tweet) > 280:
            tweet = tweet[:277] + "..."
            
        return tweet
    except requests.exceptions.RequestException as e:
        print("❌ Grok API error:", str(e))
        return None
    except (KeyError, IndexError) as e:
        print("❌ Grok response parsing error:", str(e))
        return None