---
name: newproject
description: Use when bootstrapping a new project under a configured workspace directory ($WORKSPACE_DIR, default ~/projects/), or when an existing project folder needs the standard infrastructure (CLAUDE.md stub, memory dir, optional git init + GitHub repo, optional umbrella entry). Triggers only when the user references a project folder under the workspace — do NOT use for generic git init, npm/Xcode init, or single-file creation. Idempotent — never overwrites existing user content.
argument-hint: "[project-name]"
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Grep
  - Glob
  - AskUserQuestion
---

# /newproject — Bootstrap or finish setting up a workspace project

The user wants to start a project under their workspace directory `$WORKSPACE_DIR` (default `~/projects/`). The folder may not exist yet OR it may already exist with partial setup (e.g., they did `mkdir $WORKSPACE_DIR/foo` and `code $WORKSPACE_DIR/foo` already). Your job: detect what's in place and create only what's missing — **never overwrite existing user content**.

## What ends up created

1. `$WORKSPACE_DIR/<name>/` — empty project directory
2. `$WORKSPACE_DIR/<name>/CLAUDE.md` — starter project documentation (stub)
3. `~/.claude/projects/<project-slug>/memory/` — memory dir (with universal-symlink fan-out if a `fanout-memory.sh` helper exists in `$WORKSPACE_DIR/scripts/`)
4. **Optional:** `$WORKSPACE_DIR/<name>/.git/` — initialized git repo with sensible `.gitignore`
5. **Optional:** a GitHub repo (private by default) with `origin` set and a bootstrap commit pushed — plus any web-session skills copied into `$WORKSPACE_DIR/<name>/.claude/skills/` if your workspace keeps a `scripts/web-skills/` source (private repos only)
6. **Optional:** updated `$WORKSPACE_DIR/CLAUDE.md` — if an umbrella file exists with a `## Subprojects` section, append an entry

## Step 1 — Resolve `WORKSPACE_DIR`

Check the env var:

```bash
echo "${WORKSPACE_DIR:-}"
```

- If set, use that path (expand `~` if present).
- If unset, **ask the user once** via `AskUserQuestion`:
  > "WORKSPACE_DIR isn't set. Default is `~/projects/`. Use that, or specify a different path?"
  > Options: `Use ~/projects/` | `Use a different path` (free-text)
