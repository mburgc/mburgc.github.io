#!/usr/bin/env python3
"""Genera index.html (EN) y es/index.html (ES) desde site/content.py."""

from __future__ import annotations

import html
import json
from pathlib import Path

from content import CONTENT, LINKS, NAME, PORTRAIT, canonical, previews

ROOT = Path(__file__).resolve().parent.parent

BASE_HEAD = """<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{description}">
<link rel="canonical" href="{canonical}">
<link rel="alternate" hreflang="en" href="https://mburgc.github.io/">
<link rel="alternate" hreflang="es" href="https://mburgc.github.io/es/">
<link rel="alternate" hreflang="x-default" href="https://mburgc.github.io/">
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
<div class="shell">
"""


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


def rows_html(items: list) -> str:
    return "".join(
        f'      <div class="row"><b>{a}</b><span>{b}</span></div>' for a, b in items
    )


def render(lang: str) -> str:
    c = CONTENT[lang]
    L = c["labels"]
    prev = json.dumps(previews(lang), ensure_ascii=False).replace("</", "<\\/")

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
            "knowsAbout": ["Offensive Security", "Software Architecture", "AI Systems", "Python", "AWS"],
        },
        ensure_ascii=False,
        indent=1,
    )

    head = BASE_HEAD.format(
        lang=c["lang"],
        title=html.escape(c["title"]),
        description=html.escape(c["description"]),
        canonical=canonical(lang),
        portrait=PORTRAIT,
        jsonld=jsonld,
    )

    experience = "".join(job_html(j, L) for j in c["experience"])
    projects = "".join(project_html(p, L) for p in c["projects"])
    talks = "".join(talk_html(t, L) for t in c["talks"])
    skills = rows_html(c["skills"])
    education = rows_html(c["education"])

    video = "YwhioxWlUWo"
    video_label = next(t["title"] for t in c["talks"] if t.get("video"))

    body = f"""  <main id="main" class="doc">
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
      <a href="{LINKS['logbook']}">Red Team LogBook</a>
      <a href="{LINKS['experiments']}">Experiments</a>
      <a href="{LINKS['lab']}">Lab</a>
      <a href="{LINKS['cv_pdf']}">CV (PDF)</a>
      <a href="{LINKS['reddit']}">Reddit</a>
      <a href="{LINKS['youtube']}">YouTube</a>
      <span class="colophon">{L['colophon']}</span>
    </footer>
  </main>

  <aside class="margin" id="margin-panel" aria-label="{L['peek']}"
         data-label-now="{L['now']}" data-label-preview="{L['peek']}" data-label-close="{L['close']}">
    <div class="margin-card" id="margin-card">
      <p class="margin-label"><span id="margin-label-text">{L['now']}</span></p>
      <div class="margin-idle" id="margin-idle">
        <p class="idle-note">{L['idle_note']}</p>
        <a class="poster" data-video="{video}" href="https://www.youtube.com/live/{video}" target="_blank" rel="noopener">
          <img src="https://i.ytimg.com/vi/{video}/hqdefault.jpg" alt="" loading="lazy" decoding="async">
          <span class="poster-play"><span>&#9654;</span></span>
        </a>
        <p class="idle-hint">{video_label} · {L['idle_hint']}</p>
      </div>
      <div class="margin-body" id="margin-body" hidden aria-live="polite"></div>
    </div>
  </aside>
</div>

<dialog class="sheet" id="sheet" aria-label="{L['peek']}">
  <div class="sheet-card">
    <button class="sheet-close" type="button" aria-label="{L['close']}">&times;</button>
    <div id="sheet-body"></div>
  </div>
</dialog>

<script type="application/json" id="previews">{prev}</script>
<script src="/assets/js/preview.js" defer></script>
</body>
</html>
"""
    return head + body


def main() -> None:
    (ROOT / "index.html").write_text(render("en"), encoding="utf-8")
    (ROOT / "es").mkdir(exist_ok=True)
    (ROOT / "es" / "index.html").write_text(render("es"), encoding="utf-8")
    print("index.html + es/index.html generados")


if __name__ == "__main__":
    main()
