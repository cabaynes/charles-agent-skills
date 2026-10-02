# Codex test results — 2026-09-29

Codex CLI `0.158.0-alpha.2.1`, model `gpt-6-astra`, reasoning effort `medium`. Every scenario ran
through the real `codex exec` in a throwaway `CODEX_HOME`, with git pushes going to a local bare repo.

## 1. End-to-end scenarios — 30/30

`python3 tests/codex/run_tests.py` · raw results in [last-run.json](last-run.json)

| Skill | Checks | What was checked |
|---|---|---|
| grill-me | 4/4 | Session file at the skill's path; ends on a question; writes nothing else |
| takenotes | 7/7 | Vendor fact → project note; "in every project" preference → global note; loader block added to global `AGENTS.md`; Operational block in the report; a second run adds no duplicate loader block |
| putdown | 7/7 | Handoff in `$CODEX_HOME/putdowns/`; "Must address" holds the requested item; paste line is `$pickup`; clean tree; **exactly one** commit; pushed |
| pickup | 3/3 | Briefing repeats the "Must address" item; stops for confirmation (no edits, no commits) |
| newproject | 5/5 | `AGENTS.md` stub, no `CLAUDE.md`, notes folder + index, git initialized |
| skill-dict | 4/4 | Library created; installed skills catalogued; `show` prints an entry |

**Run history, reported rather than hidden.** The first full run found a harness gap: Codex's
sandbox write-protects `.git`, so putdown couldn't commit. The skill reported this prominently
instead of failing silently. The harness now routes that approval through `--approve-for-me`. One
later full run had putdown write its handoff but not commit, and the runs right after it hit the
ChatGPT plan's Codex usage limit. That run's logs weren't kept, so its cause is unconfirmed. The
harness now stops and reports `BLOCKED` on a usage limit instead of scoring skill failures. The 30/30
run above used an API key (`--api-key-from`), in an isolated test home.

## 2. Spec check — 53/54

`python3 tests/codex/spec_check.py` checks each generated `SKILL.md` against the
[Agent Skills specification](https://agentskills.io/specification): name format and folder match,
description length, only spec frontmatter fields, and that relative links resolve. It also checks
this repo's conventions: the description says when to use the skill and when not to, and the body
shows the `$name` invocation.

- **The one miss:** `skill-dict`'s description never says when *not* to use it. The Claude version
  has the same gap. Fixing it changes a trigger description, which needs the Claude trigger eval
  re-run (see [MAINTAINING.md](../../MAINTAINING.md)), so it is recorded here rather than patched.

## 3. Behavior rubric — graded against each skill's own output rules

Graded from the final messages and files of the 30/30 run. Each item is something the skill itself
requires.

| Skill | Rubric item | Result |
|---|---|---|
| putdown | Announces the two-skill run before starting | ✓ (in log) |
| putdown | Step 5 order: path → fresh-start steps for CLI **and** app → `$pickup` block → takenotes line → push result | ✓ |
| putdown | Skips the in-repo copy when repo visibility can't be confirmed, and says so | ✓ |
| pickup | Briefing format: Resumed from / Where we left off / Must address / Next up / Blockers | ✓ |
| pickup | "Must address" items quoted **verbatim** from the handoff | ✓ (checked by exact string match) |
| pickup | Reports what it couldn't check (fetch blocked by sandbox) instead of skipping it silently | ✓ |
| takenotes | Flags the global write as applying to all projects | ✓ |
| takenotes | Reports adding the loader block to the global `AGENTS.md` | ✓ |
| takenotes | Marks an unverifiable claim `NOT RUN` rather than asserting it | ✓ |
| takenotes | Report uses the full Step 5 block layout (Memory / Instructions / Operational / Claims) | ◐ Operational and Claims present; notes and instructions condensed into bullets |
| newproject | Summary uses ✓ / ⊘ for done vs. skipped | ✓ |
| skill-dict | Records missing metadata as `unknown` instead of inventing it | ✓ |
| **Cross-session** | A preference saved as a global note in one session is **followed in a later, separate session** | ✓ newproject ran a dry-run first because the takenotes scenario saved "always show a dry-run before any bulk write" |

The cross-session row is the most important result. Codex doesn't load a notes folder by itself, and
the Codex takenotes relies on a loader block in the global `AGENTS.md` to make notes load. This run
shows the block working.

## Re-runs

- **2026-10-02, after making putdown + pickup + takenotes one required set (0.9.2):** putdown and
  pickup re-ran **10/10** on the ChatGPT plan. A separate run installed only putdown + pickup, and
  Codex's own message printed the incomplete-set warning
  (`$putdown: takenotes isn't installed — the session-continuity set is putdown + pickup + takenotes.`),
  checked in the agent's messages, not the log, where the skill text itself also appears.

## Not measured

**Trigger accuracy in Codex.** Whether Codex picks each skill *implicitly* at the right moments is
unmeasured; every scenario invoked the skill explicitly (`$name`). The 100% trigger numbers in
[eval-results.md](../../eval-results.md) are Claude Code only.
