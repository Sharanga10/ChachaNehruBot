# grok_tracker.py

USD_TO_INR = 84
INPUT_COST_PER_1K = 0.001  # Estimated based on current rates
OUTPUT_COST_PER_1K = 0.002  # Slightly higher than ChatGPT
MAX_MONTHLY_INR = 250  # Your budget for Grok

# Runtime counters
grok_input_tokens = 0
grok_output_tokens = 0

def estimate_cost_inr(input_tokens, output_tokens):
    input_usd = (input_tokens / 1000) * INPUT_COST_PER_1K
    output_usd = (output_tokens / 1000) * OUTPUT_COST_PER_1K
    return (input_usd + output_usd) * USD_TO_INR

def should_use_grok():
    cost = estimate_cost_inr(grok_input_tokens, grok_output_tokens)
    return cost < MAX_MONTHLY_INR

def track_tokens(input_tokens, output_tokens):
    global grok_input_tokens, grok_output_tokens
    grok_input_tokens += input_tokens
    grok_output_tokens += output_tokens

def get_token_usage():
    return {
        "input_tokens": grok_input_tokens,
        "output_tokens": grok_output_tokens,
        "estimated_inr": estimate_cost_inr(grok_input_tokens, grok_output_tokens)
    }