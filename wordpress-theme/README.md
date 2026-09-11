# Mature Ministries — WordPress package (for Brian)

This is a self-contained WordPress theme + content import, built as an alternative to the Cloudflare Pages/Astro deployment, for hosting on Brian's own WordPress environment.

The theme does **not** depend on any specific sermon-manager plugin — it registers its own `mm_sermon` post type and `mm_series` taxonomy in `functions.php`, so it works alongside whatever other plugins are already installed.

## What's in this folder

- `mature-ministries/` — the theme (also packaged as `mature-ministries-theme.zip` for a one-click upload via WP Admin → Appearance → Themes → Add New → Upload Theme).
- `mature-ministries-import.xml` — a WordPress eXtended RSS (WXR) file with all 498 sermons (title, date, series, transcript, YouTube video ID, and links to the study guide PDFs), ready for WP's built-in importer.

## Install steps

1. **Upload and activate the theme.** WP Admin → Appearance → Themes → Add New → Upload Theme → choose `mature-ministries-theme.zip` → Install → Activate.

2. **Copy the sermon assets (PDF guides + thumbnails) onto the server.** From the main project repo, copy the `public/assets/` folder to:
   ```
   wp-content/uploads/mature-ministries-assets/
   ```
   so it contains `mature-ministries-assets/guides/*.pdf` and `mature-ministries-assets/thumbnails/*.jpg`. (This is ~1.7GB — copy it directly via SFTP/SSH/hosting file manager rather than through the WordPress admin uploader.) The import file's guide links point at this exact path.

3. **Import the sermons.** WP Admin → Tools → Import → WordPress → install/run the importer → upload `mature-ministries-import.xml`.
   - If the file (3.3MB) exceeds your host's upload limit, either raise `upload_max_filesize`/`post_max_size` in `php.ini`, or import via WP-CLI instead, which has no upload limit:
     ```sh
     wp import mature-ministries-import.xml --authors=create
     ```
   - When the importer asks about attachments, decline "Download and import file attachments" — the PDFs/thumbnails are handled by step 2, not by the importer.
   - Assign all content to whichever WordPress user account should be listed as the post author.

4. **Set the homepage.** WP Admin → Settings → Reading → "Your homepage displays" → set to use the theme's front page (the theme's `front-page.php` is used automatically once the theme is active and no other static front page is assigned).

5. **Permalinks.** WP Admin → Settings → Permalinks → click Save (no changes needed) to flush rewrite rules so `/sermons/` and `/sermons/<slug>/` resolve correctly.

## What you get vs. the Cloudflare/Astro version

Same design ("Pulpit Card Catalog" — see the main repo's `DESIGN.md`), same 498 sermons, same data (transcript, video, guides), same search/filter on the catalog page — rebuilt as PHP templates against WordPress's own post/taxonomy system instead of a static site, so it's editable through the normal WP Admin (Sermons menu item) going forward.

## Known data gaps (same as the other version — source-side, not an import bug)

- 5 sermons have no YouTube video: `hbc-kids-camp-2024`, `o-holy-night-christmas-eve-worship`, `the-just-shall-live-by-faith-romans-11-7`, and two "Hear What the Spirit Says unto the Churches" entries. See the main repo's `PRODUCT.md` for detail.
- 46 sermons have no PDF study guide.
- 5 sermons have a very short transcript.

## Updating content later

New sermons: re-run `scripts/scrape_sermons.py` in the main repo, re-run `scripts/generate_wxr.py`, then import the new/changed items the same way (WordPress's importer skips posts with a matching `post_name`/slug it already has, so re-importing is safe). Or just add sermons directly through WP Admin → Sermons → Add New, filling in the Series taxonomy and the `mm_youtube_id`/`mm_pdf_guides` custom fields.
