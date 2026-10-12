---
name: openthreads
description: Keeps a project's living to-do list — OPEN-THREADS.md — of everything pending that no single session owns. Use when the user says "openthreads", "add this to the open threads", "what's still open", "mark X done", or parks an idea to come back to later; also invoked by $putdown to reconcile the list at session end. Do NOT use for in-session task tracking (that is the plan tool), for durable facts or preferences (that is $takenotes), or for personal reminders that don't need this repo open (those belong in a personal task manager, not the repo).
---

> **Codex version.** Invoke with `$openthreads`, optionally followed by a mode (`$openthreads add <text>`,
> `$openthreads done <text>`, `$openthreads list`, `$openthreads reconcile`). Paths below use `$CODEX_DIR`,
> meaning `${CODEX_HOME:-$HOME/.codex}`. The file format is shared with the Claude Code version of this
> skill, so a list kept in a repo is read and edited by either tool.

# $openthreads — The project's living to-do list

A putdown records one session's next steps. Notes record facts. Neither holds **the project's
backlog**: the ideas parked mid-session, the decisions still waiting on the user, the work that no
session has picked up yet. Those lived in people's heads and in open terminal windows. Now they
live in one file per project, `OPEN-THREADS.md`, which `$pickup` reads every fresh session so the
user gets the "oh right, that" moment without re-reading a fortnight of putdowns.

## The file

**Location.** `<repo root>/OPEN-THREADS.md` for a private repo (git-tracked, so other machines and
web sessions see it and `git log` is its history). For a **public** repo or a GitHub-Pages-served
one, the file would be published — keep it at `$CODEX_DIR/putdowns/<project-slug>/OPEN-THREADS.md`
instead, the same rule and the same folder `$putdown` already uses for that case. `<project-slug>`
is exactly what `$putdown` names its folder: the **basename** of the CWD (`my-app`), or the slug the
user passed — **not** the full-path slug the `$takenotes` notes store uses, or `$pickup` won't find
the file. Non-git folders: the folder root. Check visibility the way `$putdown` does
(`gh repo view --json visibility`, or the project `AGENTS.md`); if you still can't tell, use the
`$CODEX_DIR/putdowns/` location and say so — a to-do
list that stays out of a repo is a small loss, one that gets published is not.

**Shape.** Five fixed `##` sections, in this order, so every skill that reads the file finds the same
thing: four for what's open, then **Closed**. `###` subheadings under the four open sections are
free (by component, by store, by customer — whatever the project calls its parts); under Closed they
are fixed — the same four groups, same order, and an empty one stays in the file.

```markdown
# Open threads — <project>

<2-3 lines: what this file is, who maintains it (openthreads / putdown / pickup); closed items move
to Closed, rewritten as the outcome, and are pruned after 60 days.>

## Due now / time-sensitive
- [ ] <item> — added YYYY-MM-DD (<source>), due YYYY-MM-DD

## Decisions waiting on you
- [ ] <question, with the recommended answer if there is one> — added YYYY-MM-DD (<source>)

## Work waiting on the agent
### <subgroup>
- [ ] <concrete action — file paths, commands, the gate it waits behind> — added YYYY-MM-DD (<source>)

## Waiting on outside parties
- [ ] <what, who, since when> — added YYYY-MM-DD (<source>)

## Closed
Outcomes, newest first, kept 60 days. Same four groups as above.

### Due now / time-sensitive
- [x] <outcome> — added YYYY-MM-DD (<source>), closed YYYY-MM-DD

### Decisions waiting on you

### Work waiting on the agent

### Waiting on outside parties
```

**One line per open item.** It ends with `— added YYYY-MM-DD (<source>)`, where source is `user`,
`session`, `putdown`, or a note filename. A deadline appends `, due YYYY-MM-DD`. No HTML in the
file (some Markdown editors strip it on save).

**Closed items are not deleted and not just ticked.** They move to the matching subheader under
**Closed**, rewritten as the **outcome**, newest first:

```markdown
- [x] <outcome> — added YYYY-MM-DD (<source>), closed YYYY-MM-DD
```

The outcome is not the original task text. For a *Decision* it is the decision made. For *Work* it
is what shipped and where it is logged (the changelog entry, the commit, the file). The original
`added` date and source are kept; `closed` is the day it closed. The section is a 60-day window:
`reconcile` prunes lines whose `closed` date is older than that (delete them — git history is the
archive beyond that), so the file never turns into a changelog.

**What belongs here vs elsewhere:**

| It is… | Goes to |
|---|---|
| Work, a decision, or an idea for *this project* that needs the repo open | **this file** |
| The next step of the thread *currently being worked* | the putdown's "Immediate next steps" — it comes here only if it won't be picked up next session |
| What to do *right now*, within this session | the plan tool (`update_plan`) or a checklist in chat, never this file |
| A fact, a preference, a dead end, how a tool behaves | `$takenotes` → a note or AGENTS.md |
| A personal reminder that needs no repo (buy, call, book) | the user's own task manager — say so, don't add it |

## Modes

Pick from the argument or from what the user said. When nothing matches, **list**.

### `add <text>` — park something

1. Locate the file (above). If it doesn't exist, create it with the header, the four empty open
   sections, and an empty Closed section (with its four `###` groups) and say so — do not ask
   permission for a file whose whole point is to exist.
