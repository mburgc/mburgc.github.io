# Plan de Implementación: Bitácora Red Team - Manual de Explotación Kernel Linux

> **Para Claude:** REQUIRED SUB-SKILL: Usa superpowers:subagent-driven-development para ejecutar este plan tarea por tarea.

**Objetivo:** Convertir el PDF del manual "Bitácora Red Team - Explotación Moderna del Kernel de Linux" en una página HTML navegable, estilizada al estilo HackTricks, integrada visualmente con el sitio portfolio existente.

**Arquitectura:** Sistema de generación estática simple que convierte archivos Markdown estructurados en HTML con sidebar de navegación jerárquica, tablas de contenido automáticas, y sintaxis resaltada para código. El sitio se genera localmente y se despliega a GitHub Pages.

**Tech Stack:**
- Lenguaje: HTML5, CSS3, JavaScript (vanilla)
- Extracción PDF: `pdftotext` o Python con `PyMuPDF`
- Markdown: python-markdown con extensiones (toc, codehilite, tables)
- Highlight: Highlight.js (ya tienen animate.css y font-awesome)
- Generación: Script Python simple que lee MD y genera HTML
- Hospedaje: GitHub Pages (build local, push estático)

---

## Fase 1: Extracción y Estructuración del Contenido

### Tarea 1: Extraer contenido del PDF a Markdown

**Archivos:**
- Crear: `bitacora-red-team/`

**Paso 1: Instalar dependencias de extracción**

```bash
pip install pymupdf python-markdown pygments
```

**Paso 2: Crear script de extracción**

Crear `bitacora-red-team/extract.py`:

```python
#!/usr/bin/env python3
"""
Extrae el contenido del PDF y lo convierte a archivos Markdown
organizados por capítulos.
"""
import fitz  # PyMuPDF
import re
from pathlib import Path

PDF_PATH = "../1770937337663.pdf"
OUTPUT_DIR = Path(".")

def extract_pdf():
    doc = fitz.open(PDF_PATH)
    print(f"Total páginas: {len(doc)}")
    
    # Estructura de capítulos basada en el índice
    chapters = {
        "01-introduccion.md": [],
        "02-clases-vulnerabilidades.md": [],
        "03-fuzzing.md": [],
        "04-patch-diffing.md",
        "05-analisis-crashes.md"
    }
    
    # Por ahora, extraer texto completo
    full_text = ""
    for page_num, page in enumerate(doc):
        text = page.get_text()
        full_text += f"\n--- Página {page_num + 1} ---\n{text}\n"
    
    # Guardar texto raw para análisis
    (OUTPUT_DIR / "00-raw-extract.txt").write_text(full_text, encoding="utf-8")
    print("Extracción completada: 00-raw-extract.txt")
    
    return full_text

if __name__ == "__main__":
    extract_pdf()
```

**Paso 3: Ejecutar extracción**

```bash
cd bitacora-red-team
python extract.py
```

**Paso 4: Analizar estructura y crear markdown por capítulos**

Basado en el índice extraído:

```
Capítulo 1: Clases de Vulnerabilidades
  - 1.1 Fundamentos de Corrupción de Memoria
    - 1.1.1 Stack Buffer Overflow
    - 1.1.2 Use-After-Free (UAF)
    - 1.1.3 Heap Buffer Overflow
    - 1.1.4 Out-of-Bounds Read
    - 1.1.5 Uninitialized Memory Use
    - 1.1.6 Reference Counting Bugs
    - 1.1.7 NULL Pointer Dereference
  - 1.2 Vulnerabilidades Lógicas y Condiciones de Carrera
  - 1.3 Confusión de Tipos y Enteros
  - 1.4 Vulnerabilidades de Strings y Formato
  - 1.5 Vulnerabilidades de Drivers y Sistemas de Archivos
  - 1.6 Evaluación de Impacto y Clasificación

Capítulo 2: Fuzzing
  - 2.1 Fundamentos
  - 2.2 AFL++ y Cobertura
  - 2.3 FuzzTest
  - 2.4 Honggfuzz
  - 2.5 Syzkaller
  - 2.6 Configuración Práctica
  - 2.7 Análisis de Crashes
  - 2.8 Desarrollo de Harnesses

Capítulo 3: Patch Diffing
  - 3.1 Fundamentos
  - 3.2 Extracción de Parches Windows
  - 3.3 Herramientas de Diffing (Ghidra/Ghidriff)
  - 3.4 Caso de Estudio: CVE-2022-34718 EvilESP
  - 3.5 Automatización
  - 3.6 Linux Kernel
  - 3.7 Caso de Estudio: 7-Zip

Capítulo 4: Análisis de Crashes
  - 4.1 Fundamentos
  - (contenido adicional...)
```

