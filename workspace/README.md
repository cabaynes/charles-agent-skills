# A multi-project workspace for Claude Code

The four day-to-day skills in this repo work on any single project folder. They work best on a **workspace**: one root folder, one subfolder per project, and shared memory that follows you between them. This page is the copy-and-paste setup for that layout. Terminal blocks are marked **Terminal**; prompt blocks are pasted into Claude Code.

Time to a working setup: about twenty minutes. Assumes macOS and a fresh Claude Code install; the shell steps also work on Linux.

## If you are a Claude agent reading this for someone

A person may point you at this page and say "set me up like this." Treat it as a runbook, in order:

1. **Check preconditions before anything else:** `claude --version`, `git --version`, and whether `gh auth status` succeeds. Report what is missing, ask, and only then run Step 0's commands for what is missing.
2. **Follow Step 1 and Prompts 1 through 3 in order, using the commands exactly as written.** Prompts 1 and 2 are written as things the person would paste to you; carry out what they describe. Prompt 2 is a live interview: ask the questions and wait for answers; never invent a profile. For Prompt 3 use its non-slash form, and ask the person what to name their first project.
3. **Ask before anything with an external footprint:** creating a GitHub repo, installing a plugin, appending to `~/.zshrc`. Step 1's block contains the `~/.zshrc` append; ask once before running the block.
4. **The person's details go only into their own memory hub** (`user_profile.md` under `~/.claude/projects/`). Nothing from this setup is written back into this repo or anywhere public.
5. **Finish by running the test** from the cloned repo and showing the person its last line, then tell them to open a fresh Claude Code window:

```
bash /tmp/charles-agent-skills/workspace/test-fanout.sh
```

If they want the extra tooling the maintainer runs, [STACK.md](STACK.md) in this folder lists it in install order with the reason for each. This file's raw URL, for fetching directly: https://raw.githubusercontent.com/cabaynes/charles-agent-skills/main/workspace/README.md

## Why this layout

Claude Code reads a file called `CLAUDE.md` from the folder you open **and every folder above it**, and it keeps a private memory directory **per project folder**. That gives you two problems as soon as you have a second project: instructions you want everywhere have to be repeated in every project, and memory you want everywhere is stuck in one project.

The workspace fixes both:

- One root folder, `~/CLAUDE`, with a short **umbrella** `CLAUDE.md` that lists your projects and the house rules. Every project is a subfolder with its own `CLAUDE.md`. Open a project and Claude sees the umbrella rules plus that project's rules, and nothing from the other projects.
- The root folder's memory directory is the **hub**. Anything universal (who you are, how you like Claude to work) lives there once, and `fanout-memory.sh` symlinks it into each project's memory. Edit it once, every project sees it. Project-specific memory stays in the project.
- The four skills run the day-to-day: `/newproject` builds a subfolder with all of this wired up, `/putdown` saves a handoff at the end of a session and pushes to GitHub, `/pickup` reloads it in the next session, and `/takenotes` files anything you say "remember this" about into the right memory, hub or project. `/takenotes` detects the symlinks on its own; nothing else needs configuring.

## What you end up with

```
~/.claude/CLAUDE.md                                   global rules for every folder on the machine (optional)
~/.claude/skills/{newproject,putdown,pickup,takenotes}/
~/.claude/projects/-Users-<you>-CLAUDE/memory/         the HUB: user_profile.md, feedback_*.md, MEMORY.md
~/.claude/projects/-Users-<you>-CLAUDE-recipes/memory/ one project's memory, with symlinks back to the hub
~/CLAUDE/CLAUDE.md                                    umbrella: project list + house rules
~/CLAUDE/scripts/fanout-memory.sh                     the symlink helper
~/CLAUDE/docs/                                        long reference docs the umbrella links to
~/CLAUDE/recipes/CLAUDE.md                            one project (its own git repo)
~/CLAUDE/recipes/.claude/skills/                      copies of the session skills, for claude.ai/code
```

The root can be any path. `~/CLAUDE` is used throughout because the folder name says what it is; if you pick something else, set `WORKSPACE_DIR` to match in Step 1 and the skills follow.

## Step 0: prerequisites (Terminal)

You need Claude Code, git, and optionally the GitHub CLI so `/newproject` can create private repos. Skip the `gh` lines if you never want GitHub; `/newproject` handles that cleanly.

```
xcode-select --install 2>/dev/null
which brew >/dev/null || /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
eval "$(/opt/homebrew/bin/brew shellenv 2>/dev/null || /usr/local/bin/brew shellenv)"
```

The Homebrew installer asks you to press Return and for your password; answer it, then let the block finish. On Apple Silicon Macs Homebrew lives in `/opt/homebrew`, which is not on the default path; the last line puts it there for this Terminal window, and the installer prints the line to add to your shell profile so it sticks.

Run these two one at a time; both are interactive:

```
brew install gh
gh auth login
```

Accept the defaults in `gh auth login` (GitHub.com, HTTPS, log in with a browser).

## Step 1: install the skills, the helper, and the umbrella (Terminal)

