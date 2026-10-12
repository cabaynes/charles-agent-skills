# Codex test results — 2026-10-12 (0.10.0, with the 0.11.0 partial re-run)

Codex CLI `0.160.0`, model `gpt-6-astra`, reasoning effort `medium`. Every scenario ran through the
real `codex exec` in a throwaway `CODEX_HOME`, with git pushes going to a local bare repo. The
previous headline run (2026-09-29, Codex CLI `0.158.0-alpha.2.1`, six skills, 30/30) is summarised
under **Earlier runs**.

## 0. 0.11.0 re-run — partial, 21/22 then BLOCKED (2026-10-12, later the same day)

0.11.0 changed `openthreads` (closed items move to a `## Closed` section as outcomes instead of
being deleted; `list` reports the closed count; `reconcile` prunes at 60 days) and reworded one
line each in `putdown` and `pickup`. The openthreads scenario grew to 10 checks (suite: 42) and
was re-run against the rebuilt skill:

| Skill | Checks | Result |
|---|---|---|
| grill-me | 4/4 | unchanged skill, passed |
| takenotes | 7/7 | unchanged skill, passed |
| openthreads | **10/10** | five `##` sections with Closed's four `###` groups on creation; dated line with due date; second add, no duplicate; `list` with per-section counts **and** `Closed in the last 60 days: 0`, file untouched; `done` removed the item from the open sections only and wrote `- [x] <outcome> … added … (user), closed 2026-10-12` under Closed; no commit |
| putdown → skill-dict | — | **BLOCKED**: the ChatGPT plan's Codex usage limit was reached as `putdown` started. The harness stops and reports rather than scoring failures. |

So the behaviour that changed is verified; the four unchanged scenarios (`putdown`, `pickup`,
`newproject`, `skill-dict`) have not been re-run on 0.11.0. [last-run.json](last-run.json) is kept
at the last **complete** run (0.10.0, 41/41, below) rather than overwritten by the partial one.
Re-run `python3 tests/codex/run_tests.py` when the limit resets (or with `--api-key-from`) and
replace this section with the full table.

## 1. End-to-end scenarios — 41/41

`python3 tests/codex/run_tests.py` · raw results in [last-run.json](last-run.json)

| Skill | Checks | What was checked |
|---|---|---|
| grill-me | 4/4 | Session file at the skill's path; ends on a question; writes nothing else |
| takenotes | 7/7 | Vendor fact → project note; "in every project" preference → global note; loader block added to global `AGENTS.md`; Operational block in the report; a second run adds no duplicate loader block |
| openthreads | 9/9 | `add` creates `OPEN-THREADS.md` in exactly one of its two allowed places, with the four fixed `##` sections and the item as one dated line carrying its due date; a second `add` appends without duplicating; `list` prints both items with per-section counts and leaves the file byte-identical; `done` deletes only the named line and keeps the sections; no commit |
| putdown | 8/8 | Handoff in `$CODEX_HOME/putdowns/`; "Must address" holds the requested item; paste line is `$pickup`; final message carries a labelled `openthreads:` line; clean tree; **exactly one** commit; pushed |
| pickup | 4/4 | Briefing repeats the "Must address" item; briefs an **Open threads** block naming the item openthreads parked; stops for confirmation (no edits, no commits) |
| newproject | 5/5 | `AGENTS.md` stub, no `CLAUDE.md`, notes folder + index, git initialized |
| skill-dict | 4/4 | Library created; installed skills catalogued; `show` prints an entry |

The scenarios chain on purpose: openthreads parks two items in the test repo, putdown reconciles
the list on the way out, and pickup must surface what is still open on the way back in.

**What the first run of the day caught, reported rather than hidden.** The first full run scored
33/40:

- **openthreads wrote its file where pickup would never look.** The test repo's origin is a local
  bare repo, so `gh repo view` can't tell its visibility and the skill correctly kept the file out of
  the repo — but under `putdowns/<full-path-slug>/`, the slug the Codex *notes* store uses, instead
  of `putdowns/app/`, the basename slug putdowns and pickup use. The skill text said
  `<project-slug>` without defining it. Both versions now pin it to the CWD basename, "never a
  full-path slug, or pickup won't find the file". Everything else in the scenario (sections, line
  format, counts, no commit) was right the first time.
- **putdown stopped short of committing.** Codex CLI 0.160's automatic review (what
  `--approve-for-me` routes the commit approval through) rejected `git commit && git push` to `main`
  as "not clearly authorized" by `$putdown` alone. The skill did the right thing — it saved the
  handoff, printed every other Step 5 line, said prominently that the commit was blocked and asked
  for approval — but the harness check "exactly one new commit" failed. The test prompt now says
  "You have my approval to commit and push to main; that is what a putdown does", standing in for
  the user who would approve it interactively. This is the confirmed cause of the unexplained
  "wrote its handoff but did not commit" run noted on 2026-09-29.

The 41/41 run above followed those two fixes, on the ChatGPT plan's Codex limit (no API key).

## 2. Spec check — 62/63

