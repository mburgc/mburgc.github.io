#!/usr/bin/env python3
"""Genera index.html (EN), es/index.html (ES) y el indice /work/ en ambos idiomas."""

from __future__ import annotations

import html
import json
from pathlib import Path

from content import (
    CONTENT,
    JULIA,
    LINKS,
    LOGBOOK,
    NAME,
    PORTRAIT,
    canonical,
    previews,
    work_groups,
)

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

HEAD = """<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{description}">
<link rel="canonical" href="{canonical}">
<link rel="alternate" hreflang="en" href="https://mburgc.github.io{en_path}">
<link rel="alternate" hreflang="es" href="https://mburgc.github.io{es_path}">
<link rel="alternate" hreflang="x-default" href="https://mburgc.github.io{en_path}">
<meta property="og:type" content="profile">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{description}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="https://mburgc.github.io{portrait}">
<meta name="theme-color" content="#ffffff">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' fill='%23101820'/%3E%3Ctext x='16' y='22' font-family='Georgia,serif' font-size='16' fill='%23ffffff' text-anchor='middle'%3EMB%3C/text%3E%3C/svg%3E">
<link rel="stylesheet" href="/assets/css/editorial.css">
<script type="application/ld+json">
{jsonld}
</script>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
"""

MARGIN = """
  <aside class="margin" id="margin-panel" aria-label="{peek}"
         data-label-now="{now}" data-label-preview="{peek}" data-label-close="{close}" data-label-play="{play}">
    <div class="margin-card" id="margin-card">
      <p class="margin-label"><span id="margin-label-text">{now}</span></p>
      <div class="margin-idle" id="margin-idle">
        <p class="idle-note">{idle_note}</p>
        <a class="poster" data-video="{video}" href="https://www.youtube.com/live/{video}" target="_blank" rel="noopener" aria-label="{play}: {video_label}">
          <img src="https://i.ytimg.com/vi/{video}/hqdefault.jpg" alt="" loading="lazy" decoding="async">
          <span class="poster-play"><span>&#9654;</span></span>
        </a>
        <p class="idle-hint">{video_label} · {idle_hint}</p>
      </div>
      <div class="margin-body" id="margin-body" hidden aria-live="polite"></div>
    </div>

    <nav class="margin-index" aria-label="{index}">
      <p class="margin-label"><span>{index}</span></p>
      <a href="#s-profile">{nav_profile}</a>
      <a href="#s-exp">{nav_exp}</a>
      <a href="#s-projects">{nav_projects}</a>
      <a href="#s-work">{nav_work}</a>
      <a href="#s-talks">{nav_talks}</a>
      <a href="#s-skills">{nav_skills}</a>
      <a href="#s-edu">{nav_edu}</a>
      <p class="margin-contact">
        <a href="mailto:{email}">{email}</a>
        <a href="{cv}">CV (PDF)</a>
      </p>
    </nav>
  </aside>
</div>

<dialog class="sheet" id="sheet" aria-label="{peek}">
  <div class="sheet-card">
    <button class="sheet-close" type="button" aria-label="{close}">&times;</button>
    <div id="sheet-body"></div>
  </div>
</dialog>
"""


def load(name: str) -> list:
    path = DATA / name
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))


def job_html(job: dict, labels: dict) -> str:
    subs = "".join(f'<p class="entry-sub">{s}</p>' for s in job.get("subroles") or [])
    return f"""      <article class="entry" data-preview="{job['id']}">
        <div class="entry-head">
          <h3 class="entry-title">{job['company']}</h3>
          <span class="entry-period">{job['period']}</span>
        </div>
        <p class="entry-role">{job['role']}</p>
        <p class="entry-meta">{job['location']}</p>{subs}
        <button class="peek" type="button" data-peek="{job['id']}" aria-label="{labels['peek']}: {job['company']}">i</button>
      </article>"""


