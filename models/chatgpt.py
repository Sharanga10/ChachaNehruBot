import openai
from models.model_config import get_model_config

def generate_tweet_chatgpt(content_idea: str) -> str:
    config = get_model_config("chatgpt")
    prompt = f"""Generate a first-person, emotionally resonant, context-aware tweet based on this idea:

Topic: {content_idea}

Format:
- Must feel like a human wrote it
- No hashtags, no emojis
- Max 280 characters
"""
    try:
        response = openai.ChatCompletion.create(
            model=config.get("model", "gpt-4o-mini"),
            messages=[{"role": "user", "content": prompt}],
            max_tokens=config.get("max_tokens", 100),
            temperature=config.get("temperature", 0.7),
        )
        return response.choices[0].message["content"].strip()
    except Exception as e:
        print("❌ ChatGPT fallback failed:", str(e))
        return None