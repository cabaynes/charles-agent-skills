# Session continuity — `/putdown` + `/pickup`, plus `/takenotes`

> `/putdown` and `/pickup` are a **required pair** — install both, not one. `/takenotes` is an
> **optional third** that works with them or entirely on its own.

## What

Skills that preserve work across Claude Code context resets — but across two different timescales:

**The pair — carrying a session forward (temporary state):**

- **`/putdown`** — at the end of a session (or whenever your context window is filling up), writes a structured handoff file that captures what you accomplished, what's still in flight, file paths you were mid-edit on, decisions you made and why, blockers waiting on you, and (critically) approaches you ruled out so the next session doesn't redo them.
- **`/pickup`** — at the start of a fresh session, finds the most recent handoff for the current project, reads it, and primes the new agent with full context. Asks you to confirm before continuing.

`/pickup` reads files that `/putdown` writes. Without `/putdown`, `/pickup` has nothing to load. Without `/pickup`, `/putdown`'s handoff sits unused.

**The optional third — keeping knowledge permanently:**

- **`/takenotes`** — harvests what a session *learned* into permanent storage (typed memory, `CLAUDE.md`, or a `docs/` file), and — the part nothing else does — goes back over what's **already** stored and corrects whatever this session made false.

The distinction that matters: a putdown is a **note to your next session** and goes stale the moment you act on it. A takenote is a **fact you want to keep forever**. Different lifetimes, different destinations, which is why they're separate skills.

## Why the pair exists

Claude Code's context window is finite. As a session grows, you hit limits. Three things people try:

1. **`/clear` and hope.** Loses every bit of judgment from the prior session — what you tried, what didn't work, why you took the third option instead of the obvious one.
2. **Auto-compaction.** Lossy and unstructured. Compresses recent history but doesn't differentiate "this was a dead end, don't redo" from "this is the next step."
3. **"Reload Window" in VSCode.** This doesn't actually free Claude Code's context-window memory. It feels like it should, but it doesn't. Only closing the Claude Code window with `Cmd+W` and opening a new one starts a fresh agent process.

`/putdown` solves all three by writing a structured markdown file with sections specifically designed for re-entering work: **Where we are right now**, **Must address next session**, **What's in progress (resume here)**, **Immediate next steps**, **Blockers**, **Key decisions made & why**, and **What NOT to redo**. The file lives at `~/.claude/putdowns/<project-slug>/<timestamp>.md`.

`/pickup` then loads it in a fresh session and confirms with you before picking up the work.

## `/takenotes` — the optional third

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

**With all three installed, you don't type `/takenotes` at session end — `/putdown` runs it for you.** Its Steps 2–3 invoke `/takenotes` before the handoff is written, which means everything the harvest wrote gets swept into the same commit and push at the end. That ordering is the reason it's chained rather than left to you: run them the other way round and the memory work sits uncommitted.

```
/putdown
  → 1. /takenotes — harvest + reconcile into permanent storage
  → 2. handoff file, commit, push (sweeps up what takenotes wrote)
```

You'd still type `/takenotes` directly **mid-session** — after solving something, when you're nowhere near ending. That's the case `/putdown` can't cover.

If you use Claude Code on the web, `/takenotes` also drains `.putdowns/MEMORY-INBOX.md` — a queue where a cloud session parks memory-bound findings it can't write itself, since `~/.claude/projects/` only exists on your machine.

**If you install all three, `/putdown` chains to `/takenotes` for you.** Its Steps 2–3 invoke `/takenotes` when present, so a single `/putdown` gets the full harvest-and-reconcile before writing the handoff and pushing. It announces both skills up front so you can see the order, and reports what `/takenotes` wrote on its own labelled line at the end.

If `/takenotes` **isn't** installed, `/putdown` falls back to its own inline memory step — reduced, with no reconcile pass, but it still works. Neither skill hard-depends on the other.

## Benefits — how each saves context

| Skill | Token cost saved |
|---|---|
| `/putdown` | Distills ~10k tokens of session state into a ~1k-token structured handoff |
| `/pickup` | Restores full context in ~30s vs. 5–10 minutes of manual scroll-back-and-paste |
| `/takenotes` | Keeps `CLAUDE.md` an index rather than a document — content over ~15 lines becomes a `docs/` file that loads only when relevant, instead of costing tokens on every session start forever |

The structured format means the next agent skips ~80% of the context that would otherwise need re-explaining, and goes straight to "Immediate next steps."

## How to use them

The workflow is four steps:

1. **In the current session** (when you're at ~50% context usage or stepping away): type `/putdown`. If `/takenotes` is installed it runs first, automatically — you don't type it separately.
2. **Close the Claude Code window** with `Cmd+W`. (Do not use "Reload Window" — it doesn't actually free the context window.)
3. **Open a fresh Claude Code window.**
4. **Type `/pickup`.** It finds your most recent putdown, summarizes it, and asks you to confirm before continuing.

If you have multiple parallel sessions in the same project (e.g. two VSCode windows in the same folder), `/pickup` shows a picker with the 4 most recent putdowns so you can grab the right one.

## Best practices

- **Run `/putdown` at ~50% context, not 90%.** Writing a good handoff takes tokens. Leave room for the agent to do it well.
- **Always close the window after `/putdown`.** "Reload Window" looks like it would work but doesn't.
- **`/pickup` should be the very first thing in a new session**, not the fifth. Read the handoff before you start typing new instructions.
- **Trust the "What NOT to redo" section.** If the prior session ruled something out, don't relitigate it without a reason.
- **For multi-project parents** (a CWD that contains several subprojects), pass the slug: `/putdown myproject`.

## Why this is better than alternatives

| Alternative | Problem | How the pair solves it |
|---|---|---|
| `/clear` and hope | Loses judgment, file paths, blockers, ruled-out approaches | `/putdown` captures all of that in a structured file |
| Auto-compaction at the model layer | Lossy; misses "what NOT to redo"; not human-reviewable | `/putdown` has explicit "What NOT to redo" section; the file is markdown you can read and edit |
| Manual scroll-back-and-paste | Tedious, error-prone, forgets edge cases | `/pickup` loads the structured handoff in seconds |
| External handoff doc you maintain by hand | Drifts; gets stale; forgotten between sessions | `/putdown` is a single slash command at end of session |

## Eval result

`/putdown` and `/pickup` each passed skill-creator's trigger-accuracy benchmark at 100% precision and 100% recall on a 20-query test set (10 should-trigger + 10 adversarial should-not-trigger). See the root [eval-results.md](../../eval-results.md) for full methodology.

`/takenotes` passed the same benchmark at 100% / 100% on 2026-08-03 — including adversarial near-misses aimed at its broad trigger surface, such as *"take notes on this meeting transcript"* (contains the skill's literal name, correctly excluded) and *"remind me to call the vendor tomorrow"*. It also stayed out of `/putdown`'s and `/pickup`'s lanes, which matters when all three ship together.

It was additionally validated **behaviourally**: subagents ran it against a sandbox containing a deliberately poisoned memory — one asserting the opposite of what the session had just built — across two rounds that found and closed ten defects. Details for both in [eval-results.md](../../eval-results.md).

## Install

See the root [INSTALL.md](../../INSTALL.md). Quick version:

```bash
# The required pair:
cp -r charles-agent-skills/claude/session-continuity/{putdown,pickup} ~/.claude/skills/

# Plus the optional third:
cp -r charles-agent-skills/claude/session-continuity/takenotes ~/.claude/skills/
```

Then close your Claude Code window and open a fresh one.
