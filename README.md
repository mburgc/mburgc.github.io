# mburgc.github.io

Personal site of **Marcelo Burgos** — an editorial CV that doubles as a portfolio.

The page *is* the résumé: one column, print-like typography, and a glass margin
panel that previews an entry when you hover or focus it. No framework, no
bundler, no tracking.

## Structure

```
├── index.html              # generated — English
├── es/index.html           # generated — Spanish
├── work/index.html         # generated — index of everything published (EN)
├── es/work/index.html      # generated — same, Spanish
├── site/
│   ├── content.py          # single source of truth (ES/EN + previews)
│   └── build.py            # renders the four pages
├── data/
│   ├── repos.json          # GitHub snapshot (no API calls at runtime)
│   ├── videos.json         # YouTube snapshot
│   └── reddit.json         # curated Reddit threads
├── assets/
│   ├── css/editorial.css   # design system
│   ├── js/preview.js       # margin panel + deferred video
│   ├── fonts/              # 6 self-hosted woff2
│   └── cv/                 # CV in PDF
├── lab/index.html          # "what your browser reveals" demo
├── bitacora/               # Red Team LogBook (own Python build)
└── experimentos/           # JULIA diary
```

## Build

```bash
cd site
python build.py     # writes the four HTML pages
```

No dependencies. The HTML is generated, so edit `content.py`, never the output.

To refresh the GitHub and YouTube snapshots:

```bash
python site/fetch_data.py   # rewrites data/repos.json and data/videos.json
cd site && python build.py
```

It keeps the curated parts (featured flags, hand-written descriptions, video
tags) and only updates what the APIs own: stars, languages, dates and titles.

## Work index

The CV carries a **Work** section with five bodies of work, each one previewed
in the margin panel:

| Group | Source | Content |
|---|---|---|
| Red Team LogBook | `bitacora/` | 5 chapters, ES/EN |
| Code | `data/repos.json` | 8 public repositories |
| JULIA | `experimentos/julia/` | 6 diary entries, ES/EN |
| Video | `data/videos.json` | 5 YouTube pieces |
| On Reddit | `data/reddit.json` | 7 curated threads |

The full index lives at `/work/` (and `/es/work/`). Data files are committed
snapshots: the browser never calls the GitHub, YouTube or Reddit APIs, so there
are no CORS proxies and no third-party scripts.

## Design

- Palette and type inherited from the CV: `#101820` ink, `#2f6f8f` accent,
  Raleway for headings, Source Sans 3 for body, both self-hosted.
- The margin panel is sticky on desktop and becomes a bottom sheet on mobile
  (the `i` button on each entry).
- The panel has a fixed height, so previews never shift the index below it.
- Video is deferred: a poster loads first, the YouTube iframe only on click.
- `prefers-reduced-motion` disables every transition.

## Privacy

- No cookies, no analytics, no fingerprinting.
- No third-party requests on load, except the YouTube thumbnail in the margin
  panel.
- The old "visitor information" demo moved to [`/lab/`](https://mburgc.github.io/lab/)
  and is `noindex`.

## Deploy

GitHub Pages publishes from the `main` branch (legacy source), so a push to
`main` is enough. The Bitácora has its own workflow that rebuilds
`bitacora/**` with Python.
