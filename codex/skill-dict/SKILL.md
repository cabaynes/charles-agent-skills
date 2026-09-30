---
name: skill-dict
description: Use when the user types `$skill-dict`, asks about their personal skill library at ~/skills-library/, asks "what does <skill> do" about a library entry, asks to sync the library after installing a Codex plugin or skill, or asks to add a skill to the library.
---

> **Codex version.** Invoke with `$skill-dict` followed by a subcommand:
> `$skill-dict list`, `$skill-dict show <name>`, `$skill-dict sync`, `$skill-dict add <name>`,
> `$skill-dict check-updates`. The argument is plain text after the skill name — read it from the
> user's message. Paths below use `$CODEX_DIR`, meaning `${CODEX_HOME:-$HOME/.codex}`.
>
> **One library, two platforms.** The same `~/skills-library/` can also be maintained by the Claude
> version of this skill. Every entry this version writes carries `platform: codex` in its frontmatter,
> is saved as `<name>.codex.md` (so a Codex `pdf` plugin never overwrites a Claude `pdf` entry), and
> shows as `<name> (codex)` in `INDEX.md`. Entries without a `platform:` field belong to Claude —
> list and show them, but never sync, retire, or update-check them from here.

# $skill-dict — Personal skill library at `~/skills-library/`

You maintain a hand-curated catalog of every Codex skill and plugin you've installed or authored (and, if you also use Claude, its skills too — see the note above). One markdown file per **parent unit** (a plugin or top-level user-authored skill). Sub-skills inside a plugin live inside the parent's entry, not as separate files.

**Library root:** `~/skills-library/`

```
skills-library/
├── README.md          ← overview, conventions, entry template
├── INDEX.md           ← scannable table of all entries
├── plugins/           ← installed from marketplaces or npm
│   └── *.md           ← Codex entries are <name>.codex.md
└── authored/          ← your own skills
    └── *.md           ← Codex entries are <name>.codex.md
```

The skill has 5 subcommands. Pick the one matching the text after `$skill-dict`; if none was given, ask which as a numbered list in chat and wait for the answer.

## Subcommands

### `list` (inline)
Print the contents of `~/skills-library/INDEX.md` and stop. Do NOT read other files. The index is a single markdown table — that's the whole point of having it.

### `show <name>` (inline)
1. Locate the file: try `plugins/<name>.codex.md`, `plugins/<name>.md`, `authored/<name>.codex.md`, then `authored/<name>.md`. List the two folders (`ls`, or `rg --files`) if the user used a partial name.
2. If multiple matches (including a Codex and a Claude entry with the same name), list them as a numbered question in chat and wait for the answer.
3. If no match, tell the user and suggest `$skill-dict list` to see what's available.
4. Read just that one file and print it. Do NOT read other library files.

### `sync`
Reconcile the library against installed plugins + user-authored skills. Idempotent. **See [references/sync.md](references/sync.md)** for the full algorithm.

### `check-updates`
Audit comparing installed Codex plugin versions to what their marketplaces offer; changes nothing installed. **See [references/check-updates.md](references/check-updates.md)** for the full flow.

### `add <name>`
Interactive guided add for self-authored skills. **See [references/add.md](references/add.md)** for the questions and template.

## General rules

- **Never read more than one library entry file in a single invocation** unless the user explicitly asks for "all entries" — the whole point is to keep context cost low.
- **Never delete or move existing library files** without explicit user confirmation. `sync` only adds.
- **Never auto-fill the user's "Where I use it" / "Why I kept it" sections** from external assumption — those are your own notes. Stubs leave them empty.
- **No git commits.** Leave committing the library to the user, even if it lives in a git repo.
- **Preserve hand-edits.** When `sync` finds an existing file, do not modify it — even if the manifest disagrees on `installed:` or `version:`. your edits win.
