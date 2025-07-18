import os
import requests

def generate_tweet_grok(content_idea: str) -> str:
    """
    Generates a tweet using the official Grok API (xAI's chat-completions endpoint).
    
    This function connects to https://api.x.ai/v1/chat/completions using the 
    GROK-compatible model like 'grok-4-0709' and returns a tweet-like response
    based on the provided content idea.

    Environment Variable:
        - XAI_API_KEY : Bearer token for authentication

    Reference: https://x.ai/api
    """
    api_url = "https://api.x.ai/v1/chat/completions"
    api_key = os.getenv("XAI_API_KEY")
    if not api_key:
        print("❌ Grok API key not found. Please set XAI_API_KEY in environment.")
        return None

    payload = {
        "model": "grok-4-0709",
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful assistant that writes concise, engaging tweets."
            },
            {
                "role": "user",
                "content": f"Generate a tweet in 280 characters or less about: {content_idea}"
            }
        ],
        "temperature": 0.7,
        "max_tokens": 100
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(api_url, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"].strip()
    except requests.exceptions.RequestException as e:
        print("❌ Grok API error:", str(e))
        return None