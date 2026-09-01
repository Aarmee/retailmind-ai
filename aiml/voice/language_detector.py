from transformers import pipeline


# Multilingual language identification model
language_classifier = pipeline(
    "text-classification",
    model="papluca/xlm-roberta-base-language-detection",
    top_k=3
)


# Languages currently supported by RetailMind
SUPPORTED_LANGUAGES = {
    "en": "English",
    "hi": "Hindi",
    "mr": "Marathi"
}


def detect_language(text):

    if not text or not text.strip():
        return {
            "language": "unknown",
            "confidence": 0.0
        }

    results = language_classifier(text)

    # Depending on Transformers version, results can be nested
    if results and isinstance(results[0], list):
        results = results[0]

    for result in results:

        label = result["label"].lower()
        score = float(result["score"])

        if label in SUPPORTED_LANGUAGES:

            return {
                "language": label,
                "language_name": SUPPORTED_LANGUAGES[label],
                "confidence": round(score, 3)
            }

    return {
        "language": "unknown",
        "language_name": "Unknown",
        "confidence": 0.0
    }