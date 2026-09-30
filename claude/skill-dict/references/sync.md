# `/skill-dict sync` — reconcile library with disk

Reconciliation between disk reality and the library. Idempotent — safe to re-run.

## 1. Read the plugin manifest

```
Read: ~/.claude/plugins/installed_plugins.json
```

Extract each plugin name (strip `@marketplace` suffix) and its `installedAt` ISO timestamp from the first scope entry.

## 2. Inventory user-authored skills

```bash
ls -1 ~/.claude/skills/
```

Filter out anything that is itself the name of a plugin from step 1 OR a known plugin namespace prefix (e.g. `gsd-*` belongs to the `gsd` parent — the parent is `gsd`, the children are not separate authored skills). The classification heuristic:

- If it's listed in `installed_plugins.json` → plugin (already covered).
- If it has a `gsd-` prefix → child of `gsd`, skip.
- Otherwise → likely authored. Confirm by checking the SKILL.md frontmatter — if it has a recognizable plugin marker, skip; otherwise treat as authored.
- Default authored set: `putdown`, `pickup`, `newproject`, plus the `gsd` parent name itself (since GSD installs to `~/.claude/skills/` not via plugin manifest).

## 3. List existing library files

```bash
ls -1 ~/skills-library/plugins/
ls -1 ~/skills-library/authored/
```

## 4. Compute the diff

- **To add (plugins):** plugins in manifest but no `<name>.md` in `plugins/`.
- **To add (authored):** authored skills with no `<name>.md` in `authored/`.
- **Possibly retired:** library files whose source plugin/skill no longer exists on disk.

## 5. For each "to add" item, create a stub

Use the template from `README.md`. Pre-fill what's known:

- `name` from the directory/manifest name.
- `display-name` Title-Cased.
- `source` from the manifest (`@marketplace-name`) or `self-authored` for authored.
- `scope: user`.
- `installed:` from manifest `installedAt` (date only, `YYYY-MM-DD`) or today's date for authored.
- `version` from manifest if present.
- `status: active`.
- `activation:` — classify by inspecting the skill:
  - `always-on` if the plugin installs a `SessionStart` or always-firing hook in `~/.claude/settings.json`, OR if it's a meta-skill loaded as a system-prompt directive.
  - `auto-on-match` if the SKILL.md frontmatter description starts with "Use when..." or describes content-based triggers (the agent will auto-invoke).
  - `manual` if the description is a slash-command-style verb ("Create...", "Show...", "Run...") with no auto-trigger language, or if it's clearly user-driven (`/putdown`, `/pickup`, `/<plugin>:<skill>` with no auto-trigger).
  - Combine with `+` if multiple modes apply (e.g. `always-on (hook) + manual (sub-skills)`).
- "What it is" — write a 2-3 sentence description by reading the skill's own SKILL.md frontmatter `description:` field. Do NOT just copy the description verbatim — distill it.
- "How to trigger it" — fill in:
  - **Slash command:** the actual command (e.g. `/skill-name` for user-scope, `/<plugin>:<skill>` for plugin-namespaced).
  - **Auto-trigger conditions:** if `activation` includes `auto-on-match`, paraphrase the trigger conditions from the skill's description. Otherwise write "none — fully manual."
  - **Lifetime:** "one-shot per invocation" by default. If always-on, "active for entire session via hook."
- "When I'd trigger it" — leave as `_(fill in — see <skill>'s description for canonical use cases)_` so the user writes their own. Don't auto-paraphrase the description here; that's their personal note section.
- All remaining sections (Where I use it, Why I kept it, Notes, Related) empty (`_(fill in)_`).

## 6. Append rows to `INDEX.md`

For each new entry. Match the column order: Skill | Installed | Source | Status | Activation | What.

## 7. For "possibly retired" items, do NOT delete or move them

Just print a heads-up: `looks like X was uninstalled (no entry in manifest, no folder at ~/.claude/skills/X) — consider setting status: retired and moving to retired/ subfolder.`

## 8. Print a one-screen summary

```
/skill-dict sync results:
Added (plugins): <count> — <names>
Added (authored): <count> — <names>
Possibly retired: <count> — <names>
No-op: <count of unchanged entries>
```

If everything matches, output `Added: 0, Possibly retired: 0 — library is in sync.`