- After resolution, recommend (don't enforce) that the user export it in their shell rc so they don't have to set it each session.

For the rest of this skill, **`$WORKSPACE_DIR`** is the resolved absolute path (e.g. `/Users/alice/projects`).

## Step 2 — Get the project name and one-line description

If the user provided a name as an argument, use it. Otherwise ask:

> "What's the project name? (lowercase, hyphens for spaces, no special characters — e.g., `tax-tracking`, `family-recipes`)"

Then ask:

> "One-line description for the umbrella CLAUDE.md? (e.g., 'Personal tax document tracker' or 'Recipe collection app')"

If `$WORKSPACE_DIR/CLAUDE.md` doesn't exist, the description is optional — skip if blank.

## Step 3 — Validate the name

Must match `^[a-z][a-z0-9-]*$` — starts with lowercase letter, then lowercase alphanumerics and hyphens. If not, ask the user to choose a different name (don't auto-correct, since they may have a specific naming preference).

## Step 4 — Survey current state (read-only)

Run all checks in parallel:

- `test -d "$WORKSPACE_DIR/<name>" && echo HAS_FOLDER || echo NEW_FOLDER` — note whether folder exists; either case is fine.
- `test -f "$WORKSPACE_DIR/<name>/CLAUDE.md" && echo HAS_CLAUDE_MD || echo NO_CLAUDE_MD` — note whether the project already has a CLAUDE.md.
- `test -d "$WORKSPACE_DIR/<name>/.git" && echo HAS_GIT || echo NO_GIT` — note whether git is already initialized.
- `test -f "$WORKSPACE_DIR/CLAUDE.md" && echo HAS_UMBRELLA || echo NO_UMBRELLA` — does the workspace have an umbrella CLAUDE.md to update?
- `test -x "$WORKSPACE_DIR/scripts/fanout-memory.sh" && echo HAS_FANOUT || echo NO_FANOUT` — does the optional fan-out helper exist?

These are all informational — they tell you which steps below to skip vs. run.

Quickly summarize to the user what you found, e.g.:

> "Folder already exists. Has: nothing yet. Will set up: CLAUDE.md stub, memory dir, optionally git. Umbrella file: present, will append entry. Fan-out script: not found, will use plain mkdir for memory dir."

## Step 5 — Create the folder (only if missing)

```bash
mkdir -p "$WORKSPACE_DIR/<name>"
```

`mkdir -p` is safe regardless of whether the folder exists.

## Step 6 — Generate the starter CLAUDE.md (ONLY if missing)

If the survey reported `HAS_CLAUDE_MD`, **skip this step entirely** and tell the user "CLAUDE.md already exists, leaving alone." Never overwrite a CLAUDE.md the user may have already started writing.

If `NO_CLAUDE_MD`, write `$WORKSPACE_DIR/<name>/CLAUDE.md` with this template (substituting name and description):

```markdown
# <Name>

<one-line description from Step 2, or omit if blank>

## Project goals
_(Add as the project takes shape.)_

## Repo layout
_(Document folders/files as the structure emerges.)_

## Conventions
_(Add as patterns appear — naming, error handling, commit style, etc.)_

## External references
_(Links to related repos, docs, dashboards, vendor accounts.)_

## Notes
_(Track ongoing decisions and context here.)_
```

Capitalize the project name appropriately (e.g., `tax-tracking` → `Tax Tracking`, `RecipeBox` → `RecipeBox`). Use sensible title-casing.

## Step 7 — Set up the memory directory

Compute the project slug from the absolute project path (this matches how Claude Code derives memory dir names):

```bash
SLUG="$(echo "$WORKSPACE_DIR/<name>" | tr '/' '-')"   # keeps the leading '-': /Users/a/x → -Users-a-x
MEMORY_DIR="$HOME/.claude/projects/$SLUG/memory"
```

Then:

**If `HAS_FANOUT`**: run the helper to set up the memory dir with universal-symlink fan-out:

```bash
"$WORKSPACE_DIR/scripts/fanout-memory.sh" <name>
```

(The fan-out helper ships with this skill's repo at `workspace/fanout-memory.sh`, with a setup guide at `workspace/README.md`. It symlinks universal memories from a workspace-level hub into each project's memory dir. If it isn't installed, the fallback below handles you.)

**Otherwise**: create the memory directory plainly:

```bash
mkdir -p "$MEMORY_DIR"
# Seed an empty MEMORY.md if one doesn't exist
if [ ! -f "$MEMORY_DIR/MEMORY.md" ]; then
  touch "$MEMORY_DIR/MEMORY.md"
fi
```

Show the user what was created vs. already present.

## Step 8 — Git + GitHub (only if not already set up)

### 8a — Local git

If the survey reported `HAS_GIT`, **skip the local-init part** (git already initialized) and go to 8b to check the remote.

If `NO_GIT`, ask: *"Initialize git for this project? (y/n)"*

If the user declines git entirely, **skip the rest of Step 8** (no remote, no commit). If yes:

```bash
cd "$WORKSPACE_DIR/<name>" && git init -b main
```

Then create `.gitignore` with sensible defaults (only if no `.gitignore` exists yet):

```
.DS_Store
.env
.env.local
*.log
__pycache__/
node_modules/
.venv/
venv/
build/
dist/
*.pyc
.idea/
.vscode/*.local.json
```

### 8b — GitHub repo + push (optional)

If the user keeps projects on GitHub, the skill can create the remote repo and push an initial scaffold so the project is immediately available from other machines or the web. Skip this for deliberately local-only projects. This step needs the `gh` CLI authenticated — if it isn't, see Edge cases (skip cleanly, don't error).

**First, check for an existing remote** (read-only):

```bash
git -C "$WORKSPACE_DIR/<name>" remote get-url origin 2>/dev/null
```

If `origin` already points to a `github.com[:/]…` URL, **skip creation** and report "GitHub repo already linked." Otherwise, ask:

> *"Create a GitHub repo (private by default) and push the scaffold? (y/n — choose n for local-only projects.)"*

**If declined:** stop Step 8 here.

**If yes:**

1. **Derive the owner** (don't hardcode a username):

   ```bash
   gh api user --jq .login
   ```

2. **Repo name:** default to the folder `<name>`; offer one override prompt — *"GitHub repo name? (default: `<name>`)"*.

3. **Visibility:** default **private**. Only create a public repo if the user explicitly asks.

4. **Create the repo and link `origin`** (use `--public` instead of `--private` if the user chose public):

   ```bash
   cd "$WORKSPACE_DIR/<name>" && gh repo create <owner>/<repo> --private --source=. --remote=origin
   ```

5. **Optional — seed web-session skills (private repos only):** some workspaces keep copies of session-continuity skills to commit into each repo so cloud/web sessions can resume work. If such a source exists, copy it in. **Skip entirely for public repos** so nothing private gets published.

   ```bash
   if [ -d "$WORKSPACE_DIR/scripts/web-skills" ]; then
     mkdir -p "$WORKSPACE_DIR/<name>/.claude/skills"
     cp -R "$WORKSPACE_DIR/scripts/web-skills/"* "$WORKSPACE_DIR/<name>/.claude/skills/"
   fi
   ```

6. **Bootstrap commit + push:**

   ```bash
   cd "$WORKSPACE_DIR/<name>" && git add CLAUDE.md .gitignore $(test -d .claude/skills && echo .claude/skills) && git commit -m "Bootstrap <name> scaffold" && git branch -M main && git push -u origin main
   ```

   The `-u` on the first push establishes upstream tracking. It stages only the scaffold, by name. The folder may already hold the user's own files (this skill runs on existing folders too), and `git add -A` would commit them unreviewed. After the push, run `git status --porcelain`: if other untracked files remain, list them and ask whether to commit them — never add them silently.

## Step 9 — Update the umbrella CLAUDE.md (only if applicable)

If `NO_UMBRELLA` (no `$WORKSPACE_DIR/CLAUDE.md` exists), **skip this step**. Don't create an umbrella file unprompted.

If `HAS_UMBRELLA`, look for a `## Subprojects` section in `$WORKSPACE_DIR/CLAUDE.md`. If absent, **skip** — don't restructure the user's umbrella file unprompted.

If present, check whether the project is already listed:

```bash
grep -q "^- \[<name>/](<name>/) " "$WORKSPACE_DIR/CLAUDE.md" && echo HAS_ENTRY || echo NO_ENTRY
```

If `NO_ENTRY`, append a new line in the same format as existing entries:

```
- [<name>/](<name>/) — <one-line description from Step 2>
```

Keep alphabetical order if the existing list is alphabetical, otherwise append at the end.

## Step 10 — Confirmation summary

Print a tight summary that matches what was actually done. Use ✓ for things created and ⊘ (or "skipped") for things already in place. Example output for a half-existing project:

```
Project: tax-tracking
WORKSPACE_DIR: /Users/alice/projects

  ⊘ Folder already existed at /Users/alice/projects/tax-tracking/
  ✓ Created CLAUDE.md (starter — fill in as you go)
  ✓ Memory dir set up at ~/.claude/projects/-Users-alice-projects-tax-tracking/memory/ (fallback — no fan-out script found)
  ✓ Initialized git + .gitignore
  ✓ GitHub repo (private) created + scaffold pushed → <owner>/tax-tracking
  ✓ Added entry to umbrella /Users/alice/projects/CLAUDE.md

Next:
  Open in VSCode:  code /Users/alice/projects/tax-tracking
  Or in this session:  cd /Users/alice/projects/tax-tracking
```

For a local-only project (GitHub declined or `gh` unavailable), show `⊘ Local-only (no GitHub repo)` in place of the GitHub line.

If this skill ran in a session launched inside the new folder, note that the freshly written `CLAUDE.md` and memory dir won't be in context until a fresh window is opened ("Reload Window" doesn't pick them up).

End the skill cleanly — don't start working on the project unless the user asks.

## Edge cases

- **`WORKSPACE_DIR` unset and user doesn't want `~/projects/`**: ask for a custom path, validate it exists (or offer to `mkdir -p`), then proceed.
- **No argument given for name**: ask the user (Step 2).
- **Invalid name**: ask the user to rename, don't auto-correct.
- **Folder already exists with partial setup**: that's the expected case — proceed additively. Never overwrite existing `CLAUDE.md`, `.git`, or other user content.
- **Folder doesn't exist**: also fine — `mkdir -p` creates it.
- **No description given**: prompt the user for one before updating the umbrella file (or skip the umbrella update if they don't have one). Don't write "TBD" into the umbrella — that file is user-facing and a placeholder there is awkward.
- **Fan-out script missing**: not an error — use the plain `mkdir` fallback in Step 7 and tell the user.
- **`gh` missing or unauthenticated** (`gh api user` fails): warn that the GitHub step is being skipped and the project is local-only for now; do NOT abort the rest of the skill. Suggest `gh auth login`, then they can re-run to add the remote.
- **GitHub repo name already taken** (`gh repo create` errors): surface `gh`'s message and ask the user for a different name; don't retry blindly.
- **Public repo chosen**: skip the web-session skills copy (8b step 5) so nothing private gets published.

## Why this is a skill rather than just a script

A pure shell script could do most of this but would feel rigid; the skill lets the agent:

- Adapt the starter CLAUDE.md template to match existing-project conventions
- Ask about description, git, and GitHub preferences conversationally (repo name, visibility, local-only)
- Update the umbrella file in a way that matches its existing structure (alphabetical vs. chronological, with vs. without descriptions)
- Skip steps cleanly when they're already done, without erroring

The conversational shape is the point — bootstrap workflows benefit from a moment of judgment per step.
