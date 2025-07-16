import os
import requests

def generate_with_sarvam(prompt, api_key=None):
    if api_key is None:
        api_key = os.environ.get("SARVAM_API_KEY")

    if not api_key:
        print("❌ Sarvam API Key missing.")
        return {
            "text": "⚠️ SARVAM_API_KEY missing.",
            "inferred_prompt": prompt
        }

    url = "https://api.sarvam.ai/v1/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "sarvam-mistral",
        "prompt": prompt,
        "temperature": 0.7,
        "max_tokens": 400
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()
        return {
            "text": result.get("choices", [{}])[0].get("text", "").strip(),
            "inferred_prompt": prompt
        }
    except Exception as e:
        print(f"❌ Sarvam Exception: {e}")
        return {
            "text": "⚠️ Sarvam API failed.",
            "inferred_prompt": prompt
        }