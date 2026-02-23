import markdown
import os


def generate_html(
    text, title, language, other_language_path, chapters, current_chapter, all_chapters
):
    chapter_num = ""
    chapter_title = ""

    for ch in all_chapters:
        if ch["file"] == current_chapter:
            chapter_num = ch["num"]
            chapter_title = ch["title_es"] if language == "es" else ch["title_en"]
            break

    search_script = """<script>
document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('searchbar');
    const searchBtn = document.getElementById('search-btn');
    
    function performSearch() {
        let input = searchInput.value.toLowerCase().trim();
        let content = document.querySelector('.content-area');
        let elements = content.querySelectorAll('p, li, h1, h2, h3, h4, h5, h6, pre, code');
        
        elements.forEach(el => {
            el.style.display = '';
            if (el.classList.contains('search-highlight')) {
                el.innerHTML = el.textContent;
                el.classList.remove('search-highlight');
            }
        });
        
        if (input === "") return;
        
        elements.forEach(el => {
            if (el.textContent.toLowerCase().includes(input)) {
                let html = el.innerHTML;
                let regex = new RegExp('(' + input + ')', 'gi');
                el.innerHTML = html.replace(regex, '<span class="search-highlight">$1</span>');
            } else {
                el.style.display = 'none';
            }
        });
    }
    
    if (searchBtn) searchBtn.addEventListener('click', performSearch);
    if (searchInput) searchInput.addEventListener('keyup', e => { if (e.key === 'Enter') performSearch(); });
    
    const menuToggle = document.getElementById('menu-toggle');
    const sidebar = document.querySelector('.sidebar');
    const overlay = document.querySelector('.sidebar-overlay');
    if (menuToggle) menuToggle.addEventListener('click', () => { sidebar.classList.toggle('active'); overlay.classList.toggle('active'); });
    if (overlay) overlay.addEventListener('click', () => { sidebar.classList.remove('active'); overlay.classList.remove('active'); });
});
</script>"""

    html = markdown.markdown(text, extensions=["tables", "fenced_code", "codehilite"])
    html = html.replace(".md", ".html")

    chapter_nav = ""
    for ch in chapters:
        active_class = "active" if ch["file"] == current_chapter else ""
        if language == "en":
            filename = (
                ch["file"]
                .replace("clases-vulnerabilidades", "vulnerability-classes")
                .replace("analisis-crashes", "crash-analysis")
                .replace("introduccion", "introduction")
            )
        else:
            filename = ch["file"]
        chapter_nav += f'<a href="{filename}.html" class="toc-link {active_class}"><span class="chapter-num">{ch["num"]}</span><span class="chapter-title">{ch["title"]}</span></a>'

    if language == "en":
        search_placeholder = "Search..."
        switch_label = "Español"
        chapter_label = "Chapter"
        prev_label = "Previous"
        next_label = "Next"
        home_label = "Home"
    else:
        search_placeholder = "Buscar..."
        switch_label = "English"
        chapter_label = "Capítulo"
        prev_label = "Anterior"
        next_label = "Siguiente"
        home_label = "Inicio"

    current_idx = next(
        (i for i, ch in enumerate(chapters) if ch["file"] == current_chapter), -1
    )
    prev_ch = chapters[current_idx - 1] if current_idx > 0 else None
    next_ch = chapters[current_idx + 1] if current_idx < len(chapters) - 1 else None

    nav_buttons = ""
    if prev_ch:
        fn = prev_ch["file"]
        if language == "en":
            fn = (
                fn.replace("clases-vulnerabilidades", "vulnerability-classes")
                .replace("analisis-crashes", "crash-analysis")
                .replace("introduccion", "introduction")
            )
        nav_buttons += f'<a href="{fn}.html" class="nav-btn nav-prev"><i class="fas fa-chevron-left"></i><span>{prev_label}</span></a>'
    nav_buttons += f'<a href="index.html" class="nav-btn nav-home"><i class="fas fa-home"></i><span>{home_label}</span></a>'
    if next_ch:
        fn = next_ch["file"]
        if language == "en":
            fn = (
                fn.replace("clases-vulnerabilidades", "vulnerability-classes")
                .replace("analisis-crashes", "crash-analysis")
                .replace("introduccion", "introduction")
            )
        nav_buttons += f'<a href="{fn}.html" class="nav-btn nav-next"><span>{next_label}</span><i class="fas fa-chevron-right"></i></a>'

    return f"""<!DOCTYPE html>
<html lang="{language}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} | Red Team Logbook</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link href="https://fonts.googleapis.com/css2?family=Fira+Code:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
:root {{--crimson:#DC143C;--crimson-dark:#8B0000;--crimson-glow:rgba(220,20,60,0.6);--gray-900:#0a0a0a;--gray-800:#1a1a1a;--gray-700:#2d2d2d;--gray-600:#404040;--gray-500:#525252;--gray-400:#737373;--gray-300:#a3a3a3;--gray-200:#d4d4d4;--white:#fff;--green:#39ff14;--mono:'Fira Code',monospace;--sidebar:280px;--header:70px;}}
* {{margin:0;padding:0;box-sizing:border-box;}}
body {{font-family:var(--mono);background:var(--gray-900);color:var(--gray-200);line-height:1.7;min-height:100vh;}}
.bg {{position:fixed;top:0;left:0;width:100%;height:100%;z-index:-2;background:linear-gradient(135deg,rgba(10,10,10,0.95),rgba(26,26,26,0.9)),url('images/image-000.jpg');background-size:cover;background-position:center;}}
.bg::before {{content:'';position:absolute;top:0;left:0;width:100%;height:100%;background:repeating-linear-gradient(0deg,rgba(0,0,0,0.1) 0,rgba(0,0,0,0.1) 1px,transparent 1px,transparent 3px);}}
.header {{position:fixed;top:0;left:0;right:0;height:var(--header);background:linear-gradient(180deg,rgba(10,10,10,0.98),rgba(26,26,26,0.95));backdrop-filter:blur(10px);border-bottom:1px solid rgba(220,20,60,0.3);z-index:1000;display:flex;align-items:center;justify-content:space-between;padding:0 30px;}}
.logo {{display:flex;align-items:center;gap:15px;}}
.logo-icon {{width:40px;height:40px;background:linear-gradient(135deg,var(--crimson),var(--crimson-dark));border-radius:8px;display:flex;align-items:center;justify-content:center;color:var(--white);box-shadow:0 0 20px var(--crimson-glow);}}
.logo-text {{font-size:1.1rem;font-weight:600;color:var(--white);letter-spacing:1px;}}
.logo-text span {{color:var(--crimson);}}
.home-btn {{display:flex;align-items:center;justify-content:center;width:36px;height:36px;background:rgba(45,45,45,0.8);border:1px solid var(--gray-600);border-radius:8px;color:var(--gray-300);text-decoration:none;transition:all 0.3s;margin-left:15px;}}
.home-btn:hover {{background:var(--crimson);border-color:var(--crimson);color:var(--white);box-shadow:0 0 15px var(--crimson-glow);}}
.controls {{display:flex;align-items:center;gap:20px;}}
.search {{position:relative;}}
.search input {{background:rgba(45,45,45,0.8);border:1px solid rgba(220,20,60,0.3);border-radius:8px;padding:8px 15px;padding-right:40px;color:var(--gray-200);font-family:var(--mono);font-size:0.85rem;width:200px;transition:all 0.3s;}}
.search input:focus {{outline:none;border-color:var(--crimson);box-shadow:0 0 15px rgba(220,20,60,0.3);width:260px;}}
.search button {{position:absolute;right:10px;top:50%;transform:translateY(-50%);background:none;border:none;color:var(--gray-400);cursor:pointer;}}
.search button:hover {{color:var(--crimson);}}
.lang-btn {{background:transparent;border:1px solid var(--gray-600);color:var(--gray-300);padding:6px 14px;border-radius:6px;font-family:var(--mono);font-size:0.75rem;cursor:pointer;transition:all 0.3s;text-transform:uppercase;text-decoration:none;letter-spacing:1px;}}
.lang-btn:hover {{background:var(--crimson);border-color:var(--crimson);color:var(--white);box-shadow:0 0 15px var(--crimson-glow);}}
.menu-btn {{display:none;background:transparent;border:1px solid var(--gray-600);color:var(--gray-200);padding:8px 12px;border-radius:6px;cursor:pointer;}}
.sidebar {{position:fixed;top:var(--header);left:0;width:var(--sidebar);height:calc(100vh - var(--header));background:linear-gradient(180deg,rgba(10,10,10,0.98),rgba(26,26,26,0.95));border-right:1px solid rgba(220,20,60,0.2);overflow-y:auto;z-index:900;padding:30px 20px;}}
.sidebar-title {{font-size:0.7rem;text-transform:uppercase;letter-spacing:3px;color:var(--gray-500);margin-bottom:20px;padding-bottom:10px;border-bottom:1px solid rgba(220,20,60,0.2);}}
.toc-link {{display:flex;align-items:center;gap:12px;padding:12px 15px;color:var(--gray-300);text-decoration:none;border-radius:8px;margin-bottom:8px;transition:all 0.3s;font-size:0.85rem;}}
.toc-link:hover {{background:rgba(220,20,60,0.1);color:var(--white);transform:translateX(5px);}}
.toc-link.active {{background:linear-gradient(135deg,rgba(220,20,60,0.2),rgba(220,20,60,0.1));color:var(--crimson);border-left:3px solid var(--crimson);}}
.chapter-num {{font-size:0.7rem;font-weight:700;color:var(--crimson);background:rgba(220,20,60,0.1);padding:4px 8px;border-radius:30px;}}
.chapter-title {{flex:1;}}
.overlay {{display:none;position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.7);z-index:850;}}
.content {{margin-left:var(--sidebar);margin-top:var(--header);min-height:calc(100vh - var(--header));padding:40px 50px;}}
.wrapper {{max-width:900px;margin:0 auto;}}
.article {{background:linear-gradient(135deg,rgba(26,26,26,0.95),rgba(45,45,45,0.9));border:1px solid rgba(220,20,60,0.2);border-radius:16px;padding:50px;box-shadow:0 10px 40px rgba(0,0,0,0.5),0 0 30px rgba(220,20,60,0.1);}}
.article h1 {{font-size:2.2rem;color:var(--white);margin-bottom:30px;padding-bottom:15px;border-bottom:2px solid var(--crimson);}}
.article h2 {{font-size:1.6rem;color:var(--crimson);margin-top:40px;margin-bottom:20px;padding-left:15px;border-left:3px solid var(--crimson);}}
.article h3 {{font-size:1.3rem;color:var(--gray-100);margin-top:30px;margin-bottom:15px;}}
.article p {{margin-bottom:20px;color:var(--gray-200);text-align:justify;}}
.article a {{color:var(--crimson);text-decoration:none;transition:all 0.3s;border-bottom:1px solid transparent;}}
.article a:hover {{color:#ff4444;border-bottom-color:#ff4444;}}
.article ul,.article ol {{margin-bottom:20px;padding-left:30px;}}
.article li {{margin-bottom:10px;}}
.article code {{font-family:var(--mono);background:rgba(220,20,60,0.1);color:#ff4444;padding:2px 8px;border-radius:4px;font-size:0.9em;}}
.article pre {{background:var(--gray-900);border:1px solid rgba(220,20,60,0.3);border-radius:8px;padding:20px;overflow-x:auto;margin:20px 0;}}
.article pre code {{background:none;padding:0;color:var(--green);}}
.article table {{width:100%;border-collapse:collapse;margin:25px 0;}}
.article th {{background:linear-gradient(135deg,var(--crimson-dark),var(--crimson));color:var(--white);padding:15px;text-align:left;font-weight:600;text-transform:uppercase;font-size:0.8rem;}}
.article td {{padding:12px 15px;border-bottom:1px solid rgba(220,20,60,0.1);}}
.article tr:hover {{background:rgba(220,20,60,0.05);}}
.highlight {{background:var(--crimson);color:var(--white);padding:2px 6px;border-radius:3px;}}
.nav {{display:flex;justify-content:space-between;align-items:center;margin-top:40px;padding-top:30px;border-top:1px solid rgba(220,20,60,0.2);}}
.nav-btn {{display:flex;align-items:center;gap:10px;padding:12px 25px;background:linear-gradient(135deg,rgba(220,20,60,0.2),rgba(220,20,60,0.1));border:1px solid rgba(220,20,60,0.3);border-radius:8px;color:var(--gray-200);text-decoration:none;font-size:0.85rem;transition:all 0.3s;}}
.nav-btn:hover {{background:linear-gradient(135deg,var(--crimson),var(--crimson-dark));border-color:var(--crimson);color:var(--white);box-shadow:0 0 20px var(--crimson-glow);transform:translateY(-2px);}}
.nav-home {{background:linear-gradient(135deg,rgba(45,45,45,0.8),rgba(26,26,26,0.8));border-color:var(--gray-600);}}
.nav-home:hover {{background:linear-gradient(135deg,var(--gray-600),var(--gray-700));border-color:var(--gray-400);box-shadow:0 0 15px rgba(255,255,255,0.1);}}
.footer {{text-align:center;padding:30px;color:var(--gray-500);font-size:0.8rem;border-top:1px solid rgba(220,20,60,0.1);margin-top:50px;}}
.footer a {{color:var(--crimson);text-decoration:none;}}
@media(max-width:1024px){{.sidebar{{transform:translateX(-100%)}}.sidebar.active{{transform:translateX(0)}}.overlay.active{{display:block}}.content{{margin-left:0;padding:30px 20px}}.menu-btn{{display:block}}}}
@media(max-width:768px){{.header{{padding:0 15px}}.logo-text{{display:none}}.search{{display:none}}.content{{padding:20px 15px}}.article{{padding:30px 20px}}.article h1{{font-size:1.6rem}}.article h2{{font-size:1.3rem}}.nav{{flex-wrap:wrap;gap:15px}}.nav-btn{{flex:1;justify-content:center;min-width:100px}}}}
@media(max-width:480px){{.article{{padding:20px 15px;border-radius:12px}}.article h1{{font-size:1.4rem}}.nav{{flex-direction:column}}.nav-btn{{width:100%;justify-content:center}}}}
</style>
</head>
<body>
    <div class="bg"></div>
    <header class="header">
        <div class="logo">
            <button class="menu-btn"><i class="fas fa-bars"></i></button>
            <div class="logo-icon"><i class="fas fa-skull"></i></div>
            <div class="logo-text">RED<span>TEAM</span> LOG</div>
            <a href="../../../" class="home-btn" title="Back to Home"><i class="fas fa-home"></i></a>
        </div>
        <div class="controls">
            <div class="search">
                <input type="text" id="searchbar" placeholder="{search_placeholder}">
                <button id="search-btn"><i class="fas fa-search"></i></button>
            </div>
            <a href="{other_language_path}" class="lang-btn">{switch_label}</a>
        </div>
    </header>
    <div class="overlay"></div>
    <nav class="sidebar">
        <div class="sidebar-title">{chapter_label}s</div>
        {chapter_nav}
    </nav>
    <main class="content">
        <div class="wrapper">
            <article class="article">{html}</article>
            <div class="nav">{nav_buttons}</div>
            <footer class="footer"><p>© 2024 Red Team Logbook | <a href="https://github.com/mburgc" target="_blank"><i class="fab fa-github"></i> mburgc</a></p></footer>
        </div>
    </main>
    {search_script}
</body>
</html>"""