**Paso 5: Commit**

```bash
git add bitacora-red-team/
git commit -m "feat: add PDF extraction script"
```

---

### Tarea 2: Crear estructura de archivos Markdown

**Archivos:**
- Crear: `bitacora-red-team/markdown/01-introduccion.md`
- Crear: `bitacora-red-team/markdown/02-clases-vulnerabilidades.md`
- Crear: `bitacora-red-team/markdown/03-fuzzing.md`
- Crear: `bitacora-red-team/markdown/04-patch-diffing.md`
- Crear: `bitacora-red-team/markdown/05-analisis-crashes.md`

**Paso 1: Crear template de capítulo Markdown**

Cada capítulo debe tener frontmatter:

```markdown
---
title: "Capítulo X: Título"
chapter: X
sections:
  - title: "Sección X.Y"
    anchor: "seccion-x-y"
---

# Capítulo X: Título

## X.Y Sección
Contenido...
```

**Paso 2: Poblar contenido**

Para cada capítulo, crear el archivo MD con:
- Frontmatter (metadata)
- Encabezados jerárquicos (##, ###)
- Código en bloques \`\`\`
- Listas donde corresponda
- Tablas para comparaciones

**Paso 3: Commit**

```bash
git add bitacora-red-team/markdown/
git commit -m "feat: add structured markdown chapters"
```

---

## Fase 2: Generación de HTML

### Tarea 3: Crear template HTML base

**Archivos:**
- Crear: `bitacora-red-team/templates/base.html`

**Paso 1: Crear estructura HTML con sidebar**

```html
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }} | Bitácora Red Team</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/animate.css/4.1.1/animate.min.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Lato:wght@300;400;700&family=Montserrat:wght@400;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github-dark.min.css">
    <style>
        /* Variables - matches existing site */
        :root {
            --primary-color: #0D47A1;
            --secondary-color: #E3F2FD;
            --accent-color: #42A5F5;
            --text-color: #1A237E;
            --bg-color: #FFFFFF;
            --glass-bg: rgba(255, 255, 255, 0.7);
            --glass-border: rgba(255, 255, 255, 0.3);
            
            /* Sidebar */
            --sidebar-width: 280px;
            --sidebar-collapsed: 60px;
        }
        
        * { box-sizing: border-box; margin: 0; padding: 0; }
        
        body {
            font-family: 'Lato', sans-serif;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            color: var(--text-color);
            line-height: 1.8;
        }
        
        /* Layout */
        .layout {
            display: flex;
            min-height: 100vh;
        }
        
        /* Sidebar */
        .sidebar {
            width: var(--sidebar-width);
            background: var(--glass-bg);
            backdrop-filter: blur(15px);
            -webkit-backdrop-filter: blur(15px);
            border-right: 1px solid var(--glass-border);
            position: fixed;
            height: 100vh;
            overflow-y: auto;
            transition: width 0.3s ease;
            z-index: 100;
        }
        
        .sidebar.collapsed {
            width: var(--sidebar-collapsed);
        }
        
        .sidebar-header {
            padding: 20px;
            background: linear-gradient(135deg, #0a1628 0%, #0D47A1 50%, #1565C0 100%);
            color: white;
        }
        
        .sidebar-header h1 {
            font-family: 'Montserrat', sans-serif;
            font-size: 1.2rem;
            margin-bottom: 5px;
        }
        
        .sidebar-header .subtitle {
            font-size: 0.75rem;
            opacity: 0.8;
        }
        
        /* Navigation */
        .nav-section {
            padding: 10px 0;
            border-bottom: 1px solid rgba(0,0,0,0.05);
        }
        
        .nav-section-title {
            padding: 8px 20px;
            font-size: 0.7rem;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: var(--accent-color);
            font-weight: 700;
        }
        
        .nav-item {
            display: block;
            padding: 8px 20px;
            color: var(--text-color);
            text-decoration: none;
            font-size: 0.9rem;
            transition: all 0.2s ease;
            border-left: 3px solid transparent;
        }
        
        .nav-item:hover {
            background: var(--secondary-color);
            border-left-color: var(--accent-color);
        }
        
        .nav-item.active {
            background: var(--secondary-color);
            border-left-color: var(--primary-color);
            font-weight: 700;
        }
        
        .nav-item i {
            width: 20px;
            margin-right: 10px;
            color: var(--accent-color);
        }
        
        /* Nested navigation */
        .nav-subitem {
            padding-left: 50px;
            font-size: 0.85rem;
        }
        
        /* Main Content */
        .main-content {
            flex: 1;
            margin-left: var(--sidebar-width);
            padding: 40px 60px;
            max-width: calc(100vw - var(--sidebar-width));
        }
        
        /* Toggle button */
        .sidebar-toggle {
            position: fixed;
            top: 20px;
            left: 20px;
            z-index: 200;
            background: var(--primary-color);
            color: white;
            border: none;
            padding: 10px 15px;
            border-radius: 8px;
            cursor: pointer;
            display: none;
        }
        
        /* Content styling */
        .content-header {
            margin-bottom: 40px;
            padding-bottom: 20px;
            border-bottom: 2px solid var(--accent-color);
        }
        
        .content-header h1 {
            font-family: 'Montserrat', sans-serif;
            font-size: 2.5rem;
            color: var(--primary-color);
            margin-bottom: 10px;
        }
        
        .breadcrumb {
            font-size: 0.85rem;
            color: #666;
        }
        
        .breadcrumb a {
            color: var(--accent-color);
            text-decoration: none;
        }
        
        /* Chapter sections */
        .section {
            background: var(--glass-bg);
            backdrop-filter: blur(10px);
            border: 1px solid var(--glass-border);
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 30px;
        }
        
        .section h2 {
            font-family: 'Montserrat', sans-serif;
            color: var(--primary-color);
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid var(--accent-color);
        }
        
        .section h3 {
            color: var(--text-color);
            margin: 25px 0 15px;
        }
        
        .section h4 {
            color: #444;
            margin: 20px 0 10px;
            font-size: 1rem;
        }
        
        .section p {
            margin-bottom: 15px;
        }
        
        .section ul, .section ol {
            margin: 15px 0 15px 30px;
        }
        
        .section li {
            margin-bottom: 8px;
        }
        
        /* Code blocks */
        .section pre {
            background: #1e1e1e;
            border-radius: 10px;
            padding: 20px;
            overflow-x: auto;
            margin: 20px 0;
        }
        
        .section code {
            font-family: 'Fira Code', 'Consolas', monospace;
            font-size: 0.9em;
        }
        
        .section :not(pre) > code {
            background: var(--secondary-color);
            padding: 2px 8px;
            border-radius: 4px;
            color: var(--primary-color);
        }
        
        /* Tables */
        .section table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }
        
        .section th, .section td {
            padding: 12px 15px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        
        .section th {
            background: var(--secondary-color);
            font-weight: 700;
            color: var(--primary-color);
        }
        
        .section tr:hover {
            background: rgba(66, 165, 245, 0.05);
        }
        
        /* Cards for vulnerabilities */
        .vuln-card {
            background: linear-gradient(135deg, rgba(13, 71, 161, 0.05) 0%, rgba(66, 165, 245, 0.1) 100%);
            border-left: 4px solid var(--accent-color);
            padding: 20px;
            margin: 20px 0;
            border-radius: 0 10px 10px 0;
        }
        
        .vuln-card.danger {
            border-left-color: #f44336;
            background: linear-gradient(135deg, rgba(244, 67, 54, 0.05) 0%, rgba(244, 67, 54, 0.1) 100%);
        }
        
        .vuln-card.warning {
            border-left-color: #ff9800;
            background: linear-gradient(135deg, rgba(255, 152, 0, 0.05) 0%, rgba(255, 152, 0, 0.1) 100%);
        }
        
        .vuln-card.success {
            border-left-color: #4caf50;
            background: linear-gradient(135deg, rgba(76, 175, 80, 0.05) 0%, rgba(76, 175, 80, 0.1) 100%);
        }
        
        /* Table of Contents */
        .toc {
            background: var(--secondary-color);
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 30px;
        }
        
        .toc h3 {
            margin-top: 0;
            color: var(--primary-color);
            font-size: 1rem;
        }
        
        .toc ul {
            list-style: none;
            margin: 0;
            padding: 0;
        }
        
        .toc li {
            margin: 8px 0;
        }
        
        .toc a {
            color: var(--text-color);
            text-decoration: none;
            font-size: 0.9rem;
        }
        
        .toc a:hover {
            color: var(--accent-color);
        }
        
        /* Navigation arrows */
        .page-nav {
            display: flex;
            justify-content: space-between;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
        }
        
        .page-nav a {
            display: inline-flex;
            align-items: center;
            gap: 10px;
            padding: 12px 20px;
            background: var(--glass-bg);
            border: 1px solid var(--glass-border);
            border-radius: 10px;
            text-decoration: none;
            color: var(--text-color);
            transition: all 0.3s ease;
        }
        
        .page-nav a:hover {
            background: var(--primary-color);
            color: white;
            transform: translateY(-2px);
        }
        
        /* Responsive */
        @media (max-width: 768px) {
            .sidebar-toggle {
                display: block;
            }
            
            .sidebar {
                transform: translateX(-100%);
            }
            
            .sidebar.open {
                transform: translateX(0);
            }
            
            .main-content {
                margin-left: 0;
                padding: 60px 20px;
            }
        }
        
        /* Scrollbar */
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }
        
        ::-webkit-scrollbar-track {
            background: rgba(0,0,0,0.05);
        }
        
        ::-webkit-scrollbar-thumb {
            background: var(--accent-color);
            border-radius: 4px;
        }
    </style>
