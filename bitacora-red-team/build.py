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

CHAPTER_NAMES = {
    "01": ("01-introduccion", "Introducción"),
    "02": ("02-clases-vulnerabilidades", "Clases de Vulnerabilidades"),
    "03": ("03-fuzzing", "Fuzzing"),
    "04": ("04-patch-diffing", "Patch Diffing"),
    "05": ("05-analisis-crashes", "Análisis de Crashes"),
}


def load_template():
    return TEMPLATE_FILE.read_text(encoding="utf-8")


def get_navigation(markdown_files):
    nav = ""
    chapter_icons = {
        "01-introduccion": "fa-book",
        "02-clases-vulnerabilidades": "fa-bug",
        "03-fuzzing": "fa-flask",
        "04-patch-diffing": "fa-code-branch",
        "05-analisis-crashes": "fa-exclamation-triangle",
    }

    for i, chapter_key in enumerate(CHAPTER_ORDER):
        chapter_file = f"{chapter_key}.md"
        file_info = next((f for f in markdown_files if f.name == chapter_file), None)

        if file_info:
            icon = chapter_icons.get(chapter_key, "fa-file")
            title = CHAPTER_NAMES.get(
                chapter_key.split("-")[0], (chapter_key, chapter_key)
            )[1]
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


def convert_text_tables_to_markdown(content):
    """
    Convert text that looks like tables to proper Markdown tables.
    Detects patterns like:
    Campo
    Valor
    Título
    Bitácora
    """
    lines = content.split("\n")
    result = []
    i = 0

    while i < len(lines):
        line = lines[i].strip()

        # Detect potential table: multiple short lines in sequence that could be key-value
        # Pattern: 3+ lines of short text (not headers, not bullets)
        potential_table = []
        if (
            line
            and not line.startswith("#")
            and not line.startswith("•")
            and not line.startswith("-")
            and not line.startswith("|")
            and len(line) < 60
            and i + 1 < len(lines)
        ):
            j = i
            while j < len(lines) and j < i + 20:
                current = lines[j].strip()
                if (
                    current
                    and not current.startswith("#")
                    and not current.startswith("•")
                    and not current.startswith("-")
                    and not current.startswith("|")
                    and not current.startswith("---")
                    and len(current) < 60
                ):
                    potential_table.append(current)
                    j += 1
                else:
                    break

            # If we have 4+ lines that could be a table, convert it
            if len(potential_table) >= 4:
                # Check if even-indexed lines could be values (pairs)
                if len(potential_table) >= 4:
                    # Split into pairs: even = key, odd = value
                    table_lines = []
                    for k in range(0, len(potential_table) - 1, 2):
                        key = potential_table[k].strip()
                        val = (
                            potential_table[k + 1].strip()
                            if k + 1 < len(potential_table)
                            else ""
                        )
                        if key and val:
                            table_lines.append(f"| {key} | {val} |")

                    if len(table_lines) >= 2:
                        # Add header separator
                        header_len = max(len(l) for l in table_lines)
                        separator = f"|{'--' * (header_len // 2 + 1)}|"

                        result.append("")
                        result.append("| Campo | Valor |")
                        result.append(separator)
                        result.extend(table_lines)
                        result.append("")
                        i = j
                        continue

        result.append(line)
        i += 1

    return "\n".join(result)


