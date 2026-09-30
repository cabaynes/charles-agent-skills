# `/grill-me` — make yourself defend the plan

> An interviewer, not an executor. It asks; it never builds.

## What

`/grill-me <topic>` turns Claude into a sharp, collegial interrogator for a plan, design, or idea you are about to commit to. It does its homework first (reads the files, docs, or prior session you point it at), then works through weak points one thread at a time: assumptions you have not tested, risks you have not priced, the option you dismissed too fast. It keeps a running session file with a decision log, open threads, and a parking lot, so a long interrogation can pause and resume.

It works on anything with a plan behind it: product design, software architecture, business strategy, creative writing, research proposals.

The one hard rule: **it never performs the task being discussed.** "Grill me about migrating to Postgres" gets you questions about your migration strategy, not migration scripts. The more doable the task sounds, the more the skill resists doing it, because the planning conversation is the point.

## Origins

Written for this workflow in the tradition of community "grill me" interviewer prompts; the interviewer-not-executor rule, the session file, and the wrap-up are this version's own.

## Benefits

- **It is the only skill in this repo that pushes back.** Everything else makes it easier to build; this one makes it harder to build the wrong thing.
- **Decisions get a written trail.** The session file records what was decided and why, which `/takenotes` can later harvest into permanent memory.
- **Resumable.** Stop mid-interrogation, come back tomorrow, and it picks up the open threads instead of starting over.

## Best practices

- **Run it before anything hard to reverse:** a spend, a launch, a lease, a rewrite, a migration.
- **Give it material.** Point it at the plan doc, the repo, or the spreadsheet. Questions grounded in what you actually wrote are far better than generic ones.
- **Answer honestly, including "I don't know".** Unknowns go to the parking lot and become the to-do list.
- **Name the session.** It asks for a short plan name so the session file is findable later; sessions live in `grill-me-sessions/` in the current directory (add `grill-me-sessions/` to your project's `.gitignore` so planning notes are never committed by accident; this repo already does).
- **Wrap up explicitly.** Say you are done and it writes the summary; then run `/takenotes` if the decisions should outlive the session.

## Why this is better than alternatives

| Alternative | Problem | How `/grill-me` solves it |
|---|---|---|
| "What do you think of my plan?" | Gets a summary plus mild encouragement | Interrogation is adversarial by design; it looks for what is missing |
| Asking Claude to write the plan | You get a plan you did not think through | It refuses to execute; you do the thinking, it finds the gaps |
| A rubber-duck session with yourself | No one asks the question you are avoiding | It reads the material and asks about what you left out |
| A generic "devil's advocate" prompt | Forgets where it was after one reply | Persistent session file with threads, decisions, and a parking lot |

## Eval result

Trigger-accuracy benchmark, LLM-as-judge over 20 queries (10 realistic should-trigger, 10 adversarial should-not-trigger): **recall 10/10, precision 10/10** on 2026-09-08. That is after one description revision: round 1 missed a resume-my-session phrasing (9/10 recall), so the trigger list now names it. The adversarial half included the literal word "grill" in a cooking question, "quiz me" (interrogation without a plan), and execution requests that name a plan ("write the migration plan"). Full per-query results in the root [eval-results.md](../../eval-results.md).

## Install

```bash
cp -r charles-agent-skills/claude/grill-me ~/.claude/skills/
```

Then close your Claude Code window and open a fresh one. Say "grill me about ..." or type `/grill-me <topic>`.
