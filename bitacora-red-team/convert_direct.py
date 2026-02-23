import pdfplumber
import re
from pathlib import Path
from collections import defaultdict

PDF_FILE = Path(__file__).parent.parent / "1770937337663.pdf"
OUTPUT_DIR = Path(__file__).parent.parent / "bitacora"

CHAPTER_BOUNDS = [
    (7, 9, "01-introduccion", "Capítulo 01: Introducción"),
    (9, 45, "02-clases-vulnerabilidades", "Capítulo 02: Clases de Vulnerabilidades"),
    (45, 60, "03-fuzzing", "Capítulo 03: Fuzzing"),
    (60, 91, "04-patch-diffing", "Capítulo 04: Patch Diffing"),
    (91, 144, "05-analisis-crashes", "Capítulo 05: Análisis de Crashes"),
]


def extract_pages_with_structure(pdf):
    pages_data = []

    for page_num, page in enumerate(pdf.pages, 1):
        text = page.extract_text()
        tables = page.extract_tables()

        pages_data.append({"num": page_num, "text": text, "tables": tables})

    return pages_data


def detect_chapter_start(text):
    patterns = [
        r"^CAP?ÍTULO\s+(\d+)",
        r"^Capítulo\s+(\d+)",
        r"^(\d+)\.\s+[A-Z]",
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.MULTILINE | re.IGNORECASE)
        if match:
            return int(match.group(1))
    return None


def extract_chapters(pages_data):
    chapters = defaultdict(list)
    current_chapter = None

    for page in pages_data:
        text = page["text"]
        if not text:
            continue

        chapter_match = detect_chapter_start(text)
        if chapter_match:
            current_chapter = chapter_match

        if current_chapter:
            chapters[current_chapter].append(page)

    return chapters


def clean_text(text):
    if not text:
        return ""

    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"(\w)\.(\w)", r"\1. \2", text)
    text = text.replace("‐", "-").replace("‑", "-")
    text = text.replace("﴾", "(").replace("﴿", ")")

    return text.strip()


def text_to_html(text, tables=None):
    if not text:
        return ""

    lines = text.split("\n")
    html_lines = []
    in_code_block = False
    in_list = False

    for line in lines:
        line = line.strip()
        if not line:
            continue

        line = clean_text(line)

        if line.startswith("```"):
            if in_code_block:
                html_lines.append("</code></pre>")
                in_code_block = False
            else:
                html_lines.append("<pre><code>")
                in_code_block = True
            continue

        if in_code_block:
            html_lines.append(line)
            continue

        if re.match(r"^\d+\.\s+", line):
            if not in_list:
                html_lines.append("<ol>")
                in_list = True
            content = re.sub(r"^\d+\.\s+", "", line)
            html_lines.append(f"  <li>{content}</li>")
            continue
        elif in_list:
            html_lines.append("</ol>")
            in_list = False

        if re.match(r"^#{1,6}\s+", line):
            level = len(re.match(r"^(#{1,6})\s+", line).group(1))
            content = re.sub(r"^#{1,6}\s+", "", line)
            html_lines.append(f"<h{level}>{content}</h{level}>")
            continue

        if line.isupper() and len(line) < 80:
            html_lines.append(f"<h2>{line}</h2>")
            continue

        if len(line) > 3:
            html_lines.append(f"<p>{line}</p>")

    if in_list:
        html_lines.append("</ol>")
    if in_code_block:
        html_lines.append("</code></pre>")

    return "\n".join(html_lines)