Skills have to exist **before** Claude Code starts, so this step is Terminal, not a prompt. Paste as one block:

```
mkdir -p ~/CLAUDE/scripts ~/CLAUDE/docs ~/.claude/skills
cd /tmp && rm -rf charles-agent-skills && git clone https://github.com/cabaynes/charles-agent-skills.git
cp -r charles-agent-skills/claude/session-continuity/{putdown,pickup,takenotes} ~/.claude/skills/
cp -r charles-agent-skills/claude/newproject ~/.claude/skills/
cp charles-agent-skills/workspace/fanout-memory.sh ~/CLAUDE/scripts/ && chmod +x ~/CLAUDE/scripts/fanout-memory.sh
if [ ! -f ~/CLAUDE/CLAUDE.md ]; then cp charles-agent-skills/workspace/CLAUDE.md.template ~/CLAUDE/CLAUDE.md; fi
grep -q 'WORKSPACE_DIR' ~/.zshrc 2>/dev/null || echo 'export WORKSPACE_DIR=~/CLAUDE' >> ~/.zshrc
export WORKSPACE_DIR=~/CLAUDE
ls ~/.claude/skills ~/CLAUDE ~/CLAUDE/scripts
```

You should see four skill folders (`newproject`, `pickup`, `putdown`, `takenotes`), a `CLAUDE.md` in `~/CLAUDE`, and `fanout-memory.sh` in `~/CLAUDE/scripts`. The `WORKSPACE_DIR` line tells `/newproject` where the workspace lives so it never asks. If your shell is bash, use `~/.bashrc` instead of `~/.zshrc`.

Open `~/CLAUDE` in your editor and start Claude Code. Every prompt below is pasted into that Claude Code window.

## Prompt 1: build the memory hub

Claude Code creates a project's memory directory the first time it needs one, but the hub has to exist before the helper can fan anything out. This prompt creates it and runs the helper once.

```
I'm setting up a Claude Code workspace following the workspace pattern from the charles-agent-skills repo. My workspace root is ~/CLAUDE, WORKSPACE_DIR=~/CLAUDE is exported in my shell, the umbrella ~/CLAUDE/CLAUDE.md already exists, and ~/CLAUDE/scripts/fanout-memory.sh is installed. Do the following, creating only what is missing and never overwriting anything that exists. Use absolute paths in everything you report back.

1. Claude Code keeps per-folder memory at ~/.claude/projects/<slug>/memory/, where <slug> is the folder's absolute path with every "/" replaced by "-" (for example /Users/alice/CLAUDE becomes -Users-alice-CLAUDE). Work out the slug for ~/CLAUDE on this machine, mkdir -p that memory directory, and create an empty MEMORY.md inside it if there isn't one. Show me the exact path.

2. Run ~/CLAUDE/scripts/fanout-memory.sh with no arguments. It should report that there are no universal memory files yet; that is expected until the next prompt.

3. Read ~/CLAUDE/CLAUDE.md and confirm it has a "## Subprojects" section and a "## House rules" section. Do not change it.

4. Report what you created as a short checklist with full paths, and tell me to close this Claude Code window and open a fresh one so the umbrella CLAUDE.md loads.
```

After it finishes: close the Claude Code window and open a new one in `~/CLAUDE`. "Reload Window" in VSCode does not pick up a new `CLAUDE.md` or new skills; only a fresh window does.

## Prompt 2: write your user profile (the first universal memory)

The hub is empty until this. Claude interviews you, writes the profile in the memory format the skills expect, and runs the helper.

```
Interview me to build my universal user profile memory, then save it. Ask a few questions at a time, not all at once: my name and what I do; my technical comfort level (do I read code, do I use Terminal, do I want you to explain commands before running them); the kinds of projects I'll keep in this workspace; how I like you to communicate (brief or detailed, ask first or just do it, how much to explain); and any hard rules you should always follow. When you have enough, write the answers to the hub memory directory you created earlier, ~/.claude/projects/<slug-for-~/CLAUDE>/memory/user_profile.md, in exactly this format:

---
name: user-profile
description: Who I am, my technical level, and how I like Claude to work with me
metadata:
  type: user
---

(the profile, as short bullets, with today's date noted at the top)

Then add one line to MEMORY.md in that same directory in the form "- [User profile](user_profile.md) — <one short hook>". MEMORY.md is an index and only ever holds one line per memory, never the content. Finally run ~/CLAUDE/scripts/fanout-memory.sh with no arguments and show me the output; it should list user_profile.md as a universal memory and say there are no subprojects yet.
```

## Prompt 3: create the first project

`/newproject` is a slash command, so type it directly. Replace `recipes` with a lowercase, hyphenated name; the skill rejects capitals and spaces, and lowercase names also avoid a macOS case quirk in the memory folder names. If you also want new repos to carry the session skills for claude.ai/code, do the optional Terminal step further down before running this.

```
/newproject recipes
```

If you would rather not use slash commands, this does the same thing:

```
Bootstrap a new subproject called recipes under my workspace at ~/CLAUDE using the newproject skill. One-line description: "Family recipe collection". Yes to git, yes to a private GitHub repo if gh is logged in, otherwise local-only is fine.
```

