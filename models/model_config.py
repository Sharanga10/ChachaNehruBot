import json
import os

def get_model_config(model_name: str = None) -> dict:
    """
    Load and return config for the given model name from models/model_config.json.
    If no model_name provided, returns the entire config.
    Returns empty dict if not found or on error.
    """
    config_path = os.path.join(os.path.dirname(__file__), "model_config.json")
    try:
        with open(config_path, "r") as f:
            all_configs = json.load(f)
        
        if model_name is None:
            return all_configs
        
        return all_configs.get("models", {}).get(model_name, {})
    except Exception as e:
        print(f"⚠️ Error loading model config: {e}")
        return {}

def load_model_config():
    """For compatibility with older imports"""
    return get_model_config()