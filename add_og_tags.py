"""Add Open Graph / Twitter Card tags to all guide pages, matching each page's
existing title/description/canonical. Idempotent — skips files that already
have og:title."""
import os
import re

GUIDE_DIR = os.path.join(os.path.dirname(__file__), "kitesurf_app", "web", "guide")
SITE = "https://southwestkitesurf.co.uk"
OG_IMAGE = f"{SITE}/icons/Icon-512.png"
SITE_NAME = "South West Kitesurf"

TITLE_RE = re.compile(r"<title>(.*?)</title>", re.DOTALL)
DESC_RE = re.compile(r'<meta name="description" content="(.*?)">', re.DOTALL)
CANONICAL_RE = re.compile(r'<link rel="canonical" href="(.*?)">')

files = sorted(f for f in os.listdir(GUIDE_DIR) if f.endswith(".html"))

updated = 0
skipped = 0

for filename in files:
    path = os.path.join(GUIDE_DIR, filename)
    with open(path, "r", encoding="utf-8") as fh:
        html = fh.read()

    if "og:title" in html:
        print(f"  SKIP (already has OG tags): {filename}")
        skipped += 1
        continue

    title_m = TITLE_RE.search(html)
    desc_m = DESC_RE.search(html)
    canonical_m = CANONICAL_RE.search(html)

    if not title_m or not desc_m or not canonical_m:
        print(f"  WARN (missing title/description/canonical): {filename}")
        skipped += 1
        continue

    title = title_m.group(1)
    description = desc_m.group(1)
    url = canonical_m.group(1)

    og_block = (
        f'    <meta property="og:type" content="website">\n'
        f'    <meta property="og:site_name" content="{SITE_NAME}">\n'
        f'    <meta property="og:title" content="{title}">\n'
        f'    <meta property="og:description" content="{description}">\n'
        f'    <meta property="og:image" content="{OG_IMAGE}">\n'
        f'    <meta property="og:url" content="{url}">\n'
        f'    <meta name="twitter:card" content="summary_large_image">\n'
        f'    <meta name="twitter:title" content="{title}">\n'
        f'    <meta name="twitter:description" content="{description}">\n'
        f'    <meta name="twitter:image" content="{OG_IMAGE}">\n'
    )

    # Insert right after the canonical link tag
    canonical_line = canonical_m.group(0)
    new_html = html.replace(canonical_line, canonical_line + "\n" + og_block, 1)

    with open(path, "w", encoding="utf-8") as fh:
        fh.write(new_html)

    print(f"  OK: {filename}")
    updated += 1

print(f"\nDone: {updated} updated, {skipped} skipped.")
