import subprocess
import os
from .audio_loader import load_audio

def load_youtube(url: str, download_dir: str = "uploads") -> list[dict]:
    audio_path = os.path.join(download_dir, "yt_audio.wav")
    
    # Download audio only using yt-dlp
    subprocess.run([
        "yt-dlp", "-x", "--audio-format", "wav",
        "--audio-quality", "0",
        "-o", audio_path,
        url
    ], check=True)
    
    chunks = load_audio(audio_path)
    for c in chunks:
        c["source_type"] = "youtube"
        c["source"] = url
    
    os.remove(audio_path)
    return chunks
