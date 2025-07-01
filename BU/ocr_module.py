import os
import pytesseract
from pdf2image import convert_from_path
from PIL import Image

# 🔧 Update these paths for your setup
POPPLER_PATH = r"C:\Program Files\poppler-windows-24.08.0-0\Library\bin"
TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Link Tesseract to pytesseract
pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH


def extract_text_from_pdf(pdf_path):
    try:
        print(f"📄 Converting PDF to images: {pdf_path}")
        images = convert_from_path(pdf_path, poppler_path=POPPLER_PATH)

        text = ""
        for i, image in enumerate(images):
            print(f"🔍 Running OCR on page {i + 1}")
            page_text = pytesseract.image_to_string(image)
            text += page_text + "\n"

        return text.strip()

    except Exception as e:
        print(f"❌ Error extracting text from PDF: {e}")
        return ""


def extract_text_from_image(image_path):
    try:
        print(f"🖼️ Running OCR on image: {image_path}")
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image)
        return text.strip()
    except Exception as e:
        print(f"❌ Error extracting text from image: {e}")
        return ""


def extract_text(file_path):
    if file_path.lower().endswith(".pdf"):
        return extract_text_from_pdf(file_path)
    elif file_path.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".tiff")):
        return extract_text_from_image(file_path)
    else:
        print(f"⚠️ Unsupported file type: {file_path}")
        return ""
