import markdown
import os


# Complete HTML template with hacker red team aesthetic
def generate_html(
    text, title, language, other_language_path, chapters, current_chapter, all_chapters
):
    # Get chapter info
    chapter_num = ""
    chapter_title = ""

    for ch in all_chapters:
        if ch["file"] == current_chapter:
            chapter_num = ch["num"]
            chapter_title = ch["title_es"] if language == "es" else ch["title_en"]
            break

    search_script = """
<script>
document.addEventListener('DOMContentLoaded', function() {
    // Search functionality
    const searchInput = document.getElementById('searchbar');
    const searchBtn = document.getElementById('search-btn');
    
    function performSearch() {
        let input = searchInput.value.toLowerCase().trim();
        let content = document.querySelector('.content-area');
        let paragraphs = content.getElementsByTagName('p');
        let lis = content.getElementsByTagName('li');
        let headers = content.querySelectorAll('h1, h2, h3, h4, h5, h6');
        let codeBlocks = content.querySelectorAll('pre, code');
        
        let all_elements = [...paragraphs, ...lis, ...headers, ...codeBlocks];
        
        // Reset all elements first
        for (let i = 0; i < all_elements.length; i++) {
            let el = all_elements[i];
            el.style.display = '';
            if (el.classList.contains('highlight')) {
                el.classList.remove('highlight');
                el.innerHTML = el.textContent;
            }
        }
        
        if (input === "") {
            return;
        }
        
        for (let i = 0; i < all_elements.length; i++) {
            let element = all_elements[i];
            let text = element.textContent.toLowerCase();
            if (text.includes(input)) {
                element.style.display = "";
                let originalText = element.textContent;
                let escaped = input.replace(/[.*+?^${}()|[\\]\\\\]/g, '\\\\$&');
                let newText = originalText.replace(new RegExp('(' + escaped + ')', 'gi'), '<span class="search-highlight">$1</span>');
                element.innerHTML = newText;
            } else {
                element.style.display = "none";
            }
        }
        
        // Show no results message
        let visibleCount = 0;
        for (let i = 0; i < all_elements.length; i++) {
            if (all_elements[i].style.display !== "none") visibleCount++;
        }
        
        let noResults = document.getElementById('no-results');
        if (visibleCount === 0) {
            if (!noResults) {
                noResults = document.createElement('div');
                noResults.id = 'no-results';
                noResults.className = 'no-results';
                noResults.innerHTML = '<i class="fas fa-search"></i> No se encontraron resultados / No results found';
                content.insertBefore(noResults, content.firstChild);
            }
            noResults.style.display = 'block';
        } else if (noResults) {
            noResults.style.display = 'none';
        }
    }
    
    if (searchBtn) {
        searchBtn.addEventListener('click', performSearch);
    }
    if (searchInput) {
        searchInput.addEventListener('keyup', function(e) {
            if (e.key === 'Enter') performSearch();
            if (this.value === '') {
                let all_elements = document.querySelectorAll('.search-highlight');
                all_elements.forEach(el => {
                    let parent = el.parentNode;
                    parent.innerHTML = parent.textContent;
                });
                let noResults = document.getElementById('no-results');
                if (noResults) noResults.style.display = 'none';
            }
        });
    }
    
    // Mobile menu toggle
    const menuToggle = document.getElementById('menu-toggle');
    const sidebar = document.querySelector('.sidebar');
    const overlay = document.querySelector('.sidebar-overlay');
    
    if (menuToggle) {
        menuToggle.addEventListener('click', function() {
            sidebar.classList.toggle('active');
            overlay.classList.toggle('active');
        });
    }
    
    if (overlay) {
        overlay.addEventListener('click', function() {
            sidebar.classList.remove('active');
            overlay.classList.remove('active');
        });
    }
    
    // Scroll animations
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        });
    }, observerOptions);
    
    document.querySelectorAll('.content-area > *').forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(el);
    });
    
    // Trigger initial animation
    setTimeout(() => {
        document.querySelectorAll('.content-area > *').forEach((el, index) => {
            setTimeout(() => {
                el.style.opacity = '1';
                el.style.transform = 'translateY(0)';
            }, index * 50);
        });
    }, 100);
    
    // Table of contents highlighting
    const tocLinks = document.querySelectorAll('.toc-link');
    const contentHeaders = document.querySelectorAll('.content-area h1, .content-area h2, .content-area h3');
    
    window.addEventListener('scroll', () => {
        let current = '';
        contentHeaders.forEach(header => {
            const headerTop = header.offsetTop;
            if (window.pageYOffset >= headerTop - 100) {
                current = header.getAttribute('id');
            }
        });
        
        tocLinks.forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('href') === '#' + current) {
                link.classList.add('active');
            }
        });
    });
});
</script>
"""

    html = markdown.markdown(text, extensions=["tables", "fenced_code", "codehilite"])

    # Build chapter navigation
    chapter_nav = ""
    for ch in chapters:
        active_class = "active" if ch["file"] == current_chapter else ""
        chapter_nav += f'''<a href="{ch["file"]}.html" class="toc-link {active_class}">
            <span class="chapter-num">{ch["num"]}</span>
            <span class="chapter-title">{ch["title"]}</span>
        </a>'''

    # Language labels
    if language == "en":
        search_placeholder = "Search content..."
        switch_label = "Español"
        chapter_label = "Chapter"
        prev_label = "Previous"
        next_label = "Next"
        home_label = "Home"
    else:
        search_placeholder = "Buscar contenido..."
        switch_label = "English"
        chapter_label = "Capítulo"
        prev_label = "Anterior"
        next_label = "Siguiente"
        home_label = "Inicio"

    # Get prev/next chapters
    current_idx = next(
        (i for i, ch in enumerate(chapters) if ch["file"] == current_chapter), -1
    )
    prev_ch = chapters[current_idx - 1] if current_idx > 0 else None
    next_ch = chapters[current_idx + 1] if current_idx < len(chapters) - 1 else None

    nav_buttons = ""
    if prev_ch:
        nav_buttons += f'''<a href="{prev_ch["file"]}.html" class="nav-btn nav-prev">
            <i class="fas fa-chevron-left"></i>
            <span>{prev_label}</span>
        </a>'''
    nav_buttons += f"""<a href="index.html" class="nav-btn nav-home">
        <i class="fas fa-home"></i>
        <span>{home_label}</span>
    </a>"""
    if next_ch:
        nav_buttons += f'''<a href="{next_ch["file"]}.html" class="nav-btn nav-next">
            <span>{next_label}</span>
            <i class="fas fa-chevron-right"></i>
        </a>'''

    return f"""<!DOCTYPE html>
<html lang="{language}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} | Bitácora Red Team</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Fira+Code:wght@300;400;500;600;700&family=JetBrains+Mono:wght@300;400;500;600;700&family=Source+Code+Pro:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
:root {{
    /* Hacker Red Team Color Palette */
    --crimson-dark: #8B0000;
    --crimson: #DC143C;
    --crimson-light: #FF2442;
    --crimson-glow: rgba(220, 20, 60, 0.6);
    
    /* Grays */
    --gray-900: #0a0a0a;
    --gray-800: #1a1a1a;
    --gray-700: #2d2d2d;
    --gray-600: #404040;
    --gray-500: #525252;
    --gray-400: #737373;
    --gray-300: #a3a3a3;
    --gray-200: #d4d4d4;
    --gray-100: #f5f5f5;
    --white: #ffffff;
    
    /* Accent colors */
    --accent-red: #ff4444;
    --accent-orange: #ff6b35;
    --matrix-green: #00ff41;
    --terminal-green: #39ff14;
    
    /* Typography */
    --font-mono: 'Fira Code', 'JetBrains Mono', 'Source Code Pro', monospace;
    
    /* Sizing */
    --sidebar-width: 280px;
    --header-height: 70px;
}}

* {{
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}}

html {{
    scroll-behavior: smooth;
}}

body {{
    font-family: var(--font-mono);
    background: var(--gray-900);
    color: var(--gray-200);
    line-height: 1.8;
    min-height: 100vh;
    overflow-x: hidden;
}}

/* Background with cover image */
.page-background {{
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    z-index: -2;
    background: 
        linear-gradient(135deg, rgba(10, 10, 10, 0.95) 0%, rgba(26, 26, 26, 0.9) 50%, rgba(45, 45, 45, 0.85) 100%),
        url('images/image-000.jpg');
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}}

/* Scanline effect */
.page-background::before {{
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: repeating-linear-gradient(
        0deg,
        rgba(0, 0, 0, 0.1) 0px,
        rgba(0, 0, 0, 0.1) 1px,
        transparent 1px,
        transparent 3px
    );
    pointer-events: none;
    animation: scanlines 10s linear infinite;
}}

@keyframes scanlines {{
    0% {{ transform: translateY(0); }}
    100% {{ transform: translateY(3px); }}
}}

/* Matrix rain effect (subtle) */
.matrix-rain {{
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    z-index: -1;
    pointer-events: none;
    opacity: 0.03;
    background: 
        linear-gradient(180deg, transparent 0%, var(--crimson) 100%),
        repeating-linear-gradient(
            0deg,
            transparent 0px,
            transparent 40px,
            var(--accent-red) 40px,
            var(--accent-red) 42px
        );
}}

/* Header */
.main-header {{
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    height: var(--header-height);
    background: linear-gradient(180deg, rgba(10, 10, 10, 0.98) 0%, rgba(26, 26, 26, 0.95) 100%);
    backdrop-filter: blur(10px);
    border-bottom: 1px solid rgba(220, 20, 60, 0.3);
    z-index: 1000;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 30px;
}}

.logo {{
    display: flex;
    align-items: center;
    gap: 15px;
}}

.logo-icon {{
    width: 40px;
    height: 40px;
    background: linear-gradient(135deg, var(--crimson) 0%, var(--crimson-dark) 100%);
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.2rem;
    color: var(--white);
    box-shadow: 0 0 20px var(--crimson-glow);
}}

.logo-text {{
    font-size: 1.1rem;
    font-weight: 600;
    color: var(--white);
    letter-spacing: 1px;
}}

.logo-text span {{
    color: var(--crimson);
}}

.header-controls {{
    display: flex;
    align-items: center;
    gap: 20px;
}}

.search-container {{
    position: relative;
}}

.search-input {{
    background: rgba(45, 45, 45, 0.8);
    border: 1px solid rgba(220, 20, 60, 0.3);
    border-radius: 8px;
    padding: 8px 15px;
    padding-right: 40px;
    color: var(--gray-200);
    font-family: var(--font-mono);
    font-size: 0.85rem;
    width: 220px;
    transition: all 0.3s ease;
}}

.search-input:focus {{
    outline: none;
    border-color: var(--crimson);
    box-shadow: 0 0 15px rgba(220, 20, 60, 0.3);
    width: 280px;
}}

.search-input::placeholder {{
    color: var(--gray-500);
}}

.search-btn {{
    position: absolute;
    right: 10px;
    top: 50%;
    transform: translateY(-50%);
    background: none;
    border: none;
    color: var(--gray-400);
    cursor: pointer;
    transition: color 0.3s ease;
}}

.search-btn:hover {{
    color: var(--crimson);
}}

.language-switch {{
    display: flex;
    align-items: center;
    gap: 10px;
}}

.lang-btn {{
    background: transparent;
    border: 1px solid var(--gray-600);
    color: var(--gray-300);
    padding: 6px 14px;
    border-radius: 6px;
    font-family: var(--font-mono);
    font-size: 0.75rem;
    cursor: pointer;
    transition: all 0.3s ease;
    text-transform: uppercase;
    letter-spacing: 1px;
}}

.lang-btn:hover, .lang-btn.active {{
    background: var(--crimson);
    border-color: var(--crimson);
    color: var(--white);
    box-shadow: 0 0 15px var(--crimson-glow);
}}

.menu-toggle {{
    display: none;
    background: transparent;
    border: 1px solid var(--gray-600);
    color: var(--gray-200);
    padding: 8px 12px;
    border-radius: 6px;
    cursor: pointer;
    font-size: 1rem;
}}

/* Sidebar */
.sidebar {{
    position: fixed;
    top: var(--header-height);
    left: 0;
    width: var(--sidebar-width);
    height: calc(100vh - var(--header-height));
    background: linear-gradient(180deg, rgba(10, 10, 10, 0.98) 0%, rgba(26, 26, 26, 0.95) 100%);
    border-right: 1px solid rgba(220, 20, 60, 0.2);
    overflow-y: auto;
    z-index: 900;
    padding: 30px 20px;
    transition: transform 0.3s ease;
}}

.sidebar::-webkit-scrollbar {{
    width: 6px;
}}

.sidebar::-webkit-scrollbar-track {{
    background: var(--gray-800);
}}

.sidebar::-webkit-scrollbar-thumb {{
    background: var(--gray-600);
    border-radius: 3px;
}}

.sidebar::-webkit-scrollbar-thumb:hover {{
    background: var(--crimson);
}}

.sidebar-title {{
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 3px;
    color: var(--gray-500);
    margin-bottom: 20px;
    padding-bottom: 10px;
    border-bottom: 1px solid rgba(220, 20, 60, 0.2);
}}

.toc-link {{
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px 15px;
    color: var(--gray-300);
    text-decoration: none;
    border-radius: 8px;
    margin-bottom: 8px;
    transition: all 0.3s ease;
    font-size: 0.85rem;
}}

.toc-link:hover {{
    background: rgba(220, 20, 60, 0.1);
    color: var(--white);
    transform: translateX(5px);
}}

.toc-link.active {{
    background: linear-gradient(135deg, rgba(220, 20, 60, 0.2) 0%, rgba(220, 20, 60, 0.1) 100%);
    color: var(--crimson);
    border-left: 3px solid var(--crimson);
}}

.chapter-num {{
    font-size: 0.7rem;
    font-weight: 700;
    color: var(--crimson);
    background: rgba(220, 20, 60, 0.1);
    padding: 4px 8px: 4px;
    min-width;
    border-radius: 30px;
    text-align: center;
}}

.chapter-title {{
    flex: 1;
    line-height: 1.3;
}}

.sidebar-overlay {{
    display: none;
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.7);
    z-index: 850;
}}

/* Main content */
.main-content {{
    margin-left: var(--sidebar-width);
    margin-top: var(--header-height);
    min-height: calc(100vh - var(--header-height));
    padding: 40px 50px;
}}

.content-wrapper {{
    max-width: 900px;
    margin: 0 auto;
}}

/* Content area styling */
.content-area {{
    background: linear-gradient(135deg, rgba(26, 26, 26, 0.95) 0%, rgba(45, 45, 45, 0.9) 100%);
    border: 1px solid rgba(220, 20, 60, 0.2);
    border-radius: 16px;
    padding: 50px;
    box-shadow: 
        0 10px 40px rgba(0, 0, 0, 0.5),
        0 0 30px rgba(220, 20, 60, 0.1);
    backdrop-filter: blur(10px);
}}

.content-area h1 {{
    font-size: 2.2rem;
    color: var(--white);
    margin-bottom: 30px;
    padding-bottom: 15px;
    border-bottom: 2px solid var(--crimson);
    text-shadow: 0 0 20px var(--crimson-glow);
}}

.content-area h2 {{
    font-size: 1.6rem;
    color: var(--crimson);
    margin-top: 40px;
    margin-bottom: 20px;
    padding-left: 15px;
    border-left: 3px solid var(--crimson);
}}

.content-area h3 {{
    font-size: 1.3rem;
    color: var(--gray-100);
    margin-top: 30px;
    margin-bottom: 15px;
}}

.content-area h4 {{
    font-size: 1.1rem;
    color: var(--gray-300);
    margin-top: 25px;
    margin-bottom: 10px;
}}

.content-area p {{
    margin-bottom: 20px;
    color: var(--gray-200);
    text-align: justify;
}}

.content-area a {{
    color: var(--crimson);
    text-decoration: none;
    transition: all 0.3s ease;
    border-bottom: 1px solid transparent;
}}

.content-area a:hover {{
    color: var(--crimson-light);
    border-bottom-color: var(--crimson-light);
    text-shadow: 0 0 10px var(--crimson-glow);
}}

.content-area ul, .content-area ol {{
    margin-bottom: 20px;
    padding-left: 30px;
}}

.content-area li {{
    margin-bottom: 10px;
    color: var(--gray-200);
}}

.content-area li::marker {{
    color: var(--crimson);
}}

/* Code blocks */
.content-area code {{
    font-family: var(--font-mono);
    background: rgba(220, 20, 60, 0.1);
    color: var(--crimson-light);
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 0.9em;
}}

.content-area pre {{
    background: var(--gray-900);
    border: 1px solid rgba(220, 20, 60, 0.3);
    border-radius: 8px;
    padding: 20px;
    overflow-x: auto;
    margin: 20px 0;
    box-shadow: inset 0 2px 10px rgba(0, 0, 0, 0.5);
}}

.content-area pre code {{
    background: none;
    padding: 0;
    color: var(--terminal-green);
    font-size: 0.85rem;
    line-height: 1.6;
}}

/* Tables */
.content-area table {{
    width: 100%;
    border-collapse: collapse;
    margin: 25px 0;
    font-size: 0.9rem;
}}

.content-area th {{
    background: linear-gradient(135deg, var(--crimson-dark) 0%, var(--crimson) 100%);
    color: var(--white);
    padding: 15px;
    text-align: left;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1px;
    font-size: 0.8rem;
}}

.content-area td {{
    padding: 12px 15px;
    border-bottom: 1px solid rgba(220, 20, 60, 0.1);
    color: var(--gray-200);
}}

.content-area tr:hover {{
    background: rgba(220, 20, 60, 0.05);
}}

.content-area tr:nth-child(even) {{
    background: rgba(45, 45, 45, 0.3);
}}

/* Search highlight */
.search-highlight {{
    background: var(--crimson);
    color: var(--white);
    padding: 2px 6px;
    border-radius: 3px;
    box-shadow: 0 0 10px var(--crimson-glow);
}}

.no-results {{
    text-align: center;
    padding: 40px;
    color: var(--gray-400);
    font-size: 1.1rem;
    display: none;
}}

.no-results i {{
    font-size: 2rem;
    margin-bottom: 15px;
    color: var(--crimson);
}}

/* Navigation buttons */
.nav-buttons {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 40px;
    padding-top: 30px;
    border-top: 1px solid rgba(220, 20, 60, 0.2);
}}

.nav-btn {{
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 12px 25px;
    background: linear-gradient(135deg, rgba(220, 20, 60, 0.2) 0%, rgba(220, 20, 60, 0.1) 100%);
    border: 1px solid rgba(220, 20, 60, 0.3);
    border-radius: 8px;
    color: var(--gray-200);
    text-decoration: none;
    font-size: 0.85rem;
    transition: all 0.3s ease;
}}

.nav-btn:hover {{
    background: linear-gradient(135deg, var(--crimson) 0%, var(--crimson-dark) 100%);
    border-color: var(--crimson);
    color: var(--white);
    box-shadow: 0 0 20px var(--crimson-glow);
    transform: translateY(-2px);
}}

.nav-btn i {{
    transition: transform 0.3s ease;
}}

.nav-btn:hover i {{
    transform: scale(1.2);
}}

.nav-prev i {{
    margin-right: 5px;
}}

.nav-next i {{
    margin-left: 5px;
}}

.nav-home {{
    background: linear-gradient(135deg, rgba(45, 45, 45, 0.8) 0%, rgba(26, 26, 26, 0.8) 100%);
    border-color: var(--gray-600);
}}

.nav-home:hover {{
    background: linear-gradient(135deg, var(--gray-600) 0%, var(--gray-700) 100%);
    border-color: var(--gray-400);
    box-shadow: 0 0 15px rgba(255, 255, 255, 0.1);
}}

/* Footer */
.page-footer {{
    text-align: center;
    padding: 30px;
    color: var(--gray-500);
    font-size: 0.8rem;
    border-top: 1px solid rgba(220, 20, 60, 0.1);
    margin-top: 50px;
}}

.page-footer a {{
    color: var(--crimson);
    text-decoration: none;
}}

.page-footer a:hover {{
    text-shadow: 0 0 10px var(--crimson-glow);
}}

/* Animations */
@keyframes fadeInUp {{
    from {{
        opacity: 0;
        transform: translateY(30px);
    }}
    to {{
        opacity: 1;
        transform: translateY(0);
    }}
}}

@keyframes pulse {{
    0%, 100% {{
        opacity: 1;
    }}
    50% {{
        opacity: 0.5;
    }}
}}

@keyframes glow {{
    0%, 100% {{
        box-shadow: 0 0 20px var(--crimson-glow);
    }}
    50% {{
        box-shadow: 0 0 40px var(--crimson-glow), 0 0 60px var(--crimson-glow);
    }}
}}

.logo-icon {{
    animation: glow 3s ease-in-out infinite;
}}

/* Responsive */
@media (max-width: 1024px) {{
    .sidebar {{
        transform: translateX(-100%);
    }}
    
    .sidebar.active {{
        transform: translateX(0);
    }}
    
    .sidebar-overlay.active {{
        display: block;
    }}
    
    .main-content {{
        margin-left: 0;
        padding: 30px 20px;
    }}
    
    .menu-toggle {{
        display: block;
    }}
    
    .search-input {{
        width: 150px;
    }}
    
    .search-input:focus {{
        width: 200px;
    }}
}}

@media (max-width: 768px) {{
    .main-header {{
        padding: 0 15px;
    }}
    
    .logo-text {{
        display: none;
    }}
    
    .search-container {{
        display: none;
    }}
    
    .language-switch {{
        gap: 5px;
    }}
    
    .lang-btn {{
        padding: 5px 10px;
        font-size: 0.65rem;
    }}
    
    .content-area {{
        padding: 30px 20px;
    }}
    
    .content-area h1 {{
        font-size: 1.6rem;
    }}
    
    .content-area h2 {{
        font-size: 1.3rem;
    }}
    
    .content-area h3 {{
        font-size: 1.1rem;
    }}
    
    .nav-buttons {{
        flex-wrap: wrap;
        gap: 15px;
    }}
    
    .nav-btn {{
        flex: 1;
        justify-content: center;
        min-width: 100px;
    }}
}}

@media (max-width: 480px) {{
    .content-area {{
        padding: 20px 15px;
        border-radius: 12px;
    }}
    
    .content-area h1 {{
        font-size: 1.4rem;
    }}
    
    .nav-buttons {{
        flex-direction: column;
    }}
    
    .nav-btn {{
        width: 100%;
        justify-content: center;
    }}
}}

/* Print styles */
@media print {{
    .page-background,
    .matrix-rain,
    .sidebar,
    .main-header,
    .nav-buttons {{
        display: none !important;
    }}
    
    .main-content {{
        margin-left: 0;
        padding: 0;
    }}
    
    .content-area {{
        box-shadow: none;
        border: 1px solid #ccc;
    }}
}}
</style>
</head>
<body>
    <div class="page-background"></div>
    <div class="matrix-rain"></div>
    
    <!-- Header -->
    <header class="main-header">
        <div class="logo">
            <button class="menu-toggle" id="menu-toggle">
                <i class="fas fa-bars"></i>
            </button>
            <div class="logo-icon">
                <i class="fas fa-skull"></i>
            </div>
            <div class="logo-text">
                RED<span>TEAM</span> LOG
            </div>
        </div>
        
        <div class="header-controls">
            <div class="search-container">
                <input type="text" class="search-input" id="searchbar" placeholder="{search_placeholder}">
                <button class="search-btn" id="search-btn">
                    <i class="fas fa-search"></i>
                </button>
            </div>
            
            <div class="language-switch">
                <a href="{other_language_path}" class="lang-btn">{switch_label}</a>
            </div>
        </div>
    </header>
    
    <!-- Sidebar overlay for mobile -->
    <div class="sidebar-overlay"></div>
    
    <!-- Sidebar -->
    <nav class="sidebar">
        <div class="sidebar-title">{chapter_label}s</div>
        {chapter_nav}
    </nav>
    
    <!-- Main Content -->
    <main class="main-content">
        <div class="content-wrapper">
            <article class="content-area">
                {html}
            </article>
            
            <!-- Navigation -->
            <div class="nav-buttons">
                {nav_buttons}
            </div>
            
            <!-- Footer -->
            <footer class="page-footer">
                <p>© 2024 Red Team Logbook | <a href="https://github.com/mburgc/mburgc.github.io" target="_blank">
                    <i class="fab fa-github"></i> mburgc
                </a></p>
            </footer>
        </div>
    </main>
    
    {search_script}
</body>
</html>"""