def project_html(item: dict, labels: dict) -> str:
    return f"""      <article class="entry" data-preview="{item['id']}">
        <div class="entry-head">
          <h3 class="entry-title">{item['title']}</h3>
        </div>
        <p class="entry-meta">{item['meta']}</p>
        <p class="entry-desc">{item['desc']}</p>
        <button class="peek" type="button" data-peek="{item['id']}" aria-label="{labels['peek']}: {item['title']}">i</button>
      </article>"""


def talk_html(item: dict, labels: dict) -> str:
    return f"""      <article class="entry" data-preview="{item['id']}">
        <div class="entry-head">
          <h3 class="entry-title">{item['event']}</h3>
        </div>
        <p class="entry-role">{item['title']}</p>
        <p class="entry-meta">{item['meta']}</p>
        <button class="peek" type="button" data-peek="{item['id']}" aria-label="{labels['peek']}: {item['title']}">i</button>
      </article>"""


def group_html(group: dict, labels: dict) -> str:
    sample = " · ".join(html.escape(i["label"]) for i in group["items"][:3])
    rest = len(group["items"]) - 3
    if rest > 0:
        sample += f" · +{rest}"
    return f"""      <article class="entry" data-preview="{group['id']}">
        <div class="entry-head">
          <h3 class="entry-title"><a href="{group['href']}">{group['title']}</a></h3>
          <span class="entry-period">{group['meta']}</span>
        </div>
        <p class="entry-desc">{sample}</p>
        <button class="peek" type="button" data-peek="{group['id']}" aria-label="{labels['peek']}: {group['title']}">i</button>
      </article>"""


def rows_html(items: list, cls: str = "") -> str:
    return "".join(
        f'      <div class="row {cls}"><b>{a}</b><span>{b}</span></div>' for a, b in items
    )


def group_preview(group: dict) -> dict:
    return {
        "kind": "group",
        "title": group["title"],
        "meta": group["meta"],
        "items": group["items"],
        "link": {"href": group.get("source", group["href"]), "label": group["cta"]},
    }


