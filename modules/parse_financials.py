import pdfplumber
import pandas as pd
from PIL import Image
import pytesseract

def extract_text_from_pdf(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text

def extract_tables_from_pdf(pdf_path):
    tables = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            table = page.extract_table()
            if table and len(table) > 1:
                columns = table[0]
                cleaned_columns = []
                used_names = set()

                for i, col in enumerate(columns):
                    name = col if col and str(col).strip() != "" else f"Unnamed_{i}"
                    if name in used_names:
                        name += f"_{i}"
                    used_names.add(name)
                    cleaned_columns.append(name)

                try:
                    df = pd.DataFrame(table[1:], columns=cleaned_columns)
                    tables.append(df)
                except Exception as e:
                    print(f"⚠️ Failed to create DataFrame: {e}")
    return tables

def parse_financial_data(pdf_path):
    raw_text = extract_text_from_pdf(pdf_path)
    tables = extract_tables_from_pdf(pdf_path)

    # Placeholder: Just returning raw output for now
    return {
        "raw_text": raw_text,
        "tables": tables
    }
pytesseract.pytesseract.tesseract_cmd = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"  # ← Only on Windows
def extract_text_from_image(image_path):
    image = Image.open(image_path)
    return pytesseract.image_to_string(image)