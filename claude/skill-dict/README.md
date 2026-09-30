# `/skill-dict` — personal catalog of installed Claude Code skills

> One markdown file per skill (or parent plugin). Hand-curated. Read-only most of the time. Saves you ~4000 tokens every time you ask "what skills do I have?"

## What

`/skill-dict` manages a catalog of every Claude Code skill you've installed or authored, stored as markdown files in a configurable library directory (default `~/skills-library/`). One file per **parent unit** — a plugin or a top-level user-authored skill. Sub-skills inside a plugin (e.g. `superpowers:brainstorming`) live inside the parent's entry, not as separate files.

The catalog is also queryable from VSCode — open the folder in your editor and the files are right there, no Claude Code session needed.

## Subcommands

| Subcommand | What it does |
|---|---|
| `list` | Prints the contents of `INDEX.md` — a single scannable markdown table. That's it. No other files read. |
| `show <name>` | Prints one entry's file. Glob match if you use a partial name. |
| `sync` | Reconciles the library against `~/.claude/plugins/installed_plugins.json` and `~/.claude/skills/`. Adds entries for newly-installed plugins, flags possibly-retired entries. Idempotent. |
| `add <name>` | Interactive guided add for skills you authored from scratch (vs. installed via plugin). Asks 5–7 questions, then writes a stub. |
| `check-updates` | Read-only audit comparing installed plugin versions to upstream sources. Prints a status table. Never auto-upgrades. |

Detailed algorithms for `sync`, `check-updates`, and `add` live in [references/](references/) so the main `SKILL.md` stays scannable.

## Benefits — context savings

Asking Claude "what skills do I have installed?" without `/skill-dict` dumps every skill's full description into the chat — typically 4000+ tokens of context overhead.

Asking with `/skill-dict list` returns a single markdown table — ~500 tokens. **About 8× cheaper, every time.**

For per-skill detail, `/skill-dict show <name>` reads exactly one file. The catalog never accidentally loads the whole library.

## How it pairs with VSCode

The library lives as plain markdown at `~/skills-library/`:

```
skills-library/
├── README.md          ← overview and entry template
├── INDEX.md           ← the scannable table that `list` prints
├── plugins/           ← installed from marketplaces or npm
│   └── *.md
└── authored/          ← your own skills
    └── *.md
```

You curate it by editing files in VSCode (no Claude session burning context). The slash command is just the read/sync surface from inside Claude Code.

## Best practices

- **Run `/skill-dict sync` after installing a new plugin.** It scans `installed_plugins.json` and adds stub entries for anything not yet in the library. Existing entries are left alone — your hand-edits win.
- **Use `show <name>` for one entry, not `list`.** `list` is the index; `show` is the detail. The index is short by design.
- **Run `check-updates` monthly.** It changes nothing installed and tells you which plugins have newer versions upstream. You decide whether to upgrade.
- **Don't auto-fill the "Where I use it" / "Why I kept it" sections** when running `sync` — those are personal notes. The skill leaves them as `_(fill in)_` stubs so you write them in VSCode at your own pace.

## Why this is better than alternatives

| Alternative | Problem | How `/skill-dict` solves it |
|---|---|---|
| Apple Note / Notion of installed skills | Not surfaceable to Claude; goes stale; lives in a different app | Markdown files in `~/skills-library/`; Claude reads on demand; you edit in VSCode |
| Memorize what's installed | Doesn't scale beyond ~5 skills | Index + detail + sync handle 20+ entries comfortably |
| `ls ~/.claude/plugins/` + Claude's auto-load | Bare names, no metadata, dumps everything into context | Curated entries with descriptions; `list` returns one table |
| Plugin manifest direct read | JSON; not friendly; no notes | Markdown with your own context per entry |

## Configuration

The skill assumes `~/skills-library/` by default. To use a different path, edit `~/.claude/skills/skill-dict/SKILL.md` and `~/.claude/skills/skill-dict/references/*.md` — search-and-replace `~/skills-library/` for your preferred location. (The library path appears in a handful of places; ~5 minutes of editing.)

To bootstrap an empty library, just `mkdir -p ~/skills-library/{plugins,authored}` and write a starter `INDEX.md` with the header row of your choice. Then run `/skill-dict sync` to populate from your installed plugins.

## Eval result

Trigger-accuracy benchmark: 100% precision and 100% recall on a 20-query test set. The description's enumerated trigger phrases (`/skill-dict`, "skills library", "what does <skill> do") cleanly distinguish from unrelated dictionary/library queries. See [eval-results.md](../../eval-results.md) for full methodology.

## Install

See the root [INSTALL.md](../../INSTALL.md). Quick version:

```bash
mkdir -p ~/.claude/skills
cp -r charles-agent-skills/claude/skill-dict ~/.claude/skills/
mkdir -p ~/skills-library/{plugins,authored}
```

Then close your Claude Code window and open a fresh one, and run `/skill-dict sync` to seed the library from your installed plugins.
