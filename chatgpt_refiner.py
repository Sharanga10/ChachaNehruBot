# chatgpt_refiner.py

import openai
from chatgpt_tracker import track_tokens

openai.api_key = "YOUR_API_KEY"

def refine_with_chatgpt(text):
    messages = [
        {"role": "system", "content": "You are a satire assistant for Nehru bot."},
        {"role": "user", "content": text}
    ]
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.7,
    )

    usage = response["usage"]
    track_tokens(usage["prompt_tokens"], usage["completion_tokens"])

    return response["choices"][0]["message"]["content"]