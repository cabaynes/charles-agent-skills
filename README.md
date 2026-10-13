# charles-agent-skills

Seven skills that I've built that are fundamental to my agentic workflow. Built for both **[Claude Code](https://claude.com/claude-code)** and **[OpenAI Codex](https://developers.openai.com/codex)**. Both tools use the same open [Agent Skills](https://agentskills.io/specification) format, so every skill here ships in two versions: one per tool, built from a single source so they never drift apart.

- **Claude Code:** evaluated against Anthropic's `writing-skills` + `skill-creator` rubric, with **100% trigger accuracy** on a 20-query precision/recall benchmark per skill.
- **Codex:** every skill tested end to end through the real Codex CLI (**42/42** checks), plus a spec check and a behavior rubric.

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

**The Session Continuity Loop** — one folder, one set: `openthreads`, `takenotes`, `putdown` and `pickup` go together, in the order you meet them in a session. Docs: [claude/session-continuity/README.md](claude/session-continuity/README.md)

Without this four-skill set, an agent's working memory resets with every fresh session. These four fill the memory gap between sessions and keep that memory healthy and complete, preventing duplicated mistakes and stale knowledge. Use openthreads and takenotes during a work session as you see fit, then end every session with a putdown. Start your next session with a pickup, and never repeat yourself again.

**`/openthreads`**
- **What it does:** Keeps the project's living to-do list in one file: parked ideas, decisions waiting on you, work nobody has picked up yet. Finished items become a 60-day log of outcomes.
- **Why I built it:** A handoff holds one session's next steps and memory holds facts. Neither held the backlog, so parked ideas lived in people's heads until someone re-read two weeks of notes.
- **When to use it:** As you work, whenever something gets parked: an idea for later, a question for someone else, a task no session owns yet. Putdown sweeps up anything you forgot.

**`/takenotes`**
- **What it does:** Saves what a session learned (decisions, dead ends, how the tools really behave) to permanent memory, then goes back over what's already stored and fixes anything that has become false.
- **Why I built it:** Every assistant can save new facts; almost none check whether old ones are still true. Stale memory is worse than none: it argues the agent out of work that's already done.
- **When to use it:** Any time you learn something that should outlive the session, not only at the end. A Putdown is a sticky note for tomorrow; a Takenote is a fact for forever.

**`/putdown`**
- **What it does:** Ends a session with a handoff note: where things stand, what's half-done, what must not slip, what was tried and failed. Then it saves everything to GitHub.
- **Why I built it:** A fresh session wipes the agent's working memory. Without a handoff, every session starts from zero and repeats the same dead ends.
- **When to use it:** At the end of every working session, or when the context window is filling up. It runs Takenotes first and Openthreads last, so one command saves all three.

**`/pickup`**
- **What it does:** Starts a fresh session by finding the latest handoff and the open threads, briefing you on both, and waiting for your go-ahead before doing anything.
- **Why I built it:** The other half of Putdown. A note nobody reads is useless; this makes reading it automatic. A handoff written in Claude Code can even be picked up in Codex, and vice versa.
- **When to use it:** First thing in a new session, before any other work, so you start with the backlog and last session's state in view.

The split is by lifetime: a putdown is a note to your next session and goes stale once you act on it; a takenote is a fact you keep forever; an open thread is a task that outlives any one session and becomes a one-line outcome, kept 60 days, the day it's done. `putdown` runs `takenotes` as its harvest step and `openthreads` as its reconcile step, so one command saves all three.

**Stand-alone skills.** Three skills that work on their own, with no set to join. Pick whichever you like; each installs with one line (see Install below).

**`/newproject`** — docs: [claude/newproject/README.md](claude/newproject/README.md)
- **What it does:** One command builds a new project folder with everything it needs: agent instructions, a memory folder, git, an optional GitHub repo, and an entry in the workspace index.
- **Why I built it:** Setting a project up by hand takes a dozen steps and it's easy to forget one.
- **When to use it:** Whenever you start a project. It's safe to re-run on a folder you already have: it only adds what's missing and never overwrites anything.