def main():
    all_chapters = [
        {
            "num": "01",
            "file": "01-introduccion",
            "title_es": "Introducción",
            "title_en": "Introduction",
        },
        {
            "num": "02",
            "file": "02-clases-vulnerabilidades",
            "title_es": "Clases de Vulnerabilidades",
            "title_en": "Vulnerability Classes",
        },
        {
            "num": "03",
            "file": "03-fuzzing",
            "title_es": "Fuzzing",
            "title_en": "Fuzzing",
        },
        {
            "num": "04",
            "file": "04-patch-diffing",
            "title_es": "Patch Diffing",
            "title_en": "Patch Diffing",
        },
        {
            "num": "05",
            "file": "05-analisis-crashes",
            "title_es": "Análisis de Crashes",
            "title_en": "Crash Analysis",
        },
    ]

    for d in ["es", "en"]:
        os.makedirs(d, exist_ok=True)

    es_md = [f for f in os.listdir("src") if f.endswith(".md") and f != "README.md"]
    es_ch = []
    for ch in all_chapters:
        for md in es_md:
            if ch["file"].replace("-", "") in md.replace("-", ""):
                es_ch.append(
                    {"num": ch["num"], "file": ch["file"], "title": ch["title_es"]}
                )
                break
    es_ch.sort(key=lambda x: x["num"])

    for md in es_md:
        if md == "README.md":
            continue
        with open(os.path.join("src", md), "r", encoding="utf-8") as f:
            text = f.read()

        cur = ""
        for ch in all_chapters:
            if ch["file"].replace("-", "") in md.replace("-", ""):
                cur = ch["file"]
                break

        en_fn = (
            cur.replace("clases-vulnerabilidades", "vulnerability-classes")
            .replace("analisis-crashes", "crash-analysis")
            .replace("introduccion", "introduction")
            + ".html"
        )
        lang_path = "../en/" + en_fn

        title = "Red Team Logbook"
        for line in text.split("\n"):
            if line.startswith("# "):
                title = line[2:].strip()
                break

        html = generate_html(text, title, "es", lang_path, es_ch, cur, all_chapters)
        out = os.path.splitext(md)[0] + ".html"
        with open(os.path.join("es", out), "w", encoding="utf-8") as f:
            f.write(html)

    en_md = [f for f in os.listdir("src/en") if f.endswith(".md") and f != "README.md"]
    en_ch = []
    for ch in all_chapters:
        for md in en_md:
            # Use English filename for matching English chapters
            en_file = (
                ch["file"]
                .replace("clases-vulnerabilidades", "vulnerability-classes")
                .replace("analisis-crashes", "crash-analysis")
                .replace("introduccion", "introduction")
            )
            if en_file.replace("-", "") in md.replace("-", ""):
                en_ch.append(
                    {"num": ch["num"], "file": ch["file"], "title": ch["title_en"]}
                )
                break
    en_ch.sort(key=lambda x: x["num"])

    for md in en_md:
        if md == "README.md":
            continue
        with open(os.path.join("src/en", md), "r", encoding="utf-8") as f:
            text = f.read()

        cur = ""
        for ch in all_chapters:
            # Use English filename for matching English chapters
            en_file = (
                ch["file"]
                .replace("clases-vulnerabilidades", "vulnerability-classes")
                .replace("analisis-crashes", "crash-analysis")
                .replace("introduccion", "introduction")
            )
            if en_file.replace("-", "") in md.replace("-", ""):
                cur = ch["file"]
                break

        es_fn = (
            cur.replace("vulnerability-classes", "clases-vulnerabilidades")
            .replace("crash-analysis", "analisis-crashes")
            .replace("introduction", "introduccion")
            + ".html"
        )
        lang_path = "../es/" + es_fn

        title = "Red Team Logbook"
        for line in text.split("\n"):
            if line.startswith("# "):
                title = line[2:].strip()
                break

        html = generate_html(text, title, "en", lang_path, en_ch, cur, all_chapters)
        out = os.path.splitext(md)[0] + ".html"
        with open(os.path.join("en", out), "w", encoding="utf-8") as f:
            f.write(html)

    idx = """<!DOCTYPE html>
<html lang="es">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>Red Team Logbook</title>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
<link href="https://fonts.googleapis.com/css2?family=Fira+Code:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<style>
:root{--crimson:#DC143C;--crimson-glow:rgba(220,20,60,0.6);--gray-900:#0a0a0a;--gray-200:#d4d4d4;--white:#fff;--mono:'Fira Code',monospace;}
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:var(--mono);background:var(--gray-900);color:var(--gray-200);min-height:100vh;display:flex;align-items:center;justify-content:center;padding:40px 20px}
.bg{position:fixed;top:0;left:0;width:100%;height:100%;z-index:-2;background:linear-gradient(135deg,rgba(10,10,10,0.92),rgba(26,26,26,0.88)),url('images/image-000.jpg');background-size:cover}
.grid{position:fixed;top:0;left:0;width:100%;height:100%;z-index:-1;background-image:linear-gradient(rgba(220,20,60,0.03)1px,transparent 1px),linear-gradient(90deg,rgba(220,20,60,0.03)1px,transparent 1px);background-size:50px 50px}
.box{max-width:700px;width:100%}
h1{font-size:2.5rem;color:var(--white);text-align:center;margin-bottom:10px}
h1 span{color:var(--crimson)}
p{text-align:center;color:var(--gray-200);margin-bottom:40px;font-size:1.1rem}
.btns{display:flex;justify-content:center;gap:20px;margin-bottom:40px;flex-wrap:wrap}
.btn{padding:18px 40px;font-family:var(--mono);font-size:1rem;font-weight:600;text-decoration:none;border-radius:10px;transition:all 0.3s;min-width:200px;display:flex;align-items:center;gap:12px;justify-content:center}
.btn-es{background:linear-gradient(135deg,var(--crimson),#8B0000);color:var(--white);border:2px solid var(--crimson);box-shadow:0 0 30px var(--crimson-glow)}
.btn-es:hover{transform:translateY(-5px);box-shadow:0 10px 40px var(--crimson-glow)}
.btn-en{background:linear-gradient(135deg,rgba(45,45,45,0.9),rgba(26,26,26,0.9));color:var(--gray-200);border:2px solid #404040}
.btn-en:hover{border-color:var(--crimson);color:var(--crimson);transform:translateY(-5px)}
ul{list-style:none}
li{margin-bottom:15px}
a{display:flex;align-items:center;gap:20px;padding:20px 25px;background:linear-gradient(135deg,rgba(26,26,26,0.9),rgba(45,45,45,0.8));border:1px solid rgba(220,20,60,0.2);border-radius:10px;text-decoration:none;color:var(--gray-200);transition:all 0.3s}
a:hover{background:linear-gradient(135deg,rgba(220,20,60,0.2),rgba(220,20,60,0.1));border-color:var(--crimson);transform:translateX(10px);box-shadow:0 0 30px var(--crimson-glow)}
.num{font-size:1.5rem;font-weight:700;color:var(--crimson);min-width:50px}
.name{flex:1}
.arrow{color:var(--crimson);opacity:0;transition:all 0.3s}
a:hover .arrow{opacity:1;transform:translateX(5px)}
.back{color:var(--crimson);text-decoration:none;margin-bottom:30px;display:inline-flex;align-items:center;gap:10px;transition:all 0.3s}
.back:hover{text-shadow:0 0 15px var(--crimson-glow)}
@media(max-width:600px){h1{font-size:1.8rem}a{padding:15px}.num{font-size:1.2rem}}
</style>
</head>
<body>
<div class="bg"></div><div class="grid"></div>
<div class="box">
<a href="../../../" class="back"><i class="fas fa-arrow-left"></i> Back to Home</a>
<h1>RED<span>TEAM</span> LOGBOOK</h1>
<p>Select Language / Seleccionar Idioma</p>
<div class="btns">
<a href="es/" class="btn btn-es"><i class="fas fa-book"></i>Español</a>
<a href="en/" class="btn btn-en"><i class="fas fa-book-open"></i>English</a>
</div>
<ul>
<li><a href="es/01-introduccion.html"><span class="num">01</span><span class="name">Introducción</span><i class="fas fa-chevron-right arrow"></i></a></li>
<li><a href="es/02-clases-vulnerabilidades.html"><span class="num">02</span><span class="name">Clases de Vulnerabilidades</span><i class="fas fa-chevron-right arrow"></i></a></li>
<li><a href="es/03-fuzzing.html"><span class="num">03</span><span class="name">Fuzzing</span><i class="fas fa-chevron-right arrow"></i></a></li>
<li><a href="es/04-patch-diffing.html"><span class="num">04</span><span class="name">Patch Diffing</span><i class="fas fa-chevron-right arrow"></i></a></li>
<li><a href="es/05-analisis-crashes.html"><span class="num">05</span><span class="name">Análisis de Crashes</span><i class="fas fa-chevron-right arrow"></i></a></li>
</ul>
</div>
</body>
</html>"""

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(idx)

    es_idx = (
        idx.replace("Select Language", "Índice")
        .replace("Back to Home", "Volver")
        .replace('href="es/"', 'href="index.html"')
        .replace('href="en/"', 'href="../en/"')
    )
    with open("es/index.html", "w", encoding="utf-8") as f:
        f.write(es_idx)

    en_idx = (
        idx.replace("Índice", "Index")
        .replace("Volver", "Back")
        .replace("Introducción", "Introduction")
        .replace("Clases de Vulnerabilidades", "Vulnerability Classes")
        .replace("Análisis de Crashes", "Crash Analysis")
        .replace('href="es/"', 'href="index.html"')
        .replace('href="en/"', 'href="index.html"')
        .replace("Español", "Spanish")
    )
    with open("en/index.html", "w", encoding="utf-8") as f:
        f.write(en_idx)

    print("Build complete!")


if __name__ == "__main__":
    main()
