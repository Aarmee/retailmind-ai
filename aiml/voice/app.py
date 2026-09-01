import sys

from speech_to_text import transcribe_audio
from language_detector import detect_language
from nlp import extract_transaction
from validation import validate_transaction


def process_voice_transaction(audio_file):

    # --------------------------------
    # 1. Voice → Text
    # --------------------------------

    transcription = transcribe_audio(audio_file)

    text = transcription["text"]

    # --------------------------------
    # 2. Text → Language Detection
    # --------------------------------

    language_result = detect_language(text)

    detected_language = language_result["language"]

    # --------------------------------
    # 3. Text → Transaction Extraction
    # --------------------------------

    transaction = extract_transaction(
        text,
        detected_language
    )

    # --------------------------------
    # 4. Validation
    # --------------------------------

    validation = validate_transaction(transaction)

    return {
        "transcription": text,
        "language_detection": language_result,
        "transaction": transaction,
        "validation": validation
    }


if __name__ == "__main__":

    audio_file = (
        sys.argv[1]
        if len(sys.argv) > 1
        else "Recording.m4a"
    )

    result = process_voice_transaction(audio_file)

    print("\n========== TRANSCRIPTION ==========")
    print(result["transcription"])

    print("\n========== LANGUAGE DETECTION ==========")
    print(result["language_detection"])

    print("\n========== AI EXTRACTION ==========")
    print(result["transaction"])

    print("\n========== VALIDATION ==========")
    print(result["validation"])