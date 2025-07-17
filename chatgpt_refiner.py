import os
from openai import OpenAI
from openai.types.chat import ChatCompletion

# ✅ Correct environment variable name
CHATGPT_API_KEY = os.getenv("CHATGPT_API_KEY")

# ✅ Check for None before using
if CHATGPT_API_KEY is None:
    raise ValueError("CHATGPT_API_KEY not found in environment variables.")

# ✅ Initialize OpenAI client
client = OpenAI(api_key=CHATGPT_API_KEY)

def refine_with_chatgpt(topic: str) -> str:
    try:
        system_prompt = (
            "You are Chacha Nehru, a nationalist voice of reason. "
            "Generate a powerful, emotionally resonant, satirical Hindi tweet about this topic:\n\n"
            f"\"{topic}\""
        )

        response: ChatCompletion = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": topic}
            ],
            max_tokens=200,
            temperature=0.8
        )

        # ✅ Defensive access
        if response.choices and response.choices[0].message.content:
            return response.choices[0].message.content.strip()
        else:
            return ""

    except Exception as e:
        print(f"[ChatGPT Refiner Error] {e}")
        return ""