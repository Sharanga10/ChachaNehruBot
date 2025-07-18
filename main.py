import os
import sys
import logging
from datetime import datetime
from dotenv import load_dotenv  # ✅ Added
load_dotenv()  # ✅ Added

from tweet_generator import generate_tweet_with_fallback  # ✅ Updated import
from post_to_twitter import post_to_twitter
from utils import (
    save_metadata,
    log_post,
    load_banned_keywords,
    load_feature_flags,
    get_model_name,
    get_scheduler_config
)

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s — %(levelname)s — %(message)s')

def run_bot():
    try:
        now = datetime.now()
        current_time_str = now.strftime("%Y-%m-%d %H:%M:%S")
        logging.info(f"⏰ Current Time: {current_time_str} IST")

        mode = os.environ.get("BOT_MODE", "day").upper()
        logging.info(f"🌙 Running in mode: {mode}")

        feature_flags = load_feature_flags()
        banned_keywords = load_banned_keywords()
        scheduler_config = get_scheduler_config()
        model_name = get_model_name()

        # Tweet Generation
        try:
            topic = None  # ✅ Let fallback logic handle topic selection
            tweet, metadata = generate_tweet_with_fallback(topic, mode=mode)

            if not tweet:
                logging.warning("🚫 No tweet was generated.")
                return

            # Tweet Posting
            result = post_to_twitter(tweet)
            logging.info(f"✅ Tweet posted: {result}")

            # Post Log
            log_post(tweet, metadata)

            # Metadata Save
            save_metadata(metadata)

        except Exception as e:
            logging.error(f"❌ Error during tweet generation or posting: {e}", exc_info=True)

    except Exception as e:
        logging.error(f"❌ Unhandled exception in run_bot: {e}", exc_info=True)

if __name__ == "__main__":
    run_bot()