It asks for a description, then git and GitHub preferences, then prints a checklist. The lines that matter are the memory dir with universal symlinks, the umbrella entry, and the GitHub repo. Then open `~/CLAUDE/recipes` **directly** in a new editor window; that is where all real work on that project happens.

## Prompt 4 (optional): global rules for every folder on the machine

The umbrella covers everything under `~/CLAUDE`. A global `~/.claude/CLAUDE.md` covers everything, including folders opened outside the workspace. Keep it tiny.

```
Create ~/.claude/CLAUDE.md, my global Claude Code instructions that apply in every folder on this machine, if it doesn't already exist. Keep it under 20 lines. Contents: a heading "Global rules (all projects)"; a line saying my personal workspace is ~/CLAUDE and each subfolder there is its own project with its own CLAUDE.md; a line saying to check the project's CLAUDE.md and memory before asking me questions the files already answer; and a line saying never to commit .env files or secrets. Show me the file when done.
```

## Optional Terminal step: let claude.ai/code use the same skills

Private repos can carry copies of the session skills at `.claude/skills/` so a web session can `/putdown` and `/pickup` too. `/newproject` seeds those copies automatically **if** a source folder exists. One Terminal line sets that up (this is a Terminal command, not a prompt):

```
mkdir -p ~/CLAUDE/scripts/web-skills && cp -r ~/.claude/skills/{putdown,pickup,takenotes} ~/CLAUDE/scripts/web-skills/ && ls ~/CLAUDE/scripts/web-skills
```

Do this before running `/newproject` for the first time if you want it from day one; projects created earlier can get the copies by hand later.

## The daily rhythm

Once set up, the whole system runs on four habits:

| When | You type | What happens |
|---|---|---|
| Opening a project | `/pickup` | Loads the last handoff and asks you to confirm before continuing |
| Mid-session, something worth keeping | `remember that ...` or `/takenotes` | Files it into project memory, or the hub if it applies everywhere, and fixes anything stored that has gone stale |
| Wrapping up, or context feels full | `/putdown` | Runs takenotes, writes the handoff, commits and pushes |
| Starting something new | `/newproject <name>` | Folder, CLAUDE.md, memory dir with hub symlinks, git, GitHub, umbrella entry |

A prompt for a universal rule at any time:

```
Remember this as a universal rule that applies in every project, not just this one: always show me the git diff before committing. Save it in the hub as a feedback memory with Why and How to apply lines, add it to the hub MEMORY.md, and fan it out with ~/CLAUDE/scripts/fanout-memory.sh --all.
```

## Gotchas

- **Fresh window, not Reload Window.** New skills and new `CLAUDE.md` files only load in a new Claude Code window. VSCode's "Reload Window" looks like it should work and does not.
- **Open the project, not the umbrella.** Working from `~/CLAUDE` itself means Claude sees only the umbrella file and the hub memory. Real work happens with `~/CLAUDE/recipes` open directly.
- **Universal memories need the helper run.** A `feedback_*` or `user_*` file written to the hub applies nowhere until `fanout-memory.sh --all` runs. The house rules in the umbrella tell Claude to do this, but it is worth knowing why.
- **Editing a symlinked memory inside a project edits it for every project.** That is the point, but Claude should say so when it does it. `/takenotes` detects symlinks and asks.
- **Lowercase project names.** Claude Code sometimes lowercases the memory folder slug for mixed-case folders, which makes the helper miss it. Lowercase names sidestep this entirely.
- **`.env` never goes to GitHub.** `/newproject` writes a `.gitignore` that excludes it, but the habit still matters: check `git status` before every commit.
- **`/putdown` from the umbrella folder needs a project name.** If you run it from `~/CLAUDE` instead of a project, pass the slug: `/putdown recipes`.

## One honest caveat

`fanout-memory.sh` depends on two things Claude Code does today that are observed behavior, not a documented contract: memory lives at `~/.claude/projects/<slug>/memory/`, and `<slug>` is the absolute path with `/` replaced by `-`. Both have held through 2026. If a release changes either, the fix is the `HUB_SLUG` and `HUB_MEMORY` lines near the top of the script; `test-fanout.sh` will tell you the moment it breaks:

```
bash /tmp/charles-agent-skills/workspace/test-fanout.sh
```

That path is where Step 1 cloned the repo; macOS clears `/tmp` on reboot, so re-clone or run it from wherever you keep the checkout.

## Files in this folder

| File | What it is |
|---|---|
| `fanout-memory.sh` | The helper. `fanout-memory.sh` shows status, `fanout-memory.sh <name>` seeds one project, `fanout-memory.sh --all` syncs every project. Honours `WORKSPACE_DIR`. |
| `test-fanout.sh` | Eight-scenario test against a throwaway `HOME`. Exit 0 means the helper works on this machine. |
| `CLAUDE.md.template` | The umbrella file Step 1 installs. Has the `## Subprojects` heading `/newproject` appends to. |
| `STACK.md` | Everything the maintainer runs on top of this, in install order, with the reason for each. |
| `README.md` | This page. |