</head>
<body>
    <button class="sidebar-toggle" onclick="toggleSidebar()">
        <i class="fas fa-bars"></i>
    </button>
    
    <div class="layout">
        <!-- Sidebar -->
        <aside class="sidebar" id="sidebar">
            <div class="sidebar-header">
                <h1><i class="fas fa-shield-alt"></i> Bitácora</h1>
                <div class="subtitle">Red Team</div>
            </div>
            
            <nav>
                <!-- Navigation generated by build script -->
                {{ navigation }}
            </nav>
        </aside>
        
        <!-- Main Content -->
        <main class="main-content">
            <div class="content-header">
                <div class="breadcrumb">{{ breadcrumb }}</div>
                <h1>{{ title }}</h1>
            </div>
            
            {{ content }}
            
            <div class="page-nav">
                {{ prev_page }}
                {{ next_page }}
            </div>
        </main>
    </div>
    
    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
    <script>
        // Toggle sidebar on mobile
        function toggleSidebar() {
            document.getElementById('sidebar').classList.toggle('open');
        }
        
        // Highlight code blocks
        hljs.highlightAll();
        
        // Active link highlighting
        const currentPath = window.location.pathname;
        document.querySelectorAll('.nav-item').forEach(item => {
            if (item.getAttribute('href') === currentPath) {
                item.classList.add('active');
            }
        });
    </script>
