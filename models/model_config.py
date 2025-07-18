import json
import os

def get_model_config():
    """For compatibility with older imports"""
    return load_model_config()

def load_model_config():
    config_path = os.path.join(os.path.dirname(__file__), 'model_config.json')
    with open(config_path, 'r') as f:
        return json.load(f)