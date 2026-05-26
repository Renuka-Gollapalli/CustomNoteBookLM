from docx import Document

def load_docx(file_path: str) -> list[dict]:
    doc = Document(file_path)
    full_text = "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
    return [{
        "text": full_text,
        "page": 1,
        "source": file_path,
        "source_type": "docx"
    }]