</body>
</html>
```

**Paso 2: Commit**

```bash
git add bitacora-red-team/templates/
git commit -m "feat: add HTML template base"
```

---

### Tarea 4: Crear script de generación

**Archivos:**
- Crear: `bitacora-red-team/build.py`

**Paso 1: Crear script de build**

```python
#!/usr/bin/env python3
"""
Genera archivos HTML estáticos a partir de los archivos Markdown.
"""
import os
import re
from pathlib import Path
import markdown
from markdown.extensions.toc import TocExtension
from markdown.extensions.codehilite import CodeHiliteExtension

# Configuración
MARKDOWN_DIR = Path("markdown")
TEMPLATE_FILE = Path("templates/base.html")
OUTPUT_DIR = Path("../docs")  # GitHub Pages usa /docs

def load_template():
    return TEMPLATE_FILE.read_text(encoding="utf-8")

def get_navigation(markdown_files):
    """Genera la navegación lateral desde los archivos MD."""
    nav = '<div class="nav-section">'
    
    for md_file in sorted(markdown_files):
        chapter_num = md_file.stem.split('-')[0]
        title = extract_title(md_file)
        
        nav += f'''
        <div class="nav-section-title">Capítulo {chapter_num}</div>
        <a href="{md_file.stem}.html" class="nav-item">
            <i class="fas fa-book"></i>{title}
        </a>
        '''
    
    nav += '</div>'
    return nav

