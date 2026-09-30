# charles-agent-skills

Production-quality agent skills for **[Claude Code](https://claude.com/claude-code)** and **[OpenAI Codex](https://developers.openai.com/codex)**. Both tools use the same open [Agent Skills](https://agentskills.io/specification) format, so every skill here ships in two versions: one per tool, built from a single source so they never drift apart.

- **Claude Code:** evaluated against Anthropic's `writing-skills` + `skill-creator` rubric, with **100% trigger accuracy** on a 20-query precision/recall benchmark per skill.
- **Codex:** every skill tested end to end through the real Codex CLI (**30/30** checks), plus a spec check and a behavior rubric.

![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)
![Trigger accuracy](https://img.shields.io/badge/trigger%20accuracy-100%25-brightgreen)
![Claude Code](https://img.shields.io/badge/Claude%20Code-skills-purple)
![OpenAI Codex](https://img.shields.io/badge/OpenAI%20Codex-skills-black)

> Renamed from `charles-claude-skills` on 2026-09-29, when the Codex versions shipped. Old links redirect here. The Claude skills moved from `skills/` to `claude/`.

## Pick your tool

| You use… | Install from | Run a skill with | Project instructions file |
|---|---|---|---|
| **Claude Code** | [`claude/`](claude/) → `~/.claude/skills/` | `/putdown` | `CLAUDE.md` |
| **OpenAI Codex** | [`codex/`](codex/) → `~/.agents/skills/` | `$putdown` | `AGENTS.md` |
| **Both** | Install each folder into its own tool | either | Handoffs in a repo's `.putdowns/` work across both tools |

**How the repo is laid out:**

```
claude/            Claude Code versions — also the single source for everything
codex/             Codex versions — GENERATED from claude/, never edited by hand
codex-overlays/    only what differs for Codex, one file per skill
scripts/           snapshot.sh (refresh claude/), build-codex.py (build codex/)
tests/codex/       end-to-end Codex tests, spec check, results
workspace/         the multi-project workspace pattern these skills assume
```

**If you're an agent installing these for someone:** find out which tool they use, copy the matching folder's skill directories into that tool's skills folder (table above), and tell them to start a fresh session. Don't mix them: the `claude/` versions call Claude-only tools, and the `codex/` versions call Codex's.

## Skills in this repo

Names below use Claude Code's `/name`; in Codex, type `$name`.

**Session continuity (one folder — `putdown` + `pickup` are a required pair; `takenotes` is an optional third):**

| Skill | What it does |
|---|---|
| `/putdown` | Distills session state into a handoff file before you start fresh, then commits and pushes |
| `/pickup` | Loads the most recent putdown in a fresh session |
| `/takenotes` | Harvests what a session *learned* into memory (Claude) or notes (Codex), the project instructions file, or `docs/` — and corrects what's already stored and has since gone stale |

Docs: [claude/session-continuity/README.md](claude/session-continuity/README.md)

The split is by lifetime: a putdown is a note to your next session and goes stale once you act on it; a takenote is a fact you keep forever. Install all three and `putdown` chains to `takenotes` automatically; install only the pair and `putdown` falls back to its own lighter memory step.

**Standalone utilities:**

| Skill | What it does | Docs |
|---|---|---|
| `/newproject` | Bootstrap a configurable workspace project (idempotent) | [claude/newproject/README.md](claude/newproject/README.md) |
| `/skill-dict` | Manage a personal catalog of your installed skills (Claude, Codex, or both) | [claude/skill-dict/README.md](claude/skill-dict/README.md) |
| `/grill-me` | Interrogate a plan, design, or idea before you commit; it asks, it never builds | [claude/grill-me/README.md](claude/grill-me/README.md) |

**What changes in the Codex versions:** the workflow is the same; only tool-specific parts differ. `AGENTS.md` replaces `CLAUDE.md`; questions come as numbered lists in chat; `/new` or a New chat replaces `/clear`; `takenotes` saves Markdown notes that a short block in your global `AGENTS.md` loads each session (Codex has no memory a skill can write to). Full table: [INSTALL.md](INSTALL.md#using-openai-codex-instead-or-as-well).

## The workspace pattern these skills assume

Each skill works on a single project folder. Together they work best on a **multi-project workspace**: one root folder with a short umbrella `CLAUDE.md`, one subfolder per project, and a shared memory hub that a small script symlinks into every project so a preference written once applies everywhere. `/newproject` builds the spokes, `/takenotes` routes memory to hub or project, `/putdown` + `/pickup` carry sessions across the gaps, and `/grill-me` (installed separately, see INSTALL.md) makes you defend a plan before any of that starts.

The [`workspace/`](workspace/) folder has the whole thing: a copy-and-paste setup guide, the `fanout-memory.sh` helper that `/newproject` and `/takenotes` look for, an umbrella `CLAUDE.md` template, a test script that proves the helper works on your machine, and [`STACK.md`](workspace/STACK.md), the rest of the tool stack in install order.

**Setting someone else up, or letting Claude do it?** Point Claude at the guide and say "set me up like this":

```
https://raw.githubusercontent.com/cabaynes/charles-agent-skills/main/workspace/README.md
```

The guide opens with a runbook section written for a Claude agent acting on a person's behalf.

## Install (quick)

### Claude Code

```bash
git clone https://github.com/cabaynes/charles-agent-skills.git
mkdir -p ~/.claude/skills
# Session-continuity pair (one command, both halves):
cp -r charles-agent-skills/claude/session-continuity/{putdown,pickup} ~/.claude/skills/
# Optional third — memory harvesting; /putdown will chain to it if present:
cp -r charles-agent-skills/claude/session-continuity/takenotes ~/.claude/skills/
# Standalone, opt-in:
cp -r charles-agent-skills/claude/{newproject,skill-dict,grill-me} ~/.claude/skills/
```

Then **close your Claude Code window and open a fresh one** so the new skills register. (`Cmd+Shift+P → Developer: Reload Window` does NOT free Claude Code's context memory — only a fresh window does.)

### OpenAI Codex

```bash
git clone https://github.com/cabaynes/charles-agent-skills.git
mkdir -p ~/.agents/skills
# All six (or drop the ones you don't want — putdown + pickup go together):
cp -r charles-agent-skills/codex/{grill-me,newproject,pickup,putdown,skill-dict,takenotes} ~/.agents/skills/
```

Then start a **new chat** (`/new` in the CLI, `Cmd+N` in the app) and run them as `$putdown`, `$pickup`, and so on.

Full instructions, symlink-vs-copy trade-offs, and troubleshooting for both tools in [INSTALL.md](INSTALL.md).

## How these were evaluated

### Claude Code — trigger accuracy

These aren't just "skills I wrote" — each was scored against an 18-rule rubric distilled from Anthropic's `writing-skills` and `skill-creator` reference docs, then run through skill-creator's description-optimization benchmark eval:

- **20 trigger queries per skill** (10 should-trigger + 10 should-not-trigger, near-miss adversarial)
- **LLM-as-judge scoring** against the skill description
- **Threshold**: ≥80% precision and recall to pass

**Results:**

| Skill | Recall | Precision | Run |
|---|---|---|---|
| `/putdown` | 10/10 | 10/10 | 2026-05-13 |
| `/pickup` | 10/10 | 10/10 | 2026-05-13 |
| `/newproject` | 10/10 (post-revision) | 10/10 | 2026-05-13 |
| `/skill-dict` | 10/10 | 10/10 | 2026-05-13 |
| `/takenotes` | 10/10 | 10/10 | 2026-08-03 |
| `/grill-me` | 10/10 (post-revision) | 10/10 | 2026-09-08 |

`/takenotes` also went through a second, different kind of validation: subagents **executed** it against a sandbox seeded with a deliberately poisoned memory, over two rounds that found and closed ten defects — and again on 2026-09-25 against a memory that claimed a fix nobody had ever run (0.8.0). Trigger accuracy measures whether a skill *fires at the right time*; that measures whether it *does the right thing once it fires*. Both are in [eval-results.md](eval-results.md).

Full methodology, per-query verdicts, and revision rationale in [eval-results.md](eval-results.md).

### Codex — end-to-end behavior

Before porting, Codex itself reviewed every skill read-only. Its findings shaped the Codex versions and surfaced five real bugs in the Claude versions, fixed in 0.8.2. Each Codex version then ran through the real Codex CLI in a throwaway environment:

- **30/30 end-to-end checks.** For example: `putdown` makes exactly one commit and pushes, `pickup` repeats the handoff's "Must address" items word for word and then waits, and `takenotes` stores a cross-project preference that a *later, separate* session follows.
- **53/54 spec checks** against the Agent Skills specification. The one miss, `skill-dict`'s description lacking a when-not-to-use clause, applies to both versions and is recorded, not hidden.
- **A behavior rubric** grading each skill's output against the skill's own rules.

Codex *trigger* accuracy (whether Codex picks a skill without being asked) is not measured yet; every Codex test invoked the skill by name. Details in [tests/codex/RESULTS.md](tests/codex/RESULTS.md).

## Maintaining this repo

If you're forking or contributing, see [MAINTAINING.md](MAINTAINING.md) for the release workflow — how to refresh the Claude skills from a canonical source, rebuild and test the Codex versions, run the eval, bump the CHANGELOG, and verify sanitization before pushing.

## License

[MIT](LICENSE) — copyright 2026 Charles Baynes. Per-skill `LICENSE` files are also included in each skill folder so the folder is self-contained when copied alone.
