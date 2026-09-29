# Changelog

All notable changes to this project will be documented here. Format roughly follows [Keep a Changelog](https://keepachangelog.com/).

## [0.8.1] — 2026-09-29

### Changed

- **`/putdown` + `/pickup` — a "Must address next session" section replaces hand-written pickup
  prompts.** Users were asking putdown for a separate prompt to paste into the next session, to be sure
  specific items got covered. That prompt lived only in chat (never saved or committed), and pickup's
  briefing shows just the first 1–3 next steps, so an item lower in the file could be read but never
  surfaced. Now putdown writes the must-happen items into the handoff file itself, the paste line is
  plain `/pickup`, and pickup echoes the section verbatim in its briefing (a **Must address:** line)
  and tracks those items first. Older putdowns without the section load unchanged. Descriptions
  unchanged, so no trigger re-eval.

## [0.8.0] — 2026-09-25

### Changed

- **`/takenotes` — fix claims now carry their proof, and get re-checked.** Prompted by a real
  failure: a memory recorded a script as "fixed, verified functionally" on one date; the script had a
  missing `import` and raised `NameError` on its first real call for 16 days, while `py_compile` kept
  passing and every session trusted the note. Three separately documented bugs recurred verbatim in the
  same project. The skill captured *claims* but no *evidence*, and nothing ever re-checked a claim.
  Four edits, no new top-level step (+62 lines):
  - **Step 0 memory format** — any memory asserting a fix, a capability, or "now works" carries a
    `**Verified by:** <command> → <result>` line, written only if that command was run this session;
    otherwise `NOT RUN — <what would settle it>`. Spells out what is *not* a run: `py_compile`, a
    linter, a successful `import`, a helper called in isolation. The run is the entry point on
    real-shaped input (`--dry-run`, `--help`, `/dev/null`, a one-item list).
  - **Step 3 item 4** — "do its paths exist?" becomes "do its claims still hold?": re-run stored
    `Verified by` commands for memories in areas the session touched, add one where missing, bounded to
    fast side-effect-free checks. A failed check is a finding.
  - **Step 4 recurrence gate** — grep memory for the failure's distinctive term before writing; a hit
    is a recurrence, marked `RECURRED <date>` in the memory's first lines rather than stacked as a second
    account. Then *know vs repeat*: a bug an agent will repeat regardless of knowing gets a named
    code-level guard as the memory's first "How to apply" line (or a CLAUDE.md gotcha when there is no
    code to guard).
  - **Step 5** — a required `Claims` block (`RAN` / `NOT RUN` / `RECURRED` lines), so an unmarked
    claim is visible by its absence, the same way the `Operational` block works.
- Tested with subagents against a sandbox reproducing the failure (planted `NameError` that passes
  `py_compile`, a memory claiming it verified, a documented recurring trap). 16-rep baseline on the
  prior skill caught the false claim 14/16; the two failures shared one shape (never ran the entry
  point, kept the stale claim, wrote "verify with `py_compile` + helper call" into a durable file).
  6/6 treatment reps ran the entry point, wrote `Verified by` lines, flagged the recurrence and named
  a guard first. Details in [eval-results.md](eval-results.md).
- Description unchanged, so prior trigger-accuracy numbers are unaffected.

## [0.7.0] — 2026-09-08

### Added

- **`workspace/` — the multi-project layout the skills were built for, now shippable.** Until now `/newproject` and `/takenotes` both *looked for* a memory fan-out helper that this repo never provided ("a user-supplied helper"). The folder closes that gap: `fanout-memory.sh` reads `$WORKSPACE_DIR`, derives the workspace's memory hub from it, symlinks every `user_*.md` and `feedback_*.md` from the hub into each project's memory directory, and appends the matching `MEMORY.md` index lines (idempotently; `project_*` and `reference_*` files are deliberately left local). `test-fanout.sh` proves it on the current machine in eight scenarios against a throwaway `HOME`. `CLAUDE.md.template` is an umbrella file with the `## Subprojects` heading `/newproject` appends to and five house rules. `README.md` is a copy-and-paste walkthrough that opens with a runbook section for a Claude agent setting someone else up: Terminal install, a hub-bootstrap prompt, a user-profile interview prompt, first project, optional global rules, optional web-session skills, the daily rhythm, and the gotchas.
- **`workspace/STACK.md` — the rest of the stack in install order.** Layer 2 (official plugins: superpowers, frontend-design, skill-creator), Layer 3 (optional: context-mode, Playwright MCP with its own browser profile, claude.ai connectors), and Layer 4 (patterns not to copy verbatim: hard-blocking hooks, a CLAUDE.md size reminder, language servers). Each entry has the exact `claude` CLI command and the reason it earns its place; versions pinned as of 2026-09-08.
- **`/grill-me`** — sixth published skill. A structured interrogator for plans, designs, and ideas that asks and never builds; keeps a resumable session file. Passed the 20-query trigger benchmark at 10/10 recall, 10/10 precision (LLM-as-judge variant) on 2026-09-08, after one description revision that added the resume-a-session trigger; frontmatter brought to the repo standard with `argument-hint` and `allowed-tools`. `snapshot.sh` now copies it from the local canonical source alongside `pickup` and `skill-dict`.

