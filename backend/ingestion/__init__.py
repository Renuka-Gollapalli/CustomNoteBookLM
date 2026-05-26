import os
from .pdf_loader import load_pdf
from .docx_loader import load_docx
from .pptx_loader import load_pptx
from .txt_loader import load_txt
from .image_loader import load_image
from .audio_loader import load_audio
from .video_loader import load_video
from .youtube_loader import load_youtube

EXTENSION_MAP = {
    ".pdf": load_pdf,
    ".docx": load_docx,
    ".pptx": load_pptx,
    ".txt": load_txt,
    ".png": load_image,
    ".jpg": load_image,
    ".jpeg": load_image,
    ".mp3": load_audio,
    ".wav": load_audio,
    ".mp4": load_video,
    ".mov": load_video,
}

def ingest_file(file_path: str) -> list[dict]:
    ext = os.path.splitext(file_path)[1].lower()
    loader = EXTENSION_MAP.get(ext)
    if loader is None:
        raise ValueError(f"Unsupported file type: {ext}")
    return loader(file_path)

def ingest_youtube(url: str) -> list[dict]:
    return load_youtube(url)