def render(lang: str, repos: list, videos: list, posts: list) -> str:
    c = CONTENT[lang]
    L = c["labels"]
    groups = work_groups(lang, repos, videos, posts)
    cv_groups = groups

    prev = previews(lang)
    for g in groups:
        prev[g["id"]] = group_preview(g)
    prev_json = json.dumps(prev, ensure_ascii=False).replace("</", "<\\/")

    jsonld = json.dumps(
        {
            "@context": "https://schema.org",
            "@type": "Person",
            "name": NAME,
            "jobTitle": c["role"],
            "url": canonical(lang),
            "image": f"https://mburgc.github.io{PORTRAIT}",
            "email": "mailto:" + LINKS["email"],
            "address": {"@type": "PostalAddress", "addressLocality": "Santiago", "addressCountry": "CL"},
            "sameAs": [LINKS["linkedin"], LINKS["github"], LINKS["reddit"], LINKS["youtube"]],
        },
        ensure_ascii=False,
        indent=1,
    )

    head = HEAD.format(
        lang=c["lang"],
        title=html.escape(c["title"]),
        description=html.escape(c["description"]),
        canonical=canonical(lang),
        en_path="/" if lang == "en" else "/",
        es_path="/es/" if lang == "en" else "/es/",
        portrait=PORTRAIT,
        jsonld=jsonld,
    )

    experience = "".join(job_html(j, L) for j in c["experience"])
    projects = "".join(project_html(p, L) for p in c["projects"])
    talks = "".join(talk_html(t, L) for t in c["talks"])
    work = "".join(group_html(g, L) for g in cv_groups)
    skills = rows_html(c["skills"])
    education = rows_html(c["education"], "row--edu")
    video = "YwhioxWlUWo"
    work_path = "/work/" if lang == "en" else "/es/work/"
    book_href = LOGBOOK[lang]["href"]
    book_title = LOGBOOK[lang]["title"]
    julia_href = JULIA[lang]["href"]
    julia_title = JULIA[lang]["title"]

    body = f"""<div class="shell">
  <main id="main" class="doc">
    <header class="masthead">
      <img class="portrait" src="{PORTRAIT}" alt="{NAME}" width="88" height="88" decoding="async">
      <div>
        <h1>{NAME}</h1>
        <p class="role">{c['role']}</p>
        <p class="kicker">{c['kicker']}</p>
        <p class="contact">
          <span>Santiago, Chile</span>
          <span><a href="mailto:{LINKS['email']}">{LINKS['email']}</a></span>
          <span><a href="{LINKS['linkedin']}" rel="me noopener">LinkedIn</a></span>
          <span><a href="{LINKS['github']}" rel="me noopener">GitHub</a></span>
        </p>
      </div>
      <nav class="lang" aria-label="Language">
        <a href="{c['other']['href']}" hreflang="{c['other']['label'].lower()}">{c['other']['label']}</a>
      </nav>
    </header>

    <section aria-labelledby="s-profile">
      <h2 id="s-profile">{L['profile']}</h2>
      <p class="lead">{c['profile']}</p>
    </section>

    <section aria-labelledby="s-exp">
      <h2 id="s-exp">{L['experience']}</h2>
{experience}
    </section>

    <section aria-labelledby="s-projects">
      <h2 id="s-projects">{L['projects']}</h2>
{projects}
    </section>

    <section aria-labelledby="s-work">
      <h2 id="s-work">{L['work']}</h2>
{work}
    </section>

    <section aria-labelledby="s-talks">
      <h2 id="s-talks">{L['talks']}</h2>
{talks}
    </section>

    <section aria-labelledby="s-skills">
      <h2 id="s-skills">{L['skills']}</h2>
{skills}
    </section>

    <section aria-labelledby="s-edu">
      <h2 id="s-edu">{L['education']}</h2>
{education}
      <div class="row"><b>{L['certs']}</b><span>{c['certs']}</span></div>
    </section>

    <footer>
      <a href="{work_path}">{L['work']}</a>
      <a href="{book_href}">{book_title}</a>
      <a href="{julia_href}">{julia_title}</a>
      <a href="{LINKS['lab']}">Lab</a>
      <a href="{LINKS['cv_pdf']}">CV (PDF)</a>
      <a href="{LINKS['reddit']}">Reddit</a>
      <a href="{LINKS['youtube']}">YouTube</a>
      <span class="colophon">{L['colophon']}</span>
    </footer>
  </main>
"""
    margin = MARGIN.format(
        peek=L["peek"],
        now=L["now"],
        close=L["close"],
        idle_note=L["idle_note"],
        idle_hint=L["idle_hint"],
        video=video,
        video_label=next(t["title"] for t in c["talks"] if t.get("video")),
        play=L["play"],
        index=L["index"],
        nav_profile=L["profile"],
        nav_exp=L["experience"],
        nav_projects=L["projects"],
        nav_work=L["work"],
        nav_talks=L["talks"],
        nav_skills=L["skills"],
        nav_edu=L["education"],
        email=LINKS["email"],
        cv=LINKS["cv_pdf"],
    )
    return head + body + margin + f"""
<script type="application/json" id="previews">{prev_json}</script>
<script src="/assets/js/preview.js" defer></script>
</body>
</html>
"""


