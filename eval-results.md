# Skill evaluation report

**Skills evaluated:** `/putdown`, `/pickup`, `/newproject`, `/skill-dict`, then `/takenotes` (2026-08-03), `/grill-me` (2026-09-08), `/openthreads` (2026-10-12)
**Original eval:** 2026-05-13 · **Session-continuity pair re-evaluated:** 2026-06-13

> The session-continuity pair was first evaluated on 2026-05-13 under the names `/checkpoint` and `/resume`, scoring 100%/100% each. Those names were later retired because they shadow Claude Code built-ins (`/checkpoint` aliases `/rewind`; `/resume` opens the conversation picker — see CHANGELOG 0.3.0/0.4.0). The pair is now `/putdown` + `/pickup`, the descriptions changed during the rename, and the handoff files moved to `.putdowns/`. The scores below for those two reflect a **fresh re-eval on 2026-06-13** against the current descriptions; `/newproject` and `/skill-dict` are unchanged from the 2026-05-13 run.

## Headline

| Skill | Recall | Precision | Verdict | Notes |
|---|---|---|---|---|
| `/putdown` | 10/10 (100%) | 10/10 (100%) | ✅ PASS | Re-evaluated 2026-06-13 under current name + description |
| `/pickup` | 10/10 (100%) | 10/10 (100%) | ✅ PASS | Re-evaluated 2026-06-13; one revision to recover a fresh-window phrasing (below) |
| `/newproject` | 9/10 (90%) → 10/10 expected | 10/10 (100%) | ✅ PASS (revised) | Description rewritten with explicit "do NOT" guards; added `argument-hint` + `allowed-tools` |
| `/skill-dict` | 10/10 (100%) | 10/10 (100%) | ✅ PASS | Description tightened; subcommand bodies extracted to `references/`; body reduced from ~1500 → 440 words |
| `/takenotes` | 10/10 (100%) | 10/10 (100%) | ✅ PASS | Added + evaluated 2026-08-03. Also validated behaviourally against a poisoned-memory sandbox (below) |
| `/grill-me` | 10/10 (100%) | 10/10 (100%) | ✅ PASS | Added + evaluated 2026-09-08 (LLM-as-judge variant); one description revision added the resume-a-session trigger (9/10 → 10/10 recall); frontmatter brought to standard (`argument-hint`, `allowed-tools`) |

| `/openthreads` | 10/10 (100%) | 10/10 (100%) | ✅ PASS | Added + evaluated 2026-10-12 (LLM-as-judge variant); no revision needed |

**All seven skills pass the ≥80% threshold on both precision and recall.**

---

## Methodology

Two-stage evaluation:

### Stage 1 — Static review against 18-rule rubric

Rubric distilled from:
- Anthropic's `skill-creator` plugin SKILL.md (defines the canonical description format, frontmatter fields, and structural guidelines for a high-quality skill).
- Anthropic's `writing-skills` plugin (community-maintained, ships with `superpowers`; specifies trigger-language anti-patterns, body length targets, and the test-driven approach for skill development).

