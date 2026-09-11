# Design

<!-- impeccable:design-doc -->

## Direction: Pulpit Card Catalog

A sermon archive reads as a bound index/card catalog, not a media grid or marketing landing page. Built code-led (no image generation available this session), single committed direction — no multi-card tournament run given project scope (see PRODUCT.md).

## Palette (Restrained strategy)

- `--paper` / `--paper-raised`: stone/graphite neutrals (light) — the ground and raised card surface.
- `--ink` / `--ink-soft` / `--ink-faint`: three-step text hierarchy.
- `--oxblood` / `--oxblood-deep` / `--oxblood-tint`: single committed accent — series labels, links, primary button, active states.
- `--rule` / `--rule-strong`: hairline dividers for ruled catalog rows and the masthead's ledger-line background.
- Full light/dark pairs defined in `src/styles/global.css`; dark mode inverts to near-black ground with a brightened oxblood accent for contrast.

## Type

- IBM Plex Sans — reading prose, headings, nav.
- IBM Plex Mono — every catalog fact: dates, counts, series tags, badges (VIDEO / N GUIDES), scripture-style metadata. Reinforces "indexed record," not costume.
- Display size caps at ~3.2rem (masthead h1); body measure kept under ~68ch on the sermon transcript.

## Components

- **Masthead** (home): ruled-ledger background (repeating hairline gradient), index tag, stat line, two-column split (mission prose / recent-entries ledger).
- **Catalog row**: ruled list, not cards — date / title+series / badges grid, oxblood-tint hover.
- **Sermon detail**: series label, title, date, 16:9 YouTube embed (youtube-nocookie), study-guide download row (language-labeled from filename), full transcript in paragraphs.
- Search + series-select filter, client-side, sticky under the header on the catalog page.

## Source of truth for data

`data/sermons.json`, produced by `scripts/scrape_sermons.py` against theheritagechurch.org's `sermon` REST post type + per-page HTML (transcript/YouTube/PDF links aren't exposed via the API for this post type). Re-run the script to pick up new sermons; it checkpoints and skips already-scraped entries.

## Known data gaps (source-side, not a bug in this site)

- 13 sermons have no detectable YouTube link on their source page.
- 46 sermons have no PDF study guide.
- 5 sermons have a very short transcript (<200 chars) — likely a source page with a different layout.

These render conditionally (sections simply don't appear when data is missing) rather than showing broken placeholders.

## Disclosed process simplifications

- Skipped `impeccable`'s multi-card direction tournament (`concept-seed.mjs`) and comp-led visualization — no image-generation tool was available this session, and the project's real scope (498-item data pipeline + deploy) was the binding constraint. One direction was committed directly and confirmed with the user in one round.
- Finish review was self-conducted (desktop + mobile screenshots, live production spot-check, mechanical `detect.mjs` pass) rather than a spawned `impeccable-finish-reviewer` subagent, which was not available as an agent type in this session.
