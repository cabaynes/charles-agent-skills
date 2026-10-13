# Session Continuity Loop — `/openthreads` + `/takenotes` + `/putdown` + `/pickup`

> `/openthreads`, `/takenotes`, `/putdown` and `/pickup` are **one set** — install all four.
> The first two you use as you work; `/putdown` runs both of them on the way out, and `/pickup`
> reads what they kept on the way back in. That's the loop.

Without this four-skill set, an agent's working memory resets with every fresh session. These four fill the memory gap between sessions and keep that memory healthy and complete, preventing duplicated mistakes and stale knowledge. Use openthreads and takenotes during a work session as you see fit, then end every session with a putdown. Start your next session with a pickup, and never repeat yourself again.

## What

Four skills that preserve work across Claude Code context resets, in the order you meet them in a session. The last one leads straight back to the first, which is why it's a loop:

1. **`/openthreads`** — *as you work.* Keeps one file per project, `OPEN-THREADS.md`, of everything pending that no single session owns: ideas parked mid-session, decisions waiting on you, work no session has picked up yet, things waiting on outside parties. "Add this to the open threads" and it's parked, concretely, where the next session will see it.
2. **`/takenotes`** — *as you work.* Harvests what a session *learned* into permanent storage (typed memory, `CLAUDE.md`, or a `docs/` file), and — the part nothing else does — goes back over what's **already** stored and corrects whatever this session made false. "Remember this" writes one memory and stops.
3. **`/putdown`** — *to end the session* (or whenever your context window is filling up). Writes a structured handoff file: what you accomplished, what's still in flight, file paths you were mid-edit on, decisions you made and why, blockers waiting on you, and (critically) approaches you ruled out so the next session doesn't redo them. It runs `/takenotes` and `/openthreads reconcile` on the way, so anything you didn't park or note during the session is swept up before the commit and push.
4. **`/pickup`** — *to start the next one.* Finds the most recent handoff for the current project, reads it together with the open threads, and primes the new agent with full context. Asks you to confirm before continuing — and then you're back at step 1.

`/pickup` reads what `/putdown` writes. Without `/putdown`, `/pickup` has nothing to load. Without `/pickup`, `/putdown`'s handoff sits unused. Without the other two, `/putdown` saves the session's state but not what it learned or what it left pending.

The distinction that matters: a putdown is a **note to your next session** and goes stale the moment you act on it. A takenote is a **fact you want to keep forever**. An open thread is a **task that outlives any one session**; the day it's done it becomes a one-line outcome in the file's Closed section, kept 60 days. Three lifetimes, three destinations, which is why they're separate skills.

## Why `/putdown` and `/pickup` exist

Claude Code's context window is finite. As a session grows, you hit limits. Three things people try:

1. **`/clear` and hope.** Loses every bit of judgment from the prior session — what you tried, what didn't work, why you took the third option instead of the obvious one.
2. **Auto-compaction.** Lossy and unstructured. Compresses recent history but doesn't differentiate "this was a dead end, don't redo" from "this is the next step."
3. **"Reload Window" in VSCode.** This doesn't actually free Claude Code's context-window memory. It feels like it should, but it doesn't. Only closing the Claude Code window with `Cmd+W` and opening a new one starts a fresh agent process.

`/putdown` solves all three by writing a structured markdown file with sections specifically designed for re-entering work: **Where we are right now**, **Must address next session**, **What's in progress (resume here)**, **Immediate next steps**, **Blockers**, **Key decisions made & why**, and **What NOT to redo**. The file lives at `~/.claude/putdowns/<project-slug>/<timestamp>.md`.

`/pickup` then loads it in a fresh session and confirms with you before picking up the work.

## `/openthreads` — step 1 of the loop: park work as you go

### What it does

Keeps `OPEN-THREADS.md`, the project's living to-do list. Four fixed open sections — **Due now**, **Decisions waiting on you**, **Work waiting on the agent**, **Waiting on outside parties** — with one dated line per item, then a **Closed** section with the same four groups where finished items live for 60 days as outcomes:

