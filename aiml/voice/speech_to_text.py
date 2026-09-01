import whisper


print("Loading Whisper model...")

model = whisper.load_model("small")

print("Whisper model loaded.")


def transcribe_audio(audio_file):

    result = model.transcribe(
        audio_file,
        task="transcribe",
        fp16=False
    )

    return {
        "text": result["text"].strip()
    }