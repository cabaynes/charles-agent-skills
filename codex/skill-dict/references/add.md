# `$skill-dict add <name>` — interactive guided add

Use this for skills the user is creating from scratch (vs. installing a plugin — for that, just run `sync`).

## 1. Ask the choice questions

Ask these in chat as **one numbered list**, each with its options, and wait for the answers (a
structured user-input tool may be used instead if this session has one; the numbered list always works):

1. **Source**: self-authored | a Codex marketplace (name it) | npm | other (free-text)
2. **Scope**: user (`~/.agents/skills/` or `$CODEX_DIR/skills/`) | project (a repo's `.agents/skills/`)
3. **Status**: active | trial | retired
4. **Activation**: auto-on-match (Codex may pick it when a request matches its description) | manual (`$name` only — implicit invocation turned off in its `agents/openai.yaml`) | combo
5. **Folder**: `plugins/` or `authored/`?

## 2. Ask via free-text input

- "What it is" (2-3 sentence summary)
- How it is invoked (e.g. `$foo`, or the name it shows under in Codex's `/skills` list for a plugin skill)
- Auto-trigger conditions if `activation` includes `auto-on-match` (e.g. "user mentions building a UI")

## 3. Today's date for `installed`

## 4. Compose the file

Use the full template from `README.md`, including `## How to trigger it` and `## When I'd trigger it` sections (latter as `_(fill in)_` for you to complete in your editor). Add `platform: codex` to the frontmatter and save as `<folder>/<name>.codex.md`.

## 5. Append a row to `INDEX.md`

All 6 columns: Skill | Installed | Source | Status | Activation | What. Write the Skill cell as `<name> (codex)`.

## 6. Print confirmation

```
Added <name> at skills-library/<folder>/<name>.codex.md and updated INDEX.md.
```
