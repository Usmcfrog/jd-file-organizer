# ocr_module.py

import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io

def extract_text_from_file(file_path):
    """
    Extract text from a PDF or image file.
    Supports PDF files (multi-page) and image formats like JPG, PNG, etc.
    """
    try:
        if file_path.lower().endswith(".pdf"):
            return extract_text_from_pdf(file_path)
        else:
            return extract_text_from_image(file_path)
    except Exception as e:
        print(f"❌ OCR Error for {file_path}: {e}")
        return ""

def extract_text_from_pdf(pdf_path):
    """
    Extract text from a PDF using PyMuPDF and pytesseract.
    Falls back to OCR if page text is mostly empty.
    """
    text = ""
    doc = fitz.open(pdf_path)
    for page_num in range(len(doc)):
        page = doc[page_num]
        page_text = page.get_text()
        if len(page_text.strip()) > 100:
            text += page_text
        else:
            # Fallback to image-based OCR
            pix = page.get_pixmap(dpi=300)
            img = Image.open(io.BytesIO(pix.tobytes("png")))
            text += pytesseract.image_to_string(img)
    return text

def extract_text_from_image(image_path):
    """
    Extract text from an image file using pytesseract.
    """
    img = Image.open(image_path)
    return pytesseract.image_to_string(img)
