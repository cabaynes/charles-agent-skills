# `/newproject` — bootstrap a workspace project

> Idempotent. Conversational. Configurable. Run it on a brand-new folder or a half-set-up one — it creates only what's missing.

## What

`/newproject <name>` sets up a new project directory under a configurable workspace root. It creates:

1. The project folder itself (`mkdir -p`).
2. A starter `CLAUDE.md` documentation stub.
3. A memory directory at `~/.claude/projects/<project-slug>/memory/` so Claude Code can persist project memory across sessions.
4. **Optional**: a git repo with sensible `.gitignore`.
5. **Optional**: an entry in your workspace's umbrella `CLAUDE.md` (if you keep one with a `## Subprojects` section).

If any of those already exist, the skill detects them and skips that step — it never overwrites your work.

## Configuration

The skill reads one environment variable: **`WORKSPACE_DIR`** (default `~/projects/`). Set it once in your shell rc to skip the configuration prompt forever:

```bash
# In ~/.zshrc or ~/.bashrc:
export WORKSPACE_DIR=~/projects
```

The skill also looks for `$WORKSPACE_DIR/scripts/fanout-memory.sh`. That helper ships in this repo at [`workspace/fanout-memory.sh`](../../workspace/fanout-memory.sh): it symlinks universal memory files from a workspace-level hub into each project's memory dir, so a preference written once applies everywhere. If the helper isn't installed, the skill falls back to a plain `mkdir -p` for the memory directory; your project still gets a memory dir, just without the shared-memory fan-out. Setup guide: [workspace/README.md](../../workspace/README.md).

## What it creates (in detail)

For `/newproject foo` with `WORKSPACE_DIR=~/projects`:

| Path | Purpose |
|---|---|
| `~/projects/foo/` | The project folder |
| `~/projects/foo/CLAUDE.md` | Starter project docs (sections for goals, layout, conventions, references, notes) |
| `~/.claude/projects/-Users-<you>-projects-foo/memory/` | Claude Code's project memory dir (with hub symlinks when the workspace helper is installed) |
| `~/projects/foo/.git/` | If you say yes to git init |
| `~/projects/foo/.gitignore` | Standard ignores for Python/Node/macOS |
| Entry in `~/projects/CLAUDE.md` | If a `## Subprojects` section exists |

## Why idempotent matters

You'll re-run `/newproject foo` more than you think — when you forgot whether you initialized git, when you manually `mkdir`'d a folder and want the rest of the infrastructure, when the umbrella file isn't updated yet. The skill is designed to handle every partial state gracefully:

```
Project: foo
WORKSPACE_DIR: /Users/alice/projects

  ⊘ Folder already existed
  ⊘ CLAUDE.md already exists, leaving alone
  ✓ Memory dir set up (no fan-out script found; used plain mkdir)
  ⊘ Skipped git (already initialized)
  ✓ Added entry to umbrella ~/projects/CLAUDE.md
```

Every step is independent and safe.

## Best practices

- **Set `WORKSPACE_DIR` in your shell rc** once. The skill will ask you the first time; after that, just use it.
- **Optional umbrella file**: If you keep a top-level `$WORKSPACE_DIR/CLAUDE.md` with a `## Subprojects` section listing each project, `/newproject` will append the new project there. If you don't have one, the skill skips that step silently — it doesn't create the umbrella file unprompted.
- **Optional fan-out helper**: to share universal memory files (user profile, working preferences) across every project, install `workspace/fanout-memory.sh` to `$WORKSPACE_DIR/scripts/` and the skill will use it. See [workspace/README.md](../../workspace/README.md).
- **Don't fight the idempotence.** If `/newproject foo` skipped something because it already existed, that's intentional. Override by deleting the file/folder first if you want a fresh stub.

## Why this is better than alternatives

| Alternative | Problem | How `/newproject` solves it |
|---|---|---|
| `git init` + manual file creation | Forgetful; never the same twice | Idempotent, conversational, configurable |
| Project-template repos (`cookiecutter` etc.) | Heavy; require cloning + cleanup of unwanted files | Inline skill; no scaffolding repo to maintain |
| Shell aliases (`alias newproject='mkdir -p…'`) | Brittle; no agent context; no idempotence | Skill adapts to your existing conventions and never overwrites |
| Doing it by hand each time | Inconsistent; you forget the memory dir | Single command; never forgets |

## Eval result

Trigger-accuracy benchmark: 100% precision and 100% recall on a 20-query test set, after a description revision driven by an initial 90% recall result. See the root [eval-results.md](../../eval-results.md) for full methodology and the revision rationale.

## Install

See the root [INSTALL.md](../../INSTALL.md). Quick version:

```bash
cp -r charles-agent-skills/claude/newproject ~/.claude/skills/
export WORKSPACE_DIR=~/projects  # in your shell rc, so it persists
```

Then close your Claude Code window and open a fresh one.
