import os
import fitz  # PyMuPDF
import textract

def extract_text_from_file(file_path):
    """
    Extract text from a given file using appropriate method.
    Currently supports PDF and DOCX.
    """
    ext = os.path.splitext(file_path)[1].lower()

    try:
        if ext == ".pdf":
            return extract_text_from_pdf(file_path)
        elif ext in [".docx", ".doc"]:
            return extract_text_from_doc(file_path)
        else:
            print(f"⚠️ Unsupported file type: {ext}")
            return ""
    except Exception as e:
        print(f"❌ Failed to extract text from {file_path}: {e}")
        return ""

def extract_text_from_pdf(file_path):
    """Extract text from a PDF using PyMuPDF (fitz)."""
    text = ""
    with fitz.open(file_path) as doc:
        for page in doc:
            text += page.get_text()
    return text.strip()

def extract_text_from_doc(file_path):
    """Extract text from Word documents using textract."""
    text = textract.process(file_path)
    return text.decode("utf-8").strip()
