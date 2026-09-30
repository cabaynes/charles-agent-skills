---
name: pickup
description: Loads the most recent putdown handoff file for the current project and primes the session with full prior context. Use when the user says "pickup", asks "where were we" after opening a fresh window, or wants to resume work from a prior session that ended with /putdown. Do NOT use for reopening a previous Claude conversation (that is the built-in /resume picker) or for resuming media, downloads, paused processes, or VMs.
argument-hint: "[putdown-timestamp]"
allowed-tools:
  - Read
  - Bash
  - Grep
  - Glob
  - AskUserQuestion
---

# /pickup — Pick up from a prior putdown

The user just started a fresh session and wants to continue from where the previous session ended. There is a putdown file (a handoff note) waiting for you.

> Renamed from `/resume` on 2026-06-12 (paired with `/checkpoint` → `/putdown`) because those names shadow Claude Code built-ins. On 2026-06-13 the handoff files also moved from `.checkpoints/` → `.putdowns/`. A stray `.checkpoints/` folder, if you see one, predates the move — read it the same way.

## Step 0 — Sync check (CLI↔web handoff)

If the CWD is a git repo with a remote, run `git fetch origin` then `git rev-list --count HEAD..@{u}` before anything else. If origin is **ahead**, work happened on another surface (most likely Claude Code on the web): tell the user and offer to `git pull` before resuming — the newest putdown may be inside the pulled `.putdowns/` folder. If fetch fails (offline, no remote), or the branch has no upstream (`rev-list` errors with "no upstream configured"), say so in one line and continue with local putdowns only.

## Step 1 — Find the candidate putdown(s)

The current project's slug is the basename of the CWD. Putdowns live in two places: the local `~/.claude/putdowns/<project-slug>/` dir and the repo's own `.putdowns/` folder (synced via git so web sessions can read and write them).

List all putdowns for this project from both locations, newest first, and grab the current time so you can label them accurately later:
```
find ~/.claude/putdowns/"$(basename "$PWD")" "$PWD/.putdowns" -maxdepth 1 -name '20*.md' 2>/dev/null | awk -F/ '{print $NF "\t" $0}' | sort -r | cut -f2-; date
```

Why this shape and not `ls -t <dir>/*.md <dir>/*.md`: in zsh a glob with no match aborts the **whole** command, so a repo without a `.putdowns/` folder (every public repo) would hide the local putdowns too. `-name '20*.md'` skips `.putdowns/MEMORY-INBOX.md`, which is not a putdown. Sorting by filename, not modification time, keeps the order right after a `git pull` or checkout rewrites mtimes.

**If the user passed a timestamp argument** (e.g. `/pickup 2026-09-12-0901`), load the file with that name directly — skip the count branching and the picker below. If no file matches, say so and fall through to the normal flow.

If the same `<YYYY-MM-DD-HHMM>.md` filename appears in both locations, treat it as ONE putdown and prefer the in-repo copy — it may carry edits pushed from the other surface.

Hold onto the `date` output — you'll subtract from it in Step 1a to produce relative-time labels. The system reminder gives you today's *date* but not the current *clock time*, so without `date` you'll guess and get it wrong (e.g. labeling a 5-minute-old putdown as "2h ago").

Branch on the count:

- **0 files** — no putdown matched. Check `~/.claude/putdowns/` to list all available project subfolders, in case the user is in a different CWD than when they made the putdown (e.g. they ran `/putdown` from `<workspace-root>/my-app` but ran `/pickup` from `<workspace-root>/my-app/src`). Tell the user no putdown was found for this project, list what *is* available, and ask which to load (or to start fresh).
- **1 file** — load it directly. Skip Step 1a and proceed to Step 2 with that file.
- **2+ files** — go to Step 1a to let the user pick. (The user sometimes runs parallel VS Code conversations rooted in the same project folder, so the most recent file is not always the one they want.)

## Step 1a — Present the picker (only when 2+ putdowns exist)

For each of the **4 most recent** candidate files, extract:

