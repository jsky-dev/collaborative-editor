#!/usr/bin/env python3
"""
make_tracked_docx.py — turn an original draft + final version into a Word .docx
with NATIVE tracked changes (real insertions/deletions you can Accept or Reject
in Word).

This is the keystone "marked-up final" format for the collaborative-editor
workflow. The same .docx also carries its edits into Apple Pages (shown as
change-tracking) and Google Docs (converted to Suggestions when you open/import
it), so one file covers all three editors.

Usage:
    python3 make_tracked_docx.py ORIGINAL.txt FINAL.txt -o OUT.docx \
        [--title "Piece title"] [--author "Editor"]

Inputs are plain text or Markdown (blank line = paragraph break). The diff is at
the word/phrase level, so a one-word change shows as a one-word tracked change.
Validate the result with the docx skill's scripts/office/validate.py, and convert
to a visual-redline PDF with scripts/office/soffice.py --convert-to pdf.
"""
import argparse, difflib, html, re, zipfile, datetime


def read(p):
    with open(p, encoding="utf-8") as f:
        return f.read().strip()


def tokens(text):
    return re.findall(r"\n\n+|\S+|[ \t]+|\n", text)


def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


CT = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
<Default Extension="xml" ContentType="application/xml"/>
<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
<Override PartName="/word/settings.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.settings+xml"/>
</Types>'''

RELS = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>'''

DOC_RELS = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/settings" Target="settings.xml"/>
</Relationships>'''

# track changes on, so Word opens showing the markup
SETTINGS = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:settings xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
<w:trackRevisions/>
</w:settings>'''

W_NS = 'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"'


def run_plain(t):
    return f'<w:r><w:t xml:space="preserve">{esc(t)}</w:t></w:r>'


def run_ins(t, i, author, date):
    return (f'<w:ins w:id="{i}" w:author="{esc(author)}" w:date="{date}">'
            f'<w:r><w:t xml:space="preserve">{esc(t)}</w:t></w:r></w:ins>')


def run_del(t, i, author, date):
    return (f'<w:del w:id="{i}" w:author="{esc(author)}" w:date="{date}">'
            f'<w:r><w:delText xml:space="preserve">{esc(t)}</w:delText></w:r></w:del>')


def build_document(original, final, title, author):
    date = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    a = tokens(re.sub(r"[ \t]+", " ", original))
    b = tokens(final)
    sm = difflib.SequenceMatcher(a=a, b=b, autojunk=False)

    # flat list of (tag, text)
    segs = []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        at, bt = "".join(a[i1:i2]), "".join(b[j1:j2])
        if tag == "equal":
            segs.append(("eq", at))
        elif tag == "delete":
            segs.append(("del", at))
        elif tag == "insert":
            segs.append(("ins", bt))
        elif tag == "replace":
            segs.append(("del", at)); segs.append(("ins", bt))

    # build paragraphs, splitting any segment on paragraph breaks
    paras, cur = [], []
    wid = [1]

    def emit(tag, text):
        if text == "":
            return
        if tag == "eq":
            cur.append(run_plain(text))
        elif tag == "ins":
            cur.append(run_ins(text, wid[0], author, date)); wid[0] += 1
        elif tag == "del":
            cur.append(run_del(text, wid[0], author, date)); wid[0] += 1

    for tag, text in segs:
        pieces = re.split(r"\n\n+", text)
        for k, piece in enumerate(pieces):
            if k > 0:
                paras.append("".join(cur)); cur.clear()
            piece = piece.replace("\n", " ")
            emit(tag, piece)
    if cur:
        paras.append("".join(cur))

    body = []
    if title:
        body.append(f'<w:p><w:pPr><w:rPr><w:b/><w:sz w:val="32"/></w:rPr></w:pPr>'
                    f'<w:r><w:rPr><w:b/><w:sz w:val="32"/></w:rPr>'
                    f'<w:t xml:space="preserve">{esc(title)}</w:t></w:r></w:p>')
    for p in paras:
        body.append(f"<w:p>{p}</w:p>")
    body.append('<w:sectPr><w:pgSz w:w="12240" w:h="15840"/>'
                '<w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440" '
                'w:header="720" w:footer="720" w:gutter="0"/></w:sectPr>')

    return (f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
            f'<w:document {W_NS}><w:body>{"".join(body)}</w:body></w:document>')


def main():
    ap = argparse.ArgumentParser(description="Make a .docx with native tracked changes.")
    ap.add_argument("original")
    ap.add_argument("final")
    ap.add_argument("-o", "--out", default="tracked.docx")
    ap.add_argument("--title", default="")
    ap.add_argument("--author", default="Editor")
    args = ap.parse_args()

    doc_xml = build_document(read(args.original), read(args.final), args.title, args.author)
    with zipfile.ZipFile(args.out, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", CT)
        z.writestr("_rels/.rels", RELS)
        z.writestr("word/_rels/document.xml.rels", DOC_RELS)
        z.writestr("word/settings.xml", SETTINGS)
        z.writestr("word/document.xml", doc_xml)
    print(f"Wrote tracked-changes docx to {args.out}")


if __name__ == "__main__":
    main()
