#!/usr/bin/env bash
# Runs each per-unit install one-liner from INSTALL.md against a throwaway
# HOME, in bash and in zsh, and checks every SKILL.md landed and the temp
# clone is gone. Needs network (clones from GitHub). Usage: bash tests/install-oneliners.sh
set -u
REPO=https://github.com/cabaynes/charles-agent-skills.git
LINES=(
"d=\$(mktemp -d) && git clone --depth 1 $REPO \"\$d\" && mkdir -p ~/.claude/skills && cp -r \"\$d\"/claude/session-continuity/{openthreads,takenotes,putdown,pickup} ~/.claude/skills/ && rm -rf \"\$d\""
"d=\$(mktemp -d) && git clone --depth 1 $REPO \"\$d\" && mkdir -p ~/.claude/skills && cp -r \"\$d\"/claude/newproject ~/.claude/skills/ && rm -rf \"\$d\""
"d=\$(mktemp -d) && git clone --depth 1 $REPO \"\$d\" && mkdir -p ~/.claude/skills && cp -r \"\$d\"/claude/skill-dict ~/.claude/skills/ && rm -rf \"\$d\""
"d=\$(mktemp -d) && git clone --depth 1 $REPO \"\$d\" && mkdir -p ~/.claude/skills && cp -r \"\$d\"/claude/grill-me ~/.claude/skills/ && rm -rf \"\$d\""
"d=\$(mktemp -d) && git clone --depth 1 $REPO \"\$d\" && mkdir -p ~/.agents/skills && cp -r \"\$d\"/codex/{openthreads,takenotes,putdown,pickup} ~/.agents/skills/ && rm -rf \"\$d\""
"d=\$(mktemp -d) && git clone --depth 1 $REPO \"\$d\" && mkdir -p ~/.agents/skills && cp -r \"\$d\"/codex/newproject ~/.agents/skills/ && rm -rf \"\$d\""
"d=\$(mktemp -d) && git clone --depth 1 $REPO \"\$d\" && mkdir -p ~/.agents/skills && cp -r \"\$d\"/codex/skill-dict ~/.agents/skills/ && rm -rf \"\$d\""
"d=\$(mktemp -d) && git clone --depth 1 $REPO \"\$d\" && mkdir -p ~/.agents/skills && cp -r \"\$d\"/codex/grill-me ~/.agents/skills/ && rm -rf \"\$d\""
)
EXPECT=(claude/skills/openthreads claude/skills/takenotes claude/skills/putdown claude/skills/pickup
        claude/skills/newproject claude/skills/skill-dict claude/skills/grill-me
        agents/skills/openthreads agents/skills/takenotes agents/skills/putdown agents/skills/pickup
        agents/skills/newproject agents/skills/skill-dict agents/skills/grill-me)
fail=0
for shell in bash zsh; do
  command -v "$shell" >/dev/null || { echo "skip $shell (not installed)"; continue; }
  H=$(mktemp -d)
  before=$(ls -d "${TMPDIR:-/tmp}"/tmp.* 2>/dev/null | wc -l)
  for line in "${LINES[@]}"; do
    if ! HOME="$H" "$shell" -c "$line" >/dev/null 2>&1; then echo "FAIL [$shell] exit≠0: $line"; fail=1; fi
  done
  for p in "${EXPECT[@]}"; do
    [ -f "$H/.$p/SKILL.md" ] || { echo "FAIL [$shell] missing $H/.$p/SKILL.md"; fail=1; }
  done
  after=$(ls -d "${TMPDIR:-/tmp}"/tmp.* 2>/dev/null | wc -l)
  [ "$after" -le "$before" ] || { echo "FAIL [$shell] temp clone left behind"; fail=1; }
  # Documented property: a second run updates in place (cp -r merges into an
  # existing folder; it never nests a copy inside it).
  echo stale > "$H/.claude/skills/grill-me/SKILL.md"
  HOME="$H" "$shell" -c "${LINES[3]}" >/dev/null 2>&1
  [ ! -d "$H/.claude/skills/grill-me/grill-me" ] || { echo "FAIL [$shell] re-run nested a copy"; fail=1; }
  grep -q '^stale$' "$H/.claude/skills/grill-me/SKILL.md" && { echo "FAIL [$shell] re-run did not overwrite SKILL.md"; fail=1; }
  rm -rf "$H"
  echo "ok [$shell]"
done
exit $fail
