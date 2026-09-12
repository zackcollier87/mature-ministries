#!/usr/bin/env python3
"""Generate a WordPress eXtended RSS (WXR) file from data/sermons.json.

Brian imports this via WP Admin -> Tools -> Import -> WordPress, after
activating the bundled "Mature Ministries" theme (which registers the
mm_sermon post type + mm_series taxonomy this file targets). PDF guides and
thumbnails are NOT embedded as WordPress attachments (that would try to
push ~1.7GB through the importer) -- instead they're referenced by a
relative path under wp-content/uploads/mature-ministries-assets/, and the
README tells Brian to copy the public/assets/ folder there directly.
"""
import json
import os
import re
import sys
from datetime import datetime, timezone
from xml.sax.saxutils import escape

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "sermons.json")
OUT_PATH = os.path.join(os.path.dirname(__file__), "..", "wordpress-theme", "mature-ministries-import.xml")
ASSET_BASE = "/wp-content/uploads/mature-ministries-assets"
SITE_URL = "https://example.com"  # Brian's real URL after import; WP rewrites internal links on import.


def cdata(s: str) -> str:
    s = s or ""
    s = s.replace("]]>", "]]]]><![CDATA[>")
    return f"<![CDATA[{s}]]>"


def php_serialize(value):
    """Minimal PHP serialize() for the shapes we actually emit (list of dicts of strings)."""
    if isinstance(value, str):
        b = value.encode("utf-8")
        return f's:{len(b)}:"{value}";'
    if isinstance(value, int):
        return f"i:{value};"
    if isinstance(value, list):
        parts = "".join(f"i:{i};{php_serialize(v)}" for i, v in enumerate(value))
        return f"a:{len(value)}:{{{parts}}}"
    if isinstance(value, dict):
        parts = "".join(f"{php_serialize(k)}{php_serialize(v)}" for k, v in value.items())
        return f"a:{len(value)}:{{{parts}}}"
    raise TypeError(type(value))


def slugify_fallback(title: str) -> str:
    s = title.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s or "sermon"


def main():
    with open(DATA_PATH) as f:
        sermons = [s for s in json.load(f) if s.get("_scrape_ok")]

    sermons.sort(key=lambda s: s["date"])

    series_names = []
    seen = set()
    for s in sermons:
        for c in s.get("categories", []):
            if c not in seen:
                seen.add(c)
                series_names.append(c)

    now = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S +0000")

    terms_xml = []
    term_id_by_name = {}
    for i, name in enumerate(series_names, start=1):
        term_id_by_name[name] = i
        slug = slugify_fallback(name)
        terms_xml.append(f"""	<wp:term>
		<wp:term_id>{i}</wp:term_id>
		<wp:term_taxonomy>mm_series</wp:term_taxonomy>
		<wp:term_slug>{escape(slug)}</wp:term_slug>
		<wp:term_name>{cdata(name)}</wp:term_name>
	</wp:term>""")

    items_xml = []
    for i, s in enumerate(sermons, start=1):
        post_id = 1000 + i
        dt = datetime.fromisoformat(s["date"])
        post_date = dt.strftime("%Y-%m-%d %H:%M:%S")
        post_date_gmt = dt.strftime("%Y-%m-%d %H:%M:%S")
        pub_date = dt.strftime("%a, %d %b %Y %H:%M:%S +0000")
        slug = s["slug"]
        title = s["title"]
        link = f"{SITE_URL}/sermons/{slug}/"

        paragraphs = [p for p in (s.get("transcript") or "").split("\n\n") if p.strip()]
        content_html = "\n\n".join(f"<p>{escape(p)}</p>" for p in paragraphs)

        guides = []
        for g in s.get("pdf_guides", []):
            local_path = g.get("local_path") or ""
            filename = os.path.basename(local_path) if local_path else os.path.basename(g.get("source_url", ""))
            guides.append({
                "label": g.get("label", "Sermon Guide"),
                "url": f"{ASSET_BASE}/guides/{filename}" if filename else g.get("source_url", ""),
            })

        categories_xml = ""
        for c in s.get("categories", []):
            term_slug = slugify_fallback(c)
            categories_xml += f'\t\t<category domain="mm_series" nicename="{escape(term_slug)}">{cdata(c)}</category>\n'

        postmeta = [
            ("mm_youtube_id", s.get("youtube_id") or ""),
            ("mm_sermon_date", s["date"]),
            ("mm_source_link", s.get("link") or ""),
            ("mm_audio_url", s.get("audio_url") or ""),
        ]
        if guides:
            postmeta.append(("mm_pdf_guides", php_serialize(guides)))

        postmeta_xml = ""
        for key, val in postmeta:
            postmeta_xml += f"""		<wp:postmeta>
			<wp:meta_key>{escape(key)}</wp:meta_key>
			<wp:meta_value>{cdata(val)}</wp:meta_value>
		</wp:postmeta>\n"""

        items_xml.append(f"""	<item>
		<title>{cdata(title)}</title>
		<link>{escape(link)}</link>
		<pubDate>{pub_date}</pubDate>
		<dc:creator>{cdata("admin")}</dc:creator>
		<guid isPermaLink="false">{escape(link)}</guid>
		<description></description>
		<content:encoded>{cdata(content_html)}</content:encoded>
		<excerpt:encoded>{cdata(s.get("excerpt", ""))}</excerpt:encoded>
		<wp:post_id>{post_id}</wp:post_id>
		<wp:post_date>{post_date}</wp:post_date>
		<wp:post_date_gmt>{post_date_gmt}</wp:post_date_gmt>
		<wp:comment_status>closed</wp:comment_status>
		<wp:ping_status>closed</wp:ping_status>
		<wp:post_name>{escape(slug)}</wp:post_name>
		<wp:status>publish</wp:status>
		<wp:post_parent>0</wp:post_parent>
		<wp:menu_order>0</wp:menu_order>
		<wp:post_type>mm_sermon</wp:post_type>
		<wp:post_password></wp:post_password>
		<wp:is_sticky>0</wp:is_sticky>
{categories_xml}{postmeta_xml}	</item>""")

    xml = f"""<?xml version="1.0" encoding="UTF-8" ?>
<rss version="2.0"
	xmlns:excerpt="http://wordpress.org/export/1.2/excerpt/"
	xmlns:content="http://purl.org/rss/1.0/modules/content/"
	xmlns:wfw="http://wellformedweb.org/CommentAPI/"
	xmlns:dc="http://purl.org/dc/elements/1.1/"
	xmlns:wp="http://wordpress.org/export/1.2/"
>
<channel>
	<title>Mature Ministries</title>
	<link>{SITE_URL}</link>
	<description>Sermon archive import</description>
	<pubDate>{now}</pubDate>
	<language>en-US</language>
	<wp:wxr_version>1.2</wp:wxr_version>
	<wp:base_site_url>{SITE_URL}</wp:base_site_url>
	<wp:base_blog_url>{SITE_URL}</wp:base_blog_url>
	<wp:author>
		<wp:author_id>1</wp:author_id>
		<wp:author_login>{cdata("admin")}</wp:author_login>
		<wp:author_email>{cdata("admin@example.com")}</wp:author_email>
		<wp:author_display_name>{cdata("Pastor Wayne Edwards")}</wp:author_display_name>
	</wp:author>
{chr(10).join(terms_xml)}
{chr(10).join(items_xml)}
</channel>
</rss>
"""

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        f.write(xml)

    print(f"Wrote {len(sermons)} sermons, {len(series_names)} series to {OUT_PATH}", file=sys.stderr)


if __name__ == "__main__":
    main()
