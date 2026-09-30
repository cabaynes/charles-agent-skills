#!/usr/bin/env python3
"""build-codex.py — generate the Codex versions of the skills from the Claude versions.

Source of truth: claude/**/SKILL.md (the Claude Code versions, refreshed by snapshot.sh).
Overlays:        codex-overlays/<name>.overlay   (only what differs for Codex)
Output:          codex/<name>/                   (never edit by hand — rebuilt every run)

Overlay directives (each block runs until the next line starting with "@@ "):

  @@ frontmatter            full Codex frontmatter body (the lines between the --- fences)
  @@ prepend                text inserted right after the frontmatter
  @@ section <heading>      replace that heading and its body (up to the next heading of the
                            same or higher level, ignoring headings inside code fences)
  @@ drop <heading>         remove that heading and its body
  @@ replace [N]            exact old text; must occur exactly N times (default 1) ...
  @@ with                   ... replaced by this text
  @@ file <relative path>   later directives target that file (default SKILL.md); used for
                            skill-dict's references/
  @@ allow <regex>          permit a leak-check match on lines matching this regex

The build fails, and writes nothing, when an overlay's anchor text or heading is not found
exactly as expected (the Claude source drifted — update the overlay) or when a Codex output
still contains a Claude-only term not covered by an `@@ allow`.
"""

import pathlib
import re
import shutil
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SKILLS = {
    "grill-me": "claude/grill-me",
    "newproject": "claude/newproject",
    "skill-dict": "claude/skill-dict",
    "putdown": "claude/session-continuity/putdown",
    "pickup": "claude/session-continuity/pickup",
    "takenotes": "claude/session-continuity/takenotes",
}
# Files copied from each Claude skill folder into its Codex folder (README.md is Claude install
# docs, so it is not carried over; the repo INSTALL.md covers Codex).
CARRY = ("SKILL.md", "LICENSE", "references")
LEAKS = re.compile(
    r"AskUserQuestion|TodoWrite|CLAUDE_CODE_ENTRYPOINT|~/\.claude|\$HOME/\.claude|"
    r"CLAUDE\.md|MEMORY\.md|Claude Code|\bSkill tool\b|/clear\b|allowed-tools|argument-hint"
)


class BuildError(Exception):
    pass


def parse_overlay(text):
    ops, cur = [], None
    for line in text.split("\n"):
        if line.startswith("@@ ") or line == "@@":
            if cur:
                ops.append(cur)
            parts = line[3:].split(" ", 1)
            cur = {"op": parts[0], "arg": parts[1] if len(parts) > 1 else "", "body": []}
        elif cur is not None:
            cur["body"].append(line)
        elif line.strip():
            raise BuildError(f"text before the first @@ directive: {line!r}")
    if cur:
        ops.append(cur)
    for o in ops:
        o["body"] = "\n".join(o["body"]).strip("\n")
    return ops


def split_frontmatter(s):
    m = re.match(r"---\n(.*?)\n---\n", s, re.S)
    if not m:
        raise BuildError("no frontmatter")
    return m.group(1), s[m.end():]


def heading_level(line):
    m = re.match(r"(#{1,6}) ", line)
    return len(m.group(1)) if m else 0


def find_section(body, heading):
    lines = body.split("\n")
    fence, start = False, None
    level = heading_level(heading)
    if not level:
        raise BuildError(f"not a markdown heading: {heading!r}")
    for i, line in enumerate(lines):
        if line.lstrip().startswith("```"):
            fence = not fence
            continue
        if fence:
            continue
        if start is None:
            if line.rstrip() == heading.rstrip():
                start = i
        elif 0 < heading_level(line) <= level:
            return lines, start, i
    if start is None:
        raise BuildError(f"heading not found: {heading!r}")
    return lines, start, len(lines)