### Changed

- `/newproject` README and SKILL body, `INSTALL.md`, and the root `README.md` now point at the shipped helper instead of describing it as something you would write yourself. The root README also says where to point a Claude agent. No existing skill description changed, so prior trigger-accuracy numbers in [eval-results.md](eval-results.md) are unaffected.
- `INSTALL.md`'s uninstall line now includes `/takenotes` and `/grill-me`; 0.5.0 added `/takenotes` to the install steps but not the removal.
- `MAINTAINING.md`'s canonical-source table no longer claims `snapshot.sh` refreshes `/putdown` and `/takenotes`; both have been hand-maintained forks since 0.5.0 and the script's own header says so.

### Notes

- The helper depends on two observed Claude Code behaviors (memory at `~/.claude/projects/<slug>/memory/`, slug = absolute path with `/` → `-`). The guide says so plainly and names the two lines to change if a release moves them.
- `STACK.md` install commands are verified against the `claude` CLI on the release date; re-verify when Claude Code updates.

## [0.6.0] — 2026-08-22

### Added

- **`/takenotes` Step 3.5 — superseded-fact sweep.** The reconcile pass discovered its targets through the `MEMORY.md` index hooks, which left a blind spot: when a session changes a previously-true fact (a location, an employer, a vendor), the memory that *owns* the topic gets corrected, but a file that merely *mentions* the old fact — under a one-line hook that says nothing about it — never gets opened, so the stale claim survives every reconcile. Found in the author's own store, where a changed fact was corrected in the owning project's memory the day it happened yet sat wrong in the shared user profile for 19 days. Step 3.5 closes the gap: grep for the **old** term (not the topic — the topic also matches the freshly-corrected files) across the project's memory and, where one exists, the shared canonical store, then reconcile every hit. Historical mentions explicitly recorded as superseded are kept; only the old fact asserted as *current* is stale.

## [0.5.0] — 2026-08-03

### Added

- **`/takenotes`** — a third skill in `skills/session-continuity/`, optional and independent of the `/putdown` + `/pickup` pair. Where a putdown carries *session state* forward (and goes stale the moment you act on it), `/takenotes` writes what a session *learned* into permanent storage: typed memory, `CLAUDE.md`, or a `docs/` file. Three passes — **harvest** the session, **reconcile** what's already stored against what this session established, **route** each finding to where it belongs. The reconcile pass is the part nothing else does: a memory saying *"do not add a webhook receiver, the vendor cannot call out"* doesn't just sit there being outdated, it argues a future session out of work you already shipped. It also guards `CLAUDE.md` — anything over ~15 lines becomes a `docs/` spoke with a descriptive pointer, regardless of the file's current length, because a block that fits under any cap still costs context on every session start.

### Changed

- **`/putdown` now chains to `/takenotes` when it's installed.** Its Steps 2–3 invoke `/takenotes` instead of doing memory updates inline, so a single `/putdown` gets the full harvest-and-reconcile before the handoff is written — and the commit in Step 4.5 sweeps up whatever it wrote. A new **Step 0** announces both skills and their order before any work starts, and Step 5 reports `/takenotes`' result on its own labelled line (explicitly saying so when nothing durable was found, since a silent absence looks like a skipped step).
- **`/putdown` degrades gracefully without `/takenotes`.** If the skill isn't installed it falls back to a reduced inline memory step — no reconcile pass, but functional. Neither skill hard-depends on the other, and `/takenotes` can be installed or removed later without touching `/putdown`.
- **`/putdown`'s description no longer omits the memory step.** It previously described only the handoff and the commit/push, which risked an agent following the description and skipping Steps 2–3 entirely — the exact failure mode Anthropic's skill-authoring guidance warns about when a description summarises the workflow.

### Notes

- `/takenotes` passed the same 20-query trigger-accuracy benchmark as the other four skills — 100% precision, 100% recall — and was additionally validated behaviourally against a poisoned-memory sandbox. Both are documented in [eval-results.md](eval-results.md).
- The public `/takenotes` is a **parameterised fork**, hand-maintained like `/newproject` rather than auto-snapshotted. The author's local copy is coupled to a specific shared-memory layout (a canonical store with symlinks fanned into each project); the public version treats that as an optional pattern it detects rather than a requirement.

## [0.4.0] — 2026-06-13

### Changed (breaking: storage path)

