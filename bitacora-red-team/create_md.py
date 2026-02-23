import re
from pathlib import Path

RAW_FILE = Path(
    r"C:\Users\c\Documents\GitHub\mburgc.github.io\bitacora-red-team\00-raw-extract.txt"
)
OUTPUT_DIR = Path(
    r"C:\Users\c\Documents\GitHub\mburgc.github.io\bitacora-red-team\markdown"
)

CHAPTERS = {
    "01-introduccion": {"title": "Introducción", "start": 1, "end": 6},
    "02-clases-vulnerabilidades": {
        "title": "Clases de Vulnerabilidades",
        "start": 7,
        "end": 42,
    },
    "03-fuzzing": {"title": "Fuzzing", "start": 43, "end": 57},
    "04-patch-diffing": {"title": "Patch Diffing", "start": 58, "end": 88},
    "05-analisis-crashes": {"title": "Análisis de Crashes", "start": 89, "end": 144},
}


def parse_raw_text():
    content = RAW_FILE.read_text(encoding="utf-8")
    pages = {}
    current_page = None
    current_content = []

    for line in content.split("\n"):
        if line.startswith("--- Página"):
            if current_page is not None:
                pages[current_page] = "\n".join(current_content)
            match = re.search(r"Página (\d+)", line)
            current_page = int(match.group(1)) if match else None
            current_content = []
        elif current_page is not None:
            current_content.append(line)

    if current_page is not None:
        pages[current_page] = "\n".join(current_content)

    return pages


def clean_page_content(text):
    text = re.sub(r"^={50,}$", "", text, flags=re.MULTILINE)
    text = re.sub(r"^—+ Página \d+ —+$", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\d+$", "", text, flags=re.MULTILINE)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def convert_to_markdown(text, chapter_num):
    lines = text.split("\n")
    md_lines = []
    in_code = False
    code_lang = ""

    for line in lines:
        line = line.strip()
        if not line:
            md_lines.append("")
            continue

        if line.startswith("    ") or "\t" in line:
            if not in_code:
                in_code = True
                code_lang = (
                    "c"
                    if any(
                        kw in line.lower()
                        for kw in ["int", "void", "char", "printf", "struct"]
                    )
                    else ""
                )
                md_lines.append(f"```{code_lang}")
            md_lines.append(line)
            continue
        elif in_code:
            md_lines.append("```")
            in_code = False

        if re.match(r"^\d+\.\d+", line):
            md_lines.append(f"### {line}")
        elif re.match(r"^[A-Z][A-Z\s]+:$", line):
            md_lines.append(f"## {line}")
        elif len(line) < 80 and line.isupper():
            md_lines.append(f"### {line}")
        else:
            md_lines.append(line)

    if in_code:
        md_lines.append("```")

    return "\n".join(md_lines)


def create_markdown_files():
    pages = parse_raw_text()
    print(f"Parsed {len(pages)} páginas")

    for chapter_key, chapter_info in CHAPTERS.items():
        content_parts = []

        for page_num in range(chapter_info["start"], chapter_info["end"] + 1):
            if page_num in pages:
                cleaned = clean_page_content(pages[page_num])
                content_parts.append(cleaned)

        full_content = "\n\n---\n\n".join(content_parts)
        md_content = convert_to_markdown(full_content, chapter_info["start"])

        frontmatter = f'''---
title: "Capítulo {chapter_key[:2]}: {chapter_info["title"]}"
chapter: {chapter_key[:2]}
description: "{chapter_info["title"]} - Manual de Explotación del Kernel de Linux"
---

'''

        output_file = OUTPUT_DIR / f"{chapter_key}.md"
        output_file.write_text(frontmatter + md_content, encoding="utf-8")
        print(f"Creado: {output_file.name} ({len(md_content)} chars)")


if __name__ == "__main__":
    create_markdown_files()
    print("¡Archivos Markdown creados!")
