import logging
from content_generator import generate_tweet
from utils.fallback_logic import get_next_model

def generate_tweet_with_fallback(mode: str, model_name: str, feature_flags: dict):
    """
    Try generating a tweet using fallback models if primary fails.

    Parameters:
    - mode (str): 'DAY' or 'NIGHT'
    - model_name (str): Primary model to use first
    - feature_flags (dict): Feature flags from config

    Returns:
    - (tweet, metadata): The generated tweet and any metadata
    """
    tried_models = set()

    while model_name:
        if model_name in tried_models:
            logging.error(f"🔁 Already tried model '{model_name}', stopping to avoid loop.")
            break

        tried_models.add(model_name)

        try:
            logging.info(f"🤖 Attempting to generate tweet using model: {model_name}")
            tweet, metadata = generate_tweet(mode=mode, model_name=model_name, feature_flags=feature_flags)
            logging.info(f"✅ Successfully generated tweet with {model_name}")
            return tweet, metadata
        except Exception as e:
            logging.warning(f"⚠️ Failed with model {model_name}: {e}")
            model_name = get_next_model(model_name)

    logging.error("❌ All fallback models failed to generate a tweet.")
    raise RuntimeError("All fallback models failed.")