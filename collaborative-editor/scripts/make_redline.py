#!/usr/bin/env python3
"""
make_redline.py — produce a color-coded, track-changes style HTML comparison
of an original draft against the final edited version.

Use this for the "marked-up final" step of the collaborative-editor workflow,
so the writer can see every change at a glance instead of trusting a hand-marked
list. It does a word/phrase-level diff (not whole-paragraph) so a one-word swap
shows as a one-word change.

Usage:
    python3 make_redline.py ORIGINAL.txt FINAL.txt -o OUT.html [--title "My Piece"]

Both inputs are plain text or Markdown. Paragraph breaks (blank lines) are
preserved. The output HTML has three tabs: Redline, Clean final, Original.
Green = added/changed-to, struck red = removed.
"""
import argparse, difflib, html, re, sys


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read().strip()


def tokens(text):
    # keep paragraph breaks as their own token; otherwise split words + spaces
    return re.findall(r"\n\n+|\S+|[ \t]+|\n", text)


def esc(s):
    return html.escape(s).replace("\n\n", "</p><p>").replace("\n", " ")


def build(original, final, title):
    # normalize runs of spaces in the original so spacing tics don't show as diffs
    a = tokens(re.sub(r"[ \t]+", " ", original))
    b = tokens(final)
    sm = difflib.SequenceMatcher(a=a, b=b, autojunk=False)

    parts, ins, dele = [], 0, 0
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        at, bt = "".join(a[i1:i2]), "".join(b[j1:j2])
        if tag == "equal":
            parts.append(esc(at))
        elif tag == "delete":
            parts.append(f"<del>{esc(at)}</del>"); dele += 1
        elif tag == "insert":
            parts.append(f"<ins>{esc(bt)}</ins>"); ins += 1
        elif tag == "replace":
            parts.append(f"<del>{esc(at)}</del><ins>{esc(bt)}</ins>"); ins += 1; dele += 1

    redline = "<p>" + "".join(parts) + "</p>"
    final_html = "<p>" + esc(final) + "</p>"
    orig_html = "<p>" + esc(re.sub(r"[ \t]+", " ", original)) + "</p>"

    return f"""<!DOCTYPE html><html><head><meta charset="utf-8"><title>{html.escape(title)} — redline</title>
<style>
 body{{font:17px/1.7 Georgia,serif;max-width:820px;margin:0 auto;padding:32px;color:#1a1a1a;background:#fafaf8}}
 h1{{font:600 22px system-ui;margin:0 0 4px}} .sub{{font:14px system-ui;color:#666;margin-bottom:18px}}
 .legend{{font:14px system-ui;background:#fff;border:1px solid #e3e3df;border-radius:8px;padding:10px 14px;margin-bottom:22px}}
 .tabs{{display:flex;gap:8px;margin-bottom:16px}}
 .tabs button{{font:14px system-ui;padding:7px 14px;border:1px solid #d4d4cf;background:#fff;border-radius:6px;cursor:pointer}}
 .tabs button.active{{background:#1a1a1a;color:#fff;border-color:#1a1a1a}}
 .view{{display:none}} .view.active{{display:block}}
 p{{margin:0 0 14px}}
 ins{{background:#d8f0d8;color:#0a5a0a;text-decoration:none;border-radius:2px;padding:0 1px}}
 del{{background:#f7dcdc;color:#9a1c1c;text-decoration:line-through;border-radius:2px;padding:0 1px}}
</style></head><body>
<h1>{html.escape(title)} — marked-up final</h1>
<div class="sub">Original vs. final, with every change shown</div>
<div class="legend"><b>Legend:</b> <ins>green = added / changed-to</ins> &nbsp; <del>red = removed</del> &nbsp;·&nbsp; {ins} insertions/changes, {dele} deletions</div>
<div class="tabs">
 <button class="active" onclick="show('rl',this)">Redline</button>
 <button onclick="show('fin',this)">Clean final</button>
 <button onclick="show('orig',this)">Original</button>
</div>
<div id="rl" class="view active">{redline}</div>
<div id="fin" class="view">{final_html}</div>
<div id="orig" class="view">{orig_html}</div>
<script>function show(id,btn){{document.querySelectorAll('.view').forEach(v=>v.classList.remove('active'));document.getElementById(id).classList.add('active');document.querySelectorAll('.tabs button').forEach(b=>b.classList.remove('active'));btn.classList.add('active');}}</script>
</body></html>"""


def main():
    ap = argparse.ArgumentParser(description="Make a color-coded redline HTML comparison.")
    ap.add_argument("original", help="path to the original draft (txt/md)")
    ap.add_argument("final", help="path to the final edited version (txt/md)")
    ap.add_argument("-o", "--out", default="redline.html", help="output HTML path")
    ap.add_argument("--title", default="Draft", help="title shown in the header")
    args = ap.parse_args()

    page = build(read(args.original), read(args.final), args.title)
    with open(args.out, "w", encoding="utf-8") as f:
        f.write(page)
    print(f"Wrote redline to {args.out}")


if __name__ == "__main__":
    main()
