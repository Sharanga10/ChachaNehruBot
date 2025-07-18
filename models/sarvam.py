import requests
from models.model_config import get_model_config

def generate_tweet_sarvam(content_idea: str) -> str:
    config = get_model_config("sarvam")
    prompt = f"""Write a short, culturally-rooted, first-person style tweet on the topic below.

Topic: {content_idea}

Constraints:
- Should feel emotionally strong
- Use simple but poetic language
- Max 280 characters
"""
    api_url = config.get("api_url")
    api_key = config.get("api_key")

    if not api_url or not api_key:
        print("⚠️ Sarvam API config missing")
        return None

    try:
        response = requests.post(
            api_url,
            headers={"Authorization": f"Bearer {api_key}"},
            json={"prompt": prompt, "max_tokens": config.get("max_tokens", 100)},
            timeout=10
        )
        if response.status_code == 200:
            return response.json().get("text", "").strip()
        else:
            print("⚠️ Sarvam fallback failed:", response.text)
            return None
    except Exception as e:
        print("❌ Sarvam error:", str(e))
        return None