def main():
    # Define all chapters (both languages share the same structure)
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

    # Create the output directories
    if not os.path.exists("../bitacora"):
        os.makedirs("../bitacora")
    if not os.path.exists("../bitacora/es"):
        os.makedirs("../bitacora/es")
    if not os.path.exists("../bitacora/en"):
        os.makedirs("../bitacora/en")

    # Copy images folder
    if os.path.exists("images"):
        if not os.path.exists("../bitacora/images"):
            os.makedirs("../bitacora/images")
        import shutil

        for file in os.listdir("images"):
            src = os.path.join("images", file)
            dst = os.path.join("../bitacora/images", file)
            if os.path.isfile(src):
                shutil.copy2(src, dst)

    # Spanish files
    es_markdown_files = [
        f for f in os.listdir(".") if f.endswith(".md") and f != "README.md"
    ]
    es_chapters = []
    for ch in all_chapters:
        for md_file in es_markdown_files:
            if ch["file"].replace("-", "") in md_file.replace("-", "").replace(" ", ""):
                es_chapters.append(
                    {"num": ch["num"], "file": ch["file"], "title": ch["title_es"]}
                )
                break

    # Sort by chapter number
    es_chapters.sort(key=lambda x: x["num"])

    for md_file in es_markdown_files:
        if md_file == "README.md":
            continue
        with open(md_file, "r", encoding="utf-8") as f:
            text = f.read()

            # Determine current chapter
            current_chapter = ""
            for ch in all_chapters:
                if ch["file"].replace("-", "") in md_file.replace("-", "").replace(
                    " ", ""
                ):
                    current_chapter = ch["file"]
                    break

            # Determine English path
            en_filename = ""
            for ch in all_chapters:
                if ch["file"].replace("-", "") in md_file.replace("-", "").replace(
                    " ", ""
                ):
                    en_filename = (
                        ch["file"]
                        .replace("clases-vulnerabilidades", "vulnerability-classes")
                        .replace("analisis-crashes", "crash-analysis")
                        + ".html"
                    )
                    break
            other_language_path = os.path.join("../en", en_filename)

            # Get title from first h1
            lines = text.split("\n")
            title = "Bitácora Red Team"
            for line in lines:
                if line.startswith("# "):
                    title = line[2:].strip()
                    break

            html_content = generate_html(
                text,
                title,
                "es",
                other_language_path,
                es_chapters,
                current_chapter,
                all_chapters,
            )
            html_file = os.path.join(
                "../bitacora/es", os.path.splitext(md_file)[0] + ".html"
            )
            with open(html_file, "w", encoding="utf-8") as f:
                f.write(html_content)

    # English files
    en_markdown_files = [
        f for f in os.listdir("en") if f.endswith(".md") and f != "README.md"
    ]
    en_chapters = []
    for ch in all_chapters:
        for md_file in en_markdown_files:
            if ch["file"].replace("-", "") in md_file.replace("-", "").replace(" ", ""):
                en_chapters.append(
                    {"num": ch["num"], "file": ch["file"], "title": ch["title_en"]}
                )
                break

    en_chapters.sort(key=lambda x: x["num"])

    for md_file in en_markdown_files:
        if md_file == "README.md":
            continue
        with open(os.path.join("en", md_file), "r", encoding="utf-8") as f:
            text = f.read()

            # Determine current chapter
            current_chapter = ""
            for ch in all_chapters:
                if ch["file"].replace("-", "") in md_file.replace("-", "").replace(
                    " ", ""
                ):
                    current_chapter = ch["file"]
                    break

            # Determine Spanish path
            es_filename = ""
            for ch in all_chapters:
                if ch["file"].replace("-", "") in md_file.replace("-", "").replace(
                    " ", ""
                ):
                    es_filename = (
                        ch["file"]
                        .replace("vulnerability-classes", "clases-vulnerabilidades")
                        .replace("crash-analysis", "analisis-crashes")
                        + ".html"
                    )
                    break
            other_language_path = os.path.join("../es", es_filename)

            # Get title from first h1
            lines = text.split("\n")
            title = "Red Team Logbook"
            for line in lines:
                if line.startswith("# "):
                    title = line[2:].strip()
                    break

            html_content = generate_html(
                text,
                title,
                "en",
                other_language_path,
                en_chapters,
                current_chapter,
                all_chapters,
            )
            html_file = os.path.join(
                "../bitacora/en", os.path.splitext(md_file)[0] + ".html"
            )
            with open(html_file, "w", encoding="utf-8") as f:
                f.write(html_content)

    # Create main index.html with cover
    index_html = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bitácora Red Team | Explotación Moderna del Kernel de Linux</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Fira+Code:wght@300;400;500;600;700&family=JetBrains+Mono:wght@300;400;500;600;700&family=Source+Code+Pro:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