def add_cross_references(content):
    """
    Convert chapter references like 'Capítulo 1', 'Capítulo 2', etc. to clickable links.
    Also converts section references to anchor links.
    """
    # Map chapter numbers to file paths
    for ch_num, (ch_file, ch_title) in CHAPTER_NAMES.items():
        # Match "Capítulo X" or "Capítulo X: Title"
        pattern = rf"(Capítulo\s+{ch_num}[^\n<]*)"
        replacement = rf"[\1]({ch_file}.html)"
        content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)

        # Also handle "Capítulo 1", "Capítulo 2", etc. in any context
        pattern2 = rf"\*?(Capítulo\s+{ch_num}[^\n\*]*)\*?"
        replacement2 = rf"**[\1]({ch_file}.html)**"
        content = re.sub(pattern2, replacement2, content, flags=re.IGNORECASE)

    # Convert section references to anchor links (e.g., "Sección 1.1" -> link to #11)
    content = re.sub(
        r"(Sección\s+(\d+\.\d+))", r"[\1](#\2)", content, flags=re.IGNORECASE
    )

    # Convert "Ver capítulo X" or "Véase capítulo X" references
    for ch_num, (ch_file, ch_title) in CHAPTER_NAMES.items():
        patterns = [
            rf"(?:Ver|Véase|Consultar)\s+capítulo\s+{ch_num}",
            rf"(?:capítulo|chapter)\s+{ch_num}",
        ]
        for pattern in patterns:
            content = re.sub(
                pattern, rf"[{ch_title}]({ch_file}.html)", content, flags=re.IGNORECASE
            )

    return content


def format_hyperlinks(content):
    """
    Convert raw URLs to clickable Markdown links.
    """
    # Match URLs that aren't already in markdown link format
    url_pattern = r"(?<!\[)(?<!\])(https?://[^\s\)<>\]]+)(?!\])"

    def replace_url(match):
        url = match.group(1)
        # Truncate long URLs for display
        display = url
        if len(url) > 50:
            display = url[:47] + "..."
        return f"[{display}]({url})"

    content = re.sub(url_pattern, replace_url, content)

    # Convert email addresses to mailto links
    email_pattern = r"([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})"
    content = re.sub(email_pattern, r"[\1](mailto:\1)", content)

    return content


def clean_markup(content):
    lines = content.split("\n")
    result = []
    
    for line in lines:
        original = line
        
        line = re.sub(r"\(\s*(\w+)\s*\)", r"\1", line)
        line = re.sub(r"  +", " ", line)
        
        line = re.sub(r"(\d+\.\d+)\s+\1", r"\1", line)
        
        line = re.sub(r"^(###+)\s+\d+\.\s+(\d+\.\d+)", r"\1 \2", line)
        line = re.sub(r"^(###+)\s+(\d+\.\d+)\.\s*", r"\1 \2", line)
        line = re.sub(r"^(####+)\s+\d+\.\s+(\d+\.\d+)", r"\1 \2", line)
        line = re.sub(r"^(####+)\s+(\d+\.\d+)\.\s*", r"\1 \2", line)
        
        line = re.sub(r"\.(\s+)", r"\1", line)
        line = re.sub(r"\.{3,}", "", line)
        line = line.strip()
        
        if line == "###" or line == "####":
            continue
            
        result.append(line)
    
    content = "\n".join(result)
    
    content = content.replace("﴾", "(").replace("﴿", ")")
    content = content.replace("‐", "-").replace("‑", "-").replace("–", "-")
    content = content.replace('"', '"').replace('"', '"')
    content = content.replace(""", "'").replace(""", "'")

    return content


def preprocess_markdown(content):
    """
    Apply all preprocessing steps to clean and enhance the markdown.
    """
    content = clean_markup(content)
    content = convert_text_tables_to_markdown(content)
    content = add_cross_references(content)
    content = format_hyperlinks(content)
    return content


def markdown_to_html(content):
    fm, content = extract_frontmatter(content)

    # Pre-process markdown before conversion
    content = preprocess_markdown(content)

    md = markdown.Markdown(
        extensions=[
            "extra",
            "codehilite",
            TocExtension(baselevel=1),
            "tables",
            "fenced_code",
            "nl2br",  # Convert newlines to <br>
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

    index_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="refresh" content="0;url=01-introduccion.html">
</head>
<body>
    <p>Redireccionando a <a href="01-introduccion.html">Capítulo 1: Introducción</a>...</p>
</body>
</html>"""
    (OUTPUT_DIR / "index.html").write_text(index_content, encoding="utf-8")

    print("¡Generación completada!")


if __name__ == "__main__":
    main()
