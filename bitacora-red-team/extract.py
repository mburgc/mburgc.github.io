#!/usr/bin/env python3
"""
Extrae el contenido del PDF y lo organiza por páginas.
"""

import fitz  # PyMuPDF
from pathlib import Path

PDF_PATH = r"C:\Users\c\Documents\GitHub\mburgc.github.io\1770937337663.pdf"
OUTPUT_DIR = Path(r"C:\Users\c\Documents\GitHub\mburgc.github.io\bitacora-red-team")


def extract_pdf():
    doc = fitz.open(PDF_PATH)
    print(f"Total páginas: {len(doc)}")

    full_text = ""
    for page_num, page in enumerate(doc):
        text = page.get_text()
        full_text += (
            f"\n{'=' * 50}\n--- Página {page_num + 1} ---\n{'=' * 50}\n{text}\n"
        )

    # Guardar texto raw para análisis
    (OUTPUT_DIR / "00-raw-extract.txt").write_text(full_text, encoding="utf-8")
    print("Extracción completada: 00-raw-extract.txt")
    print(f"Caracteres extraídos: {len(full_text)}")

    return full_text


if __name__ == "__main__":
    extract_pdf()