def apply_ops(files, ops, name):
    target, allows, pending = "SKILL.md", [], None
    for o in ops:
        op, arg, text = o["op"], o["arg"], o["body"]
        if op == "file":
            target = arg.strip()
            if target not in files:
                raise BuildError(f"{name}: @@ file {target} does not exist")
            continue
        if op == "allow":
            allows.append(re.compile(arg.strip()))
            continue
        s = files[target]
        if op == "frontmatter":
            _, rest = split_frontmatter(s)
            files[target] = f"---\n{text}\n---\n{rest}"
        elif op == "prepend":
            fm, rest = split_frontmatter(s)
            files[target] = f"---\n{fm}\n---\n\n{text}\n\n{rest.lstrip(chr(10))}"
        elif op in ("section", "drop"):
            lines, a, b = find_section(s, arg)
            new = [] if op == "drop" else text.split("\n") + [""]
            files[target] = "\n".join(lines[:a] + new + lines[b:])
        elif op == "replace":
            pending = (text, int(arg) if arg.strip() else 1)
        elif op == "with":
            if pending is None:
                raise BuildError(f"{name}: @@ with without a preceding @@ replace")
            old, want = pending
            got = s.count(old)
            if got != want:
                raise BuildError(f"{name}/{target}: replace anchor found {got}x, expected {want}x:\n  {old[:120]!r}")
            files[target] = s.replace(old, text)
            pending = None
        else:
            raise BuildError(f"{name}: unknown directive @@ {op}")
    if pending is not None:
        raise BuildError(f"{name}: @@ replace without @@ with")
    return allows


def leak_check(files, allows, name):
    problems = []
    for path, s in files.items():
        fence_free = s
        for n, line in enumerate(fence_free.split("\n"), 1):
            if LEAKS.search(line) and not any(a.search(line) for a in allows):
                problems.append(f"  codex/{name}/{path}:{n}: {line.strip()[:140]}")
    return problems


def build(only=None):
    out_root = ROOT / "codex"
    staged, errors = {}, []
    for name, rel in SKILLS.items():
        if only and name not in only:
            continue
        src = ROOT / rel
        overlay = ROOT / "codex-overlays" / f"{name}.overlay"
        if not overlay.exists():
            errors.append(f"{name}: missing {overlay.relative_to(ROOT)}")
            continue
        files = {"SKILL.md": (src / "SKILL.md").read_text()}
        refs = src / "references"
        if refs.is_dir():
            for f in sorted(refs.glob("*.md")):
                files[f"references/{f.name}"] = f.read_text()
        try:
            allows = apply_ops(files, parse_overlay(overlay.read_text()), name)
        except BuildError as e:
            errors.append(str(e))
            continue
        leaks = leak_check(files, allows, name)
        if leaks:
            errors.append(f"{name}: Claude-only terms left in the Codex version:\n" + "\n".join(leaks))
            continue
        staged[name] = (src, files)
    if errors:
        print("BUILD FAILED — nothing written.\n", file=sys.stderr)
        print("\n\n".join(errors), file=sys.stderr)
        return 1
    if out_root.exists() and not only:
        shutil.rmtree(out_root)
    for name, (src, files) in staged.items():
        dest = out_root / name
        if dest.exists():
            shutil.rmtree(dest)
        for path, text in files.items():
            p = dest / path
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(text if text.endswith("\n") else text + "\n")
        if (src / "LICENSE").exists():
            shutil.copy(src / "LICENSE", dest / "LICENSE")
        print(f"  built codex/{name}/ ({len(files)} file{'s' if len(files) != 1 else ''})")
    (out_root / "README.md").write_text(
        "# Codex versions — generated, do not edit\n\n"
        "Built by `scripts/build-codex.py` from the Claude Code skills in `claude/` plus the overlays in\n"
        "`codex-overlays/`. Edit those, then rebuild. Install: see the Codex section of `INSTALL.md`.\n"
    )
    return 0


if __name__ == "__main__":
    # `build-codex.py name [name...]` rebuilds only those skills (for working on one overlay);
    # with no arguments it rebuilds everything from scratch.
    sys.exit(build(set(sys.argv[1:]) or None))