def generate_html_page(chapter_key, chapter_title, pages_data):
    content_html = []

    for page in pages_data:
        text_html = text_to_html(page["text"], page.get("tables"))
        content_html.append(text_html)

    full_content = "\n".join(content_html)

    chapter_idx = None
    for i, (start, end, key, title) in enumerate(CHAPTER_BOUNDS):
        if key == chapter_key:
            chapter_idx = i
            break

    prev_link = ""
    next_link = ""

    if chapter_idx is not None:
        if chapter_idx > 0:
            prev_key, prev_title = (
                CHAPTER_BOUNDS[chapter_idx - 1][2],
                CHAPTER_BOUNDS[chapter_idx - 1][3],
            )
            prev_link = f'<a href="{prev_key}.html"><i class="fas fa-arrow-left"></i> {prev_title}</a>'
        else:
            prev_link = (
                '<a class="disabled"><i class="fas fa-arrow-left"></i> Anterior</a>'
            )

        if chapter_idx < len(CHAPTER_BOUNDS) - 1:
            next_key, next_title = (
                CHAPTER_BOUNDS[chapter_idx + 1][2],
                CHAPTER_BOUNDS[chapter_idx + 1][3],
            )
            next_link = f'<a href="{next_key}.html">{next_title} <i class="fas fa-arrow-right"></i></a>'
        else:
            next_link = (
                '<a class="disabled">Siguiente <i class="fas fa-arrow-right"></i></a>'
            )

    nav_items = ""
    for i, (start, end, key, title) in enumerate(CHAPTER_BOUNDS):
        icon = [
            "fa-book",
            "fa-bug",
            "fa-flask",
            "fa-code-branch",
            "fa-exclamation-triangle",
        ][i]
        active = " active" if key == chapter_key else ""
        nav_items += f'''
            <a href="{key}.html" class="nav-item{active}">
                <i class="fas {icon}"></i> {title.replace("Capítulo ", "").replace(": ", ": ")}
            </a>'''

    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{chapter_title} | Bitácora Red Team</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/animate.css/4.1.1/animate.min.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500;600&family=Lato:wght@300;400;700&family=Montserrat:wght@400;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github-dark.min.css">
    <style>
        :root {{
            --primary-color: #c62828;
            --primary-dark: #8e0000;
            --secondary-color: #212121;
            --accent-color: #ff5252;
            --text-color: #e0e0e0;
            --text-muted: #9e9e9e;
            --bg-dark: #121212;
            --bg-card: #1a1a1a;
            --bg-hover: #252525;
            --border-color: #333333;
            --sidebar-width: 280px;
            --code-bg: #0d0d0d;
        }}
        
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        
        body {{
            font-family: 'Lato', sans-serif;
            background: linear-gradient(145deg, #0a0a0a 0%, #151515 50%, #0d0d0d 100%);
            color: var(--text-color);
            line-height: 1.8;
            min-height: 100vh;
        }}
        
        body::before {{
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: 
                radial-gradient(ellipse at 20% 20%, rgba(198, 40, 40, 0.08) 0%, transparent 50%),
                radial-gradient(ellipse at 80% 80%, rgba(198, 40, 40, 0.05) 0%, transparent 40%);
            pointer-events: none;
            z-index: -1;
        }}
        
        .layout {{ display: flex; min-height: 100vh; }}
        
        .sidebar {{
            width: var(--sidebar-width);
            background: rgba(26, 26, 26, 0.95);
            backdrop-filter: blur(20px);
            border-right: 1px solid var(--border-color);
            position: fixed;
            height: 100vh;
            overflow-y: auto;
            z-index: 100;
        }}
        
        .sidebar::-webkit-scrollbar {{ width: 6px; }}
        .sidebar::-webkit-scrollbar-track {{ background: var(--bg-dark); }}
        .sidebar::-webkit-scrollbar-thumb {{ background: var(--primary-color); border-radius: 3px; }}
        
        .sidebar-header {{
            padding: 20px;
            background: linear-gradient(180deg, var(--primary-dark) 0%, var(--secondary-color) 100%);
            color: white;
            border-bottom: 2px solid var(--primary-color);
        }}
        
        .sidebar-header h1 {{
            font-family: 'Montserrat', sans-serif;
            font-size: 1rem;
            margin: 0;
        }}
        
        .sidebar-header p {{
            font-size: 0.75rem;
            color: var(--text-muted);
            margin-top: 5px;
        }}
        
        .nav-section {{
            padding: 15px 0;
        }}
        
        .nav-item {{
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 12px 20px;
            color: var(--text-muted);
            text-decoration: none;
            font-size: 0.9rem;
            transition: all 0.2s ease;
            border-left: 3px solid transparent;
        }}
        
        .nav-item:hover {{
            background: var(--bg-hover);
            color: var(--text-color);
            border-left-color: var(--accent-color);
        }}
        
        .nav-item.active {{
            background: rgba(198, 40, 40, 0.15);
            border-left-color: var(--primary-color);
            font-weight: 600;
            color: var(--accent-color);
        }}
        
        .nav-item i {{ width: 18px; text-align: center; color: var(--text-muted); }}
        .nav-item.active i {{ color: var(--accent-color); }}
        
        .main-content {{
            flex: 1;
            margin-left: var(--sidebar-width);
            padding: 40px 50px;
            max-width: calc(100vw - var(--sidebar-width));
        }}
        
        .content-header {{
            margin-bottom: 35px;
            padding-bottom: 20px;
            border-bottom: 2px solid var(--primary-color);
        }}
        
        .content-header h1 {{
            font-family: 'Montserrat', sans-serif;
            font-size: 2rem;
            color: var(--text-color);
        }}
        
        .section h2 {{
            font-family: 'Montserrat', sans-serif;
            color: var(--accent-color);
            margin: 30px 0 20px;
            padding-bottom: 10px;
            border-bottom: 1px solid var(--border-color);
            font-size: 1.4rem;
        }}
        
        .section h3, .section h4 {{
            color: var(--text-color);
            margin: 25px 0 15px;
            font-weight: 600;
        }}
        
        .section p {{ margin-bottom: 15px; text-align: justify; color: #bdbdbd; }}
        
        .section a {{
            color: var(--accent-color);
            text-decoration: none;
            border-bottom: 1px dotted var(--accent-color);
            transition: all 0.2s;
        }}
        
        .section a:hover {{ color: var(--primary-color); }}
        
        .section ul, .section ol {{ margin: 15px 0 15px 25px; color: #bdbdbd; }}
        .section li {{ margin-bottom: 8px; }}
        .section li::marker {{ color: var(--primary-color); }}
        
        .section pre {{
            background: var(--code-bg);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 20px;
            overflow-x: auto;
            margin: 20px 0;
        }}
        
        .section code {{
            font-family: 'Fira Code', monospace;
            font-size: 0.9rem;
        }}
        
        .section table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        
        .section th, .section td {{
            padding: 12px 15px;
            text-align: left;
            border: 1px solid var(--border-color);
        }}
        
        .section th {{
            background: var(--bg-card);
            color: var(--accent-color);
            font-weight: 600;
        }}
        
        .section tr:nth-child(even) {{ background: rgba(255, 255, 255, 0.02); }}
        .section tr:hover {{ background: rgba(198, 40, 40, 0.08); }}
        
        .page-nav {{
            display: flex;
            justify-content: space-between;
            margin-top: 50px;
            padding-top: 25px;
            border-top: 1px solid var(--border-color);
        }}
        
        .page-nav a {{
            display: inline-flex;
            align-items: center;
            gap: 10px;
            padding: 14px 24px;
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            text-decoration: none;
            color: var(--text-muted);
            transition: all 0.3s ease;
        }}
        
        .page-nav a:hover {{
            background: var(--primary-color);
            color: white;
            border-color: var(--primary-color);
            transform: translateY(-3px);
            box-shadow: 0 6px 20px rgba(198, 40, 40, 0.3);
        }}
        
        .page-nav a.disabled {{ opacity: 0.4; pointer-events: none; }}
        
        @media (max-width: 900px) {{
            .sidebar {{ transform: translateX(-100%); }}
            .sidebar.open {{ transform: translateX(0); }}
            .main-content {{ margin-left: 0; padding: 70px 20px 30px; }}
        }}
        
        ::-webkit-scrollbar {{ width: 8px; }}
        ::-webkit-scrollbar-track {{ background: var(--bg-dark); }}
        ::-webkit-scrollbar-thumb {{ background: var(--primary-color); border-radius: 4px; }}
    </style>
</head>
<body>
    <div class="layout">
        <aside class="sidebar" id="sidebar">
            <div class="sidebar-header">
                <h1><i class="fas fa-shield-alt"></i> Bitácora Red Team</h1>
                <p>Explotación Moderna del Kernel de Linux</p>
            </div>
            <nav class="nav-section">
                {nav_items}
            </nav>
        </aside>
        
        <main class="main-content">
            <div class="content-header">
                <h1>{chapter_title}</h1>
            </div>
            
            <div class="section">
                {full_content}
            </div>
            
            <div class="page-nav">
                {prev_link}
                {next_link}
            </div>
        </main>
    </div>
    
    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
    <script>
        hljs.highlightAll();
        
        const currentPath = window.location.pathname;
        const fileName = currentPath.split('/').pop().replace('.html', '');
        
        document.querySelectorAll('.nav-item').forEach(item => {{
            const href = item.getAttribute('href');
            if (href && href.replace('.html', '') === fileName) {{
                item.classList.add('active');
            }}
        }});
    </script>
</body>
</html>"""

    return html


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)

    print(f"Abriendo PDF: {PDF_FILE}")

    with pdfplumber.open(PDF_FILE) as pdf:
        print(f"Total de páginas: {len(pdf.pages)}")

        pages_data = extract_pages_with_structure(pdf)

        for start_page, end_page, chapter_key, chapter_title in CHAPTER_BOUNDS:
            chapter_pages = pages_data[start_page - 1 : end_page]
            print(f"Generando {chapter_key}.html ({len(chapter_pages)} páginas)")

            html = generate_html_page(chapter_key, chapter_title, chapter_pages)

            output_path = OUTPUT_DIR / f"{chapter_key}.html"
            output_path.write_text(html, encoding="utf-8")

    index_content = """<!DOCTYPE html>
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
