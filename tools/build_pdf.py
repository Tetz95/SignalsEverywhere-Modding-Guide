"""Builds the guide as one PDF: SignalsEverywhere-Modding-Guide.pdf in the repository root.

    python tools/build_pdf.py

Needs the `markdown` package (python -m pip install markdown) and Microsoft Edge, which prints the
combined HTML to PDF in headless mode. Links between pages become links inside the PDF.
"""
import datetime
import html
import os
import re
import subprocess
import sys

import markdown

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGES = ["README.md"] + sorted(f for f in os.listdir(ROOT) if re.match(r"\d\d-.*\.md$", f)) + ["reference.md"]
OUT_PDF = os.path.join(ROOT, "SignalsEverywhere-Modding-Guide.pdf")
OUT_HTML = os.path.join(ROOT, "tools", "guide.html")
EDGE = [r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"]

CSS = """
@page { size: Letter; margin: 0.75in 0.7in; }
body { font-family: "Segoe UI", Arial, sans-serif; font-size: 10.5pt; line-height: 1.45; color: #1d1d1f; }
h1 { font-size: 21pt; border-bottom: 2px solid #2f5d50; padding-bottom: 4px; color: #2f5d50; margin-top: 0; }
h2 { font-size: 14.5pt; color: #2f5d50; margin-top: 1.4em; break-after: avoid; }
h3 { font-size: 12pt; margin-top: 1.2em; break-after: avoid; }
section.chapter { break-before: page; }
a { color: #2f5d50; text-decoration: none; }
code { font-family: Consolas, "Cascadia Mono", monospace; font-size: 9pt; background: #f1f3f2; padding: 0 2px; border-radius: 2px; }
pre { background: #f1f3f2; border-left: 3px solid #2f5d50; padding: 8px 10px; white-space: pre-wrap; word-break: break-word; }
pre code { background: none; padding: 0; font-size: 8.5pt; }
table { border-collapse: collapse; margin: 0.6em 0; font-size: 9pt; width: 100%; break-inside: auto; }
tr { break-inside: avoid; }
th, td { border: 1px solid #c9d1ce; padding: 4px 6px; vertical-align: top; text-align: left; }
th { background: #e4ebe8; }
td code { white-space: nowrap; }
p, li { orphans: 3; widows: 3; }
blockquote { border-left: 3px solid #c9d1ce; margin-left: 0; padding-left: 10px; color: #444; }
.title { break-after: page; text-align: center; padding-top: 2.4in; }
.title h1 { border: none; font-size: 30pt; }
.title p { font-size: 12pt; color: #444; }
"""


def slug(text):
    """GitHub-style heading anchor."""
    text = re.sub(r"<[^>]+>", "", html.unescape(text)).strip().lower()
    text = re.sub(r"[^\w\- ]", "", text)
    return text.replace(" ", "-")


def page_id(name):
    return os.path.splitext(name)[0].lower()


def convert(name):
    with open(os.path.join(ROOT, name), encoding="utf-8") as f:
        text = f.read()
    body = markdown.markdown(text, extensions=["tables", "fenced_code", "sane_lists"])
    pid = page_id(name)

    # Unique anchors across the whole document: <page>--<heading>.
    def heading(m):
        return f'<h{m.group(1)} id="{pid}--{slug(m.group(2))}">{m.group(2)}</h{m.group(1)}>'
    body = re.sub(r"<h([1-6])>(.*?)</h\1>", heading, body)

    # Links to other pages (and their headings) point inside the document.
    def link(m):
        target, anchor = m.group(1), m.group(2)
        if target and not target.endswith(".md"):
            return m.group(0)
        dest = page_id(target) if target else pid
        return f'href="#{dest}--{anchor}"' if anchor else f'href="#{dest}"'
    body = re.sub(r'href="([^"#:]*)(?:#([^"]*))?"', link, body)
    return f'<section class="chapter" id="{pid}">{body}</section>'


def main():
    # README opens the PDF as the introduction; its contents list links to every chapter.
    chapters = [convert(p) for p in PAGES]
    chapters[0] = chapters[0].replace('>SignalsEverywhere Modding Guide</h1>', '>Introduction</h1>', 1)
    today = datetime.date.today().strftime("%B %Y")
    doc = f"""<!doctype html><html><head><meta charset="utf-8"><title>SignalsEverywhere Modding Guide</title>
<style>{CSS}</style></head><body>
<div class="title"><h1>SignalsEverywhere Modding Guide</h1>
<p>Adding and changing signals in Railroader</p><p>Tetz95 &middot; {today} &middot; SignalsEverywhere 1.4</p></div>
{''.join(chapters)}</body></html>"""
    with open(OUT_HTML, "w", encoding="utf-8") as f:
        f.write(doc)

    edge = next((e for e in EDGE if os.path.exists(e)), None)
    if not edge:
        sys.exit("Microsoft Edge not found")
    subprocess.run([edge, "--headless", "--disable-gpu", "--no-pdf-header-footer",
                    f"--print-to-pdf={OUT_PDF}", "file:///" + OUT_HTML.replace("\\", "/")],
                   check=True, capture_output=True, timeout=120)
    print(f"wrote {OUT_PDF} ({os.path.getsize(OUT_PDF) // 1024} KB)")


if __name__ == "__main__":
    main()