:root {
    --crimson-dark: #8B0000;
    --crimson: #DC143C;
    --crimson-light: #FF2442;
    --crimson-glow: rgba(220, 20, 60, 0.6);
    --gray-900: #0a0a0a;
    --gray-800: #1a1a1a;
    --gray-700: #2d2d2d;
    --gray-600: #404040;
    --gray-500: #525252;
    --gray-400: #737373;
    --gray-300: #a3a3a3;
    --gray-200: #d4d4d4;
    --gray-100: #f5f5f5;
    --white: #ffffff;
    --terminal-green: #39ff14;
    --font-mono: 'Fira Code', 'JetBrains Mono', 'Source Code Pro', monospace;
}

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

html {
    scroll-behavior: smooth;
}

body {
    font-family: var(--font-mono);
    background: var(--gray-900);
    color: var(--gray-200);
    line-height: 1.8;
    min-height: 100vh;
    overflow-x: hidden;
}

/* Cover Background */
.cover-background {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    z-index: -2;
    background: 
        linear-gradient(135deg, rgba(10, 10, 10, 0.92) 0%, rgba(26, 26, 26, 0.88) 50%, rgba(45, 45, 45, 0.85) 100%),
        url('images/image-000.jpg');
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}

/* Scanline effect */
.cover-background::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: repeating-linear-gradient(
        0deg,
        rgba(0, 0, 0, 0.1) 0px,
        rgba(0, 0, 0, 0.1) 1px,
        transparent 1px,
        transparent 3px
    );
    pointer-events: none;
    animation: scanlines 8s linear infinite;
}

