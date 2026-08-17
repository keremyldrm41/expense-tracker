import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.environ.get("ANTHROPIC_API_KEY")
URL = "https://api.anthropic.com/v1/messages"
MODEL = "claude-haiku-4-5"
TIMEOUT_SECONDS = 5

CATEGORIES = ["Food", "Transport", "Sports", "Entertainment", "Other"]

SYSTEM_PROMPT = (
    "You classify expense descriptions into exactly one category.\n"
    f"The only allowed categories are: {', '.join(CATEGORIES)}.\n"
    "Reply with the category name alone. No explanation, no punctuation, "
    "no extra words.\n"
    "If the description is unclear, empty, or fits none of the categories, "
    "reply with Other."
)


def _ask_model(description):
    if not API_KEY:
        return None

    headers = {
        "x-api-key": API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    body = {
        "model": MODEL,
        "max_tokens": 10,
        "temperature": 0,
        "system": SYSTEM_PROMPT,
        "messages": [{"role": "user", "content": description}],
    }

    try:
        response = requests.post(
            URL, headers=headers, json=body, timeout=TIMEOUT_SECONDS
        )
    except requests.exceptions.RequestException:
        return None

    if response.status_code != 200:
        return None

    try:
        return response.json()["content"][0]["text"]
    except (ValueError, KeyError, IndexError, TypeError):
        return None


def suggest_category(description):
    if not description or not description.strip():
        return None

    reply = _ask_model(description)

    if reply is None:
        return None

    cleaned = reply.strip()

    if cleaned in CATEGORIES:
        return cleaned

    return None