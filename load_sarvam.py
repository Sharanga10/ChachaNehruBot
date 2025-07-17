from openai import OpenAI
import os

SARVAM_API_KEY = os.getenv("SARVAM_API_KEY")

client = OpenAI(
    base_url="https://api.sarvam.ai/v1",
    api_key=SARVAM_API_KEY,
)

def query_sarvam(prompt: str) -> str:
    messages = [
        {"role": "system", "content": "You are a helpful AI assistant."},
        {"role": "user", "content": prompt},
    ]

    # type: ignore
    response = client.chat.completions.create(
        model="sarvam-m",
        messages=messages,
        reasoning_effort="medium",
        max_completion_tokens=400,
    )
    content = response.choices[0].message.content
    return content.strip() if content else ""

if __name__ == "__main__":
    print(query_sarvam("भारत के प्रथम प्रधानमंत्री कौन थे?"))