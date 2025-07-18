import hashlib
import textwrap


def trim_tweet(content):
    """
    Ensures tweet content is within 280 characters.
    Trims intelligently with ellipsis if needed.
    """
    if len(content) <= 280:
        return content.strip()

    trimmed = textwrap.shorten(content, width=277, placeholder="...")
    return trimmed.strip()


def generate_tweet_id(content):
    """
    Generates a unique tweet ID using SHA256 hash of content.
    """
    return hashlib.sha256(content.encode('utf-8')).hexdigest()


def clean_text(text):
    """
    Cleans up whitespace and line breaks.
    """
    return ' '.join(text.strip().split())