- **Timestamp** from the filename (`2026-04-27-0933.md` → `2026-04-27 09:33`) plus a relative-time hint like `"5m ago"`, `"2h ago"`, or `"yesterday"`. Compute the delta against the `date` output you captured in Step 1 — don't eyeball it. A file from earlier today is hours ago only if the clock time actually differs by hours.
- **Session goal** — the text after `**Session goal (this conversation)**:` in the file header. Truncate to ~60 chars.
- **First sentence of `## Where we are right now`** — used for the option's description. Truncate to ~140 chars.

A quick way to grab the metadata cheaply is `head -n 25 "$PUTDOWN_FILE"` and then parse the relevant lines.

Call `AskUserQuestion` with:

- `question`: `"Which putdown do you want to load?"`
- `header`: `"Load which?"`
- `multiSelect`: `false`
- `options`: one per putdown, newest first. For each option:
  - `label`: `"<relative-time> — <session-goal truncated>"` (e.g. `"2h ago — Pipeline seed flag bug"`). Append `" (Recommended)"` to the **first** option only — it's the newest, which is the same as today's default behavior.
  - `description`: first sentence of "Where we are right now". If that section can't be parsed, use `"(no summary available)"`.

If a candidate file is missing both the `Session goal` line and the `Where we are right now` section (corrupt or hand-edited), still include it in the picker but use the bare filename timestamp as the label and `"(no summary available)"` as the description — don't fail the whole picker over one malformed file.

If there are **5 or more** putdowns, show only the 4 newest in the picker, and print one line of chat above the picker like: `"Showing the 4 most recent of N putdowns — pick 'Other' to specify an older timestamp."` The harness's auto-provided `"Other"` option lets the user paste an older timestamp (e.g. `2026-03-12-0901`) if they really want one.

Once the user picks, use the chosen file as the putdown for the rest of the flow and continue to Step 2.

## Step 2 — Read the putdown and recent state

In parallel:
- Read the putdown file in full
- `pwd` to confirm CWD
- `git status` and `git log --oneline -5` to see if anything changed since the putdown was written
- Read the project `CLAUDE.md` if one exists
- Read the user's auto-memory `MEMORY.md` index (already loaded by the harness, but re-confirm)

If git state has drifted significantly from what the putdown described (e.g. new commits, files modified outside what was listed), flag this to the user — the world may have moved since the putdown.

## Step 3 — Brief the user

Reply with a tight summary so the user can confirm you've loaded the right context. Structure:

```
Resumed from: <putdown file path> (<how long ago it was written>)
<If a picker was shown: append " — chosen from N available putdowns in this project">

**Where we left off:** <one sentence>

**Must address:** <every item from "## Must address next session", verbatim — omit this line if the section is missing or "none">

**Next up:** <the first 1-3 next steps from the putdown>

**Blockers waiting on you:** <list, or "none">

<If git state has drifted: a "⚠️ Note:" line about what changed since the putdown.>
```

Never summarize or drop "Must address" items — they exist because the user wanted proof the next
session saw them. Older putdowns won't have the section; that's fine.

Then **stop and wait for the user to confirm or redirect.** Do NOT auto-execute the next steps. The user may want to adjust direction, skip a step, or hand off to a subagent. Once they confirm, proceed.

## Step 4 — Once confirmed, execute

Pick up the work. Use TodoWrite to track the "Must address" items (first) and the "Immediate next steps" list from the putdown; don't mark the session's work done while a "Must address" item is still open unless the user dropped it. Honor the "What NOT to redo" section — do not re-attempt approaches the previous session ruled out.

## Notes on judgment

- **One putdown at a time.** Do not auto-merge multiple putdowns. When 2+ exist, present the Step 1a picker and load only the user's choice.
- **Trust the putdown, but verify file references.** If it says "edit foo.py:142", confirm that file/line still exists before acting on it (rename/refactor may have happened).
- **If the putdown is stale** (say, more than a few days old) and significant changes have happened on disk, ask the user whether to use it or start fresh.
- **Don't recreate the previous session's chat.** You're picking up the work, not roleplaying the prior conversation. Be forward-looking.
