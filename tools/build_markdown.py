"""Builds the guide as one Markdown file: SignalsEverywhere-Modding-Guide.md in the repository root.

    python tools/build_markdown.py

Pages are joined in order (README first, as the introduction). Links between pages become links to
headings in the combined file, using GitHub's heading anchors (with -1, -2 … for repeated headings).
"""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGES = ["README.md"] + sorted(f for f in os.listdir(ROOT) if re.match(r"\d\d-.*\.md$", f)) + ["reference.md"]
OUT = os.path.join(ROOT, "SignalsEverywhere-Modding-Guide.md")
HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*$")
FENCE = re.compile(r"^\s*```")


def github_slug(text):
    text = re.sub(r"`|\*\*|\*|_(?=\w)|(?<=\w)_", "", text)  # inline markup isn't part of the anchor
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text).strip().lower()
    text = re.sub(r"[^\w\- ]", "", text)
    return text.replace(" ", "-")


def read(name):
    with open(os.path.join(ROOT, name), encoding="utf-8") as f:
        return f.read().splitlines()


def main():
    pages = {p: read(p) for p in PAGES}
    pages["README.md"][0] = "# SignalsEverywhere Modding Guide"

    # Assign anchors in document order, exactly as GitHub would for the combined file.
    used = {}
    anchors = {}  # (page, page-local slug) -> combined-file anchor
    first = {}    # page -> anchor of its first heading
    for p in PAGES:
        in_code = False
        for line in pages[p]:
            if FENCE.match(line):
                in_code = not in_code
                continue
            m = None if in_code else HEADING.match(line)
            if not m:
                continue
            base = github_slug(m.group(2))
            n = used.get(base, 0)
            used[base] = n + 1
            anchor = base if n == 0 else f"{base}-{n}"
            anchors.setdefault((p, base), anchor)
            first.setdefault(p, anchor)

    def relink(page, text):
        def fix(m):
            label, target, frag = m.group(1), m.group(2), m.group(3)
            if target and not target.endswith(".md"):
                return m.group(0)
            dest = target or page
            if dest not in pages:
                return m.group(0)
            anchor = anchors.get((dest, frag)) if frag else first[dest]
            if anchor is None:
                raise SystemExit(f"{page}: no heading '{frag}' in {dest}")
            return f"[{label}](#{anchor})"
        return re.sub(r"\[([^\]]+)\]\(([^)#:]*)(?:#([^)]*))?\)", fix, text)

    parts = []
    for p in PAGES:
        out, in_code = [], False
        for line in pages[p]:
            if FENCE.match(line):
                in_code = not in_code
            out.append(line if in_code else relink(p, line))
        parts.append("\n".join(out).strip())

    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n\n---\n\n".join(parts) + "\n")
    print(f"wrote {OUT} ({os.path.getsize(OUT) // 1024} KB)")


if __name__ == "__main__":
    main()
