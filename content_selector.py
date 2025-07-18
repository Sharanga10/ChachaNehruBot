# content_selector.py

import json
import random

def select_content_idea():
    with open("scheduler_config.json", "r") as f:
        scheduler_config = json.load(f)

    current_index = scheduler_config.get("current_index", 0)
    ideas = scheduler_config.get("tweet_content_ideas", [])

    if not ideas:
        raise Exception("No tweet content ideas found in scheduler_config.json")

    idea = ideas[current_index % len(ideas)]

    # Update index for next time
    scheduler_config["current_index"] = (current_index + 1) % len(ideas)
    with open("scheduler_config.json", "w") as f:
        json.dump(scheduler_config, f, indent=2)

    return idea