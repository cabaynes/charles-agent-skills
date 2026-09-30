#!/usr/bin/env bash
#
# snapshot.sh — refresh the public repo from local skills with sanitization.
#
# Source of truth: ~/.claude/skills/<name>/  (Charles's local, daily-use copies)
# Target:          this repo's claude/<name>/  (sanitized public snapshot)
#
# Copies pickup, skill-dict, and grill-me. The other three are NOT copied — each has a
# parameterized public fork that is
# maintained BY HAND, because the local version encodes setup this repo's users don't have:
#
#   /newproject  — local version hardcodes one workspace layout; public version is parameterized.
#   /takenotes   — local version assumes a canonical shared-memory store with symlinks fanned
#                  into every project, plus a sync script to rebuild them. The public version
#                  treats that as an optional pattern it DETECTS (Step 1c looks for symlinks)
#                  rather than a requirement, so it works on a plain single-project setup.
#   /putdown     — the public version must degrade gracefully when /takenotes is absent
#                  ("if installed, invoke it; otherwise do this inline"). The local version
#                  invokes it unconditionally, because locally it is always installed.
#                  Auto-copying would silently delete that fallback and break standalone installs.
#
# These three are still SANITIZED and residue-checked below (sanitization is idempotent, so
# running it over an already-clean hand-maintained file is a harmless no-op) — they are just
# never overwritten from ~/.claude/skills/.
#
# Run from anywhere; resolves its own location.

set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOCAL_SKILLS="${HOME}/.claude/skills"
PUBLIC_SKILLS="${REPO_DIR}/claude"

echo "Refreshing public snapshot in ${PUBLIC_SKILLS}/ from ${LOCAL_SKILLS}/"

# --- 1. Copy pickup (putdown + takenotes are hand-maintained forks — see header) ---
echo "  • copying pickup into session-continuity/"
mkdir -p "${PUBLIC_SKILLS}/session-continuity/pickup"
cp "${LOCAL_SKILLS}/pickup/SKILL.md" "${PUBLIC_SKILLS}/session-continuity/pickup/SKILL.md"
echo "  • SKIPPING putdown + takenotes (hand-maintained public forks — do not auto-copy)"

# --- 2. Copy skill-dict (including references/) ---
echo "  • copying skill-dict + references/"
mkdir -p "${PUBLIC_SKILLS}/skill-dict/references"
cp "${LOCAL_SKILLS}/skill-dict/SKILL.md" "${PUBLIC_SKILLS}/skill-dict/SKILL.md"
cp "${LOCAL_SKILLS}/skill-dict/references/"*.md "${PUBLIC_SKILLS}/skill-dict/references/"

# --- 2b. Copy grill-me (local canonical is a symlink into ~/CLAUDE/skills-library; cp follows it) ---
echo "  • copying grill-me"
mkdir -p "${PUBLIC_SKILLS}/grill-me"
cp "${LOCAL_SKILLS}/grill-me/SKILL.md" "${PUBLIC_SKILLS}/grill-me/SKILL.md"

# --- 3. Apply sanitization to every copied *.md file ---
# Order matters: do longer/more-specific patterns BEFORE shorter ones.
echo "  • sanitizing personal paths and names"

SANITIZE_TARGETS=(
  "${PUBLIC_SKILLS}/session-continuity/putdown/SKILL.md"
  "${PUBLIC_SKILLS}/session-continuity/pickup/SKILL.md"
  "${PUBLIC_SKILLS}/session-continuity/takenotes/SKILL.md"
  "${PUBLIC_SKILLS}/skill-dict/SKILL.md"
  "${PUBLIC_SKILLS}/skill-dict/references/sync.md"
  "${PUBLIC_SKILLS}/skill-dict/references/check-updates.md"
  "${PUBLIC_SKILLS}/skill-dict/references/add.md"
  "${PUBLIC_SKILLS}/grill-me/SKILL.md"
)

for f in "${SANITIZE_TARGETS[@]}"; do
  # Memory-dir slug specifics first (longer pattern)
  sed -i '' 's|-Users-charles-CLAUDE|<project-slug>|g' "$f"
  # Library root (specific path) before generic CLAUDE root
  sed -i '' 's|/Users/charles/CLAUDE/skills-library/|~/skills-library/|g' "$f"
  sed -i '' 's|/Users/charles/CLAUDE/skills-library|~/skills-library|g' "$f"
  # Charles's workspace root
  sed -i '' 's|/Users/charles/CLAUDE/|<workspace-root>/|g' "$f"
  sed -i '' 's|/Users/charles/CLAUDE|<workspace-root>|g' "$f"
  # .claude home dir
  sed -i '' 's|/Users/charles/.claude/|~/.claude/|g' "$f"
  sed -i '' 's|/Users/charles/.claude|~/.claude|g' "$f"
  # Catch-all home dir
  sed -i '' 's|/Users/charles/|~/|g' "$f"
  sed -i '' 's|/Users/charles|~|g' "$f"
  # Personal name (possessive first, then bare)
  sed -i '' "s|Charles's|your|g" "$f"
  sed -i '' 's|Charles |you |g' "$f"
  sed -i '' 's|Charles$|you|g' "$f"
  sed -i '' 's|Charles\.|you.|g' "$f"
  sed -i '' 's|Charles,|you,|g' "$f"
done

# --- 4. Guard against sanitization residue ---
# The sed rules above convert "Charles" / "Charles's" → "you" / "your", which only
# reads correctly when the source uses possessives or second person. A source line
# written in third-person subject form (e.g. "Charles maintains ... he's installed")
# sanitizes to broken text ("you maintains ... he's installed"): sed can't fix verb
# agreement, and bare pronouns (he/his/him/he's) referring to the maintainer aren't
# caught by the name rules. Those pronouns almost always travel with such drift, so
# fail loudly on a leaked name or pronoun — drift gets fixed at the source, never
# shipped silently. (The content has no legitimate third-person pronouns; if a future
# skill needs one referring to someone else, narrow this check then.) The same check fails on
# the maintainer's private project names, so worked examples stay generic (my-app, RecipeBox).
echo "  • checking for sanitization residue"
RESIDUE=0
for f in "${SANITIZE_TARGETS[@]}"; do
  if grep -nEi "\bCharles\b|\bhe's\b|\bhis\b|\bhim\b|\bhe\b|jessica|BookmarkSync|\blotto\b|\bSBG\b|FPSpec|\bWedding\b" "$f"; then
    echo "    ↑ residue in ${f#${REPO_DIR}/}" >&2
    RESIDUE=1
  fi
done
if [ "$RESIDUE" -ne 0 ]; then
  echo "" >&2
  echo "ERROR: sanitization residue detected (see matches above)." >&2
  echo "Fix the LOCAL source in ${LOCAL_SKILLS}/ — rewrite third-person subject" >&2
  echo "references (\"Charles maintains\", \"he's installed\") as possessives" >&2
  echo "(\"Charles's\") or second person (\"You maintain\"), then re-run." >&2
  exit 1
fi

echo ""
echo "Done. Verify with:"
echo "  grep -rE '/Users/charles|Charles' ${PUBLIC_SKILLS}/  || echo OK"
