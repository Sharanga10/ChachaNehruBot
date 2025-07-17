import os
from chatgpt_connector import refine_with_chatgpt
from grok_connector import generate_with_grok
from sarvam_connector import generate_with_sarvam

def generate_content(topic: str) -> str:
    try:
        print("[ContentGen] Trying Grok…")
        result = generate_with_grok(topic)
        if result:
            print("[ContentGen] Grok succeeded.")
            return result
    except Exception as e:
        print(f"[ContentGen] Grok failed: {e}")

    try:
        print("[ContentGen] Trying ChatGPT…")
        result = refine_with_chatgpt(topic)
        if result:
            print("[ContentGen] ChatGPT succeeded.")
            return result
    except Exception as e:
        print(f"[ContentGen] ChatGPT failed: {e}")

    try:
        print("[ContentGen] Trying Sarvam…")
        result = generate_with_sarvam(topic)
        if result:
            print("[ContentGen] Sarvam succeeded.")
            return result
    except Exception as e:
        print(f"[ContentGen] Sarvam failed: {e}")

    print("[ContentGen] All model fallbacks failed.")
    return "🙏 क्षमा करें, तकनीकी त्रुटि के कारण इस विषय पर ट्वीट तैयार नहीं हो सका।"