"""
Resume text extraction.

Strategy (kept deliberately low-weight / free):
  1. PDF  -> try direct text extraction with `pypdf` (fast, no OCR needed for
             the vast majority of resumes, which are text-based PDFs).
  2. DOCX -> direct text extraction with `python-docx`.
  3. If a PDF yields almost no text (i.e. it's a scanned/image-based PDF), or
     if the upload is a photo, fall back to OCR via `pytesseract` (Tesseract,
     a free open-source OCR engine) — PDFs are rasterized to images first
     with `pdf2image` (needs the `poppler-utils` system package; Tesseract
     itself needs the `tesseract-ocr` system package — both are installed in
     the provided Dockerfile).
  4. .txt is just read directly.

If OCR isn't available in the runtime environment (binaries missing), we
fail soft and return an empty string rather than crashing — the caller asks
the user to paste their resume as text instead.
"""

import re
from pathlib import Path
from typing import Optional

EMAIL_REGEX = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
MIN_TEXT_LENGTH_BEFORE_OCR = 50  # below this, assume the PDF is scanned/image-based


def extract_text_from_pdf(path: str) -> str:
    text = ""
    try:
        import pypdf

        reader = pypdf.PdfReader(path)
        text = "\n".join((page.extract_text() or "") for page in reader.pages).strip()
    except Exception:
        text = ""

    if len(text) < MIN_TEXT_LENGTH_BEFORE_OCR:
        ocr_text = _ocr_pdf(path)
        if len(ocr_text) > len(text):
            text = ocr_text
    return text


def _ocr_pdf(path: str) -> str:
    try:
        import pytesseract
        from pdf2image import convert_from_path

        pages = convert_from_path(path)
        return "\n".join(pytesseract.image_to_string(page) for page in pages).strip()
    except Exception:
        # Tesseract/poppler not installed, or OCR failed — fail soft.
        return ""


def extract_text_from_docx(path: str) -> str:
    try:
        import docx  # python-docx

        document = docx.Document(path)
        return "\n".join(p.text for p in document.paragraphs).strip()
    except Exception:
        return ""


def extract_text_from_image(path: str) -> str:
    try:
        import pytesseract
        from PIL import Image

        return pytesseract.image_to_string(Image.open(path)).strip()
    except Exception:
        return ""


def extract_resume_text(file_path: str, file_ext: str) -> str:
    """Dispatch to the right extractor based on file extension."""
    ext = file_ext.lower().lstrip(".")
    if ext == "pdf":
        return extract_text_from_pdf(file_path)
    if ext in ("docx", "doc"):
        return extract_text_from_docx(file_path)
    if ext in ("png", "jpg", "jpeg", "webp", "bmp"):
        return extract_text_from_image(file_path)
    if ext == "txt":
        return Path(file_path).read_text(errors="ignore").strip()
    return ""


def find_email_regex(text: str) -> Optional[str]:
    match = EMAIL_REGEX.search(text)
    return match.group(0) if match else None


def is_valid_email(text: str) -> bool:
    return bool(EMAIL_REGEX.fullmatch(text.strip()))
