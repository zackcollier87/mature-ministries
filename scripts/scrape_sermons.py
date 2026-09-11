#!/usr/bin/env python3
"""Scrape the Heritage Baptist Church sermon library into local JSON + assets.

Source: theheritagechurch.org /library/ (WordPress 'sermon' custom post type).
Pulls metadata via the WP REST API, then fetches each sermon's own page for
the full transcript text, YouTube link, and downloadable PDF sermon guides
(the REST API does not expose post content for this post type).
"""
import json
import os
import re
import time
import sys
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

BASE = "https://theheritagechurch.org"
OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
ASSETS_DIR = os.path.join(os.path.dirname(__file__), "..", "public", "assets")
SESSION = requests.Session()
SESSION.headers.update({"User-Agent": "MatureMinistriesArchiveBot/1.0 (personal sermon archive)"})


def get_json(url, params=None):
    for attempt in range(3):
        r = SESSION.get(url, params=params, timeout=30)
        if r.status_code == 200:
            return r
        time.sleep(2 * (attempt + 1))
    r.raise_for_status()


def fetch_all_sermons():
    sermons = []
    page = 1
    while True:
        r = get_json(f"{BASE}/wp-json/wp/v2/sermon", params={"per_page": 100, "page": page})
        batch = r.json()
        if not batch:
            break
        sermons.extend(batch)
        total_pages = int(r.headers.get("X-WP-TotalPages", page))
        print(f"  fetched page {page}/{total_pages} ({len(batch)} items)", file=sys.stderr)
        if page >= total_pages:
            break
        page += 1
        time.sleep(0.3)
    return sermons


def fetch_taxonomy(name):
    result = {}
    page = 1
    while True:
        r = get_json(f"{BASE}/wp-json/wp/v2/{name}", params={"per_page": 100, "page": page})
        batch = r.json()
        if not batch:
            break
        for t in batch:
            result[t["id"]] = t["name"]
        total_pages = int(r.headers.get("X-WP-TotalPages", page))
        if page >= total_pages:
            break
        page += 1
    return result


YOUTUBE_RE = re.compile(
    r"(?:youtube\.com/(?:watch\?v=|embed/|shorts/)|youtu\.be/)([A-Za-z0-9_-]{11})"
)


def extract_youtube_id(soup, text):
    for iframe in soup.select("iframe"):
        src = iframe.get("src", "")
        m = YOUTUBE_RE.search(src)
        if m:
            return m.group(1)
    for a in soup.select("a[href]"):
        m = YOUTUBE_RE.search(a["href"])
        if m:
            return m.group(1)
    m = YOUTUBE_RE.search(text or "")
    if m:
        return m.group(1)
    return None


def download_asset(url, subdir):
    if not url:
        return None
    try:
        fname = re.sub(r"[^A-Za-z0-9._-]", "_", os.path.basename(url.split("?")[0]))
        if not fname:
            return None
        dest_dir = os.path.join(ASSETS_DIR, subdir)
        os.makedirs(dest_dir, exist_ok=True)
        dest_path = os.path.join(dest_dir, fname)
        rel_path = f"/assets/{subdir}/{fname}"
        if os.path.exists(dest_path):
            return rel_path
        r = SESSION.get(url, timeout=60)
        if r.status_code == 200:
            with open(dest_path, "wb") as f:
                f.write(r.content)
            return rel_path
    except Exception as e:
        print(f"    asset download failed for {url}: {e}", file=sys.stderr)
    return None


def scrape_sermon_page(sermon):
    url = sermon["link"]
    r = SESSION.get(url, timeout=30)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    article = soup.select_one("article") or soup.select_one(".entry-content") or soup

    text_parts = []
    for p in article.select("p"):
        t = p.get_text(" ", strip=True)
        if t:
            text_parts.append(t)
    transcript = "\n\n".join(text_parts)

    youtube_id = extract_youtube_id(soup, r.text)

    pdf_guides = []
    seen = set()
    for a in article.select("a[href$='.pdf']"):
        href = urljoin(BASE, a["href"])
        if href in seen:
            continue
        seen.add(href)
        label = a.get_text(strip=True) or "Sermon Guide"
        local_path = download_asset(href, "guides")
        pdf_guides.append({"label": label, "source_url": href, "local_path": local_path})

    thumb_url = sermon.get("_featured_media_url")
    local_thumb = download_asset(thumb_url, "thumbnails") if thumb_url else None

    return {
        "transcript": transcript,
        "youtube_id": youtube_id,
        "pdf_guides": pdf_guides,
        "thumbnail": local_thumb,
    }


def strip_html(html):
    return BeautifulSoup(html or "", "html.parser").get_text(" ", strip=True)


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    os.makedirs(ASSETS_DIR, exist_ok=True)

    print("Fetching sermon list from REST API...", file=sys.stderr)
    raw_sermons = fetch_all_sermons()
    print(f"Total sermons found: {len(raw_sermons)}", file=sys.stderr)

    print("Fetching taxonomies...", file=sys.stderr)
    categories = fetch_taxonomy("categories")
    tags = fetch_taxonomy("tags")

    out_path = os.path.join(OUT_DIR, "sermons.json")
    existing = {}
    if os.path.exists(out_path):
        with open(out_path) as f:
            for s in json.load(f):
                existing[s["id"]] = s

    results = []
    for i, s in enumerate(raw_sermons, 1):
        sid = s["id"]
        if sid in existing and existing[sid].get("_scrape_ok"):
            results.append(existing[sid])
            continue
        print(f"[{i}/{len(raw_sermons)}] scraping {s['slug']}", file=sys.stderr)
        try:
            featured_media_url = None
            if s.get("featured_media"):
                mr = SESSION.get(f"{BASE}/wp-json/wp/v2/media/{s['featured_media']}", timeout=30)
                if mr.status_code == 200:
                    featured_media_url = mr.json().get("source_url")
            s["_featured_media_url"] = featured_media_url
            page_data = scrape_sermon_page(s)
            record = {
                "id": sid,
                "slug": s["slug"],
                "title": strip_html(s["title"]["rendered"]),
                "date": s["date"],
                "link": s["link"],
                "excerpt": strip_html(s["excerpt"]["rendered"]),
                "categories": [categories.get(c, str(c)) for c in s.get("categories", [])],
                "tags": [tags.get(t, str(t)) for t in s.get("tags", [])],
                "transcript": page_data["transcript"],
                "youtube_id": page_data["youtube_id"],
                "pdf_guides": page_data["pdf_guides"],
                "thumbnail": page_data["thumbnail"],
                "_scrape_ok": True,
            }
        except Exception as e:
            print(f"  FAILED: {e}", file=sys.stderr)
            record = {
                "id": sid,
                "slug": s["slug"],
                "title": strip_html(s["title"]["rendered"]),
                "date": s["date"],
                "link": s["link"],
                "_scrape_ok": False,
                "_error": str(e),
            }
        results.append(record)
        # checkpoint every 20 so a long run can resume
        if i % 20 == 0:
            with open(out_path, "w") as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
        time.sleep(0.2)

    with open(out_path, "w") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    ok = sum(1 for r in results if r.get("_scrape_ok"))
    print(f"\nDone. {ok}/{len(results)} sermons scraped successfully.", file=sys.stderr)
    print(f"Output: {out_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
