"""Tag kite-school links in each guide page's 'Lessons' section with
data-track="school", and inject click-tracking.js on every guide page.
Idempotent — safe to re-run after regenerating/editing guide pages."""
import os
import re

GUIDE_DIR = os.path.join(os.path.dirname(__file__), "kitesurf_app", "web", "guide")

LESSONS_SECTION_RE = re.compile(r"(<h2>Lessons</h2>)(.*?)(?=<h2>|$)", re.DOTALL)
ANCHOR_RE = re.compile(r'<a\s+href="(https?://[^"]+)"([^>]*)>')

SCRIPT_TAG = '<script src="/guide/click-tracking.js"></script>\n'

files = sorted(f for f in os.listdir(GUIDE_DIR) if f.endswith(".html"))

tagged_links = 0
tagged_pages = 0
scripts_added = 0
scripts_skipped = 0

for filename in files:
    path = os.path.join(GUIDE_DIR, filename)
    with open(path, "r", encoding="utf-8") as fh:
        html = fh.read()

    original = html

    # 1. Tag external anchors inside the Lessons section
    def tag_section(m):
        heading, body = m.group(1), m.group(2)

        def tag_anchor(am):
            url, attrs = am.group(1), am.group(2)
            if "data-track=" in attrs:
                return am.group(0)  # already tagged
            global tagged_links
            tagged_links += 1
            return '<a href="{0}" data-track="school"{1}>'.format(url, attrs)

        new_body = ANCHOR_RE.sub(tag_anchor, body)
        return heading + new_body

    before = html
    html = LESSONS_SECTION_RE.sub(tag_section, html, count=1)
    if html != before:
        tagged_pages += 1

    # 2. Inject click-tracking.js before </body>, once
    if "click-tracking.js" in html:
        scripts_skipped += 1
    elif "</body>" in html:
        html = html.replace("</body>", SCRIPT_TAG + "</body>", 1)
        scripts_added += 1
    else:
        print(f"  WARN (no </body> found): {filename}")

    if html != original:
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(html)
        print(f"  OK: {filename}")
    else:
        print(f"  SKIP (no change): {filename}")

print(f"\nDone: {tagged_links} school link(s) tagged across {tagged_pages} page(s); "
      f"{scripts_added} script tag(s) added, {scripts_skipped} already present.")
