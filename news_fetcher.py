import random
from datetime import datetime

def fetch_latest_headlines():
    # Simulated dummy headlines for bot to reference
    dummy_news = [
        "भारत में शिक्षा सुधारों पर नई बहस",
        "ग्रामीण इलाकों में पानी की समस्या गंभीर",
        "संविधान के मूल मूल्यों की चर्चा तेज़",
        "देश में विज्ञान और अनुसंधान को नया बढ़ावा",
        "रोज़गार को लेकर युवाओं की आवाज़",
        "महिलाओं की सुरक्षा को लेकर नया कानून"
    ]

    random.shuffle(dummy_news)
    return {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "headlines": dummy_news[:3]  # Return 3 latest
    }