# The full stack, in install order

The workspace guide in this folder gets you the skeleton: one root folder, per-project subfolders, shared memory, and the four day-to-day skills from this repo. This page is everything else the maintainer runs on top of that, in the order it makes sense to add it, with the one-line installer and the reason each one earns its place.

Versions and commands verified 2026-09-08. Installing a plugin or MCP server takes effect in a **fresh** Claude Code window, not the current one.

## Layer 0: prerequisites

Claude Code, git, and optionally the GitHub CLI. Covered by Step 0 of [README.md](README.md). Nothing here is Claude-specific.

## Layer 1: the workspace pattern and this repo's skills

Covered end to end by [README.md](README.md): the umbrella `CLAUDE.md`, the memory hub and `fanout-memory.sh`, and the five day-to-day skills, `/newproject`, `/putdown`, `/pickup`, `/takenotes`, and `/openthreads`. The two other skills in this repo are optional and install with one `cp` each per the root [INSTALL.md](../INSTALL.md): `/skill-dict` (a catalog of the skills you have installed) and `/grill-me` (interrogates a plan before you commit to it). Do this first; everything below assumes it.

## Layer 2: recommended for everyone (official plugins, no accounts needed)

These come from Anthropic's plugin marketplace, which Claude Code ships with. If `claude plugin marketplace list` does not show `claude-plugins-official`, add it once:

```
claude plugin marketplace add anthropics/claude-plugins-official
```

| Plugin | Install | What it adds | Why it is in the stack |
|---|---|---|---|
| **superpowers** (6.3.0) | `claude plugin install superpowers@claude-plugins-official` | Process skills that fire on their own: brainstorming before building, test-driven development, systematic debugging, writing and executing plans, subagent-driven development, verification before claiming done | The single biggest change in how Claude works. It stops the "build first, think later" failure mode by making Claude check for a process skill before every task. Everything in this repo was built under it. |
| **frontend-design** | `claude plugin install frontend-design@claude-plugins-official` | Design guidance when Claude builds or reshapes any UI: typography, palette, layout, avoiding template defaults | Without it, every page Claude makes looks like the same template. With it, pages get deliberate visual choices. Used for every published page in this workspace. |
| **skill-creator** | `claude plugin install skill-creator@claude-plugins-official` | Author, edit, and benchmark your own skills; runs the 20-query trigger-accuracy eval used for the numbers in [eval-results.md](../eval-results.md) | The moment you write your first skill, you need a way to know whether it fires when it should. This is that. |

## Layer 3: optional, with a reason to say no

| Tool | Install | What it adds | Trade-off |
|---|---|---|---|
| **context-mode** (1.0.169, third-party) | `claude plugin marketplace add mksglu/context-mode` then `claude plugin install context-mode@context-mode` | Runs commands in a sandbox and indexes their output, so large tool results stay out of the conversation and only the derived answer comes back | Real savings on long sessions with big outputs. Also opinionated: it installs hooks that steer Claude toward its own tools, and it occasionally needs a cache repair after plugin updates. Skip it until you have hit the context limit a few times. |
| **Playwright MCP** | `claude mcp add playwright -- npx -y @playwright/mcp@latest --browser chromium --user-data-dir ~/.cache/playwright-mcp-profile` | Lets Claude drive a browser: navigate, click, fill forms, screenshot, read the page | Essential for testing web pages and automating sites without an API. The two flags matter: `--browser chromium` uses Playwright's own bundled browser and `--user-data-dir` gives it its own profile, so automation never touches the Chrome you are logged into. |
| **claude.ai connectors** (Google Drive, Notion, and others) | Enabled in claude.ai under Settings, Connectors; nothing to install locally | Read and search files in Drive, read and write Notion pages, from Claude Code sessions signed into that account | Account-level, so they follow you across machines and into web sessions. They cannot be installed from a repo, which is why they are listed and not scripted. Note that the Drive connector reads documents but cannot write spreadsheet cells. |

## Layer 4: patterns the maintainer uses that you probably should not copy verbatim

Listed so the picture is complete, not as recommendations. None of these ship in this repo.

- **PreToolUse hooks that hard-block a rule.** Memory and `CLAUDE.md` are advisory; Claude can still forget. When a rule has been violated twice, or the word is "never", the maintainer writes a small shell hook in `~/.claude/hooks/` wired into `settings.json` that denies the tool call outright. Example targets: forcing a specific browser for automation, forbidding session files from landing outside their folder. The hooks are personal because the rules are.
- **A CLAUDE.md size reminder.** A hook that prints the current line count whenever Claude edits any `CLAUDE.md`, with the house target. Cheap, and it is why the umbrella template says "under 250 lines".
- **Language servers.** `swift-lsp@claude-plugins-official` exists here for one Swift project. Install a language-server plugin only for languages you actually write.

## After installing anything

Close the Claude Code window and open a new one. Plugins, MCP servers, and skills all register at session start. Then run `/plugin` or `claude plugin list` to confirm what loaded.
