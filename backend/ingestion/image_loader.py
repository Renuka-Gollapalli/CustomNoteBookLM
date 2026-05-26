import pytesseract
from PIL import Image

def load_image(file_path: str) -> list[dict]:
    img = Image.open(file_path)
    text = pytesseract.image_to_string(img).strip()
    if not text:
        return []
    return [{"text": text, "page": 1, "source": file_path, "source_type": "image"}]
