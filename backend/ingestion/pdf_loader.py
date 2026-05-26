import fitz  # PyMuPDF

def load_pdf(file_path: str) -> list[dict]:
    """Returns list of {text, page, source}"""
    doc = fitz.open(file_path)
    chunks = []
    for page_num, page in enumerate(doc):
        text = page.get_text().strip()
        if text:
            chunks.append({
                "text": text,
                "page": page_num + 1,
                "source": file_path,
                "source_type": "pdf"
            })
    return chunks
