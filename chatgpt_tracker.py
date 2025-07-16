# chatgpt_tracker.py

USD_TO_INR = 84
INPUT_COST_PER_1K = 0.0005  # USD
OUTPUT_COST_PER_1K = 0.0015  # USD
MAX_MONTHLY_INR = 100

# Runtime counters
chatgpt_input_tokens = 0
chatgpt_output_tokens = 0

def estimate_cost_inr(input_tokens, output_tokens):
    input_usd = (input_tokens / 1000) * INPUT_COST_PER_1K
    output_usd = (output_tokens / 1000) * OUTPUT_COST_PER_1K
    return (input_usd + output_usd) * USD_TO_INR

def should_use_chatgpt():
    cost = estimate_cost_inr(chatgpt_input_tokens, chatgpt_output_tokens)
    return cost < MAX_MONTHLY_INR

def track_tokens(input_tokens, output_tokens):
    global chatgpt_input_tokens, chatgpt_output_tokens
    chatgpt_input_tokens += input_tokens
    chatgpt_output_tokens += output_tokens

def get_token_usage():
    return {
        "input_tokens": chatgpt_input_tokens,
        "output_tokens": chatgpt_output_tokens,
        "estimated_inr": estimate_cost_inr(chatgpt_input_tokens, chatgpt_output_tokens)
    }