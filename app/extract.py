# app/extract.py
import io
from typing import Optional
from PIL import Image
import pdfplumber
import docx2txt
import pytesseract

def extract_text_from_pdf_bytes(file_bytes: bytes) -> str:
    text_parts = []
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            txt = page.extract_text()
            if txt:
                text_parts.append(txt)
    # fallback: if no text extracted (scanned PDF), run OCR on each page as image
    if not text_parts:
        # simple OCR fallback: convert pages to images via pdfplumber
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                pil = page.to_image(resolution=300).original
                text_parts.append(pytesseract.image_to_string(pil))
    return "\n\n".join(text_parts).strip()

def extract_text_from_docx_bytes(file_bytes: bytes) -> str:
    # docx2txt expects a path; write bytes to temp file
    import tempfile
    with tempfile.NamedTemporaryFile(suffix=".docx", delete=True) as tmp:
        tmp.write(file_bytes)
        tmp.flush()
        text = docx2txt.process(tmp.name)
    return text or ""

def extract_text_from_image_bytes(file_bytes: bytes) -> str:
    img = Image.open(io.BytesIO(file_bytes))
    return pytesseract.image_to_string(img)
