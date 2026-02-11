from faster_whisper import WhisperModel

# Load once per worker (very important)
model = WhisperModel(
    "base",
    device="cpu",          # later: "cuda"
    compute_type="int8"    # CPU optimized
)

def transcribe(audio_path: str) -> dict:
    segments, info = model.transcribe(
        audio_path,
        beam_size=5,
        vad_filter=True
    )

    text = " ".join(segment.text for segment in segments)

    return {
        "text": text.strip(),
        "language": info.language,
        "duration": info.duration
    }
