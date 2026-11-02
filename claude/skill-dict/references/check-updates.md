# `/skill-dict check-updates` — audit plugin versions

Check each plugin entry in the library for available updates from its upstream source. Read-only — never modifies anything except printing a summary table.

## 1. Inventory plugin entries

```bash
ls -1 ~/skills-library/plugins/
```

For each `*.md` file, read its frontmatter and extract `name`, `version`, and `source`.

## 2. For each entry, check upstream version based on `source`

### `source: claude-plugins-official`: not a git checkout (learned 2026-11-01)

`~/.claude/plugins/marketplaces/claude-plugins-official/` is a plain download that Claude Code refreshes
itself (its `lastUpdated` is in `~/.claude/plugins/known_marketplaces.json`), so `git fetch` fails with
"not a git repository". Compare the installed copy to the catalog instead:

```bash
python3 - <<'EOF'
import json,os,subprocess
d=json.load(open(os.path.expanduser('~/.claude/plugins/installed_plugins.json')))
M=os.path.expanduser('~/.claude/plugins/marketplaces/claude-plugins-official/plugins')
for k,v in d['plugins'].items():
    e=v[0]; name=k.split('@')[0]
    if not k.endswith('@claude-plugins-official'): continue
    if os.path.isdir(f'{M}/{name}'):
        r=subprocess.run(['diff','-rq','-x','.in_use','-x','.orphaned_at',f'{M}/{name}',e['installPath']],capture_output=True)
        print(name, e.get('version'), 'current' if r.returncode==0 else 'DIFFERS from catalog')
    else:
        print(name, e.get('version'), 'external source: compare gitCommitSha', e.get('gitCommitSha','')[:10], 'with the catalog entry sha')
EOF
```

Compare against each plugin's **`installPath`** from `installed_plugins.json`, never the newest folder in
`cache/` (old versions linger there marked `.orphaned_at`). Externally sourced plugins (superpowers) are
pinned by `sha` in `.claude-plugin/marketplace.json`; a matching `gitCommitSha` means current.
`claude plugin list` confirms each one is enabled.

### Other git-based marketplaces (e.g. `source: mksglu/context-mode`)

```bash
cd ~/.claude/plugins/marketplaces/<marketplace>/ && git fetch origin 2>&1 | tail -3
git log --oneline HEAD..origin/HEAD 2>/dev/null | head -10
```

Then look for the most recent version-bump commit (typically a commit message that's just a version number like `1.0.121`) or check git tags: `git tag --sort=-v:refname | head -5`. If the upstream tag is newer than the entry's `version:` field, that's an update.

If `git log HEAD..origin/HEAD` is empty, there are no new upstream commits → up-to-date. A long list of commits doesn't by itself mean an update: context-mode's were all `ci: update install stats` (2026-11-01). Compare the version in `package.json` / `.claude-plugin/plugin.json` at `HEAD` vs `origin/HEAD`, and `npm view <pkg> version`.

### `source: mksglu/context-mode` (or any marketplace under `~/.claude/plugins/marketplaces/`)

Same git fetch+log+tag pattern as above. Marketplace name comes from the source field.

### `source: npm: <package>` (e.g. `npm: get-shit-done-cc`)

```bash
npm view <package> version 2>/dev/null
```

Compare to the entry's `version:` field.

### `source: self-authored`

Skip (no upstream).

## 3. Print a summary table

```
/skill-dict check-updates results:

| Plugin | Installed | Latest | Status | Update command |
|--------|-----------|--------|--------|----------------|
| context-mode | 1.0.121 | 1.0.121 | ✅ up-to-date | — |
| superpowers | 5.1.0 | 5.2.0 | 🔄 update available | /plugin update superpowers |
| gsd | 1.41.0 | 1.42.3 | 🔄 update available | npx --yes get-shit-done-cc --claude --global |
| skill-creator | unknown | unknown | ⚠️ can't determine | check marketplace manually |
| frontend-design | unknown | unknown | ⚠️ can't determine | check marketplace manually |
```

## 4. Do NOT actually upgrade anything

This audit changes nothing installed — `git fetch` only updates the marketplace clone's remote-tracking refs, never the checked-out plugin files. Tell the user to invoke the relevant upgrade command themselves (or ask them if they want help running one).

## 5. Network failures are non-fatal

If `git fetch` or `npm view` fails (offline, rate-limited, etc.), mark that row as `⚠️ check failed` and continue with the others.
