import whisper

_model = None

def get_whisper_model():
    global _model
    if _model is None:
        _model = whisper.load_model("base")  # use "small" for better accuracy
    return _model

def load_audio(file_path: str) -> list[dict]:
    model = get_whisper_model()
    result = model.transcribe(file_path)
    segments = []
    for seg in result["segments"]:
        segments.append({
            "text": seg["text"].strip(),
            "page": None,
            "timestamp": f"{seg['start']:.1f}s - {seg['end']:.1f}s",
            "source": file_path,
            "source_type": "audio"
        })
    return segments
