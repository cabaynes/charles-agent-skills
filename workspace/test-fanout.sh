#!/usr/bin/env bash
#
# test-fanout.sh — exercise fanout-memory.sh against a throwaway HOME.
#
# Usage: bash workspace/test-fanout.sh   (from anywhere; resolves its own location)
# Exit status 0 when every check passes. Touches nothing outside a temp directory.

set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPT="$HERE/fanout-memory.sh"
[ -x "$SCRIPT" ] || { echo "FAIL: $SCRIPT missing or not executable"; exit 1; }

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
export HOME="$TMP/home"
export WORKSPACE_DIR="$HOME/CLAUDE"
mkdir -p "$WORKSPACE_DIR"

SLUG="$(printf '%s' "$WORKSPACE_DIR" | tr '/' '-')"
HUB="$HOME/.claude/projects/$SLUG/memory"
RECIPES="$HOME/.claude/projects/$SLUG-recipes/memory"

pass=0; fail=0
check() {  # check "<label>" <command...>
  local label="$1"; shift
  if "$@" >/dev/null 2>&1; then echo "  ok   $label"; pass=$((pass+1)); else echo "  FAIL $label"; fail=$((fail+1)); fi
}
not() { ! "$@"; }

echo "1. empty hub: exits 1 with a hint, and creates the hub dir"
check "exit status is non-zero" not "$SCRIPT"
check "hub dir was created"     test -d "$HUB"
check "hint names user_profile" bash -c "'$SCRIPT' 2>&1 | grep -q 'user_profile.md'"

printf -- '---\nname: user-profile\ndescription: Who I am and how I like Claude to work\nmetadata:\n  type: user\n---\n\nExample profile.\n' > "$HUB/user_profile.md"
printf -- '- [User profile](user_profile.md) — who I am\n' > "$HUB/MEMORY.md"

echo "2. status with no subprojects"
check "lists user_profile.md"  bash -c "'$SCRIPT' | grep -q 'user_profile.md'"
check "says no subprojects yet" bash -c "'$SCRIPT' | grep -q 'no subprojects yet'"

echo "3. seed one subproject"
"$SCRIPT" recipes >/dev/null
check "symlink points at the hub" test "$(readlink "$RECIPES/user_profile.md")" = "$HUB/user_profile.md"
check "MEMORY.md was seeded"      grep -q '(user_profile.md)' "$RECIPES/MEMORY.md"

echo "4. a new universal fans out with --all"
printf -- '---\nname: feedback-brief\ndescription: "Keep answers brief"\nmetadata:\n  type: feedback\n---\n\nBe brief.\n' > "$HUB/feedback_brief.md"
"$SCRIPT" --all >/dev/null
check "symlink added"         test -L "$RECIPES/feedback_brief.md"
check "index line added"      grep -qF -- '- [Keep answers brief](feedback_brief.md)' "$RECIPES/MEMORY.md"
check "YAML quotes stripped"  not grep -q '"Keep' "$RECIPES/MEMORY.md"

echo "5. re-running is idempotent"
check "reports already current"  bash -c "'$SCRIPT' --all | grep -q 'already current'"
check "no duplicate index lines" test "$(grep -c '(feedback_brief.md)' "$RECIPES/MEMORY.md")" = 1

echo "6. project_*.md and reference_*.md are not fanned out"
printf -- '---\nname: project-x\ndescription: local only\nmetadata:\n  type: project\n---\n' > "$HUB/project_x.md"
printf -- '---\nname: reference-y\ndescription: local only\nmetadata:\n  type: reference\n---\n' > "$HUB/reference_y.md"
"$SCRIPT" --all >/dev/null
check "project file not linked"   not test -e "$RECIPES/project_x.md"
check "reference file not linked" not test -e "$RECIPES/reference_y.md"

echo "7. a tilde in WORKSPACE_DIR expands to HOME"
check "hub path resolved" bash -c "WORKSPACE_DIR='~/CLAUDE' '$SCRIPT' | grep -qF '$HUB'"