@keyframes scanlines {
    0% { transform: translateY(0); }
    100% { transform: translateY(3px); }
}

/* Grid overlay */
.grid-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    z-index: -1;
    background-image: 
        linear-gradient(rgba(220, 20, 60, 0.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(220, 20, 60, 0.03) 1px, transparent 1px);
    background-size: 50px 50px;
    animation: grid-pulse 4s ease-in-out infinite;
}

@keyframes grid-pulse {
    0%, 100% { opacity: 0.5; }
    50% { opacity: 1; }
}

/* Floating particles */
.particles {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    z-index: -1;
    pointer-events: none;
}

.particle {
    position: absolute;
    width: 4px;
    height: 4px;
    background: var(--crimson);
    border-radius: 50%;
    opacity: 0.3;
    animation: float 15s infinite;
}

@keyframes float {
    0%, 100% {
        transform: translateY(100vh) rotate(0deg);
        opacity: 0;
    }
    10% {
        opacity: 0.4;
    }
    90% {
        opacity: 0.4;
    }
    100% {
        transform: translateY(-100vh) rotate(720deg);
        opacity: 0;
    }
}

/* Cover Container */
.cover-container {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    padding: 40px 20px;
    position: relative;
}

/* Cover Content */
.cover-content {
    max-width: 800px;
    text-align: center;
}

