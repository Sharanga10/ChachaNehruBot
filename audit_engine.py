import nltk
import re
import json
import requests
from transformers import pipeline
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from dotenv import load_dotenv
import os
load_dotenv()

GOOGLE_API_KEY = os.environ["GOOGLE_API_KEY"]

# Models
nltk.download('punkt')
fact_checker = pipeline("text-classification", model="roberta-large-mnli")
sentiment_analyzer = SentimentIntensityAnalyzer()

# Load banned keywords from config
with open("banned_keywords.json", "r") as f:
    banned_keywords = json.load(f)

def google_fact_check(query):
    url = f"https://factchecktools.googleapis.com/v1alpha1/claims:search?query={query}&key={GOOGLE_API_KEY}&languageCode=hi"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            claims = response.json().get('claims', [])
            for claim in claims:
                rating = claim.get('claimReview', [{}])[0].get('textualRating', '').lower()
                if 'false' in rating or 'misleading' in rating:
                    return False, rating
            return True, "No issues"
        return False, "API error"
    except Exception as e:
        return False, str(e)

def audit_content(text, premise, query):
    if not text or len(text.strip()) < 5:
        return False, "Empty or too short"

    # Rule 1: Sentence Structure
    sentences = nltk.sent_tokenize(text)
    if any(len(s.split()) < 4 or not any(verb in s for verb in ['है', 'था', 'कर']) for s in sentences):
        return False, "Incomplete sentence"

    # Rule 2: Sentiment
    sentiment = sentiment_analyzer.polarity_scores(text)
    if sentiment['compound'] < 0.9:
        return False, "Not positive enough"

    # Rule 3: NLI Fact-Check
    entailment = fact_checker(f"{premise} [SEP] {text}")[0]
    if entailment['label'] == 'CONTRADICTION' or entailment['score'] < 0.8:
        return False, "Factual issue"

    # Rule 4: External Fact-Check
    fact_valid, fact_reason = google_fact_check(query)
    if not fact_valid:
        return False, fact_reason

    # Rule 5: Banned Keywords
    for word in banned_keywords.get("words", []):
        if re.search(rf'\b{re.escape(word.lower())}\b', text.lower()):
            return False, f"Restricted keyword: {word}"

    return True, "Passed"