echo "8. a real file in a project is never replaced by a symlink; a trailing slash on WORKSPACE_DIR is harmless"
mkdir -p "$HOME/.claude/projects/$SLUG-keep/memory"
printf -- '---\nname: user-profile\ndescription: LOCAL copy that must survive\nmetadata:\n  type: user\n---\n' > "$HOME/.claude/projects/$SLUG-keep/memory/user_profile.md"
"$SCRIPT" keep >/dev/null
check "real file left in place"      not test -L "$HOME/.claude/projects/$SLUG-keep/memory/user_profile.md"
check "real file content intact"     grep -q 'LOCAL copy that must survive' "$HOME/.claude/projects/$SLUG-keep/memory/user_profile.md"
check "other universal still linked" test -L "$HOME/.claude/projects/$SLUG-keep/memory/feedback_brief.md"
check "trailing slash resolves same hub" bash -c "WORKSPACE_DIR='$WORKSPACE_DIR/' '$SCRIPT' | grep -qF '$HUB'"
check "--help works with an empty hub" bash -c "HOME='$TMP/home2' WORKSPACE_DIR='$TMP/home2/CLAUDE' '$SCRIPT' --help | grep -q 'Usage:'"

echo "9. the index is rebuilt, not appended: a hook replaces the stale line"
IDX="$RECIPES/MEMORY.md"
printf -- '---\nname: feedback-brief\ndescription: "Keep answers brief"\nhook: "Short answers; detail only on request"\nmetadata:\n  type: feedback\n---\n\nBe brief.\n' > "$HUB/feedback_brief.md"
"$SCRIPT" --all >/dev/null
check "new hook line present"   grep -qF -- '- [Short answers; detail only on request](feedback_brief.md)' "$IDX"
check "stale line gone"         not grep -qF 'Keep answers brief](' "$IDX"
check "one line per universal"  test "$(grep -c '(feedback_brief.md)' "$IDX")" = 1

echo "10. project lines are kept verbatim and sit above the shared list"
printf -- '- [Oven runs hot](project_oven.md) — bake 10 degrees lower\n' >> "$IDX"
"$SCRIPT" recipes >/dev/null
check "project line kept"       grep -qF -- '- [Oven runs hot](project_oven.md) — bake 10 degrees lower' "$IDX"
proj_ln=$(grep -n 'project_oven.md' "$IDX" | cut -d: -f1)
shared_ln=$(grep -n '^## Shared notes' "$IDX" | cut -d: -f1)
check "project line above shared list" test "$proj_ln" -lt "$shared_ln"
check "placeholder gone once a project note exists" not grep -q 'no project-specific notes yet' "$IDX"

echo "11. pinned universals come first"
printf -- '---\nname: feedback-safety\ndescription: Never run destructive commands without asking\npinned: true\nmetadata:\n  type: feedback\n---\n' > "$HUB/feedback_safety.md"
"$SCRIPT" --all >/dev/null
pin_ln=$(grep -n '(feedback_safety.md)' "$IDX" | cut -d: -f1)
check "pinned line above the project section" test "$pin_ln" -lt "$proj_ln"
check "pointer to the full list in the pinned block" grep -qF 'SHARED-NOTES.md' "$IDX"
check "full list written in the hub"  grep -qF '★ [feedback_safety.md]' "$HUB/SHARED-NOTES.md"

echo "12. a project's own copy of a universal stays a project line; the hub's index is rebuilt too"
KEEP="$HOME/.claude/projects/$SLUG-keep/memory"
printf -- '- [My own profile](user_profile.md) — local copy\n' >> "$KEEP/MEMORY.md"
"$SCRIPT" --all >/dev/null
check "local-copy line kept verbatim" grep -qF -- '- [My own profile](user_profile.md) — local copy' "$KEEP/MEMORY.md"
check "hub index has the generated list" grep -q '^## Shared notes' "$HUB/MEMORY.md"
check "hub's hand-written line replaced, not duplicated" test "$(grep -c '(user_profile.md)' "$HUB/MEMORY.md")" = 1
check "second run changes nothing" not bash -c "'$SCRIPT' --all | grep -q 'rebuilt'"

echo "13. --check reports sizes and flags an index over the limit"
check "--check passes on small indexes" "$SCRIPT" --check
for i in $(seq 1 190); do printf -- '- [Note %s](project_n%s.md) — %0150d\n' "$i" "$i" 0; done >> "$IDX"
check "--check fails on a huge index"   not "$SCRIPT" --check recipes
check "--check names the problem"       bash -c "'$SCRIPT' --check recipes | grep -q 'OVER LIMIT'"
check "--all still finishes and warns"  bash -c "'$SCRIPT' --all | grep -q 'OVER LIMIT'"

echo ""
echo "$pass passed, $fail failed"
[ "$fail" -eq 0 ]
