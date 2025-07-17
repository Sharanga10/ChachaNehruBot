import os
import logging
from openai import OpenAI

# Setup logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("ChachaNehruBot")

# Setup OpenAI client
client = OpenAI(api_key=os.getenv("CHATGPT_API_KEY"))

def refine_with_chatgpt(prompt: str) -> str:
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that improves tweets in Hindi or Hinglish without changing their core meaning. Make them more impactful, poetic, sharp, or emotionally resonant based on the tone of the input. Do not ask for clarification."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=280
        )
        content = response.choices[0].message.content if response.choices else None
        refined = content.strip() if content else prompt  # fallback
        return refined
    except Exception as e:
        logger.error(f"[ChatGPT Error] {e}")
        return prompt  # fallback