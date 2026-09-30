---
name: skill-dict
description: Use when the user types `/skill-dict`, asks about their personal skill library at ~/skills-library/, asks "what does <skill> do" about a library entry, asks to sync the library after installing a plugin, or asks to add a skill to the library.
argument-hint: "[list | show <name> | sync | add <name> | check-updates]"
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
  - AskUserQuestion
---

# /skill-dict — Personal skill library at `~/skills-library/`

You maintain a hand-curated catalog of every Claude Code skill you've installed or authored. One markdown file per **parent unit** (a plugin or top-level user-authored skill). Sub-skills inside a plugin live inside the parent's entry, not as separate files.

**Library root:** `~/skills-library/`

```
skills-library/
├── README.md          ← overview, conventions, entry template
├── INDEX.md           ← scannable table of all entries
├── plugins/           ← installed from marketplaces or npm
│   └── *.md
└── authored/          ← your own skills
    └── *.md
```

The skill has 5 subcommands. Pick the one matching the user's argument; if none was given, ask which.

## Subcommands

### `list` (inline)
Print the contents of `~/skills-library/INDEX.md` and stop. Do NOT read other files. The index is a single markdown table — that's the whole point of having it.

### `show <name>` (inline)
1. Locate the file: try `plugins/<name>.md` first, then `authored/<name>.md`. Use `Glob` if the user used a partial name.
2. If multiple matches, ask via `AskUserQuestion`.
3. If no match, tell the user and suggest `/skill-dict list` to see what's available.
4. Read just that one file with `Read` and print it. Do NOT read other library files.

### `sync`
Reconcile the library against installed plugins + user-authored skills. Idempotent. **See [references/sync.md](references/sync.md)** for the full algorithm.

### `check-updates`
Read-only audit comparing installed plugin versions to upstream sources. **See [references/check-updates.md](references/check-updates.md)** for the full flow.

### `add <name>`
Interactive guided add for self-authored skills. **See [references/add.md](references/add.md)** for the questions and template.

## General rules

- **Never read more than one library entry file in a single invocation** unless the user explicitly asks for "all entries" — the whole point is to keep context cost low.
- **Never delete or move existing library files** without explicit user confirmation. `sync` only adds.
- **Never auto-fill the user's "Where I use it" / "Why I kept it" sections** from external assumption — those are your own notes. Stubs leave them empty.
- **No git commits.** The CLAUDE workspace root is not a git repo. Don't try.
- **Preserve hand-edits.** When `sync` finds an existing file, do not modify it — even if the manifest disagrees on `installed:` or `version:`. your edits win.
