# mburgc.github.io

Personal site of **Marcelo Burgos** — an editorial CV that doubles as a portfolio.

The page *is* the résumé: one column, print-like typography, and a glass margin
panel that previews an entry when you hover or focus it. No framework, no
bundler, no tracking.

## Structure

```
├── index.html              # generated — English
├── es/index.html           # generated — Spanish
├── site/
│   ├── content.py          # single source of truth (ES/EN + previews)
│   └── build.py            # renders both pages
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
python build.py     # writes ../index.html and ../es/index.html
```

No dependencies. The HTML is generated, so edit `content.py`, never the output.

## Design

- Palette and type inherited from the CV: `#101820` ink, `#2f6f8f` accent,
  Raleway for headings, Source Sans 3 for body, both self-hosted.
- The margin panel is sticky on desktop and becomes a bottom sheet on mobile
  (the `i` button on each entry).
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