/* Book Cover Image */
.cover-image {
    width: 280px;
    height: 400px;
    object-fit: cover;
    border-radius: 8px;
    box-shadow: 
        0 20px 60px rgba(0, 0, 0, 0.8),
        0 0 40px var(--crimson-glow),
        inset 0 0 30px rgba(0, 0, 0, 0.3);
    margin-bottom: 40px;
    animation: cover-glow 3s ease-in-out infinite;
    border: 2px solid rgba(220, 20, 60, 0.3);
}

@keyframes cover-glow {
    0%, 100% {
        box-shadow: 
            0 20px 60px rgba(0, 0, 0, 0.8),
            0 0 40px var(--crimson-glow),
            inset 0 0 30px rgba(0, 0, 0, 0.3);
    }
    50% {
        box-shadow: 
            0 20px 80px rgba(0, 0, 0, 0.8),
            0 0 60px var(--crimson-glow),
            0 0 80px rgba(220, 20, 60, 0.3),
            inset 0 0 30px rgba(0, 0, 0, 0.3);
    }
}

/* Title */
.cover-title {
    font-size: 3rem;
    font-weight: 700;
    color: var(--white);
    margin-bottom: 15px;
    text-shadow: 
        0 0 20px var(--crimson-glow),
        0 0 40px var(--crimson-glow);
    letter-spacing: 3px;
    animation: title-flicker 4s ease-in-out infinite;
}

