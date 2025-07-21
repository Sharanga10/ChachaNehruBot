import openai
import os
from models.model_config import get_model_config

def generate_tweet_chatgpt(topic: str, tone: str = "emotional", language: str = "hi", mode: str = "DAY") -> str:
    """Generate a tweet using ChatGPT/OpenAI API"""
    config = get_model_config("chatgpt")
    
    # Set OpenAI API key from environment
    openai.api_key = os.getenv("OPENAI_API_KEY")
    
    if not openai.api_key:
        print("❌ OpenAI API key not found. Please set OPENAI_API_KEY in environment.")
        return None
    
    # Create appropriate prompt based on mode and language
    if language == "hi":
        prompt = f"""एक भावनात्मक और आकर्षक ट्वीट लिखें:

विषय: {topic}
टोन: {tone}
मोड: {mode}

आवश्यकताएं:
- 280 अक्षरों से कम
- प्राकृतिक और मानवीय लगे
- हैशटैग या इमोजी न हों
- पहले व्यक्ति में लिखें"""
    else:
        prompt = f"""Generate a first-person, emotionally resonant, context-aware tweet:

Topic: {topic}
Tone: {tone}
Mode: {mode}

Requirements:
- Must feel like a human wrote it
- No hashtags, no emojis
- Max 280 characters
- First person perspective"""

    try:
        response = openai.ChatCompletion.create(
            model=config.get("model", "gpt-4o-mini"),
            messages=[{"role": "user", "content": prompt}],
            max_tokens=config.get("max_tokens", 100),
            temperature=config.get("temperature", 0.7),
        )
        tweet = response.choices[0].message["content"].strip()
        
        # Ensure tweet is within character limit
        if len(tweet) > 280:
            tweet = tweet[:277] + "..."
            
        return tweet
    except Exception as e:
        print("❌ ChatGPT API error:", str(e))
        return None