```markdown
## Work waiting on the agent
### checkout
- [ ] Apply the coupon-stacking rule in `cart/totals.ts` once pricing signs off — added 2026-10-12 (session)

## Closed
Outcomes, newest first, kept 60 days. Same four groups as above.

### Work waiting on the agent
- [x] Coupon stacking now capped at one code per order in `cart/totals.ts`, commit `a1b2c3d` — added 2026-09-30 (putdown), closed 2026-10-12
```

Four modes: `add` (park something, in the right section, merged with any existing line about it), `done` (rewrite the line as its outcome — the decision made, or what shipped and where it's logged — and move it under Closed, keeping the original date and source), `list` (counted per open section, overdue items flagged, items older than 60 days marked with their age, then one line with the count closed in the last 60 days), and `reconcile` (what `/putdown` runs: closes what the session finished, adds what it left over, moves expired dates up, and prunes Closed past 60 days — git history is the archive beyond that).

### Why it exists

A putdown holds one session's next steps. Memory holds facts. Neither holds the **backlog**: the idea you parked at 11pm, the decision you said you'd make next week, the vendor you're waiting on. Those lived in people's heads and in open terminal windows, and surfaced only when someone re-read a fortnight of putdowns. Now `/pickup` briefs them every fresh session — counts, overdue items verbatim, the oldest open date — so you get the "oh right, that" moment without the re-reading.

### Where the file lives

At the repo root for a **private** repo (git-tracked, so web sessions see it and `git log` is its history). For a **public** or GitHub-Pages-served repo it would be published, so it goes in `~/.claude/putdowns/<project>/` instead — the same rule `/putdown` uses for handoffs. If the skill can't tell, it picks the out-of-repo location and says so.

### How it fits the other three

- **`/takenotes`** hands it to-dos: "remember to do X later" is a task, not a fact, so the scope gate routes it to `/openthreads add` and stops. A memory that's secretly a to-do list gets its tasks moved over when reconciled.
- **`/putdown`** reconciles it: moves what the session finished into Closed as outcomes, moves in anything from "Immediate next steps" / "Blockers" / "Must address" that *won't* be picked up next session, prunes Closed past 60 days, and reports `openthreads: 2 closed, 3 added, 1 now due, 0 pruned`. The two files never carry the same line.
- **`/pickup`** reads it and never writes it: the open counts, overdue items, the oldest date — and, only when something was closed after the putdown it's resuming, one line saying so.
- **The built-in task list** still handles what you're doing *right now*. Open threads are for what no session owns yet.

## `/takenotes` — step 2 of the loop: keep what you learned

### What it does

Three passes, in order:

1. **Harvest** — sweeps the session for what would still matter to someone who reads none of the conversation: decisions and the reasoning behind them, dead ends and why they failed, corrections you made, stable project facts.
2. **Reconcile** — re-reads what's **already** in memory and `CLAUDE.md` and checks whether this session made any of it false. Anything contradicted gets corrected in place, not appended next to.
3. **Route** — sends each finding where it belongs: typed memory (rationale, history, preferences), `CLAUDE.md` (stable structural facts), or a `docs/` file (anything over ~15 lines), with a pointer left behind.

### Why the reconcile pass is the point

Appending a new fact is easy and every assistant already does it. Almost nothing goes back to check whether what's stored is still true — so memory quietly accumulates claims that were correct months ago and are actively wrong now.

That's not a cosmetic problem. A memory reading *"do not add a webhook receiver — the vendor cannot call out"* doesn't just sit there being outdated; it argues a future session **out of** work you already shipped. Stale memory is worse than no memory, because it's trusted.

`/takenotes` verifies the concrete claims in existing memories — do the files, flags, and commands they name still exist? — and fixes or deletes what's failed. It keeps one sentence of superseded history when that history explains why the code looks the way it does, and deletes the false instruction.

### It guards `CLAUDE.md` on the way through

`CLAUDE.md` is auto-loaded on **every** session start, so every line costs tokens forever. The routing rule is deliberately stricter than "does it fit":

- **≤ 15 lines** → inline it in `CLAUDE.md`
- **> 15 lines** → write a `docs/` spoke and leave only a pointer — *regardless of how short `CLAUDE.md` currently is*

Size is the trigger, not the file's total length: a 40-line block that fits comfortably under any cap still costs you context on every single session start. And the pointer it leaves has to name the *contents*, so a future agent can decide whether to open the file without opening it:

```markdown
❌  See [docs/webhooks.md](docs/webhooks.md)
✅  Webhook signing — see [docs/webhooks.md](docs/webhooks.md) for the signature
    algorithm, header names, and replay-window handling.
```

### Using it on its own

`/takenotes` has no dependency on `/putdown` or `/pickup` — it reads the conversation and writes to memory, `CLAUDE.md`, and `docs/`. Run it any time:

- Right after solving a hard problem, so the fix **and the dead ends** don't evaporate on `/clear`
- After a decision with non-obvious reasoning, especially one that rules an approach out
- When you suspect memory or `CLAUDE.md` has drifted from reality and want a reconcile pass

It **never commits**, so it's safe to run mid-session at any moment — it leaves changes in your working tree for you (or `/putdown`) to commit.

It also handles a single fact without ceremony: "remember I prefer tabs" takes a short path that writes one memory and stops, rather than running a full session sweep.

### Using it with `/putdown`

**With all four installed, you don't type `/takenotes` at session end — `/putdown` runs it for you.** Its Steps 2–3 invoke `/takenotes` before the handoff is written, which means everything the harvest wrote gets swept into the same commit and push at the end. That ordering is the reason it's chained rather than left to you: run them the other way round and the memory work sits uncommitted.

```
/putdown
  → 1. /takenotes   — harvest + reconcile into permanent storage
  → 2. handoff file
  → 3. /openthreads — reconcile OPEN-THREADS.md against the handoff; then commit, push (sweeps up both)
```

You'd still type `/takenotes` directly **mid-session** — after solving something, when you're nowhere near ending. That's the case `/putdown` can't cover.

If you use Claude Code on the web, `/takenotes` also drains `.putdowns/MEMORY-INBOX.md` — a queue where a cloud session parks memory-bound findings it can't write itself, since `~/.claude/projects/` only exists on your machine.

**`/putdown` runs `/takenotes` and `/openthreads` for you.** Its Steps 2–3 invoke `/takenotes` and its Step 4.4 invokes `/openthreads reconcile`, so a single `/putdown` gets the full harvest-and-reconcile and an up-to-date backlog before pushing. It announces all three skills up front so you can see the order, and reports what each wrote on its own labelled line at the end.

If `/takenotes` is missing (a partial install), `/putdown` says the set is incomplete and falls back to its own inline memory step — reduced, with no reconcile pass, but it still works. If `/openthreads` is missing it skips the reconcile and says so. Install all four to get the real thing.

## Benefits — how each saves context

| Skill | Token cost saved |
|---|---|
| `/putdown` | Distills ~10k tokens of session state into a ~1k-token structured handoff |
| `/pickup` | Restores full context in ~30s vs. 5–10 minutes of manual scroll-back-and-paste |
| `/takenotes` | Keeps `CLAUDE.md` an index rather than a document — content over ~15 lines becomes a `docs/` file that loads only when relevant, instead of costing tokens on every session start forever |
| `/openthreads` | One counted list instead of re-reading old putdowns to find what's still pending; items are one line each, closed ones become one-line outcomes that age out after 60 days, so it never grows into a document |

The structured format means the next agent skips ~80% of the context that would otherwise need re-explaining, and goes straight to "Immediate next steps."

## How to use them

The loop, one session around:

1. **As you work, park what you won't do now:** "add this to the open threads" (or `/openthreads add …`). Decisions you're not ready to make, ideas for later, things waiting on someone else.
2. **As you work, keep what you learned:** `/takenotes` after solving something hard or deciding something non-obvious, or "remember this" for a single fact. You don't have to; `/putdown` will harvest the session anyway, but mid-session is when a dead end is freshest.
3. **At ~50% context, or when stepping away:** type `/putdown`. `/takenotes` runs first and `/openthreads reconcile` runs after the handoff, automatically — you don't type either separately. Then **close the Claude Code window** with `Cmd+W`. (Do not use "Reload Window" — it doesn't actually free the context window.)
4. **In a fresh Claude Code window, type `/pickup`.** It finds your most recent putdown, briefs you on it and on what's still open, and asks you to confirm before continuing. Back to step 1.