@keyframes title-flicker {
    0%, 100% { opacity: 1; }
    92% { opacity: 1; }
    93% { opacity: 0.8; }
    94% { opacity: 1; }
    96% { opacity: 0.9; }
    97% { opacity: 1; }
}

.cover-title span {
    color: var(--crimson);
}

/* Subtitle */
.cover-subtitle {
    font-size: 1.2rem;
    color: var(--gray-300);
    margin-bottom: 40px;
    letter-spacing: 2px;
}

/* Description */
.cover-description {
    font-size: 1rem;
    color: var(--gray-400);
    margin-bottom: 40px;
    line-height: 1.8;
    max-width: 600px;
    margin-left: auto;
    margin-right: auto;
}

/* Language Buttons */
.language-buttons {
    display: flex;
    justify-content: center;
    gap: 20px;
    margin-bottom: 50px;
    flex-wrap: wrap;
}

.lang-cover-btn {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 18px 40px;
    font-family: var(--font-mono);
    font-size: 1rem;
    font-weight: 600;
    text-decoration: none;
    border-radius: 10px;
    transition: all 0.3s ease;
    min-width: 200px;
    justify-content: center;
}

.lang-cover-btn.es {
    background: linear-gradient(135deg, var(--crimson) 0%, var(--crimson-dark) 100%);
    color: var(--white);
    border: 2px solid var(--crimson);
    box-shadow: 0 0 30px var(--crimson-glow);
}

.lang-cover-btn.es:hover {
    transform: translateY(-5px) scale(1.02);
    box-shadow: 0 10px 40px var(--crimson-glow), 0 0 60px var(--crimson-glow);
}

.lang-cover-btn.en {
    background: linear-gradient(135deg, rgba(45, 45, 45, 0.9) 0%, rgba(26, 26, 26, 0.9) 100%);
    color: var(--gray-200);
    border: 2px solid var(--gray-600);
}

.lang-cover-btn.en:hover {
    border-color: var(--crimson);
    color: var(--crimson);
    transform: translateY(-5px);
    box-shadow: 0 0 30px rgba(220, 20, 60, 0.3);
}

.lang-cover-btn i {
    font-size: 1.3rem;
}

/* Features */
.cover-features {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 20px;
    margin-top: 50px;
    max-width: 700px;
    margin-left: auto;
    margin-right: auto;
}

.feature-item {
    background: rgba(26, 26, 26, 0.8);
    border: 1px solid rgba(220, 20, 60, 0.2);
    border-radius: 10px;
    padding: 20px;
    transition: all 0.3s ease;
}

.feature-item:hover {
    border-color: var(--crimson);
    transform: translateY(-3px);
    box-shadow: 0 5px 20px rgba(220, 20, 60, 0.2);
}

.feature-item i {
    font-size: 1.5rem;
    color: var(--crimson);
    margin-bottom: 10px;
}

.feature-item h4 {
    color: var(--white);
    font-size: 0.9rem;
    margin-bottom: 5px;
}

.feature-item p {
    color: var(--gray-400);
    font-size: 0.8rem;
    margin: 0;
}

/* Footer */
.cover-footer {
    position: absolute;
    bottom: 30px;
    color: var(--gray-500);
    font-size: 0.8rem;
}

.cover-footer a {
    color: var(--crimson);
    text-decoration: none;
}

.cover-footer a:hover {
    text-shadow: 0 0 10px var(--crimson-glow);
}

/* Terminal effect */
.terminal-text {
    font-family: 'Fira Code', monospace;
    color: var(--terminal-green);
    font-size: 0.9rem;
}

.terminal-text::before {
    content: '> ';
    color: var(--crimson);
}

.typing-cursor {
    animation: blink 1s infinite;
}

@keyframes blink {
    0%, 50% { opacity: 1; }
    51%, 100% { opacity: 0; }
}

/* Responsive */
@media (max-width: 768px) {
    .cover-title {
        font-size: 2rem;
    }
    
    .cover-subtitle {
        font-size: 1rem;
    }
    
    .cover-image {
        width: 200px;
        height: 285px;
    }
    
    .lang-cover-btn {
        padding: 15px 30px;
        font-size: 0.9rem;
        min-width: 160px;
    }
    
    .cover-features {
        grid-template-columns: 1fr;
    }
}

