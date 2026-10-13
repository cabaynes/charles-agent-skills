# Codex test results — 2026-10-13 (0.11.0)

Codex CLI `0.160.0`, model `gpt-6-astra`, reasoning effort `medium`. Every scenario ran through the
real `codex exec` in a throwaway `CODEX_HOME`, with git pushes going to a local bare repo, on the
ChatGPT plan's Codex allowance (no API key). Earlier headline runs (0.10.0, 41/41, 2026-10-12;
0.9.0, 30/30, 2026-09-29) are summarised under **Earlier runs**.

## 1. End-to-end scenarios — 42/42

`python3 tests/codex/run_tests.py` · raw results in [last-run.json](last-run.json)

| Skill | Checks | What was checked |
|---|---|---|
| grill-me | 4/4 | Session file at the skill's path; ends on a question; writes nothing else |
| takenotes | 7/7 | Vendor fact → project note; "in every project" preference → global note; loader block added to global `AGENTS.md`; Operational block in the report; a second run adds no duplicate loader block |
| openthreads | 10/10 | `add` creates `OPEN-THREADS.md` in exactly one of its two allowed places, with the five fixed `##` sections and Closed's four `###` groups, and the item as one dated line carrying its due date; a second `add` appends without duplicating; `list` prints both items with per-section counts **and** `Closed in the last 60 days: 0`, leaving the file byte-identical; `done` removes the named line from the open sections only and writes `- [x] <outcome> — added … (user), closed 2026-10-13` under the matching Closed group; no commit |
| putdown | 8/8 | Handoff in `$CODEX_HOME/putdowns/`; "Must address" holds the requested item; paste line is `$pickup`; final message carries a labelled `openthreads:` line; clean tree; **exactly one** commit; pushed |
| pickup | 4/4 | Briefing repeats the "Must address" item; briefs an **Open threads** block naming the item openthreads parked; stops for confirmation (no edits, no commits) |
| newproject | 5/5 | `AGENTS.md` stub, no `CLAUDE.md`, notes folder + index, git initialized |
| skill-dict | 4/4 | Library created; installed skills catalogued; `show` prints an entry |

The scenarios chain on purpose: openthreads parks two items in the test repo, putdown reconciles
the list on the way out, and pickup must surface what is still open on the way back in.

**What 0.10.0's first run (2026-10-12) caught, reported rather than hidden.** That run scored
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

0.10.0's 41/41 run followed those two fixes. The 0.11.0 run above re-ran the same prompts against
the rebuilt skills, with the openthreads scenario grown by one check for the Closed section.

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

Graded from the final messages and files of the 0.10.0 41/41 run (2026-10-12). The 0.11.0 run was
not kept (`--keep` was not passed), so its messages could not be re-read; rows marked **(0.11.0)**
are the ones the harness asserts directly on the files, and were re-checked that way. Each item is
something the skill itself requires.

| Skill | Rubric item | Result |
|---|---|---|
| openthreads | `add` puts a dated item in the section its date implies (Due now) and a dateless idea under a named subgroup of Work | ✓ (`Due now`; `Work waiting on the agent — CLI`) |
| openthreads | Item line ends `— added YYYY-MM-DD (user)`, with `, due …` when given | ✓ |
| openthreads | `list` leads each section with the count line and says what is *not* there ("Nothing overdue") rather than omitting it | ✓ |
| openthreads | `done` moves the item to Closed as an **outcome** — not the task text — keeping the `added` date and source and adding a `closed` date | ✓ **(0.11.0)** file checked by regex; whether the confirmation message quoted the closed line was not re-read |
| openthreads | `list` ends with `Closed in the last 60 days: N` | ✓ **(0.11.0)** |
| openthreads | Says which placement it chose and why when visibility is unknown | ✓ ("repository visibility could not be verified") |
| putdown | Announces the **three**-skill run before starting | ✓ (in log) |
| putdown | Step 5 order: path → fresh-start steps for CLI **and** app → `$pickup` block → takenotes line → openthreads line → push result | ✓ |
| putdown | The openthreads line is labelled and non-silent even when nothing changed | ✓ ("openthreads: unchanged; existing `--dry-run` item preserved") — the 0.11.0 harness checks only that a labelled `openthreads:` line exists, not the new `N closed, N added, N now due, N pruned` wording |
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

- **2026-10-12 (0.10.0), Codex CLI `0.160.0`:** seven skills, **41/41** after the two fixes described
  in section 1. Later the same day a first attempt at the 0.11.0 suite passed grill-me, takenotes
  and openthreads (21 checks, including 10/10 on the Closed-section design) and then hit the ChatGPT
  plan's Codex usage limit as `putdown` started; the harness stopped and reported `BLOCKED` rather
  than scoring failures, and [last-run.json](last-run.json) was left at the 41/41 record until the
  full run the next morning.
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
