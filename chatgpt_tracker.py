import os
import csv
from datetime import datetime

# Configuration
CHATGPT_TOKEN_LIMIT = 100_000  # Monthly limit
CHATGPT_COST_PER_1K = 1.5      # ₹ per 1000 tokens

# Log file path
LOG_FILE = "chatgpt_usage_log.csv"

# Internal tracker
monthly_total = 0

def track_tokens(prompt_tokens, completion_tokens):
    global monthly_total

    # Token and cost calculation
    total_tokens = prompt_tokens + completion_tokens
    cost = (total_tokens / 1000) * CHATGPT_COST_PER_1K
    monthly_total += total_tokens

    # Log data
    now = datetime.now()
    row = [
        now.strftime("%Y-%m-%d %H:%M:%S"),
        prompt_tokens,
        completion_tokens,
        total_tokens,
        f"{cost:.2f}"
    ]

    # Create log file if not exists
    file_exists = os.path.isfile(LOG_FILE)
    with open(LOG_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["timestamp", "prompt_tokens", "completion_tokens", "total_tokens", "cost_inr"])
        writer.writerow(row)

    # Monthly limit warning
    if monthly_total >= CHATGPT_TOKEN_LIMIT:
        print("⚠️ CHATGPT token limit exceeded for the month!")