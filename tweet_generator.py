import random
import logging
from content_generator import generate_tweet_with_fallback
from utils import trim_tweet, log_generated_tweet
from models.model_config import load_model_config

logger = logging.getLogger(__name__)

def generate_tweet():
    try:
        model_config = load_model_config()
        selected_model = model_config.get("default_model", "chatgpt")  # grok, chatgpt, or sarvam
        content_idea = select_content_idea()

        logger.info(f"Using model: {selected_model}, content idea: {content_idea}")

        tweet = generate_tweet_with_fallback(content_idea, selected_model)
        trimmed_tweet = trim_tweet(tweet)

        log_generated_tweet(trimmed_tweet)
        return trimmed_tweet

    except Exception as e:
        logger.exception("Tweet generation failed.")
        return "चाचा नेहरू आज कुछ सोच में हैं, अभी कुछ नहीं कहेंगे।"

def select_content_idea():
    ideas = [
        "आज का व्यंग्य",
        "नेहरूजी की कल्पना",
        "राजनीति पर तंज",
        "सोशल मीडिया का हाल",
        "ऐतिहासिक संदर्भ",
        "मौजूदा घटनाओं पर नजर",
        "युवा और देश"
    ]
    return random.choice(ideas)