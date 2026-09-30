# `/skill-dict add <name>` — interactive guided add

Use this for skills the user is creating from scratch (vs. installing a plugin — for that, just run `sync`).

## 1. Ask via `AskUserQuestion`

Group into 1-2 calls of up to 4 questions each:

- **Source**: self-authored | claude-plugins-official | npm | other (free-text)
- **Scope**: user | project
- **Status**: active | trial | retired
- **Activation**: always-on | auto-on-match | manual | combo
- **Folder**: `plugins/` or `authored/`?

## 2. Ask via free-text input

- "What it is" (2-3 sentence summary)
- The slash command syntax (e.g. `/foo` or `/plugin:foo`)
- Auto-trigger conditions if `activation` includes `auto-on-match` (e.g. "user mentions building a UI")

## 3. Today's date for `installed`

## 4. Compose the file

Use the full template from `README.md`, including `## How to trigger it` and `## When I'd trigger it` sections (latter as `_(fill in)_` for you to complete in VSCode).

## 5. Append a row to `INDEX.md`

All 6 columns: Skill | Installed | Source | Status | Activation | What.

## 6. Print confirmation

```
Added <name> at skills-library/<folder>/<name>.md and updated INDEX.md.
```
