import json
import logging
import random
from chatgpt_refiner import chatgpt_generate
from sarvam_utils import generate_with_sarvam
from openai import OpenAI
import os

from chatgpt_tracker import should_use_chatgpt

# Load model config
with open("model_config.json", "r") as f:
    model_config = json.load(f)
PRIMARY_MODEL = model_config.get("primary", "grok-4")
BACKUP_MODEL = model_config.get("backup", "chatgpt")
THIRD_MODEL = model_config.get("third", "sarvam")

# Initialize Grok
XAI_API_KEY = os.environ.get("XAI_API_KEY")
xai_client = OpenAI(api_key=XAI_API_KEY, base_url="https://api.x.ai/v1")

def generate_with_grok(prompt):
    try:
        response = xai_client.chat.completions.create(
            model="grok-4",
            messages=[
                {"role": "system", "content": "You are Chacha Nehru bot. Reply in JSON: {'text':..., 'inferred_prompt':...}"},
                {"role": "user", "content": prompt}
            ]
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        logging.error(f"Grok failed: {e}")
        return None

def get_model_function(model_name):
    if model_name == "grok-4":
        return generate_with_grok
    elif model_name == "chatgpt":
        return chatgpt_generate
    elif model_name == "sarvam":
        return generate_with_sarvam
    else:
        return lambda prompt: {"text": "", "inferred_prompt": prompt}

def generate_by_quota(prompt, model_name):
    try:
        func = get_model_function(model_name)
        return func(prompt)
    except Exception as e:
        logging.warning(f"{model_name} generation failed: {e}")
        return None

def generate_content_safely(prompt, quota_id):
    model_order = {
        "grok": ["grok-4", "chatgpt", "sarvam"],
        "chatgpt": ["chatgpt", "grok-4", "sarvam"],
        "sarvam": ["sarvam", "grok-4", "chatgpt"]
    }

    model_try_order = model_order.get(quota_id, [PRIMARY_MODEL, BACKUP_MODEL, THIRD_MODEL])

    for model_name in model_try_order:
        if model_name == "chatgpt" and not should_use_chatgpt():
            continue
        result = generate_by_quota(prompt, model_name)
        if result and result.get("text"):
            return result
    return {"text": "", "inferred_prompt": prompt}