`python3 tests/codex/spec_check.py` checks each generated `SKILL.md` against the
[Agent Skills specification](https://agentskills.io/specification): name format and folder match,
description length, only spec frontmatter fields, and that relative links resolve. It also checks
this repo's conventions: the description says when to use the skill and when not to, and the body
shows the `$name` invocation. Nine checks per skill, seven skills.

- **The one miss:** `skill-dict`'s description never says when *not* to use it. The Claude version
  has the same gap. Fixing it changes a trigger description, which needs the Claude trigger eval
  re-run (see [MAINTAINING.md](../../MAINTAINING.md)), so it is recorded here rather than patched.

## 3. Behavior rubric — graded against each skill's own output rules

Graded from the final messages and files of the 41/41 run. Each item is something the skill itself
requires.

| Skill | Rubric item | Result |
|---|---|---|
| openthreads | `add` puts a dated item in the section its date implies (Due now) and a dateless idea under a named subgroup of Work | ✓ (`Due now`; `Work waiting on the agent — CLI`) |
| openthreads | Item line ends `— added YYYY-MM-DD (user)`, with `, due …` when given | ✓ |
| openthreads | `list` leads each section with the count line and says what is *not* there ("Nothing overdue") rather than omitting it | ✓ |
| openthreads | `done` confirms with the deleted text, so a wrong match would be visible | ✓ |
| openthreads | Says which placement it chose and why when visibility is unknown | ✓ ("repository visibility could not be verified") |
| putdown | Announces the **three**-skill run before starting | ✓ (in log) |
| putdown | Step 5 order: path → fresh-start steps for CLI **and** app → `$pickup` block → takenotes line → openthreads line → push result | ✓ |
| putdown | The openthreads line is labelled and non-silent even when nothing changed | ✓ ("openthreads: unchanged; existing `--dry-run` item preserved") |
| putdown | Skips the in-repo copy when repo visibility can't be confirmed, and says so | ✓ |
| pickup | Briefing format: Resumed from / Where we left off / Must address / Next up / Blockers / Open threads | ✓ |
| pickup | "Must address" items quoted **verbatim** from the handoff | ✓ (checked by exact string match) |
| pickup | Open threads block carries the per-section counts, overdue count and oldest date, then the items | ✓ ("1 open — Due now 0 · Decisions 0 · Work 1 · Outside 0; none overdue; oldest added 2026-10-12") |
| pickup | Reports what it couldn't check (fetch blocked by sandbox) instead of skipping it silently | ✓ |
| takenotes | Flags the global write as applying to all projects | ✓ |
| takenotes | Reports adding the loader block to the global `AGENTS.md` | ✓ |
| takenotes | Marks an unverifiable claim `NOT RUN` rather than asserting it | ✓ |
| takenotes | Report uses the full Step 5 block layout (Memory / Instructions / Operational / Claims) | ◐ Operational and Claims present; notes and instructions condensed into bullets (unchanged from 2026-09-29) |
| newproject | Summary uses ✓ / ⊘ for done vs. skipped | ✓ |
| skill-dict | Records missing metadata as `unknown` instead of inventing it | ✓ |
| **Cross-session** | A preference saved as a global note in one session is **followed in a later, separate session** | ✓ newproject ran a dry-run first because the takenotes scenario saved "always show a dry-run before any bulk write" |
| **Cross-skill** | An item parked by one skill is reconciled by a second and briefed by a third, each in its own session | ✓ openthreads → putdown → pickup, the `--dry-run` item |

The cross-session row is still the most important result: Codex doesn't load a notes folder by
itself, and the Codex takenotes relies on a loader block in the global `AGENTS.md` to make notes
load. The cross-skill row is new in 0.10.0 and is the reason openthreads ships inside the
session-continuity set rather than on its own.

## Earlier runs

- **2026-09-29 (0.9.0), Codex CLI `0.158.0-alpha.2.1`:** six skills, **30/30** end to end, 53/54
  spec. The first full run found a harness gap: Codex's sandbox write-protects `.git`, so putdown
  couldn't commit; the harness now routes that approval through `--approve-for-me`. A later run had
  putdown write its handoff but not commit, with logs not kept — now understood as the automatic
  review rejecting an unauthorized push (see section 1). The harness also stops and reports
  `BLOCKED` on a usage limit instead of scoring skill failures. That 30/30 run used an API key
  (`--api-key-from`) in an isolated test home.
- **2026-10-02 (0.9.2), after making putdown + pickup + takenotes one required set:** putdown and
  pickup re-ran **10/10** on the ChatGPT plan. A separate run installed only putdown + pickup, and
  Codex's own message printed the incomplete-set warning
  (`$putdown: takenotes isn't installed — the session-continuity set is putdown + pickup + takenotes.`),
  checked in the agent's messages, not the log, where the skill text itself also appears.

## Not measured

**Trigger accuracy in Codex.** Whether Codex picks each skill *implicitly* at the right moments is
unmeasured; every scenario invoked the skill explicitly (`$name`). The 100% trigger numbers in
[eval-results.md](../../eval-results.md) are Claude Code only.

**A putdown with something to reconcile.** In this run the test session's only leftover work was
the live thread (writing the seed tests), which correctly stays in the handoff, so putdown's
reconcile reported "unchanged". A scenario where the session finishes an open item (so reconcile
must *close* it) is the next check worth adding.
