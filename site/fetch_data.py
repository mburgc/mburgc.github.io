#!/usr/bin/env python3
"""Refresca los snapshots de datos del portafolio.

El sitio es estático: nada de esto corre en el navegador. Este script se ejecuta
a mano (o desde un cron) y reescribe `data/repos.json` y `data/videos.json`
conservando la curaduría: los `featured`, las descripciones escritas a mano y
los `tag` de cada video.

    python site/fetch_data.py

Solo usa la biblioteca estándar. Reddit se mantiene curado a mano en
`data/reddit.json` porque el feed devuelve hilos que no corresponden al sitio.
"""

from __future__ import annotations

import json
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
USER = "mburgc"
CHANNEL = "UCdGaa7KjkL7o58LU1jQ3SRA"
UA = "mburgc.github.io data refresh (+https://mburgc.github.io)"

NS = {
    "atom": "http://www.w3.org/2005/Atom",
    "yt": "http://www.youtube.com/xml/schemas/2015",
}


def get(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as response:
        return response.read()


def read(name: str) -> list:
    path = DATA / name
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))


def write(name: str, payload: list) -> None:
    (DATA / name).write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def refresh_repos() -> None:
    previous = {r["name"]: r for r in read("repos.json")}
    raw = json.loads(get(f"https://api.github.com/users/{USER}/repos?per_page=100&sort=pushed"))

    repos = []
    for item in raw:
        if item.get("fork"):
            continue
        name = item["name"]
        if name == USER or name == f"{USER}.github.io":
            continue
        if (item.get("description") or "").lower().startswith("fork mirror"):
            continue
        old = previous.get(name, {})
        repos.append(
            {
                "name": name,
                "description": old.get("description", item.get("description")),
                "language": item.get("language"),
                "stars": item.get("stargazers_count", 0),
                "pushed": (item.get("pushed_at") or "")[:10],
                "url": item["html_url"],
                "featured": old.get("featured", False),
            }
        )

    write("repos.json", repos)
    print(f"repos.json: {len(repos)} repositorios")


def refresh_videos() -> None:
    previous = {v["id"]: v for v in read("videos.json")}
    feed = ET.fromstring(get(f"https://www.youtube.com/feeds/videos.xml?channel_id={CHANNEL}"))

    videos = []
    for entry in feed.findall("atom:entry", NS):
        vid = entry.findtext("yt:videoId", namespaces=NS)
        if not vid:
            continue
        videos.append(
            {
                "id": vid,
                "title": entry.findtext("atom:title", namespaces=NS),
                "tag": previous.get(vid, {}).get("tag", "video"),
                "date": (entry.findtext("atom:published", namespaces=NS) or "")[:10],
            }
        )

    write("videos.json", videos)
    print(f"videos.json: {len(videos)} videos")


def main() -> None:
    DATA.mkdir(exist_ok=True)
    refresh_repos()
    refresh_videos()
    print("Listo. Revisa el diff y reconstruye con: python site/build.py")


if __name__ == "__main__":
    main()