def render_work(lang: str, repos: list, videos: list, posts: list) -> str:
    c = CONTENT[lang]
    L = c["labels"]
    groups = work_groups(lang, repos, videos, posts)
    base = "/work/" if lang == "en" else "/es/work/"

    sections = []
    for group in groups:
        items = "".join(
            '<li>'
            + (
                f'<a href="{html.escape(i["href"], quote=True)}">{html.escape(i["label"])}</a>'
                if i.get("href")
                else html.escape(i["label"])
            )
            + (f'<span>{html.escape(i["meta"])}</span>' if i.get("meta") else "")
            + "</li>"
            for i in group["items"]
        )
        sections.append(
            f"""    <section aria-labelledby="g-{group['id']}">
      <h2 id="g-{group['id']}">{group['title']}</h2>
      <p class="entry-meta" style="margin:12px 0 0">{group['meta']} · <a href="{group['source']}">{group['cta']} &rarr;</a></p>
      <ul class="idx">{items}</ul>
    </section>"""
        )

    book = LOGBOOK[lang]
    julia = JULIA[lang]
    back_href = "/" if lang == "en" else "/es/"
    other_href = "/es/work/" if lang == "en" else "/work/"
    other_label = "ES" if lang == "en" else "EN"
    if lang == "en":
        extra_text = (
            f"Everything I publish, in one place: the {book['title']} "
            f"({len(book['items'])} chapters, ES/EN), {julia['title']} "
            f"({len(julia['items'])} entries, ES/EN), {len(repos)} public repositories, "
            f"{len(videos)} videos and {len(posts)} Reddit threads."
        )
        back_label = "Back to the CV"
    else:
        extra_text = (
            f"Todo lo que publico, en un solo lugar: la {book['title']} "
            f"({len(book['items'])} capítulos, ES/EN), {julia['title']} "
            f"({len(julia['items'])} entradas, ES/EN), {len(repos)} repositorios públicos, "
            f"{len(videos)} videos y {len(posts)} hilos de Reddit."
        )
        back_label = "Volver al CV"
    extra = f"""    <p class="lead" style="font-size:.95rem">{extra_text}</p>"""

    return HEAD.format(
        lang=c["lang"],
        title=html.escape(("Work — " + NAME) if lang == "en" else ("Obra — " + NAME)),
        description=html.escape("Index of writing, code, experiments and media." if lang == "en" else "Índice de escritos, código, experimentos y medios."),
        canonical=f"https://mburgc.github.io{base}",
        en_path="/work/",
        es_path="/es/work/",
        portrait=PORTRAIT,
        jsonld=json.dumps({"@context": "https://schema.org", "@type": "CollectionPage", "name": "Work", "url": f"https://mburgc.github.io{base}"}),
    ) + f"""<div class="shell shell--single">
  <main id="main">
    <header class="masthead" style="grid-template-columns:1fr auto">
      <div>
        <h1 style="font-size:1.6rem">{L['work']}</h1>
        <p class="role">{NAME}</p>
      </div>
      <nav class="lang" aria-label="Language">
        <a href="{other_href}" hreflang="{other_label.lower()}">{other_label}</a>
      </nav>
    </header>
{extra}
{''.join(sections)}
    <a class="back" href="{back_href}">&larr; {back_label}</a>

    <footer>
      <a href="mailto:{LINKS['email']}">{LINKS['email']}</a>
      <a href="{LINKS['github']}" rel="me noopener">GitHub</a>
      <a href="{LINKS['linkedin']}" rel="me noopener">LinkedIn</a>
      <a href="{LINKS['cv_pdf']}">CV (PDF)</a>
      <span class="colophon">{L['colophon']}</span>
    </footer>
  </main>
</div>
</body>
</html>
"""


def main() -> None:
    repos = load("repos.json")
    videos = load("videos.json")
    posts = load("reddit.json")

    (ROOT / "index.html").write_text(render("en", repos, videos, posts), encoding="utf-8")
    (ROOT / "es").mkdir(exist_ok=True)
    (ROOT / "es" / "index.html").write_text(render("es", repos, videos, posts), encoding="utf-8")
    (ROOT / "work").mkdir(exist_ok=True)
    (ROOT / "work" / "index.html").write_text(render_work("en", repos, videos, posts), encoding="utf-8")
    (ROOT / "es" / "work").mkdir(parents=True, exist_ok=True)
    (ROOT / "es" / "work" / "index.html").write_text(render_work("es", repos, videos, posts), encoding="utf-8")
    print("index.html, es/index.html, work/index.html, es/work/index.html")


if __name__ == "__main__":
    main()