def extract_title(md_file):
    """Extrae el título del frontmatter."""
    content = md_file.read_text(encoding="utf-8")
    match = re.search(r'title:\s*"([^"]+)"', content)
    if match:
        return match.group(1)
    return md_file.stem

def extract_chapter(md_file):
    """Extrae el número de capítulo."""
    return md_file.stem.split('-')[0]

def markdown_to_html(content, md_file):
    """Convierte Markdown a HTML."""
    # Quitar frontmatter
    content = re.sub(r'^---.*?---\n', '', content, flags=re.DOTALL)
    
    # Configurar extensiones
    md = markdown.Markdown(
        extensions=[
            'extra',
            'codehilite',
            TocExtension(baselevel=2),
            'tables',
            'fenced_code',
        ]
    )
    
    html = md.convert(content)
    return html, md.Meta

def generate_page(template, md_file, navigation):
    """Genera una página HTML desde un archivo Markdown."""
    content, meta = markdown_to_html(md_file.read_text(encoding="utf-8"), md_file)
    title = meta.get('title', [md_file.stem])[0]
    chapter = extract_chapter(md_file)
    
    # Reemplazar variables en template
    page = template
    page = page.replace('{{ title }}', title)
    page = page.replace('{{ navigation }}', navigation)
    page = page.replace('{{ content }}', content)
    page = page.replace('{{ breadcrumb }}', f'Bitácora Red Team / Capítulo {chapter}')
    
    return page

def main():
    # Cargar template
    template = load_template()
    
    # Obtener archivos markdown
    md_files = list(MARKDOWN_DIR.glob("*.md"))
    print(f"Encontrados {len(md_files)} archivos markdown")
    
    # Generar navegación
    navigation = get_navigation(md_files)
    
    # Generar cada página
    for md_file in sorted(md_files):
        print(f"Generando: {md_file.stem}.html")
        
        page = generate_page(template, md_file, navigation)
        
        output_path = OUTPUT_DIR / f"{md_file.stem}.html"
        output_path.write_text(page, encoding="utf-8")
    
    print("¡Generación completada!")