If you have multiple parallel sessions in the same project (e.g. two VSCode windows in the same folder), `/pickup` shows a picker with the 4 most recent putdowns so you can grab the right one.

## Best practices

- **Run `/putdown` at ~50% context, not 90%.** Writing a good handoff takes tokens. Leave room for the agent to do it well.
- **Always close the window after `/putdown`.** "Reload Window" looks like it would work but doesn't.
- **`/pickup` should be the very first thing in a new session**, not the fifth. Read the handoff before you start typing new instructions.
- **Trust the "What NOT to redo" section.** If the prior session ruled something out, don't relitigate it without a reason.
- **For multi-project parents** (a CWD that contains several subprojects), pass the slug: `/putdown myproject`.
- **Park, don't promise.** When something comes up mid-session that you won't do now, say "add this to the open threads" rather than letting it ride in the chat. `/putdown` would catch it only if it made the handoff's next steps.
- **Write open threads concretely.** "Fix the nav" dies in a week; a line with the file, the command, and the gate it waits behind still means something in a month.

## Why this is better than alternatives

| Alternative | Problem | How the loop solves it |
|---|---|---|
| `/clear` and hope | Loses judgment, file paths, blockers, ruled-out approaches | `/putdown` captures all of that in a structured file |
| Auto-compaction at the model layer | Lossy; misses "what NOT to redo"; not human-reviewable | `/putdown` has explicit "What NOT to redo" section; the file is markdown you can read and edit |
| Manual scroll-back-and-paste | Tedious, error-prone, forgets edge cases | `/pickup` loads the structured handoff in seconds |
| External handoff doc you maintain by hand | Drifts; gets stale; forgotten between sessions | `/putdown` is a single slash command at end of session |

