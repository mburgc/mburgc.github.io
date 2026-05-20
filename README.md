# [mburgc.github.io](https://mburgc.github.io)

Personal portfolio and technical blog of **Marcelo Burgos** — mathematics, geometry, computation, and security research.

## Structure

```
├── index.html              # Portfolio homepage (vanilla HTML/CSS/JS)
├── bitacora/               # "Bitácora Red Team" — Linux kernel exploitation guide
│   ├── build.py            # Markdown → HTML static site generator (Python)
│   ├── src/                # Source chapters in Markdown (es + en)
│   ├── es/                 # Generated HTML — Spanish
│   ├── en/                 # Generated HTML — English
│   └── images/             # Shared assets
└── .github/workflows/      # CI: auto-builds bitacora on push to main
```

## Features

- **Portfolio**: GitHub repos, latest YouTube video, Reddit posts, visitor info — all fetched client-side via public APIs. No backend, no tracking.
- **Bitácora Red Team**: Bilingual (ES/EN) technical guide on modern Linux kernel exploitation. Full-text search, responsive sidebar, chapter navigation.
- **Theme**: Dark space aesthetic with glassmorphism, animated starfield canvas, zero external runtime dependencies.

## Tech Stack

- **Frontend**: Vanilla HTML / CSS / JavaScript (no frameworks, no bundlers)
- **Bitácora build**: Python + [markdown](https://python-markdown.github.io/)
- **Hosting**: GitHub Pages
- **CI/CD**: GitHub Actions