if __name__ == "__main__":
    main()
```

**Paso 2: Commit**

```bash
git add bitacora-red-team/build.py
git commit -m "feat: add build script"
```

---

## Fase 3: Configuración de GitHub Pages

### Tarea 5: Configurar GitHub Pages

**Archivos:**
- Modificar: `.github/workflows/deploy.yml` (crear si no existe)

**Paso 1: Crear workflow de GitHub Actions**

```yaml
name: Deploy to GitHub Pages

on:
  push:
    branches: [main]
    paths:
      - 'bitacora-red-team/**'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install python-markdown pygments
      
      - name: Build
        run: |
          cd bitacora-red-team
          python build.py
      
      - name: Deploy
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./docs
```

**Paso 2: Commit**

```bash
git add .github/workflows/
git commit -m "ci: add GitHub Pages deployment workflow"
```

---

## Fase 4: Estilo Visual (Matching con Sitio Existente)

### Tarea 6: Personalizar estilos

**Archivos:**
- Modificar: `bitacora-red-team/templates/base.html`

**Paso 1: Añadir efectos de partículas (opcional, más liviano)**

El sitio actual usa particles.js. Para el manual, podemos añadir un fondo más sutil:

```css
/* Fondo alternativo para manual - más legible */
body.manual-mode {
    background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 50%, #dee2e6 100%);
}

/* Melhorar contraste del contenido */
.section {
    background: rgba(255, 255, 255, 0.9);
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}
```

**Paso 2: Commit**

```bash
git add bitacora-red-team/
git commit -m "feat: add manual-specific styling"
```

---

## Fase 5: Mejoras Adicionales

### Tarea 7: Añadir búsqueda (opcional)

**Archivos:**
- Crear: `bitacora-red-team/templates/search.html`

**Paso 1: Añadir widget de búsqueda simple**

```html
<div class="search-box">
    <input type="text" id="search" placeholder="Buscar en el manual...">
    <div id="search-results"></div>
</div>

<script>
document.getElementById('search').addEventListener('input', function(e) {
    const query = e.target.value.toLowerCase();
    const sections = document.querySelectorAll('.section h2, .section h3');
    
    // Simple search - highlight matches
    sections.forEach(section => {
        const text = section.textContent.toLowerCase();
        if (text.includes(query)) {
            section.style.background = 'yellow';
        }
    });
});
</script>
```

**Paso 2: Commit**

```bash
git add bitacora-red-team/
git commit -m "feat: add basic search functionality"
```

---

## Verificación

### Checklist de verificación

- [ ] PDF extraído correctamente
- [ ] Archivos Markdown creados con estructura correcta
- [ ] Template HTML creado con sidebar de navegación
- [ ] Navegación genera automáticamente desde archivos MD
- [ ] Código tiene syntax highlighting
- [ ] Estilos coinciden con sitio existente (glassmorphism, colores)
- [ ] Responsive en móvil
- [ ] GitHub Pages configurado y desplegando
- [ ] Navegación entre capítulos funciona
- [ ] Table of Contents generado automáticamente

---

## commands de Ejecución

### Generación local

```bash
cd bitacora-red-team
pip install python-markdown pygments
python build.py
```

### Vista previa local

```bash
# Con Python
python -m http.server 8000 --directory ../docs

# O con PHP
php -S localhost:8000 -t ../docs
```

### Despliegue

```bash
git push origin main
# GitHub Actions despliega automáticamente a GitHub Pages
```

---

**Plan completado y guardado en:** `bitacora-red-team/docs/plan-implementacion.md`

---

## Ejecución

**Dos opciones de ejecución:**

1. **Subagent-Driven (esta sesión)** - Dispacho un subagent fresco por tarea, reviso entre tareas, iteración rápida

2. **Sesión Paralela (separada)** - Abrir nueva sesión con executing-plans, ejecución por lotes con checkpoints

**¿Qué enfoque prefieres?**