@media (max-width: 480px) {
    .cover-title {
        font-size: 1.6rem;
        letter-spacing: 1px;
    }
    
    .cover-image {
        width: 160px;
        height: 228px;
    }
    
    .language-buttons {
        flex-direction: column;
        align-items: center;
    }
}
</style>
</head>
<body>
    <div class="cover-background"></div>
    <div class="grid-overlay"></div>
    <div class="particles">
        <div class="particle" style="left: 10%; animation-delay: 0s;"></div>
        <div class="particle" style="left: 20%; animation-delay: 2s;"></div>
        <div class="particle" style="left: 30%; animation-delay: 4s;"></div>
        <div class="particle" style="left: 40%; animation-delay: 1s;"></div>
        <div class="particle" style="left: 50%; animation-delay: 3s;"></div>
        <div class="particle" style="left: 60%; animation-delay: 5s;"></div>
        <div class="particle" style="left: 70%; animation-delay: 2.5s;"></div>
        <div class="particle" style="left: 80%; animation-delay: 4.5s;"></div>
        <div class="particle" style="left: 90%; animation-delay: 1.5s;"></div>
    </div>
    
    <div class="cover-container">
        <div class="cover-content">
            <img src="images/image-000.jpg" alt="Red Team Logbook Cover" class="cover-image">
            
            <h1 class="cover-title">
                RED<span>TEAM</span> LOGBOOK
            </h1>
            <p class="cover-subtitle">Explotación Moderna del Kernel de Linux</p>
            
            <p class="cover-description">
                Una guía técnica exhaustiva sobre técnicas de explotación del kernel de Linux, 
               涵盖了漏洞利用、模糊测试、补丁差异分析和崩溃分析等核心主题。
            </p>
            
            <div class="language-buttons">
                <a href="es/index.html" class="lang-cover-btn es">
                    <i class="fas fa-book"></i>
                    Español
                </a>
                <a href="en/index.html" class="lang-cover-btn en">
                    <i class="fas fa-book-open"></i>
                    English
                </a>
            </div>
            
            <div class="cover-features">
                <div class="feature-item">
                    <i class="fas fa-bug"></i>
                    <h4>Vulnerability Classes</h4>
                    <p>Memory corruption, race conditions, type confusion</p>
                </div>
                <div class="feature-item">
                    <i class="fas fa-random"></i>
                    <h4>Fuzzing</h4>
                    <p>AFL++, Honggfuzz, Syzkaller</p>
                </div>
                <div class="feature-item">
                    <i class="fas fa-code-branch"></i>
                    <h4>Patch Diffing</h4>
                    <p>Binary analysis, exploit development</p>
                </div>
                <div class="feature-item">
                    <i class="fas fa-crash"></i>
                    <h4>Crash Analysis</h4>
                    <p>Debugging, sanitizers, triage</p>
                </div>
            </div>
            
            <p class="terminal-text">
                <span class="typing-cursor">_</span>
            </p>
        </div>
        
        <footer class="cover-footer">
            <p>© 2024 <a href="https://github.com/mburgc/mburgc.github.io" target="_blank">
                <i class="fab fa-github"></i> mburgc
            </a> | <a href="index.html">Home</a></p>
        </footer>
    </div>
</body>
</html>"""

    with open(os.path.join("../bitacora", "index.html"), "w", encoding="utf-8") as f:
        f.write(index_html)

    # Create index pages for each language
    # Spanish index
    es_index_html = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Índice | Bitácora Red Team</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Fira+Code:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
:root {
    --crimson: #DC143C;
    --crimson-glow: rgba(220, 20, 60, 0.6);
    --gray-900: #0a0a0a;
    --gray-800: #1a1a1a;
    --gray-200: #d4d4d4;
    --gray-100: #f5f5f5;
    --white: #ffffff;
    --font-mono: 'Fira Code', monospace;
}
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
    font-family: var(--font-mono);
    background: var(--gray-900);
    color: var(--gray-200);
    min-height: 100vh;
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 40px 20px;
}
.index-container {
    max-width: 700px;
    width: 100%;
}
.index-title {
    font-size: 2.5rem;
    color: var(--white);
    text-align: center;
    margin-bottom: 10px;
}
.index-title span { color: var(--crimson); }
.index-subtitle {
    text-align: center;
    color: var(--gray-200);
    margin-bottom: 40px;
    font-size: 1.1rem;
}
.chapter-list {
    list-style: none;
}
.chapter-item {
    margin-bottom: 15px;
}
.chapter-link {
    display: flex;
    align-items: center;
    gap: 20px;
    padding: 20px 25px;
    background: linear-gradient(135deg, rgba(26, 26, 26, 0.9) 0%, rgba(45, 45, 45, 0.8) 100%);
    border: 1px solid rgba(220, 20, 60, 0.2);
    border-radius: 10px;
    text-decoration: none;
    color: var(--gray-200);
    transition: all 0.3s ease;
}
.chapter-link:hover {
    background: linear-gradient(135deg, rgba(220, 20, 60, 0.2) 0%, rgba(220, 20, 60, 0.1) 100%);
    border-color: var(--crimson);
    transform: translateX(10px);
    box-shadow: 0 0 30px var(--crimson-glow);
}
.chapter-num {
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--crimson);
    min-width: 50px;
}
.chapter-name {
    flex: 1;
    font-size: 1.1rem;
}
.chapter-arrow {
    color: var(--crimson);
    opacity: 0;
    transition: all 0.3s ease;
}
.chapter-link:hover .chapter-arrow {
    opacity: 1;
    transform: translateX(5px);
}
.back-link {
    display: inline-flex;
    align-items: center;
    gap: 10px;
    color: var(--crimson);
    text-decoration: none;
    margin-bottom: 30px;
    transition: all 0.3s ease;
}
.back-link:hover {
    text-shadow: 0 0 15px var(--crimson-glow);
}
@media (max-width: 600px) {
    .index-title { font-size: 1.8rem; }
    .chapter-link { padding: 15px; }
    .chapter-num { font-size: 1.2rem; min-width: 40px; }
    .chapter-name { font-size: 0.95rem; }
}
    </style>
</head>
<body>
    <div class="index-container">
        <a href="index.html" class="back-link">
            <i class="fas fa-arrow-left"></i> Volver a Portada
        </a>
        <h1 class="index-title">BITÁCORA <span>RED TEAM</span></h1>
        <p class="index-subtitle">Índice de Contenidos</p>
        <ul class="chapter-list">
            <li class="chapter-item">
                <a href="01-introduccion.html" class="chapter-link">
                    <span class="chapter-num">01</span>
                    <span class="chapter-name">Introducción</span>
                    <i class="fas fa-chevron-right chapter-arrow"></i>
                </a>
            </li>
            <li class="chapter-item">
                <a href="02-clases-vulnerabilidades.html" class="chapter-link">
                    <span class="chapter-num">02</span>
                    <span class="chapter-name">Clases de Vulnerabilidades</span>
                    <i class="fas fa-chevron-right chapter-arrow"></i>
                </a>
            </li>
            <li class="chapter-item">
                <a href="03-fuzzing.html" class="chapter-link">
                    <span class="chapter-num">03</span>
                    <span class="chapter-name">Fuzzing</span>
                    <i class="fas fa-chevron-right chapter-arrow"></i>
                </a>
            </li>
            <li class="chapter-item">
                <a href="04-patch-diffing.html" class="chapter-link">
                    <span class="chapter-num">04</span>
                    <span class="chapter-name">Patch Diffing</span>
                    <i class="fas fa-chevron-right chapter-arrow"></i>
                </a>
            </li>
            <li class="chapter-item">
                <a href="05-analisis-crashes.html" class="chapter-link">
                    <span class="chapter-num">05</span>
                    <span class="chapter-name">Análisis de Crashes</span>
                    <i class="fas fa-chevron-right chapter-arrow"></i>
                </a>
            </li>
        </ul>
    </div>
</body>
</html>"""

    with open(os.path.join("../bitacora/es", "index.html"), "w", encoding="utf-8") as f:
        f.write(es_index_html)

    # English index
    en_index_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Index | Red Team Logbook</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Fira+Code:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