## Eval result

`/putdown` and `/pickup` each passed skill-creator's trigger-accuracy benchmark at 100% precision and 100% recall on a 20-query test set (10 should-trigger + 10 adversarial should-not-trigger). See the root [eval-results.md](../../eval-results.md) for full methodology.

`/takenotes` passed the same benchmark at 100% / 100% on 2026-08-03 — including adversarial near-misses aimed at its broad trigger surface, such as *"take notes on this meeting transcript"* (contains the skill's literal name, correctly excluded) and *"remind me to call the vendor tomorrow"*. It also stayed out of `/putdown`'s and `/pickup`'s lanes, which matters when all three ship together.

It was additionally validated **behaviourally**: subagents ran it against a sandbox containing a deliberately poisoned memory — one asserting the opposite of what the session had just built — across two rounds that found and closed ten defects. Details for both in [eval-results.md](../../eval-results.md).

`/openthreads` passed the same benchmark at 100% / 100% on 2026-10-12 on its first pass, with the adversarial half aimed at its three neighbours (in-session tasks, durable facts, personal reminders) and at every other sense of "open" and "thread" — pull requests, Slack threads, worker threads, uncommitted files.

## Install

See the root [INSTALL.md](../../INSTALL.md). Quick version:

```bash
# The Session Continuity Loop — all four go together:
mkdir -p ~/.claude/skills
cp -r charles-agent-skills/claude/session-continuity/{openthreads,takenotes,putdown,pickup} ~/.claude/skills/
```

Then close your Claude Code window and open a fresh one.
