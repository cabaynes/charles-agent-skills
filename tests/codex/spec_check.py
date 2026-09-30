#!/usr/bin/env python3
"""Static check of every generated Codex skill against the Agent Skills specification
(https://agentskills.io/specification) plus this repo's own conventions. No API calls.

Usage: python3 tests/codex/spec_check.py
"""

import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]
SPEC_FIELDS = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}


def frontmatter(text):
    m = re.match(r"---\n(.*?)\n---\n", text, re.S)
    if not m:
        return None, text
    fields, cur = {}, None
    for line in m.group(1).split("\n"):
        k = re.match(r"([A-Za-z][\w-]*):\s?(.*)$", line)
        if k and not line.startswith(" "):
            cur = k.group(1)
            fields[cur] = k.group(2).strip()
        elif cur:
            fields[cur] += " " + line.strip()
    for k, v in fields.items():
        v = v.strip()
        if v in (">", "|") or v.startswith(("> ", "| ")):
            v = v[1:].strip()
        fields[k] = v.strip('"')
    return fields, text[m.end():]


def check(skill_dir):
    rows = []
    add = lambda ok, what: rows.append((bool(ok), what))
    text = (skill_dir / "SKILL.md").read_text()
    fm, body = frontmatter(text)
    add(fm is not None, "has YAML frontmatter")
    fm = fm or {}
    name, desc = fm.get("name", ""), fm.get("description", "")
    add(name == skill_dir.name, f"name matches folder ({name!r})")
    add(re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", name) and len(name) <= 64,
        "name: 1-64 chars, lowercase letters/digits/single hyphens")
    add(0 < len(desc) <= 1024, f"description non-empty and <= 1024 chars ({len(desc)})")
    extra = set(fm) - SPEC_FIELDS
    add(not extra, f"only spec frontmatter fields{'' if not extra else ' — extra: ' + ', '.join(sorted(extra))}")
    add(re.search(r"\buse (when|at|for)\b", desc, re.I), "description says when to use it")
    add(re.search(r"\bdo not\b|\bdon't\b", desc, re.I), "description says when NOT to use it")
    add(f"${name}" in body, f"body shows Codex invocation ${name}")
    prose = re.sub(r"```.*?```", "", body, flags=re.S)       # examples in code aren't links
    prose = re.sub(r"`[^`\n]*`", "", prose)
    links = re.findall(r"\]\((?!https?:|#|mailto:)([^)\s]+)\)", prose)
    missing = [l for l in links if not (skill_dir / l.split("#")[0]).exists() and not l.startswith(("/", "~", "$", "<"))]
    add(not missing, f"relative links resolve{'' if not missing else ' — missing: ' + ', '.join(missing)}")
    return rows


def main():
    total = passed = 0
    for d in sorted(p for p in (REPO / "codex").iterdir() if p.is_dir()):
        rows = check(d)
        ok = sum(r[0] for r in rows)
        total += len(rows)
        passed += ok
        print(f"{d.name:11} {ok}/{len(rows)}")
        for good, what in rows:
            if not good:
                print(f"    FAIL  {what}")
    print(f"\n{passed}/{total} spec checks passed")
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
