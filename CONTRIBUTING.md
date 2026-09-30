# Contributing

PRs are welcome. These skills were authored for a specific personal workflow but improvements that don't break that workflow are appreciated.

## What's likely to be merged

- Bug fixes (broken paths, edge-case crashes, typos)
- Improvements to the description's trigger accuracy (provide eval results — see below)
- Tightening of body content (less words, same clarity)
- New troubleshooting entries in `INSTALL.md`
- Compatibility fixes for non-macOS platforms (`sed -i ''` is BSD-specific, etc.)
- Portability fixes to `workspace/fanout-memory.sh` (keep `workspace/test-fanout.sh` passing; add a scenario if you fix a bug it didn't catch)
- Corrections to `workspace/STACK.md` when a Claude Code release changes an install command

## What's unlikely to be merged

- New skills (this repo is curated; consider your own fork)
- Major restructuring of `/putdown` + `/pickup` (the pair has been eval-validated; changes need eval evidence)
- Stripping the `~/CLAUDE/` references from comments where they're explaining the original use case

## Before opening a PR

1. **Run the eval if you changed a description.** Use the methodology in [eval-results.md](eval-results.md):
   - Draft 20 trigger queries for the skill (10 should-trigger, 10 should-not-trigger near-misses).
   - Use an LLM-as-judge to score each query against your revised description.
   - Report precision and recall in the PR description.
   - Threshold to merge: ≥80% on both metrics. The current bar is 100% — don't regress it without good reason.

2. **Run the snapshot script.** If you edited a skill in `~/.claude/skills/<name>/` locally (the canonical source for the pair + `/skill-dict`), re-run `scripts/snapshot.sh` to refresh the repo copy. `/newproject` is maintained separately in the repo — edit `claude/newproject/SKILL.md` directly there.

3. **Verify no personal paths leaked back in:**
   ```bash
   grep -rnE '/Users/charles|Charles' claude/
   ```
   Should return zero matches.

4. **One commit per change.** Squashing is fine; mixing unrelated changes in a single commit is not.

## Reporting bugs

Open an issue with:
- Which skill (`/putdown`, `/pickup`, `/takenotes`, `/newproject`, `/skill-dict`, `/grill-me`) or `workspace/fanout-memory.sh`
- Claude Code version (`/version` in Claude Code)
- macOS / Linux / WSL
- A minimal reproduction (the exact query you typed, what you expected, what happened)

## Methodology references

If you want to learn the rubric these skills were built against, the canonical sources are bundled in Anthropic's skill-creator plugin:

- `~/.claude/plugins/marketplaces/claude-plugins-official/plugins/skill-creator/skills/skill-creator/SKILL.md`
- `~/.claude/plugins/cache/claude-plugins-official/superpowers/<version>/skills/writing-skills/SKILL.md`

The "Trigger description quality" + "Frontmatter completeness" rules drive most of the design decisions you'll see in the skills here.