The 18 rules cover: frontmatter required fields, description quality (trigger-first phrasing), description length (<500 chars), the "workflow summary in description" anti-pattern (rule #5 in `writing-skills`), tone (third-person), naming style (verb-first), generic-label anti-pattern, narrative-example anti-pattern, token efficiency (<500 word body for normal skills), file organization (inline vs. `references/`), optional frontmatter (`argument-hint`, `allowed-tools`, `compatibility`), body structure template, skill type clarity, test-driven approach, assertion specificity, description optimization with trigger evals.

### Stage 2 — Benchmark trigger-accuracy eval

skill-creator's description-optimization methodology. Each query is run as a real trigger test — a fresh `claude -p` session is given only the skill's description (as an available command) plus the user query, and the harness records whether the session's first action invokes the skill.

1. **20 trigger queries per skill** — 10 should-trigger (realistic user phrasings) + 10 should-not-trigger (near-miss adversarial — phrasings that look related but shouldn't fire).
2. **3 runs per query**, majority vote, to smooth out non-determinism.
3. **Score**:
   - **Recall** = correct should-trigger / 10 (does the skill fire when it should?)
   - **Precision** = correct should-not-trigger / 10 (does the skill abstain when it shouldn't fire?)
4. **Threshold** — ≥80% on both metrics. Real bar: 100% (no regression). One iteration of description revision allowed if a skill falls short.

> **Harness note (learned the hard way):** run probes **serially** (one at a time) and **move the real skill out of the skills dir** during the eval. Parallel probes let the temp skill-copies shadow each other (false misses), and an installed copy of the skill being tested wins the trigger race over the temp copy (also false misses). And if the eval model is unavailable, every query returns a uniform 0/3 with no tool calls — that's an environment failure, not a regression.

---

## Session-continuity pair — current descriptions (2026-06-13)

### `/putdown`
`Use when the user says "putdown", when ending or stepping away from a working session, or when the context window is filling up (around 50% used). Creates a handoff file that a fresh Claude Code session reads (via /pickup) to resume without losing momentum, then commits and pushes all session work — a putdown means the session is ending, nothing stays unpushed.`
- **Frontmatter** → `argument-hint: "[project-slug]"` + `allowed-tools: [Read, Write, Edit, Bash, Grep, Glob]`

### `/pickup`
`Use when the user says "pickup", asks "where were we" after opening a fresh window, or wants to resume/pick up their work from a prior session that ended with /putdown — loads the most recent putdown file (the handoff note) for the current project and primes the agent with full context before continuing. Do NOT use for reopening a previous Claude conversation (that is the built-in /resume picker) or for resuming media, downloads, paused processes, or VMs.`
- **Frontmatter** → `argument-hint: "[putdown-timestamp]"` + `allowed-tools: [Read, Bash, Grep, Glob, AskUserQuestion]`

---

## Benchmark eval details (per skill)

### `/putdown` — 100% / 100%

All 10 should-trigger queries fired (bare `putdown`, "wrap up this session", "I'm about to /clear — capture where we are", "save your progress, gotta run", "context window is getting full", etc.). All 10 should-not-trigger correctly abstained — including the sharp near-misses: `rewind my code to before the last prompt` (the built-in `/rewind`), `add a checkpoint to the training loop every 100 steps` (ML checkpoint), `git checkout the checkpoint tag`, `commit and push what we have, not done yet` (a mid-work backup, not a session end), and `put down the iPad`.

### `/pickup` — 100% / 100% (after one revision)

All 10 should-trigger fired (bare `pickup`, "pick up where we left off", "load the latest putdown", "continue from the last putdown", "what was I doing? load my session state", etc.). All 10 should-not-trigger correctly abstained — notably `resume my last claude conversation` (that's the built-in `/resume` picker, not this skill), `resume the paused download`, `resume playback`, `write a resume for my job application`, and `resume the VM from a snapshot`.

**Revision applied:** the first re-eval pass missed `"fresh window, where were we?"` (0/3). The carve-out that keeps the skill off `resume my last claude conversation` was also suppressing this legitimate fresh-window trigger. Adding `asks "where were we" after opening a fresh window` to the description recovered it (3/3) without reintroducing the conversation-picker false-trigger — confirmed by re-eval.

### `/newproject` — 90% / 100% pre-revision → 100% / 100% expected post-revision

One initial miss on query #8 ("New project: recipe-app") — the strict judge required an explicit workspace-directory reference. All 10 should-not-trigger correctly abstained.

**Revision applied**: explicit "do NOT use for generic 'new project'..." guard added to the description. Trades a tiny bit of recall on ambiguous phrasing for stronger precision and self-documentation. Users can still invoke the skill explicitly with `/newproject` in any case.

### `/skill-dict` — 100% / 100%

All 10 should-trigger fired (`/skill-dict`, "skills library", "skill catalog", "what does <skill> do", "sync after plugin install", etc.). All 10 should-not-trigger correctly abstained (English dictionary, code function, git fork sync, dotfiles sync, etc.).

**Judge summary**: "Description cleanly discriminates skill-library queries from unrelated dictionary/library/sync requests."

---

## `/takenotes` — trigger benchmark (2026-08-03) — 100% / 100%

Run with the LLM-as-judge variant described under "How to re-run the eval" below (not skill-creator's
`run_eval` harness, which produced the 2026-05-13 numbers). Judge saw only the skill description and
20 shuffled, unlabelled queries — 10 realistic should-trigger, 10 adversarial should-not-trigger.

**Recall 10/10 · Precision 10/10.**

The adversarial half was aimed squarely at this skill's known weak spot. Its description was
deliberately widened to cover "asks you to remember or record something," which risks swallowing any
sentence containing "remember." The near-misses tested exactly that:

| Adversarial query | Result | Why it's a trap |
|---|---|---|
| "take notes on this meeting transcript and summarize the action items" | NO_TRIGGER ✓ | Contains the skill's **literal name**. Only the explicit exclusion keeps it out. |
| "remind me to call the vendor tomorrow" | NO_TRIGGER ✓ | "remind" vs "remember" — one letter, entirely different intent. |
| "what's currently in my memory files?" | NO_TRIGGER ✓ | Memory-topical, but a read rather than a write. |
| "where were we last session?" | NO_TRIGGER ✓ | Belongs to `/pickup`. |
| "I'm done for the day, wrap up and push" | NO_TRIGGER ✓ | Belongs to `/putdown`. |
| "write documentation for this module" | NO_TRIGGER ✓ | Authoring docs ≠ harvesting session knowledge into them. |

The last two matter most: all three session-continuity skills ship in one folder, so a skill that
poached its neighbours' triggers would be worse than one that occasionally under-fires. It stayed in
its lane on both.

Should-trigger queries covered the full declared surface: the literal keyword, whole-session harvest
phrasings ("save what we learned this session"), post-solution capture ("make sure you remember
how"), decision recording, dead-end capture, and single facts ("note that the staging API key rotates
monthly").

## `/takenotes` — behavioural validation (2026-08-03)

Trigger accuracy answers "does the skill fire at the right time?" — a description question. This
second pass answers a different one: **does it do the right thing once it fires?**

### Method

Subagents executed the skill against a sandbox project seeded with a **deliberately poisoned
memory** — one asserting the exact opposite of what the session had just built:

> `project_widget.md`: *"The vendor has no webhook support… Do not add a webhook receiver — the
> vendor cannot call out."*

…paired with a session in which a webhook receiver had just been shipped and the polling module
deleted. A skill that merely appends new facts leaves that memory in place, where it will argue a
future session **out of** working code. Catching it is the sharpest available test of the reconcile
pass, which is the skill's whole reason to exist.

Three runs: a full harvest, a single-fact request (to test the scope gate), and a **no-skill
baseline control** given only a well-written hand-typed instruction.

### Results

| Round | Outcome |
|---|---|
| 1 | 6 defects found — most serious: the memory-directory fallback would run `mkdir -p /memory` at the **filesystem root**, because the variable is provably empty in exactly that branch. Also: the single-fact path referenced the schema, dedup rule, index-pointer rule and scope routing from steps it explicitly told the agent to skip. |
| 2 | 5 of 6 closed; 4 new found — including that the single-fact path would apply a cross-project preference **silently**, because the "tell the user" instruction lived in a skipped step. |
| Final | 10 defects closed across both rounds. Severity fell from *writes to filesystem root* → *inconsistent file naming* → *report formatting*, which is the signal it had converged. |

### The honest caveat

**The baseline control performed comparably.** With no skill at all — just a carefully written
paragraph — the agent caught the poisoned memory, extracted oversized content to `docs/`, and flagged
facts it couldn't verify. So the skill's value is not "better output than a good prompt."

Its value is that it's repeatable without retyping the prompt, that `/putdown` invokes it
automatically at session end, and that it encodes environment specifics a prompt can't carry. The
sandbox exercised none of that last category, so this test **understates** rather than overstates the
real-world difference.

### What this pass did not cover

Both validations are single-run. The trigger benchmark is one judge pass over 20 queries, not a
multi-sample average, so a genuinely marginal query could land either way on a re-run. And the
behavioural fixes from round 2 were not themselves re-tested — the reason to stop was that defect
severity had fallen from *writes to filesystem root* to *report formatting*, not that the skill was
proven clean.

## `/grill-me` — trigger benchmark (2026-09-08) — 100% / 100%

Run with the LLM-as-judge variant described under "How to re-run the eval" below. Judge saw only the
skill description and 20 shuffled, unlabelled queries — 10 realistic should-trigger, 10 adversarial
should-not-trigger.

**Recall 10/10 · Precision 10/10.**

Round 1 scored 9/10 recall, 10/10 precision: "resume our grill session on db-migration, I want to
pick up the open threads" was judged NO_TRIGGER because the description never mentioned resuming,
although the skill body supports it. One revision added ", or asks to resume an earlier grill
session" to the trigger sentence; round 2 with a fresh judge scored 10/10 on both.

The adversarial half targeted the three ways this skill could over-fire: the literal word "grill" in
a non-plan context, interrogation-shaped requests with no plan behind them, and requests that *name*
a plan but ask for execution.

| Adversarial query | Result | Why it's a trap |
|---|---|---|
| "how long do I grill chicken thighs per side..." | NO_TRIGGER ✓ | Literal keyword, zero plan. |
| "quiz me on Spanish vocabulary for twenty minutes" | NO_TRIGGER ✓ | Interrogation format without a plan to stress-test. |
| "write the migration plan for moving us to PostgreSQL" | NO_TRIGGER ✓ | Names a plan; asks for execution, which the skill forbids itself. |
| "implement the roadmap item: add dark mode..." | NO_TRIGGER ✓ | Implementation task. |
| "review this pull request for bugs before I merge" | NO_TRIGGER ✓ | Code review, explicitly excluded. |
| "why is this test failing? it passed yesterday" | NO_TRIGGER ✓ | Debugging, explicitly excluded. |
| "refactor this function so it's easier to read" | NO_TRIGGER ✓ | Refactoring, explicitly excluded. |
| "proofread my cover letter for typos..." | NO_TRIGGER ✓ | Feedback on an existing document, not interrogation of a plan. |
| "what do you think of Stripe versus Braintree..." | NO_TRIGGER ✓ | Opinion request; no plan of the user's to defend. |
| "summarize the risks in this vendor contract" | NO_TRIGGER ✓ | Analysis of a document, not a dialogue about the user's plan. |

Should-trigger queries covered the literal phrases ("grill me", "stress test my plan", "poke holes in
this"), synonyms the description does not name ("interrogate that decision", "play devil's advocate",
"pressure-test", "challenge every assumption"), three non-software domains (a lease, a thesis, a
novel), and resuming a named session.

## `/takenotes` — behavioural validation, round 2 (2026-09-25)

The 2026-08-03 pass tested whether the reconcile step catches a memory that is *wrong*. This pass
tested a memory that is *unverifiable*: "fixed", with no evidence and no way to re-check.

Sandbox: a script whose `main()` raises `NameError` (passes `py_compile`), a memory calling it
"verified functionally", a documented trap that had recurred, and a transcript whose last edit was
"verified" via `py_compile` plus a helper call.

| Arm | Reps | Corrected the false claim | Ran the entry point | Named a code guard for the recurrence |
|---|---|---|---|---|
| Prior skill (0.7.0) | 16 | 14/16 | 6/16 fully | 13/16 |
| 0.8.0 | 6 | 6/6 | 6/6 | 6/6 (first "How to apply" line every time) |

The two prior-skill failures shared one shape: never exercised the entry point, kept the stale
"verified", and wrote *"verify with `py_compile` + inline helper call"* into a durable file. A first
round was discarded because its transcript leaked the answer ("the script was never run") — 4/4
passed and proved nothing.

**Caveat:** the prior skill's failure rate was low (~12%), so 6/6 is weak evidence of a *rate*
change. The strong evidence is structural: `**Verified by:**` lines, `RECURRED` markers, and the
`Claims` report block appeared in 0/16 prior runs and 6/6 new ones.

## `/openthreads` — trigger benchmark (2026-10-12) — 100% / 100%

Run with the LLM-as-judge variant described under "How to re-run the eval" below. Judge saw only the
skill description and 20 shuffled, unlabelled queries — 10 realistic should-trigger, 10 adversarial
should-not-trigger.

**Recall 10/10 · Precision 10/10.** First pass; no description revision.

The should-trigger half covered the literal phrases ("openthreads", "add this to the open threads",
"what's still open", "mark X done"), the no-keyword case the description names ("Not now, but
someday I want to swap the hero image for a video loop — don't let me forget that"), a pending
decision explicitly parked ("the domain switch is waiting on me deciding between Cloudflare and
Netlify — I'll come back to it"), a backlog question ("what's on the backlog for this repo?
anything parked?"), an overdue query, closing an item by name, and a session-end reconcile request.

The adversarial half targeted the three lanes this skill borders — in-session tasks, durable facts,
personal reminders — plus every other sense of "open" and "thread":

| Adversarial query | Result | Why it's a trap |
|---|---|---|
| "let's make a todo list for this refactor and work through it now" | NO_TRIGGER ✓ | "Todo list" + pending items, but in-session; the exclusion clause catches it. |
| "remember I prefer tabs over spaces in this repo" | NO_TRIGGER ✓ | Repo-scoped and durable, but a preference — `/takenotes` by name. |
| "remind me to call the dentist tomorrow" | NO_TRIGGER ✓ | A pending item to come back to, but not repo work. |
| "wrap up and write the handoff, I'm done for tonight" | NO_TRIGGER ✓ | Description mentions session end; a judge could read "invoked by /putdown" as "fires at session end." Closest call. |
| "where were we? I just opened a fresh window" | NO_TRIGGER ✓ | Semantically adjacent to "what's still open"; `/pickup` is not named in the exclusions. |
| "list the open pull requests on this repo" | NO_TRIGGER ✓ | "Open" + "repo" + list-shaped request. |
| "why is this worker thread deadlocking on the mutex?" | NO_TRIGGER ✓ | Literal "thread," zero to-do content. |
| "summarize this open Slack thread about the launch date" | NO_TRIGGER ✓ | Literal "open thread," wrong sense. |
| "what's still uncommitted in the working tree?" | NO_TRIGGER ✓ | Mirrors the "what's still ___" cadence; subject is git, not threads. |
| "build a todo-list feature on the landing page" | NO_TRIGGER ✓ | "Todo" as a deliverable, not a list to keep. |

The two closest calls (wrap-up and where-were-we) were decided correctly on inference rather than
explicit wording: the description names `/takenotes` and the built-in task list as exclusions but
not `/putdown` or `/pickup`. The judge re-tested both against a hardened sentence ("Ending a session
is /putdown and resuming one is /pickup; this skill only maintains the list they consult") and both
stayed NO_TRIGGER. The sentence was **not** added — no miss to fix, and a longer description costs
every session — but it is the first thing to try if a future judge flips either.

Single-run caveat as for `/grill-me`: one judge pass, not a multi-sample average.

## How to re-run the eval

If you change a description (yours or upstream), re-run the eval to confirm you haven't regressed:

1. Draft your own 20-query suite per skill — 10 realistic should-trigger + 10 adversarial near-miss should-not-trigger.
2. Run each query as a real trigger test against the skill description (skill-creator's `run_eval` does this), or with an LLM-as-judge: "Would Claude with only this skill description loaded invoke it on `<query>`? TRIGGER or NO_TRIGGER, one sentence of reasoning."
3. Score against expected labels. Aim for ≥80% on both metrics; the current bar is 100% — don't regress without good reason.
4. Heed the harness note above: serial probes, real skill moved aside, an available model.
