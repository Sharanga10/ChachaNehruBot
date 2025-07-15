# sarvam_utils.py

import os
import requests

SARVAM_API_KEY = os.environ.get("SARVAM_API_KEY")

def generate_with_sarvam(prompt):
    url = "https://api.sarvam.ai/v1/completions"
    headers = {
        "Authorization": f"Bearer {SARVAM_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "sarvam-mistral",
        "prompt": prompt,
        "temperature": 0.7,
        "max_tokens": 400
    }
    response = requests.post(url, headers=headers, json=payload)
    result = response.json()
    return {
        "text": result.get("choices", [{}])[0].get("text", "").strip(),
        "inferred_prompt": prompt
    }