**`/skill-dict`** — docs: [claude/skill-dict/README.md](claude/skill-dict/README.md)
- **What it does:** Keeps a tidy catalog of every skill and plugin you've installed, with one entry per skill and a one-table index. It can sync the catalog and check for updates.
- **Why I built it:** Asking an agent "what skills do I have?" normally dumps thousands of words into the conversation. The catalog answers in one small table, about 8× cheaper every time.
- **When to use it:** When you want to know what's installed or what a skill does, and after you add or update a plugin so the catalog stays current.

**`/grill-me`** — docs: [claude/grill-me/README.md](claude/grill-me/README.md)
- **What it does:** Turns the agent into a sharp, friendly interrogator for any plan, design, or idea: it asks the questions you're avoiding, one thread at a time, and keeps a written record of what was decided.
- **Why I built it:** It's the only skill here that pushes back. Everything else makes it easier to build; this one makes it harder to build the wrong thing.
- **When to use it:** Before you build. Bring a plan, a design, or a business idea you want stress-tested. Its one hard rule: it never does the task itself, only interrogates it.

**What changes in the Codex versions:** the workflow is the same; only tool-specific parts differ. `AGENTS.md` replaces `CLAUDE.md`; questions come as numbered lists in chat; `/new` or a New chat replaces `/clear`; `takenotes` saves Markdown notes that a short block in your global `AGENTS.md` loads each session (Codex has no memory a skill can write to). Full table: [INSTALL.md](INSTALL.md#using-openai-codex-instead-or-as-well).

## The workspace pattern these skills assume

Each skill works on a single project folder. Together they work best on a **multi-project workspace**: one root folder with a short umbrella `CLAUDE.md`, one subfolder per project, and a shared memory hub that a small script symlinks into every project so a preference written once applies everywhere. `/newproject` builds the spokes, `/takenotes` routes memory to hub or project, `/putdown` + `/pickup` carry sessions across the gaps, `/openthreads` keeps each project's backlog where the next session will see it, and `/grill-me` (installed separately, see INSTALL.md) makes you defend a plan before any of that starts.

The [`workspace/`](workspace/) folder has the whole thing: a copy-and-paste setup guide, the `fanout-memory.sh` helper that `/newproject` and `/takenotes` look for, an umbrella `CLAUDE.md` template, a test script that proves the helper works on your machine, and [`STACK.md`](workspace/STACK.md), the rest of the tool stack in install order.

**Setting someone else up, or letting Claude do it?** Point Claude at the guide and say "set me up like this":

```
https://raw.githubusercontent.com/cabaynes/charles-agent-skills/main/workspace/README.md
```

The guide opens with a runbook section written for a Claude agent acting on a person's behalf.

## Install (quick)

### Claude Code

Per unit, each line self-contained (clones to a temp folder, copies, cleans up):

```bash
# The Session Continuity Loop (openthreads + takenotes + putdown + pickup go together):
d=$(mktemp -d) && git clone --depth 1 https://github.com/cabaynes/charles-agent-skills.git "$d" && mkdir -p ~/.claude/skills && cp -r "$d"/claude/session-continuity/{openthreads,takenotes,putdown,pickup} ~/.claude/skills/ && rm -rf "$d"
# Stand-alone, pick-and-choose:
d=$(mktemp -d) && git clone --depth 1 https://github.com/cabaynes/charles-agent-skills.git "$d" && mkdir -p ~/.claude/skills && cp -r "$d"/claude/newproject ~/.claude/skills/ && rm -rf "$d"
d=$(mktemp -d) && git clone --depth 1 https://github.com/cabaynes/charles-agent-skills.git "$d" && mkdir -p ~/.claude/skills && cp -r "$d"/claude/skill-dict ~/.claude/skills/ && rm -rf "$d"
d=$(mktemp -d) && git clone --depth 1 https://github.com/cabaynes/charles-agent-skills.git "$d" && mkdir -p ~/.claude/skills && cp -r "$d"/claude/grill-me ~/.claude/skills/ && rm -rf "$d"
```

Everything at once:

```bash
git clone https://github.com/cabaynes/charles-agent-skills.git
mkdir -p ~/.claude/skills
cp -r charles-agent-skills/claude/session-continuity/{openthreads,takenotes,putdown,pickup} ~/.claude/skills/
cp -r charles-agent-skills/claude/{newproject,skill-dict,grill-me} ~/.claude/skills/
```

Then **close your Claude Code window and open a fresh one** so the new skills register. (`Cmd+Shift+P → Developer: Reload Window` does NOT free Claude Code's context memory — only a fresh window does.)

### OpenAI Codex

Per unit, each line self-contained:

```bash
# The Session Continuity Loop (openthreads + takenotes + putdown + pickup go together):
d=$(mktemp -d) && git clone --depth 1 https://github.com/cabaynes/charles-agent-skills.git "$d" && mkdir -p ~/.agents/skills && cp -r "$d"/codex/{openthreads,takenotes,putdown,pickup} ~/.agents/skills/ && rm -rf "$d"
# Stand-alone, pick-and-choose:
d=$(mktemp -d) && git clone --depth 1 https://github.com/cabaynes/charles-agent-skills.git "$d" && mkdir -p ~/.agents/skills && cp -r "$d"/codex/newproject ~/.agents/skills/ && rm -rf "$d"
d=$(mktemp -d) && git clone --depth 1 https://github.com/cabaynes/charles-agent-skills.git "$d" && mkdir -p ~/.agents/skills && cp -r "$d"/codex/skill-dict ~/.agents/skills/ && rm -rf "$d"
d=$(mktemp -d) && git clone --depth 1 https://github.com/cabaynes/charles-agent-skills.git "$d" && mkdir -p ~/.agents/skills && cp -r "$d"/codex/grill-me ~/.agents/skills/ && rm -rf "$d"
```

Everything at once:

```bash
git clone https://github.com/cabaynes/charles-agent-skills.git
mkdir -p ~/.agents/skills
cp -r charles-agent-skills/codex/{grill-me,newproject,openthreads,pickup,putdown,skill-dict,takenotes} ~/.agents/skills/
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
| `/openthreads` | 10/10 | 10/10 | 2026-10-12 |

`/takenotes` also went through a second, different kind of validation: subagents **executed** it against a sandbox seeded with a deliberately poisoned memory, over two rounds that found and closed ten defects — and again on 2026-09-25 against a memory that claimed a fix nobody had ever run (0.8.0). Trigger accuracy measures whether a skill *fires at the right time*; that measures whether it *does the right thing once it fires*. Both are in [eval-results.md](eval-results.md).

Full methodology, per-query verdicts, and revision rationale in [eval-results.md](eval-results.md).

### Codex — end-to-end behavior

Before porting, Codex itself reviewed every skill read-only. Its findings shaped the Codex versions and surfaced five real bugs in the Claude versions, fixed in 0.8.2. Each Codex version then ran through the real Codex CLI in a throwaway environment:

- **42/42 end-to-end checks.** For example: `putdown` makes exactly one commit and pushes, `pickup` repeats the handoff's "Must address" items word for word and briefs the open threads before it waits, `takenotes` stores a cross-project preference that a *later, separate* session follows, and `openthreads` adds, lists and closes items without ever rewriting the file or committing.
- **62/63 spec checks** against the Agent Skills specification. The one miss, `skill-dict`'s description lacking a when-not-to-use clause, applies to both versions and is recorded, not hidden.
- **A behavior rubric** grading each skill's output against the skill's own rules.

Codex *trigger* accuracy (whether Codex picks a skill without being asked) is not measured yet; every Codex test invoked the skill by name. Details in [tests/codex/RESULTS.md](tests/codex/RESULTS.md).

## Maintaining this repo

If you're forking or contributing, see [MAINTAINING.md](MAINTAINING.md) for the release workflow — how to refresh the Claude skills from a canonical source, rebuild and test the Codex versions, run the eval, bump the CHANGELOG, and verify sanitization before pushing.

## License

[MIT](LICENSE) — copyright 2026 Charles Baynes. Per-skill `LICENSE` files are also included in each skill folder so the folder is self-contained when copied alone.
