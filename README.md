# Collaborative Editor — a Claude skill

**Edits *with* you, not *for* you.** A multi-pass editing workflow that sharpens your writing —
the argument, the structure, the sentences — without sanding off your voice. It works like a real
editor who shows up *after* the ideas are down: it flags problem spots and hands you concrete
choices, so every change is yours and the finished piece still reads like a person wrote it, not
like AI slop.

> The single worst outcome is a draft that reads like everyone else's.

## What it does

- **Four passes, in order** — structure → grammar → wording → a final coherence sweep. Big things
  before small ones, so you never polish a sentence that later gets cut.
- **Offers, never imposes** — every flag comes with real options (including "leave it as-is"),
  surfaced as clickable choices when the tool supports it.
- **Protects the voice** — your long winding sentences, stacked parentheticals, and blunt words are
  treated as voice, not clutter. It also refuses the machine-edit tics (forced em-dashes, metronomic
  cadence, generic synonyms).
- **Standard craft lenses** — it knows what good editors look for: find the real opening, stakes,
  concreteness, strong verbs, dead clichés, old-to-new sentence flow, and more — each raised as an
  option, never a mandate.
- **A marked-up final** — closes with a redline you can review: Word `.docx` with real tracked
  changes (also imports into Pages and Google Docs), plus portable HTML/PDF visual redlines.

## Install

### Claude Code

```bash
git clone https://github.com/jsky-dev/collaborative-editor.git
cp -R collaborative-editor/collaborative-editor ~/.claude/skills/
```

Or symlink it so edits stay live:

```bash
ln -s "$(pwd)/collaborative-editor/collaborative-editor" ~/.claude/skills/collaborative-editor
```

### Claude Cowork

Download [`collaborative-editor.skill`](./collaborative-editor.skill) and add it via
**Settings → Capabilities**.

## Use it

Just ask, in either environment:

> "Be my collaborative editor on this draft."

or "workshop this draft," "edit but keep my voice," "give me options, don't just rewrite it."

## What's in here

| Path | What it is |
|------|------------|
| [`collaborative-editor/SKILL.md`](./collaborative-editor/SKILL.md) | The skill itself — the full workflow and rules |
| [`collaborative-editor/scripts/make_tracked_docx.py`](./collaborative-editor/scripts/make_tracked_docx.py) | Builds a Word `.docx` with native tracked changes from original + final |
| [`collaborative-editor/scripts/make_redline.py`](./collaborative-editor/scripts/make_redline.py) | Builds a portable HTML visual redline |
| [`collaborative-editor.skill`](./collaborative-editor.skill) | Packaged skill for Claude Cowork |
| [`collaborative-editor-deck.html`](./collaborative-editor-deck.html) | A slide deck explaining the skill |

## License

MIT — see [LICENSE](./LICENSE).

---

Built by [joshbecker.md](https://www.joshbecker.md). Sharpen the writing, keep the voice.
