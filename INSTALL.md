# Install

Install any combination of the six skills in this repo. They're all standalone except for the **session-continuity pair** (`/putdown` + `/pickup`), which must always be installed together. `/takenotes` lives in the same folder as that pair but is independent — install it with them, without them, or add it later.

## Prerequisite

You need Claude Code installed. User-scope skills live at `~/.claude/skills/<name>/SKILL.md` and are auto-discovered on session start.

## 1. Session-continuity pair: `/putdown` + `/pickup`

These are a matched pair — `/pickup` reads the handoff files that `/putdown` writes. Installing one without the other gets you half a feature.

```bash
git clone https://github.com/cabaynes/charles-claude-skills.git
cp -r charles-claude-skills/skills/session-continuity/{putdown,pickup} ~/.claude/skills/
```

That copies **both** skill folders into `~/.claude/skills/` in one command. Verify:

```bash
ls ~/.claude/skills/putdown/SKILL.md ~/.claude/skills/pickup/SKILL.md
```

No environment-variable setup required.

### 1b. Recommended companion: `/takenotes`

Lives in the same folder but is **not** part of the required pair — `/putdown` and `/pickup` work without it. Install it if you want session *knowledge* kept permanently, not just session *state* carried forward:

```bash
cp -r charles-claude-skills/skills/session-continuity/takenotes ~/.claude/skills/
```

```bash
ls ~/.claude/skills/takenotes/SKILL.md
```

**Install order doesn't matter, but the effect is one-directional:** once `/takenotes` is present, `/putdown` detects it and runs it automatically as its Steps 2–3, announcing both skills up front. Without it, `/putdown` uses its own reduced inline memory step. Nothing breaks either way, and you can add or remove `/takenotes` later without touching `/putdown`.

`/takenotes` also works entirely on its own — you can install it without `/putdown` or `/pickup` at all.

No environment-variable setup required.

## 2. Optional: `/newproject`

Bootstraps a new project directory with a starter `CLAUDE.md`, memory directory, optional git init, and optional umbrella-file entry.

```bash
cp -r charles-claude-skills/skills/newproject ~/.claude/skills/
```

**Configure your workspace directory once** (the skill asks the first time, but setting this in your shell rc skips that step forever):

```bash
# In ~/.zshrc or ~/.bashrc:
export WORKSPACE_DIR=~/CLAUDE   # any path works; the workspace guide uses ~/CLAUDE
```

Optional: if `$WORKSPACE_DIR/scripts/fanout-memory.sh` exists, the skill uses it to symlink universal memory files into each new project. That helper ships in this repo; see section 4. Without it, the skill falls back to plain `mkdir`.

## 3. Optional: `/skill-dict`

Maintain a hand-curated catalog of every Claude Code skill you've installed or authored.

```bash
cp -r charles-claude-skills/skills/skill-dict ~/.claude/skills/
```

By default, the skill looks for the catalog at `~/skills-library/`. If you want a different path, edit `~/.claude/skills/skill-dict/SKILL.md` and replace the `~/skills-library/` references with your preferred location.

## 4. Optional: the workspace pattern (shared memory across projects)

If you keep more than one project, the [`workspace/`](workspace/) folder turns the skills into one system: an umbrella `CLAUDE.md` at the root, and a memory hub whose universal files (`user_*.md`, `feedback_*.md`) are symlinked into every project. Full walkthrough with copy-and-paste prompts in [workspace/README.md](workspace/README.md); the wider tool stack in [workspace/STACK.md](workspace/STACK.md). The two files it installs:

```bash
mkdir -p ~/CLAUDE/scripts
cp charles-claude-skills/workspace/fanout-memory.sh ~/CLAUDE/scripts/ && chmod +x ~/CLAUDE/scripts/fanout-memory.sh
[ -f ~/CLAUDE/CLAUDE.md ] || cp charles-claude-skills/workspace/CLAUDE.md.template ~/CLAUDE/CLAUDE.md
export WORKSPACE_DIR=~/CLAUDE   # use the SAME value you set in section 2; this guide's examples use ~/CLAUDE
```

Prove the helper works on your machine before relying on it:

```bash
bash charles-claude-skills/workspace/test-fanout.sh
```

## 5. Optional: `/grill-me`

Interrogates a plan or idea instead of building it. Sessions are written to `grill-me-sessions/` in the current directory; add that folder to your project's `.gitignore` if you do not want planning notes committed.

```bash
cp -r charles-claude-skills/skills/grill-me ~/.claude/skills/
```

## Symlink vs. copy

The instructions above use `cp -r` (copy). The alternative is `ln -s` (symlink) — that way, when you `git pull` to update the repo, the installed skills update too.

