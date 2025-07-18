# banned_words.py

import json

def load_banned_keywords():
    try:
        with open("banned_keywords.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        hard_ban = data.get("hard_ban", [])
        soft_warn = data.get("soft_warn", [])
        return set(hard_ban), set(soft_warn)
    except FileNotFoundError:
        return set(), set()

hard_ban_keywords, soft_warn_keywords = load_banned_keywords()

def is_banned(text):
    text_lower = text.lower()
    return any(word in text_lower for word in hard_ban_keywords)

def is_soft_warn(text):
    text_lower = text.lower()
    return any(word in text_lower for word in soft_warn_keywords)