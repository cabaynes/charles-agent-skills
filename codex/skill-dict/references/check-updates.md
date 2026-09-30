# `$skill-dict check-updates` — audit plugin versions

Check each Codex plugin entry in the library for available updates. Changes nothing — it only prints a summary table.

## 1. Inventory plugin entries

```bash
ls -1 ~/skills-library/plugins/*.codex.md
```

For each file, read its frontmatter and extract `name`, `version`, and `source`. Skip entries without
`platform: codex` — Claude entries are checked by the Claude version of this skill.

## 2. For each entry, compare against what Codex can see

Get the installed versions once:

```bash
codex plugin list --json
```

Then, by where the plugin comes from (`source` in the entry, or `source.source` / `marketplaceName`
in the list):

### A local marketplace (`source.source` is `local`)

The marketplace root is shown by `codex plugin marketplace list`. The version that marketplace offers
is in `<root>/plugins/<name>/.codex-plugin/plugin.json` (`version` field). Compare it with the installed
`version`:

- Same → `✅ matches marketplace`.
- Marketplace newer → `🔄 update available`.
- File missing → `⚠️ can't determine`.

This compares against the **local snapshot** of the marketplace, which may itself be behind. Refreshing
it (`codex plugin marketplace upgrade <name>`) changes Codex's state, so this audit never runs it — say
in the table that the user can run it first for a fresh comparison. Marketplaces bundled with the
Codex or ChatGPT app (their roots sit inside the app's own cache folders) update when the app updates.

### A remote plugin (`source.source` is `remote`)

Server-managed; there is no local version to compare. Mark `ℹ️ managed by OpenAI`.

### `source: npm: <package>`

```bash
npm view <package> version 2>/dev/null
```

Compare to the entry's `version:` field.

### `source: self-authored`

Skip (no upstream).

### A plugin no longer in `codex plugin list --json`

Mark `⚠️ not installed` and suggest `$skill-dict sync`.

## 3. Print a summary table

```
$skill-dict check-updates results:

| Plugin | Installed | Marketplace offers | Status | Update command |
|--------|-----------|--------------------|--------|----------------|
| docket | 1.2.0 | 1.2.0 | ✅ matches marketplace | — |
| cube | 0.3.1 | 0.4.0 | 🔄 update available | check the Plugins menu |
| gmail | 0.1.10 | — | ℹ️ managed by OpenAI | — |
| browser | 26.924.22138 | 26.924.22138 | ✅ matches marketplace | updates with the app |
```

Only put an update command in the table if you have confirmed it for that plugin (for example from
`codex plugin --help`); otherwise write "check the Plugins menu". Under the table, add one line: which
marketplaces were compared against a local snapshot that `codex plugin marketplace upgrade` would
refresh.

## 4. Do NOT actually upgrade anything

This audit changes nothing — no `codex plugin add/remove`, no `codex plugin marketplace upgrade`, no
edits to Codex's config. Tell the user which command to run themselves (or ask them if they want help
running one).

## 5. Failures are non-fatal

If `codex plugin list --json` or `npm view` fails (offline, rate-limited, etc.), mark the affected rows
as `⚠️ check failed` and continue with the others.