:root {
    --crimson: #DC143C;
    --crimson-glow: rgba(220, 20, 60, 0.6);
    --gray-900: #0a0a0a;
    --gray-800: #1a1a1a;
    --gray-200: #d4d4d4;
    --gray-100: #f5f5f5;
    --white: #ffffff;
    --font-mono: 'Fira Code', monospace;
}
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
    font-family: var(--font-mono);
    background: var(--gray-900);
    color: var(--gray-200);
    min-height: 100vh;
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 40px 20px;
}
.index-container {
    max-width: 700px;
    width: 100%;
}
.index-title {
    font-size: 2.5rem;
    color: var(--white);
    text-align: center;
    margin-bottom: 10px;
}
.index-title span { color: var(--crimson); }
.index-subtitle {
    text-align: center;
    color: var(--gray-200);
    margin-bottom: 40px;
    font-size: 1.1rem;
}
.chapter-list {
    list-style: none;
}
.chapter-item {
    margin-bottom: 15px;
}
.chapter-link {
    display: flex;
    align-items: center;
    gap: 20px;
    padding: 20px 25px;
    background: linear-gradient(135deg, rgba(26, 26, 26, 0.9) 0%, rgba(45, 45, 45, 0.8) 100%);
    border: 1px solid rgba(220, 20, 60, 0.2);
    border-radius: 10px;
    text-decoration: none;
    color: var(--gray-200);
    transition: all 0.3s ease;
}
.chapter-link:hover {
    background: linear-gradient(135deg, rgba(220, 20, 60, 0.2) 0%, rgba(220, 20, 60, 0.1) 100%);
    border-color: var(--crimson);
    transform: translateX(10px);
    box-shadow: 0 0 30px var(--crimson-glow);
}
.chapter-num {
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--crimson);
    min-width: 50px;
}
.chapter-name {
    flex: 1;
    font-size: 1.1rem;
}
.chapter-arrow {
    color: var(--crimson);
    opacity: 0;
    transition: all 0.3s ease;
}
.chapter-link:hover .chapter-arrow {
    opacity: 1;
    transform: translateX(5px);
}
.back-link {
    display: inline-flex;
    align-items: center;
    gap: 10px;
    color: var(--crimson);
    text-decoration: none;
    margin-bottom: 30px;
    transition: all 0.3s ease;
}
.back-link:hover {
    text-shadow: 0 0 15px var(--crimson-glow);
}
@media (max-width: 600px) {
    .index-title { font-size: 1.8rem; }
    .chapter-link { padding: 15px; }
    .chapter-num { font-size: 1.2rem; min-width: 40px; }
    .chapter-name { font-size: 0.95rem; }
}
    </style>
</head>
<body>
    <div class="index-container">
        <a href="index.html" class="back-link">
            <i class="fas fa-arrow-left"></i> Back to Cover
        </a>
        <h1 class="index-title">RED<span>TEAM</span> LOGBOOK</h1>
        <p class="index-subtitle">Table of Contents</p>
        <ul class="chapter-list">
            <li class="chapter-item">
                <a href="01-introduction.html" class="chapter-link">
                    <span class="chapter-num">01</span>
                    <span class="chapter-name">Introduction</span>
                    <i class="fas fa-chevron-right chapter-arrow"></i>
                </a>
            </li>
            <li class="chapter-item">
                <a href="02-vulnerability-classes.html" class="chapter-link">
                    <span class="chapter-num">02</span>
                    <span class="chapter-name">Vulnerability Classes</span>
                    <i class="fas fa-chevron-right chapter-arrow"></i>
                </a>
            </li>
            <li class="chapter-item">
                <a href="03-fuzzing.html" class="chapter-link">
                    <span class="chapter-num">03</span>
                    <span class="chapter-name">Fuzzing</span>
                    <i class="fas fa-chevron-right chapter-arrow"></i>
                </a>
            </li>
            <li class="chapter-item">
                <a href="04-patch-diffing.html" class="chapter-link">
                    <span class="chapter-num">04</span>
                    <span class="chapter-name">Patch Diffing</span>
                    <i class="fas fa-chevron-right chapter-arrow"></i>
                </a>
            </li>
            <li class="chapter-item">
                <a href="05-crash-analysis.html" class="chapter-link">
                    <span class="chapter-num">05</span>
                    <span class="chapter-name">Crash Analysis</span>
                    <i class="fas fa-chevron-right chapter-arrow"></i>
                </a>
            </li>
        </ul>
    </div>
</body>
</html>"""

    with open(os.path.join("../bitacora/en", "index.html"), "w", encoding="utf-8") as f:
        f.write(en_index_html)

    print("✅ Build complete! Output in ../bitacora/")
    print("   - Main index: _site/index.html")
    print("   - Spanish: _site/es/")
    print("   - English: _site/en/")


if __name__ == "__main__":
    main()
