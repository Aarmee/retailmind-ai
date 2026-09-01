import os
import json
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY not found in .env file")

client = genai.Client(api_key=api_key)


SYSTEM_PROMPT = """
You are the multilingual AI transaction parser for RetailMind,
a retail management application.

The supported languages currently are:
- English
- Hindi
- Marathi

The input may also contain mixed-language speech.

Your job is to understand natural speech from a small-shop owner
and convert it into structured transaction data.

Speech-to-text may contain small recognition errors.
Use the context and meaning of the sentence to understand
obvious transcription errors.

DO NOT depend on fixed sentence structures.

DO NOT use a fixed product list.

DO NOT invent missing information.

TRANSACTION TYPES:

sale
purchase
return
unknown

PAYMENT TYPES:

cash
upi
credit
unknown

NORMALIZATION:

Words or phrases meaning that goods were sold should become:
sale

Words or phrases meaning that goods were purchased should become:
purchase

Words or phrases meaning that goods were returned should become:
return

Cash-related expressions should become:
cash

UPI-related expressions should become:
upi

Credit/udhaar-related expressions should become:
credit

QUANTITY:

Convert spoken numbers into numeric values.

AMOUNT:

Convert spoken monetary amounts into numbers.

PRODUCT:

Extract the product name from the speech.

Do not invent a product name.

CUSTOMER:

Only extract a customer name when the speaker clearly
identifies a customer.

Do not treat random speech-recognition errors as customer names.

LANGUAGE:

Use the language supplied by the application.

Return one of:

en
hi
mr
mixed
unknown

CONFIDENCE:

Return a number between 0 and 1.

Return ONLY valid JSON.

OUTPUT:

{
    "intent": "sale | purchase | return | unknown",
    "product_text": null,
    "quantity": null,
    "amount": null,
    "payment_mode": "cash | upi | credit | unknown",
    "customer_text": null,
    "language": "en | hi | mr | mixed | unknown",
    "confidence": 0.0
}
"""


def extract_transaction(text, detected_language):

    prompt = f"""
{SYSTEM_PROMPT}

APPLICATION LANGUAGE DETECTION:
{detected_language}

TRANSCRIBED RETAILER SPEECH:
{text}

Understand the transaction and return only JSON.
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    raw_text = response.text.strip()

    if raw_text.startswith("```"):
        raw_text = raw_text.replace("```json", "")
        raw_text = raw_text.replace("```", "")
        raw_text = raw_text.strip()

    try:

        data = json.loads(raw_text)

        fields = {
            "intent": "unknown",
            "product_text": None,
            "quantity": None,
            "amount": None,
            "payment_mode": "unknown",
            "customer_text": None,
            "language": detected_language,
            "confidence": 0.0
        }

        for field, default in fields.items():

            if field not in data:
                data[field] = default

        return data

    except json.JSONDecodeError:

        return {
            "intent": "unknown",
            "product_text": None,
            "quantity": None,
            "amount": None,
            "payment_mode": "unknown",
            "customer_text": None,
            "language": detected_language,
            "confidence": 0.0,
            "error": "Invalid JSON returned by AI",
            "raw_response": raw_text
        }