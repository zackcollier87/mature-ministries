#!/usr/bin/env python3
"""Extract standalone audio for every sermon that has a YouTube video, upload
each MP3 to the mature-ministries-audio R2 bucket, and record the public URL
back into data/sermons.json as "audio_url".

Resumable: skips any sermon that already has an audio_url. Uses a temp dir
so nothing large is left on local disk after each upload.
"""
import json
import os
import subprocess
import sys
import tempfile

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "sermons.json")
BUCKET = "mature-ministries-audio"
PUBLIC_BASE = "https://pub-6957d3edb3084771b8f9ccebf3df45bc.r2.dev"
ACCOUNT_ID = "acd8afead736016370920aafcb8a6009"


def run(cmd, **kwargs):
    return subprocess.run(cmd, capture_output=True, text=True, **kwargs)


def main():
    with open(DATA_PATH) as f:
        sermons = json.load(f)

    targets = [s for s in sermons if s.get("_scrape_ok") and s.get("youtube_id") and not s.get("audio_url")]
    print(f"{len(targets)} sermons need audio extraction", file=sys.stderr)

    env = dict(os.environ)
    env["CLOUDFLARE_ACCOUNT_ID"] = ACCOUNT_ID

    done = 0
    failed = []
    for i, s in enumerate(targets, 1):
        slug = s["slug"]
        yt = s["youtube_id"]
        print(f"[{i}/{len(targets)}] {slug} ({yt})", file=sys.stderr)

        with tempfile.TemporaryDirectory() as tmp:
            out_template = os.path.join(tmp, "audio.%(ext)s")
            dl = run([
                sys.executable, "-m", "yt_dlp",
                "-x", "--audio-format", "mp3",
                "--postprocessor-args", "ffmpeg:-b:a 48k -ac 1",
                "-o", out_template,
                f"https://www.youtube.com/watch?v={yt}",
            ], timeout=600)

            mp3_path = os.path.join(tmp, "audio.mp3")
            if dl.returncode != 0 or not os.path.exists(mp3_path):
                print(f"  DOWNLOAD FAILED: {dl.stderr[-500:]}", file=sys.stderr)
                failed.append(slug)
                continue

            key = f"{slug}.mp3"
            up = run([
                "wrangler", "r2", "object", "put", f"{BUCKET}/{key}",
                f"--file={mp3_path}", "--content-type=audio/mpeg", "--remote",
            ], env=env, timeout=300)

            if up.returncode != 0:
                print(f"  UPLOAD FAILED: {up.stderr[-500:]}", file=sys.stderr)
                failed.append(slug)
                continue

            s["audio_url"] = f"{PUBLIC_BASE}/{key}"
            done += 1

        if i % 10 == 0:
            with open(DATA_PATH, "w") as f:
                json.dump(sermons, f, indent=2, ensure_ascii=False)
            print(f"  checkpoint saved ({done} done, {len(failed)} failed)", file=sys.stderr)

    with open(DATA_PATH, "w") as f:
        json.dump(sermons, f, indent=2, ensure_ascii=False)

    print(f"\nDone. {done} succeeded, {len(failed)} failed.", file=sys.stderr)
    if failed:
        print("Failed slugs:", file=sys.stderr)
        for s in failed:
            print(f"  - {s}", file=sys.stderr)


if __name__ == "__main__":
    main()
