---
name: putdown
description: Writes a session handoff file that a fresh Codex session reads via $pickup, harvests durable knowledge into notes and AGENTS.md (via $takenotes when installed), then commits and pushes all session work. Use when the user says "putdown", when ending or stepping away from a working session, or when the context is filling up. Do NOT use for pausing media, downloads, background processes, or VMs.
---

> **Codex version.** Invoke with `$putdown`, optionally followed by a project slug (`$putdown my-app`).
> Paths below use `$CODEX_DIR`, meaning `${CODEX_HOME:-$HOME/.codex}` — resolve it once with
> `echo "${CODEX_HOME:-$HOME/.codex}"`. Handoffs copied into a repo's `.putdowns/` folder use the same
> format as the Claude version of this skill, so either tool's `pickup` can read them.

# $putdown — Context handoff before starting a fresh chat

The user is about to start a fresh chat. Your job: capture **everything a new agent would need** so the next session loses no momentum.

> A stray `.checkpoints/` folder, if you see one, is the pre-2026-06-13 name for `.putdowns/` — treat it as a putdown.

## Step 0 — Announce what's about to run

The `takenotes` skill ships with this one as part of the session-continuity set (putdown + pickup + takenotes), so a putdown is two operations, not one. Check it is there (a `takenotes/SKILL.md` in `~/.agents/skills/`, `$CODEX_DIR/skills/`, or the repo's `.agents/skills/`). Print this first so the user knows what's running and in what order:

```
$putdown runs two skills, in this order:
  1. $takenotes — harvest this session into notes, AGENTS.md, and docs/
  2. $putdown   — write the handoff file, then commit and push everything
```

If it is missing (someone installed only part of the set), print this instead of the announcement:

```
$putdown: takenotes isn't installed — the session-continuity set is putdown + pickup + takenotes.
          Using the reduced memory step instead; install takenotes for the full harvest.
```

Either way this is an announcement, not a prompt — don't wait for confirmation, continue to Step 1.

## Step 1 — Read current state (parallel)

Before writing anything, gather context. Run these in parallel:

- `pwd` — where the session is rooted
- `git status` and `git log --oneline -10` — if it's a git repo (skip silently if not)
- `git diff --stat` — what's changed, uncommitted
- Read the project-level `AGENTS.md` if one exists in the CWD
- Read `$CODEX_DIR/notes/projects/<slug>/INDEX.md` if it exists (`<slug>` = the CWD with every `/` turned into `-`) to know which notes exist
- Check the current plan state (the `update_plan` plan, or any checklist you kept in chat — recall from conversation, don't invent)

Also pull from your conversation memory:
- What was the user actually trying to accomplish in this session?
- What did you finish? What's half-done?
- What file paths and line numbers are you in the middle of?
- What did you try that didn't work, and why?
- Any decisions made with non-obvious rationale?
- Any errors, blockers, or open questions waiting on the user?

## Steps 2–3 — Harvest durable knowledge

**Run the `takenotes` skill** — it ships with this skill as part of the session-continuity set —
**open its `SKILL.md`, read it, and follow it to completion before continuing.** (There is no
tool that runs another skill for you; reading and following its instructions is how it runs.) It
harvests the session, reconciles what is already in the notes and `AGENTS.md` against what this session
actually established (correcting anything that has since become false), and routes each finding to a
note, `AGENTS.md`, or a `docs/` spoke.

**If it's missing** (a partial install — Step 0 already told the user), do this inline instead — a reduced version with no reconcile pass:

- Write durable findings (user preferences, corrections to your approach, project status, external
  references) as short Markdown notes in `$CODEX_DIR/notes/projects/<slug>/`, one fact per file, each
  listed as one line in that folder's `INDEX.md`. Convert relative dates to absolute. Update an existing
  note rather than adding a near-duplicate.
- If there's an `AGENTS.md` in the project directory, add or update **stable** facts only
  (architecture, conventions, how to run and test it). Do NOT put session state in it — that belongs
  in the handoff file. If none exists and the project has accumulated real conventions, suggest
  creating one; don't create it unprompted.

Either way, two things hold:

- **Ephemeral session state stays out of the notes.** It belongs in the handoff file below.
- **Nothing here commits.** Step 4.5 commits and pushes everything, including whatever this step wrote.

Keep the result — you'll echo a one-line version in Step 5.

## Step 4 — Write the handoff file

Save to `$CODEX_DIR/putdowns/<project-slug>/<YYYY-MM-DD-HHMM>.md`. Create the per-project subfolder if it doesn't exist (`mkdir -p`).

**Determining `<project-slug>`:**
- If the user passed an argument (e.g. `$putdown my-app`), use that as the slug. This is the right choice when the CWD is a parent folder containing multiple projects (e.g. CWD is `projects` but the work is about my-app).
- Otherwise, use the basename of the CWD (e.g. `my-app`, `RecipeBox`).
- If the CWD basename looks like a multi-project parent (e.g. `projects`) and no argument was given, **ask the user** which project this putdown is for before saving — don't dump it under the parent folder name.

Use this structure exactly — the next agent will be reading it cold:

```markdown
# Putdown: <project> — <date> <time>

**CWD**: <absolute path>
**Branch / git state**: <branch, ahead/behind, dirty file count>
**Session goal (this conversation)**: <one paragraph — what the user came to do>

## Where we are right now
<2-4 sentences. The single most important section. If the next agent reads only this, they should be unblocked.>

## Must address next session
- <specific item the next session must not let slip — or "none">

## What's done this session
- <bullet>
- <bullet>

## What's in progress (resume here)
- <task>: <file:line>, <what state it's in>, <what's left>

## Immediate next steps (in order)
1. <concrete action with file path>
2. <concrete action>
3. <concrete action>

## Blockers / open questions for the user
- <thing waiting on user decision, or "none">

## Key decisions made & why
- <decision>: <rationale — especially anything non-obvious from the code>

## What NOT to redo
- <approaches already tried and rejected, with why — saves the next agent from repeating>

## Environment state
- Dev servers running: <list or "none">
- Background processes: <list or "none">
- Modified-but-uncommitted files: <list — should be "none" after Step 4.5 commits>
- Pushed to origin: <branch @ short SHA — filled in by Step 4.5; or "no remote" / "PUSH FAILED: <why>">
- Anything the user needs to manually do before resuming: <list or "none">

## First message to paste in the new session
> $pickup
```

**"Must address next session" replaces a hand-written pickup prompt.** Put here anything the user asked
to carry forward ("make sure next time we…"), plus anything whose slipping would waste or break work
(an unverified fix, a promised check, a deadline). Keep it to the few items that truly must happen —
routine next steps belong in "Immediate next steps". `$pickup` echoes this section verbatim in its
briefing, so the user can see it landed. If the user asks for "a prompt to paste into the next
session", write its content into this section and tell them plain `$pickup` will surface it — don't
produce a separate chat-only prompt (it isn't saved or committed, and it's lost if not copied).

## Step 4.5 — Commit + push (a putdown means the session is ending)

Skip this step entirely if the CWD is not a git repo.

1. **In-repo putdown copy — private repos only.** If the repo is **private** AND its contents are not publicly served (a GitHub Pages site publishes everything on its deployed branch), copy the just-written handoff file to `<repo>/.putdowns/<same-YYYY-MM-DD-HHMM>.md` (`mkdir -p .putdowns`). This is what makes the putdown readable from another machine, a cloud session, or a Claude session in the same repo. For **public repos** and Pages-served repos, skip the copy — committed putdowns there would be published; the local file in `$CODEX_DIR/putdowns/` is the only copy. Check visibility with `gh repo view --json visibility` or the project `AGENTS.md`; if still unsure, skip the copy and say so.
2. **Secrets gate before staging.** Run `git status --porcelain` and review the file list. Never stage `.env*` (except `.env.example`), `secrets*`, `*.pem`, `*.key`, or credential files — they should already be gitignored; if one shows up untracked, add it to `.gitignore` instead of committing it. Never use `git add -f`.
3. **Commit everything** with a descriptive message summarizing the session's work (not just "putdown" — say what changed). Include the in-repo putdown copy from substep 1.
4. **Push** the current branch if a remote exists (`git push`, or `git push -u origin <branch>` for a new branch). Then fill in the "Pushed to origin" line **in the local handoff file only** (`$CODEX_DIR/putdowns/…`, outside the repo) with `<branch> @ <short SHA>`. **Never edit or re-commit the in-repo copy after the push:** a file can't hold the SHA of the commit that contains it, so a refresh leaves the repo dirty or needs a second commit whose SHA is again one behind. Before committing, write the in-repo copy's line as `<branch> — pushed in the commit that added this file (git log -1 -- .putdowns/<file>)`. If there is **no remote** or the **push fails**, write that prominently in the handoff file and tell the user in Step 5 — never fail silently; unpushed work is invisible to every other machine and session.

## Step 5 — Show it to the user

After saving, print to chat — in this exact order:
1. The full path to the saved putdown file (so they can re-open it later)
2. **How to start fresh.** In the Codex CLI: type `/new` (or `/clear`, which also clears the screen), then `$pickup`. In the Codex desktop app: start a **New chat** in the same project (`Cmd+N` on macOS), then `$pickup`. If you can't tell which surface this is, give both. If MCP servers or config changed this session, a new chat may not load them — tell them to quit and relaunch Codex first.
3. A code block containing exactly `$pickup` — what they type in the fresh chat
4. **The result of Steps 2–3, labelled with its source** — which notes, `AGENTS.md`, and `docs/` files were written or corrected. If `takenotes` ran, label it as such so the user can see both skills fired, e.g. `takenotes: 2 notes updated, 1 created, AGENTS.md +3 lines`. If nothing durable was found, say so explicitly rather than omitting the line — a silent absence looks like a skipped step.
5. The commit + push result: `<branch> @ <short SHA> pushed to <repo>` — or a **prominent warning** if there was no remote or the push failed (that work is invisible to other machines and sessions until pushed)

Keep your final reply tight — the handoff document does the heavy lifting; don't summarize it again in chat.

## Notes on judgment

- **Be specific, not generic.** "Continue working on the auth flow" is useless. "In `<workspace-root>/my-app/src/export.py:142`, the `--seed` flag isn't being passed to the renderer; need to add it to the request payload" is useful.
- **Include failure context.** If you spent 20 minutes ruling something out, write it down so the next agent doesn't repeat it.
- **Don't overwrite prior putdowns.** Each is timestamped; keep history.
- **If the project is brand new and there's nothing meaningful to hand off, say so** rather than padding with filler.
