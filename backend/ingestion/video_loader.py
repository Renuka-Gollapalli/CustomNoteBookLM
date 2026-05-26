import subprocess
import os
from .audio_loader import load_audio

def load_video(file_path: str) -> list[dict]:
    # Extract audio from video using ffmpeg
    audio_path = file_path.rsplit(".", 1)[0] + "_audio.wav"
    subprocess.run([
        "ffmpeg", "-i", file_path,
        "-vn", "-acodec", "pcm_s16le",
        "-ar", "16000", "-ac", "1",
        audio_path, "-y"
    ], check=True, capture_output=True)
    
    chunks = load_audio(audio_path)
    # Update source_type
    for c in chunks:
        c["source_type"] = "video"
        c["source"] = file_path
    
    os.remove(audio_path)  # cleanup
    return chunks