**Copy** (default):
- ✓ Independent of the repo after install
- ✗ Updates require re-running `cp`

**Symlink:**
```bash
# Example for the session-continuity pair:
ln -s "$(pwd)/charles-claude-skills/skills/session-continuity/putdown" ~/.claude/skills/putdown
ln -s "$(pwd)/charles-claude-skills/skills/session-continuity/pickup" ~/.claude/skills/pickup
```
- ✓ `git pull` updates your installed skills
- ✗ Deleting the repo breaks your installed skills

Pick based on whether you plan to track upstream.

## After install: restart Claude Code

Newly installed skills are discovered when Claude Code starts a new session. In VSCode, **close the Claude Code window (Cmd+W) and open a fresh one**.

> ⚠️ `Cmd+Shift+P → Developer: Reload Window` does **NOT** free Claude Code's context window memory and does NOT reliably refresh the skill registry. Only opening a fresh Claude Code window works.

## Troubleshooting

**Skill doesn't appear in the registry:**
1. Confirm the folder structure: `~/.claude/skills/<name>/SKILL.md` (the `SKILL.md` file must be exactly that name).
2. Confirm the YAML frontmatter is valid (no tabs, no trailing whitespace, all required fields present: `name`, `description`).
3. Open a fresh Claude Code window (not Reload Window).

**Permission prompts every time I invoke a skill:**
Each skill ships with an `allowed-tools` frontmatter field that pre-authorizes the tools it needs. If you're still getting prompts, your Claude Code settings may be overriding this. Check `~/.claude/settings.json` and `~/.claude/settings.local.json` for permission entries that conflict.

**`/putdown` says "no project slug, multi-project parent":**
Pass the slug as an argument: `/putdown <name>`. This happens when your CWD is a parent folder containing multiple projects (e.g. you're in `~/projects/` rather than `~/projects/foo/`).

**`/pickup` can't find a putdown:**
Make sure the putdown files exist at `~/.claude/putdowns/<project-slug>/`. If you're in a different CWD than when you ran `/putdown`, the project slug won't match — see the `/pickup` skill's "no putdown found" branch, which lists all available project slugs.

**`/newproject` keeps asking about `WORKSPACE_DIR`:**
Export it in your shell rc so it persists across sessions (see step 2 above).

## Using OpenAI Codex instead (or as well)

All six skills also ship a **Codex version** in [`codex/`](codex/). Codex uses the same open
[Agent Skills](https://agentskills.io/specification) format, so these are the same skills with the
Claude-only parts swapped for Codex equivalents. They're generated, not hand-copied, so the two
versions can't drift. See [MAINTAINING.md](MAINTAINING.md#codex-versions).

```bash
git clone https://github.com/cabaynes/charles-claude-skills.git
mkdir -p ~/.agents/skills
cp -r charles-claude-skills/codex/*/ ~/.agents/skills/
```

The same pairing rules apply: `putdown` + `pickup` together, `takenotes` optional. Start a new Codex
chat afterwards so the skills register.

| | Claude Code | Codex |
|---|---|---|
| Run a skill | `/putdown` | `$putdown` (or pick it from `/skills`) |
| Project instructions | `CLAUDE.md` | `AGENTS.md` |
| Handoff files | `~/.claude/putdowns/<project>/` | `~/.codex/putdowns/<project>/` |
| Saved knowledge (`takenotes`) | Claude Code's memory folders | Markdown notes in `~/.codex/notes/global/` and `~/.codex/notes/projects/<slug>/` |
| Fresh context | `/clear` (CLI) or a new window | `/new` (CLI) or **New chat** (app) |

- **How notes load in Codex.** Codex doesn't load a notes folder by itself. The first time
  `$takenotes` saves something, it appends a short block to your global `~/.codex/AGENTS.md` telling
  every session to read the notes indexes. It never rewrites what's already there. Codex's own
  built-in memories are left alone; `takenotes` never writes to them.
- **Using both tools on one repo.** Handoffs committed to a private repo's `.putdowns/` folder use
  the same format, so a putdown written in one tool can be picked up in the other.
- **Tested in Codex.** Each skill has an end-to-end scenario run through `codex exec` in a throwaway
  environment (30/30), plus a spec check and a behavior rubric. Full results:
  [`tests/codex/RESULTS.md`](tests/codex/RESULTS.md). The trigger-accuracy numbers in
  [eval-results.md](eval-results.md) were measured on Claude Code only.

## Uninstall

```bash
rm -rf ~/.claude/skills/{putdown,pickup,takenotes,newproject,skill-dict,grill-me}
rm -f ~/CLAUDE/scripts/fanout-memory.sh   # only if you installed the workspace pattern; leaves your memory symlinks in place
```

Restart Claude Code in a fresh window.
