# `$skill-dict sync` — reconcile library with disk

Reconciliation between disk reality and the library. Idempotent — safe to re-run.

## 1. Read the installed-plugin list

```bash
codex plugin list --json
```

This is read-only. Do **not** run `codex plugin add/remove` or `codex plugin marketplace upgrade` here.
The JSON has an `installed` array; each item has `pluginId` (`<name>@<marketplace>`), `name`,
`marketplaceName`, `version`, `installed`, `enabled`, `source`, and usually `marketplaceSource`,
`installPolicy`, `authPolicy`. `source.source` is `local` (with a `path`) or `remote` (with an `id` —
a server-managed connector plugin, no local files). Keep items whose `installed` is true.

**There is no install-date field.** Never infer one from file timestamps; the stub records
`installed: unknown`. If a field you expect is missing in this Codex version, record `unknown` too.

## 2. Inventory standalone skills

List the folders that hold standalone (non-plugin) Codex skills:

```bash
CODEX_DIR="${CODEX_HOME:-$HOME/.codex}"
ls -1 ~/.agents/skills/ "$CODEX_DIR/skills/" 2>/dev/null
```

- Skip `$CODEX_DIR/skills/.system/` — those are skills bundled with Codex itself.
- Skip anything without a `SKILL.md`.
- If the command runs inside a repo, also list `<repo root>/.agents/skills/` and record those with
  `scope: project`.
- A folder name alone can't tell a self-authored skill from one installed with `$skill-installer`.
  Collect the skills that have no library entry yet and ask the user **once**, as a numbered list,
  which are self-authored and where the others came from. Anything they don't answer gets
  `source: unknown`.

## 3. List existing library files

```bash
ls -1 ~/skills-library/plugins/
ls -1 ~/skills-library/authored/
```

## 4. Compute the diff

Only Codex entries take part: `*.codex.md` files. Claude entries (no `platform:` field) are never
added, flagged, or touched here.

- **To add (plugins):** installed plugins with no `plugins/<name>.codex.md`.
- **To add (authored):** standalone skills with no `authored/<name>.codex.md` (or `plugins/` if the
  user said it was installed from somewhere).
- **Possibly retired:** `*.codex.md` files whose plugin is no longer in the installed list and whose
  skill folder no longer exists. A plugin present with `enabled: false` is **not** retired — note it as
  disabled instead.

## 5. For each "to add" item, create a stub

Use the template from `README.md`. Pre-fill what's known:

- `name` from the plugin `name` or the skill folder name.
- `display-name` Title-Cased.
- `platform: codex`.
- `source` — for plugins, `<marketplaceName>` plus `(remote)` when `source.source` is `remote`; for
  standalone skills, what the user answered in step 2 (`self-authored`, a URL, or `unknown`).
- `scope` — `user`, or `project` for a repo's `.agents/skills/`.
- `installed: unknown` for plugins (Codex records no install date); today's date for skills the user
  says they authored today, otherwise `unknown`.
- `version` from the plugin list; `unknown` for standalone skills.
- `status: active` (`disabled` in Notes if `enabled` is false).
- `activation:` — classify only from evidence in the skill's own files:
  - `manual` if its `agents/openai.yaml` sets `allow_implicit_invocation: false`.
  - `auto-on-match` otherwise when the description states when to use it (Codex may pick it
    implicitly; explicit `$name` still works).
  - If you can't find the skill's files (a remote plugin), write `unknown`.
  - Don't claim `always-on` unless you found a configuration that loads it every session.
- "What it is" — write a 2-3 sentence description by reading the skill's own SKILL.md frontmatter `description:` field (for a plugin, its `.codex-plugin/plugin.json` `description`). Do NOT just copy it verbatim — distill it.
- "How to trigger it" — fill in:
  - **Invocation:** `$<skill-name>` for a standalone skill. For a plugin's skills, use the names Codex
    shows in its `/skills` list if you can see them; otherwise write `unknown — check /skills`.
  - **Auto-trigger conditions:** if `activation` includes `auto-on-match`, paraphrase the trigger conditions from the description. Otherwise write "none — fully manual."
  - **Lifetime:** "one-shot per invocation" unless you found evidence otherwise.
- "When I'd trigger it" — leave as `_(fill in — see <skill>'s description for canonical use cases)_` so the user writes their own. Don't auto-paraphrase the description here; that's their personal note section.
- All remaining sections (Where I use it, Why I kept it, Notes, Related) empty (`_(fill in)_`).

Save as `plugins/<name>.codex.md` or `authored/<name>.codex.md`.

## 6. Append rows to `INDEX.md`

For each new entry. Match the column order: Skill | Installed | Source | Status | Activation | What. Write the Skill cell as `<name> (codex)`.

## 7. For "possibly retired" items, do NOT delete or move them

Just print a heads-up: `looks like X was uninstalled (not in codex plugin list --json, no skill folder) — consider setting status: retired and moving it to a retired/ subfolder.`

## 8. Print a one-screen summary

```
$skill-dict sync results:
Added (plugins): <count> — <names>
Added (authored): <count> — <names>
Disabled (still installed): <count> — <names>
Possibly retired: <count> — <names>
No-op: <count of unchanged entries>
```

If everything matches, output `Added: 0, Possibly retired: 0 — library is in sync.`