- **Handoff files moved from `.checkpoints/` → `.putdowns/` and the word "checkpoint" is retired.** The 0.3.0 rename freed the command names but left the files still called "checkpoints," which kept the old term in play and risked the same confusion with the built-in `/checkpoint`/`/rewind` feature. The handoff files a session produces are now called **putdowns**, stored in `~/.claude/putdowns/<project>/` locally and `.putdowns/` inside a repo. The file format is unchanged. To migrate an existing install: `mv ~/.claude/checkpoints ~/.claude/putdowns` (local store), and in any repo that has committed handoffs, `git mv .checkpoints .putdowns`. The skills still read a stray `.checkpoints/` folder if they encounter one, so nothing breaks if you migrate gradually.

## [0.3.0] — 2026-06-12

### Changed (breaking: skill names)

- **Session-continuity pair renamed: `/checkpoint` → `/putdown` and `/resume` → `/pickup`.** The old names collide with Claude Code **built-in** commands for every user: `/resume` is the built-in conversation-resume picker, and `/checkpoint` is a built-in alias for `/rewind`. Custom skills currently shadow those built-ins (locking you out of them), and updates to Claude Code can silently flip that precedence ([anthropics/claude-code#33080](https://github.com/anthropics/claude-code/issues/33080)). The handoff FILES are unchanged — still timestamped markdown in `~/.claude/checkpoints/<project>/` — so existing checkpoints keep working after the rename. To migrate an existing install: `mv ~/.claude/skills/checkpoint ~/.claude/skills/putdown && mv ~/.claude/skills/resume ~/.claude/skills/pickup` then re-copy the SKILL.md files from this release.
- **`/putdown` now ends the session cleanly: it commits and pushes all session work.** After writing the handoff file it reviews the changed-file list (with a secrets gate — `.env*`, keys, and credential files are never staged), commits everything with a descriptive message, and pushes if a remote exists, reporting the pushed SHA or a prominent warning on failure. In private repos it also copies the handoff into the repo's `.checkpoints/` folder so cloud sessions (Claude Code on the web) can read it; public and Pages-served repos skip the in-repo copy so session notes are never published.
- **`/pickup` is now cross-surface aware.** It starts with `git fetch` and flags when origin is ahead (work pushed from another surface, e.g. Claude Code on the web), and searches both `~/.claude/checkpoints/<project>/` and the repo's `.checkpoints/`, deduplicating by timestamp.

## [0.2.0] — 2026-06-08

### Changed

- **`/checkpoint`**: the post-save "free the context window" reminder is now surface-aware. It detects the running surface via `CLAUDE_CODE_ENTRYPOINT` and gives the correct instruction: in the **terminal CLI** (standalone or VSCode's integrated terminal) `/clear` genuinely frees context, so it now recommends `/clear` → `/resume` instead of closing the window; the window-closing dance is reserved for the **VSCode visual-editor panel** and other GUI surfaces where `/clear` doesn't reliably reset context. Previously the skill told every user to close the window, which was only correct for the visual editor. The MCP-servers-added-this-session exception (full process restart required) is preserved for the CLI path.

## [0.1.0] — 2026-05-13

### Added

- **Session-continuity pair**: `/checkpoint` + `/resume` (must install together — they read/write the same handoff files). Lives in `skills/session-continuity/` so the pair stays together structurally.
- **`/newproject`** (parameterized for general use): bootstrap a workspace project under `$WORKSPACE_DIR` (default `~/projects/`). Optional fan-out memory integration; optional umbrella file update.
- **`/skill-dict`**: manage a personal catalog of installed Claude Code skills. Five subcommands: `list`, `show <name>`, `sync`, `add <name>`, `check-updates`. Subcommand details live in `skills/skill-dict/references/`.
- Evaluated against Anthropic's `writing-skills` + `skill-creator` rubric:
  - 18-rule static review (description quality, frontmatter, length, structure, anti-patterns).
  - skill-creator's description-optimization benchmark eval: 20 trigger queries per skill, LLM-as-judge scoring.
  - Results: 100% precision and 100% recall on all four skills. Full report in `eval-results.md`.
- Resume-builder docs: top-level `README.md`, per-skill `README.md`s, `INSTALL.md`, `CONTRIBUTING.md`, MIT `LICENSE` (root + per-skill).
- `MAINTAINING.md` — release workflow documentation (how to push edits, add a new skill, run the eval, verify sanitization).
- `scripts/snapshot.sh` — release helper that copies the canonical local skills into this repo with personal-path sanitization.

### Notes

- The repo is a **one-way snapshot** of the maintainer's local skills at `~/.claude/skills/<name>/`. Local versions are canonical; the snapshot script refreshes the repo copies for each release.
- `/newproject` is the only skill that diverges between local and public — the local version is hard-coded to the `~/CLAUDE/` workspace convention; the public version is parameterized.