2. Choose the section: a date or a vendor-imposed window → *Due now*; a question only the user can
   answer → *Decisions*; something another party must do → *Outside parties*; everything else →
   *Work waiting on the agent*, under the subgroup whose name matches (create one if none fits).
   `add` never writes to Closed.
3. Write it as a **concrete** line — file paths, the command, the gate it waits behind — in the
   user's words where they gave any. Date it today; source `user` if they asked, `session` if you
   are parking something you noticed. "Add an idea for later" is a `Work` item with the idea stated
   plainly; it does not need to be actionable yet.
4. Before writing, `grep -i` the file for the item's distinctive term. A hit in an open section
   means update that line, not add a twin. Then check Closed for the same *subject* — closed lines
   are outcomes, so the task's wording may not recur; search its nouns (the file, the vendor, the
   question). A hit there means it was done or decided before — say so, quote the outcome, and add
   the new line anyway if the user still wants it.
5. Confirm in one line: the section it landed in and the text as written.

### `done <text>` / `close <text>` — retire something

1. Find the matching open line(s) by distinctive term (Closed is not searched). One match → take
   it. Several → show them and ask which. None → say so; don't guess.
2. **Rewrite it as the outcome**, not the task: for a Decision, the decision that was made; for Work,
   what shipped and where it is logged (changelog, commit, file); for the other two, what happened.
   Use what the user said, or what you did this session; if neither tells you the outcome, ask in
   one line rather than inventing one. Keep the original `— added YYYY-MM-DD (<source>)` and append
   `, closed YYYY-MM-DD` (today).
3. Move it: delete the open line, insert the rewritten line as the **first** item under the Closed
   subheader that matches the section it came from (newest first).
4. If the item was a *Decision* and the user just made it, the decision itself may be worth a note
   or an AGENTS.md line — mention that, don't do it unasked.
5. Confirm with the closed line as written, so a wrong match or a wrong outcome is visible
   immediately.

### `list` / no argument — what's open

Read the file and print the four open sections **grouped and counted**, in file order. Before them,
one line: `Due now (3) · Decisions (10) · Work (14) · Outside (2)` — Closed is not counted. Then
flag, inline:

- `due YYYY-MM-DD` in the past → prefix the line **OVERDUE** (and, if it isn't already, move it to
  *Due now* in the file — that move is the one write `list` is allowed).
- `added` more than 60 days ago → suffix `(open 9 weeks)`. Old is information, not shame: the user
  decides whether it's still wanted. If several are old, close with one line offering to prune.

After the four sections, one line: `Closed in the last 60 days: N` — count only the `- [x]` lines
whose `closed` date falls within the last 60 days (pruning happens in `reconcile`, so older lines
may still be present). The count only, not the lines; the user opens the file if they want the
outcomes.

Keep it to the file's content. Do not reorder, rewrite, or "tidy" items while listing.

### `reconcile` — called by `$putdown`, or when the user asks

The list is only trustworthy if something checks it against reality at session end.

1. **Close what this session finished.** For each open item, ask whether the session did it (the
   putdown's "What's done this session" is the checklist). Move each one to Closed, rewritten as
   the outcome, exactly as `done` does — the putdown and the session tell you what shipped and
   where it's logged. Unlike `done`, never stop to ask here: `reconcile` runs inside `/putdown` with
   no one waiting to answer. If the outcome isn't clear from the putdown or the session, use the
   putdown's own "What's done" line as the outcome and suffix it `(outcome unconfirmed)`; if you
   can't tell whether an item was finished at all, leave it open.
2. **Add what's left over.** From the putdown's "Immediate next steps", "Blockers / open questions",
   and "Must address next session": anything that **will not be picked up next session** comes here
   (dated today, source `putdown`). Items that *will* be picked up stay only in the putdown — the
   two files must not say the same thing twice. Routine next steps of the live thread stay out.
3. **Move expired dates** into *Due now*.
4. **Prune Closed.** Delete every `- [x]` line whose `closed` date is more than 60 days ago. Git is
   the archive; the file is not.
5. **Report the delta**, not the file: `openthreads: 2 closed, 3 added, 1 now due, 0 pruned`. Zero
   across the board is a fine answer; say it rather than omitting the line.

`reconcile` never commits — `$putdown` commits right after it and sweeps the file up. Mid-session,
`add` and `done` also leave the file for `$putdown` (or the user) to commit, unless asked.

## Notes on judgment

- **Concrete or useless.** "Fix the nav" dies here. "The settings pages (4 of them) have no nav
  entry — add one to `nav.config.ts`" survives a month and still means something.
- **Outcomes, not echoes.** A closed line that repeats the task ("settings nav — done") tells the
  next reader nothing. "Settings pages got a nav entry in `nav.config.ts`, commit `a1b2c3d`" does.
  If you can't say what happened, you don't know it's closed.
- **One copy.** If an item exists as a note, a putdown "Must address" line, *and* here, the next
  agent can't tell which is current. A to-do belongs here; a note that is secretly a to-do
  (`project_x` with "still needs a reply") should move here when `$takenotes` next touches it.
- **Decisions are not nagging.** Listing an item that's waited six weeks is reporting; adding
  "please decide" is not your call. Prefix the recommended answer where you have one and leave it.
- **Don't invent items.** Reconcile pulls from the putdown you just wrote and the session you just
  had — never from what "a project like this probably needs".
- **The file is the user's once seeded.** They edit it by hand. Read before writing; merge, never
  regenerate. That includes Closed: never reorder it, and never prune by hand outside `reconcile`.
