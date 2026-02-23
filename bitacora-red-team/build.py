import os
import re
from pathlib import Path
import markdown
from markdown.extensions.toc import TocExtension

MARKDOWN_DIR = Path(__file__).parent / "markdown"
TEMPLATE_FILE = Path(__file__).parent / "templates" / "base.html"
OUTPUT_DIR = Path(__file__).parent.parent / "bitacora"

CHAPTER_ORDER = [
    "01-introduccion",
    "02-clases-vulnerabilidades",
    "03-fuzzing",
    "04-patch-diffing",
    "05-analisis-crashes",
]


def load_template():
    return TEMPLATE_FILE.read_text(encoding="utf-8")


def get_navigation(markdown_files):
    nav = ""
    chapter_names = {
        "01-introduccion": ("Introducción", "fa-book"),
        "02-clases-vulnerabilidades": ("Clases de Vulnerabilidades", "fa-bug"),
        "03-fuzzing": ("Fuzzing", "fa-flask"),
        "04-patch-diffing": ("Patch Diffing", "fa-code-branch"),
        "05-analisis-crashes": ("Análisis de Crashes", "fa-exclamation-triangle"),
    }

    for i, chapter_key in enumerate(CHAPTER_ORDER):
        chapter_file = f"{chapter_key}.md"
        file_info = next((f for f in markdown_files if f.name == chapter_file), None)

        if file_info:
            title, icon = chapter_names.get(chapter_key, (chapter_key, "fa-file"))
            nav += f'''
            <a href="{chapter_key}.html" class="nav-item">
                <i class="fas {icon}"></i>{title}
            </a>'''

    return nav


def extract_frontmatter(content):
    match = re.search(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if match:
        fm = {}
        for line in match.group(1).split("\n"):
            if ":" in line:
                key, val = line.split(":", 1)
                fm[key.strip()] = val.strip().strip('"')
        return fm, content[match.end() :]
    return {}, content


def extract_title(md_file):
    content = md_file.read_text(encoding="utf-8")
    fm, _ = extract_frontmatter(content)
    return fm.get("title", md_file.stem.replace("-", " ").title())


def extract_chapter(md_file):
    return md_file.stem.split("-")[0]


def markdown_to_html(content):
    fm, content = extract_frontmatter(content)

    md = markdown.Markdown(
        extensions=[
            "extra",
            "codehilite",
            TocExtension(baselevel=1),
            "tables",
            "fenced_code",
        ]
    )

    html = md.convert(content)
    return html, fm


def generate_page(template, md_file, navigation, all_files):
    content = md_file.read_text(encoding="utf-8")
    html_content, fm = markdown_to_html(content)
    title = fm.get("title", md_file.stem.replace("-", " ").title())
    chapter = extract_chapter(md_file)

    chapter_idx = (
        CHAPTER_ORDER.index(md_file.stem) if md_file.stem in CHAPTER_ORDER else 0
    )

    prev_page = ""
    next_page = ""

    if chapter_idx > 0:
        prev_chapter = CHAPTER_ORDER[chapter_idx - 1]
        prev_title = extract_title(next(f for f in all_files if f.stem == prev_chapter))
        prev_page = f'<a href="{prev_chapter}.html"><i class="fas fa-arrow-left"></i>{prev_title}</a>'
    else:
        prev_page = '<a class="disabled"><i class="fas fa-arrow-left"></i>Anterior</a>'

    if chapter_idx < len(CHAPTER_ORDER) - 1:
        next_chapter = CHAPTER_ORDER[chapter_idx + 1]
        next_title = extract_title(next(f for f in all_files if f.stem == next_chapter))
        next_page = f'<a href="{next_chapter}.html">{next_title}<i class="fas fa-arrow-right"></i></a>'
    else:
        next_page = (
            '<a class="disabled">Siguiente<i class="fas fa-arrow-right"></i></a>'
        )

    page = template
    page = page.replace("{{ title }}", title)
    page = page.replace("{{ navigation }}", navigation)
    page = page.replace("{{ content }}", f'<div class="section">{html_content}</div>')
    page = page.replace(
        "{{ breadcrumb }}", f'<a href="/">Bitácora Red Team</a> / {title}'
    )
    page = page.replace("{{ prev_page }}", prev_page)
    page = page.replace("{{ next_page }}", next_page)

    return page


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)

    template = load_template()
    md_files = list(MARKDOWN_DIR.glob("*.md"))
    print(f"Encontrados {len(md_files)} archivos markdown")

    navigation = get_navigation(md_files)

    for chapter_key in CHAPTER_ORDER:
        md_file = next((f for f in md_files if f.stem == chapter_key), None)
        if md_file:
            print(f"Generando: {md_file.stem}.html")
            page = generate_page(template, md_file, navigation, md_files)
            output_path = OUTPUT_DIR / f"{md_file.stem}.html"
            output_path.write_text(page, encoding="utf-8")

    index_content = f'''<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="refresh" content="0;url=01-introduccion.html">
</head>
<body>
    <p>Redireccionando a <a href="01-introduccion.html">Capítulo 1: Introducción</a>...</p>
</body>
</html>'''
    (OUTPUT_DIR / "index.html").write_text(index_content, encoding="utf-8")

    print("¡Generación completada!")


if __name__ == "__main__":
    main()
