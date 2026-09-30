# charles-claude-skills

Production-quality slash-command skills for [Claude Code](https://claude.com/claude-code), evaluated against Anthropic's `writing-skills` + `skill-creator` rubric. **100% trigger accuracy** on a 20-query precision/recall benchmark per skill.

![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)
![Trigger accuracy](https://img.shields.io/badge/trigger%20accuracy-100%25-brightgreen)
![Claude Code](https://img.shields.io/badge/Claude%20Code-skills-purple)

## Skills in this repo

**Session continuity (one folder — `/putdown` + `/pickup` are a required pair; `/takenotes` is an optional third):**

| Skill | What it does |
|---|---|
| `/putdown` | Distills session state into a handoff file before you clear context, then commits and pushes |
| `/pickup` | Loads the most recent putdown in a fresh session |
| `/takenotes` | Harvests what a session *learned* into memory, `CLAUDE.md`, or `docs/` — and corrects what's already stored and has since gone stale |

Docs: [skills/session-continuity/README.md](skills/session-continuity/README.md)

The split is by lifetime: a putdown is a note to your next session and goes stale once you act on it; a takenote is a fact you keep forever. Install all three and `/putdown` chains to `/takenotes` automatically; install only the pair and `/putdown` falls back to its own lighter memory step.

**Standalone utilities:**

| Skill | What it does | Docs |
|---|---|---|
| `/newproject` | Bootstrap a configurable workspace project (idempotent) | [skills/newproject/README.md](skills/newproject/README.md) |
| `/skill-dict` | Manage a personal catalog of installed Claude Code skills | [skills/skill-dict/README.md](skills/skill-dict/README.md) |
| `/grill-me` | Interrogate a plan, design, or idea before you commit; it asks, it never builds | [skills/grill-me/README.md](skills/grill-me/README.md) |

## The workspace pattern these skills assume

Each skill works on a single project folder. Together they work best on a **multi-project workspace**: one root folder with a short umbrella `CLAUDE.md`, one subfolder per project, and a shared memory hub that a small script symlinks into every project so a preference written once applies everywhere. `/newproject` builds the spokes, `/takenotes` routes memory to hub or project, `/putdown` + `/pickup` carry sessions across the gaps, and `/grill-me` (installed separately, see INSTALL.md) makes you defend a plan before any of that starts.

The [`workspace/`](workspace/) folder has the whole thing: a copy-and-paste setup guide, the `fanout-memory.sh` helper that `/newproject` and `/takenotes` look for, an umbrella `CLAUDE.md` template, a test script that proves the helper works on your machine, and [`STACK.md`](workspace/STACK.md), the rest of the tool stack in install order.

**Setting someone else up, or letting Claude do it?** Point Claude at the guide and say "set me up like this":

```
https://raw.githubusercontent.com/cabaynes/charles-claude-skills/main/workspace/README.md
```

The guide opens with a runbook section written for a Claude agent acting on a person's behalf.

## Install (quick)

```bash
git clone https://github.com/cabaynes/charles-claude-skills.git
# Session-continuity pair (one command, both halves):
cp -r charles-claude-skills/skills/session-continuity/{putdown,pickup} ~/.claude/skills/
# Optional third — memory harvesting; /putdown will chain to it if present:
cp -r charles-claude-skills/skills/session-continuity/takenotes ~/.claude/skills/
# Standalone, opt-in:
cp -r charles-claude-skills/skills/{newproject,skill-dict,grill-me} ~/.claude/skills/
```

Then **close your Claude Code window and open a fresh one** so the new skills register. (`Cmd+Shift+P → Developer: Reload Window` does NOT free Claude Code's context memory — only a fresh window does.)

Full instructions, symlink-vs-copy trade-offs, and troubleshooting in [INSTALL.md](INSTALL.md).

**Using OpenAI Codex?** Every skill also has a Codex version in [`codex/`](codex/) (run as `$putdown`, `$pickup`, …), generated from the same source and tested end to end in Codex: `cp -r charles-claude-skills/codex/*/ ~/.agents/skills/`. Details in [INSTALL.md](INSTALL.md#using-openai-codex-instead-or-as-well).

## How these were evaluated

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

## Maintaining this repo

If you're forking or contributing, see [MAINTAINING.md](MAINTAINING.md) for the release workflow — how to refresh skills from a canonical source, run the eval, bump the CHANGELOG, and verify sanitization before pushing.

## License

[MIT](LICENSE) — copyright 2026 Charles Baynes. Per-skill `LICENSE` files are also included in each skill folder so the folder is self-contained when copied alone.
