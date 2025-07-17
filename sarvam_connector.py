# sarvam_connector.py
from load_sarvam import query_sarvam

def generate_with_sarvam(prompt: str, max_tokens: int = 400) -> str:
    try:
        return query_sarvam(prompt)
    except Exception as e:
        return f"[Sarvam Error] {str(e)}"