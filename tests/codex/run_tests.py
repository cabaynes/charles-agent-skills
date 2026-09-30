#!/usr/bin/env python3
"""End-to-end tests of the Codex skill versions (codex/), run through the real `codex exec`.

Isolation: every run gets a throwaway CODEX_HOME holding only these skills, a two-line config
(model + reasoning effort copied from your real config), and a SYMLINK to your existing
auth.json — credentials are never copied, and the link is removed at the end. Git "pushes" go
to a local bare repo. Your real ~/.codex (global AGENTS.md, notes, putdowns, memories) is never
written.

Usage:  python3 tests/codex/run_tests.py [scenario ...] [--keep] [--api-key-from FILE]
        --api-key-from signs the throwaway home in with FILE's OPENAI_API_KEY (billed per token)
        instead of linking your ChatGPT sign-in — useful when the plan's Codex limit is used up.
        Scenarios: grill-me takenotes putdown pickup newproject skill-dict (default: all, in order;
        pickup needs putdown's handoff, so it runs putdown first if you name only pickup).
"""

import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
import time

REPO = pathlib.Path(__file__).resolve().parents[2]
REAL_HOME = pathlib.Path(os.environ.get("CODEX_HOME") or pathlib.Path.home() / ".codex")
ORDER = ["grill-me", "takenotes", "putdown", "pickup", "newproject", "skill-dict"]


def sh(cmd, cwd=None, check=True):
    r = subprocess.run(cmd, cwd=cwd, shell=isinstance(cmd, str), capture_output=True, text=True)
    if check and r.returncode:
        raise RuntimeError(f"{cmd}: {r.stderr.strip()}")
    return r.stdout.strip()


def slug(path):
    return str(path).replace("/", "-")


class UsageLimit(Exception):
    """Codex refused the run for quota reasons: the result says nothing about the skill."""


class Env:
    def __init__(self, keep, key_file=None):
        self.keep = keep
        self.root = pathlib.Path(tempfile.mkdtemp(prefix="codex-skilltest-")).resolve()
        self.home = self.root / "codex-home"
        self.work = self.root / "work"
        self.logs = self.root / "logs"
        for d in (self.home / "skills", self.work, self.logs):
            d.mkdir(parents=True)
        cfg = (REAL_HOME / "config.toml").read_text() if (REAL_HOME / "config.toml").exists() else ""
        keep_lines = [l for l in cfg.splitlines() if re.match(r"(model|model_reasoning_effort)\s*=", l)]
        if key_file:  # keep the key in this throwaway home's auth.json, never the OS keychain
            keep_lines.append('cli_auth_credentials_store = "file"')
        (self.home / "config.toml").write_text("\n".join(keep_lines) + "\n")
        if key_file:
            # Sign the throwaway home in with an API key. Only the OPENAI_API_KEY line is read,
            # it goes to `codex login` on stdin, and it is never printed or put in any env.
            m = re.search(r"^\s*(?:export\s+)?OPENAI_API_KEY\s*=\s*['\"]?([^'\"\s#]+)",
                          pathlib.Path(key_file).expanduser().read_text(), re.M)
            if not m:
                sys.exit(f"no OPENAI_API_KEY line in {key_file}")
            r = subprocess.run(["codex", "login", "--with-api-key"], input=m.group(1) + "\n", text=True,
                               capture_output=True, env=dict(os.environ, CODEX_HOME=str(self.home)))
            if r.returncode:
                sys.exit("codex login --with-api-key failed (output withheld: it may echo the key)")
            if not (self.home / "auth.json").is_file():
                sys.exit("API key did not land in the throwaway auth.json — refusing to continue")
        else:
            auth = REAL_HOME / "auth.json"
            if not auth.exists():
                sys.exit(f"no Codex sign-in at {auth} — sign in to Codex first")
            (self.home / "auth.json").symlink_to(auth)
        for d in (REPO / "codex").iterdir():
            if d.is_dir():
                shutil.copytree(d, self.home / "skills" / d.name)
        # a project repo with a local bare "origin"
        self.app = self.work / "app"
        self.origin = self.root / "origin.git"
        sh(f"git init -q --bare {self.origin}")
        self.app.mkdir()
        (self.app / "cli.py").write_text("import argparse\n\np = argparse.ArgumentParser()\n")
        (self.app / ".gitignore").write_text(".env\n")
        sh("git init -q -b main && git add -A && git -c user.name=t -c user.email=t@t "
           f"commit -qm init && git remote add origin {self.origin} && git push -qu origin main",
           cwd=self.app)
        sh("git config user.name tester && git config user.email tester@example.com", cwd=self.app)

    def codex(self, name, prompt, cwd, extra_env=None, sandbox="workspace-write", approve=False):
        out = self.logs / f"{name}.last.md"
        env = dict(os.environ, CODEX_HOME=str(self.home), **(extra_env or {}))
        # --approve-for-me implies the workspace-write sandbox and refuses an explicit -s.
        cmd = ["codex", "exec"] + ([] if approve else ["-s", sandbox]) + ["--ephemeral", "--skip-git-repo-check",
               "-C", str(cwd), "--add-dir", str(self.root), "-o", str(out)]
        # Codex's sandbox write-protects .git; a real user approves the commit when asked.
        # --approve-for-me routes that approval through Codex's automatic review instead.
        cmd += (["--approve-for-me"] if approve else []) + ["-"]
        t = time.time()
        with open(self.logs / f"{name}.log", "w") as log:
            r = subprocess.run(cmd, input=prompt, env=env, stdout=log, stderr=subprocess.STDOUT,
                               text=True, timeout=1200)
        if re.search(r"hit your usage limit|rate limit exceeded", (self.logs / f"{name}.log").read_text(), re.I):
            raise UsageLimit(f"Codex usage limit reached during '{name}' — rerun after it resets "
                             f"(see {self.logs / (name + '.log')})")
        return r.returncode, (out.read_text() if out.exists() else ""), round(time.time() - t)

    def close(self):
        (self.home / "auth.json").unlink(missing_ok=True)
        if not self.keep:
            shutil.rmtree(self.root, ignore_errors=True)


def check(results, name, cond, what):
    results.append((name, bool(cond), what))


# ---------------------------------------------------------------- scenarios

def t_grill_me(e, R):
    d = e.work / "grill"
    d.mkdir()
    sh("git init -q", cwd=d)
    rc, last, secs = e.codex("grill-me", "$grill-me\nPlan name: db-migration.\nThe plan: move the "
                             "users table from SQLite to Postgres over one weekend with no downtime.\n"
                             "Start the session and ask your first question.", d)
    f = d / "grill-me-sessions" / "db-migration.grill.md"
    check(R, "grill-me", rc == 0, f"codex exited 0 ({secs}s)")
    check(R, "grill-me", f.exists(), "session file grill-me-sessions/db-migration.grill.md created")
    check(R, "grill-me", "?" in last, "ended by asking a question")
    stray = [p for p in sh("git status --porcelain", cwd=d).splitlines() if "grill-me-sessions" not in p]
    check(R, "grill-me", not stray, f"wrote nothing besides the session file {stray or ''}")


def t_takenotes(e, R):
    notes = e.home / "notes" / "projects" / slug(e.app)
    rc, last, secs = e.codex("takenotes", "Context from this session: we found that the vendor API "
                             "(acme) rate-limits at 5 requests/second and returns HTTP 429 with no "
                             "Retry-After header, so our client now sleeps 250ms between calls. Also, "
                             "I (the user) always want a dry-run shown before any bulk write, in every "
                             "project.\n$takenotes", e.app)
    check(R, "takenotes", rc == 0, f"codex exited 0 ({secs}s)")
    idx = notes / "INDEX.md"
    check(R, "takenotes", idx.exists(), f"project INDEX.md at notes/projects/<slug>/")
    proj_text = " ".join(p.read_text() for p in notes.glob("*.md")) if notes.exists() else ""
    check(R, "takenotes", re.search(r"429|5 requests|rate.?limit", proj_text, re.I),
          "vendor rate-limit finding stored as a project note")
    glob_dir = e.home / "notes" / "global"
    glob_text = " ".join(p.read_text() for p in glob_dir.glob("*.md")) if glob_dir.exists() else ""
    check(R, "takenotes", re.search(r"dry.?run", glob_text, re.I),
          "cross-project preference (dry-run) stored in global notes")
    agents = e.home / "AGENTS.md"
    ptr = agents.read_text().count("notes/global/INDEX.md") if agents.exists() else 0
    check(R, "takenotes", ptr >= 1, "global AGENTS.md points at notes/global/INDEX.md")
    check(R, "takenotes", "Operational" in last, "report includes the required Operational block")
    rc2, last2, secs2 = e.codex("takenotes-2", "Nothing new happened; just re-check.\n$takenotes", e.app)
    ptr2 = agents.read_text().count("notes/global/INDEX.md") if agents.exists() else 0
    check(R, "takenotes", rc2 == 0 and ptr2 == ptr, f"second run keeps one pointer (was {ptr}, now {ptr2}; {secs2}s)")


def t_putdown(e, R):
    before = int(sh("git rev-list --count HEAD", cwd=e.app))
    with open(e.app / "cli.py", "a") as f:
        f.write('p.add_argument("--seed", type=int, default=0)\n')
    rc, last, secs = e.codex("putdown", "This session: added a --seed flag to cli.py (still "
                             "uncommitted). Next step is writing tests for it. Make sure the next "
                             "session verifies the seed flag against real data before anything else.\n"
                             "$putdown", e.app, approve=True)
    check(R, "putdown", rc == 0, f"codex exited 0 ({secs}s)")
    files = sorted((e.home / "putdowns" / "app").glob("20*.md"))
    check(R, "putdown", files, "handoff written to $CODEX_HOME/putdowns/app/")
    text = files[-1].read_text() if files else ""
    must = re.search(r"## Must address next session\n(.*?)\n## ", text, re.S)
    check(R, "putdown", must and re.search(r"seed", must.group(1), re.I),
          "'Must address next session' carries the seed-verification item")
    check(R, "putdown", "$pickup" in text and "/pickup" not in text, "paste line is $pickup")
    check(R, "putdown", sh("git status --porcelain", cwd=e.app) == "", "working tree clean after commit")
    after = int(sh("git rev-list --count HEAD", cwd=e.app))
    check(R, "putdown", after - before == 1, f"exactly one new commit (got {after - before})")
    check(R, "putdown", sh("git rev-parse HEAD", cwd=e.app) == sh(f"git --git-dir {e.origin} rev-parse main"),
          "pushed: origin/main matches local HEAD")


def t_pickup(e, R):
    head = sh("git rev-parse HEAD", cwd=e.app)
    status = sh("git status --porcelain", cwd=e.app)
    rc, last, secs = e.codex("pickup", "$pickup", e.app)
    check(R, "pickup", rc == 0, f"codex exited 0 ({secs}s)")
    check(R, "pickup", re.search(r"must address", last, re.I) and re.search(r"seed", last, re.I),
          "briefing echoes the Must-address seed item")
    check(R, "pickup", sh("git status --porcelain", cwd=e.app) == status and sh("git rev-parse HEAD", cwd=e.app) == head,
          "stopped for confirmation (no edits, no commits)")


def t_newproject(e, R):
    ws = e.work / "workspace"
    ws.mkdir()
    rc, last, secs = e.codex("newproject", "$newproject demo-app\nAnswers up front: yes to git init, "
                             "no GitHub repo, no umbrella entry.", ws, extra_env={"WORKSPACE_DIR": str(ws)})
    p = ws / "demo-app"
    check(R, "newproject", rc == 0, f"codex exited 0 ({secs}s)")
    check(R, "newproject", (p / "AGENTS.md").exists(), "AGENTS.md stub created")
    check(R, "newproject", not (p / "CLAUDE.md").exists(), "no CLAUDE.md created")
    check(R, "newproject", (e.home / "notes" / "projects" / slug(p) / "INDEX.md").exists(),
          "notes folder with INDEX.md at notes/projects/<slug>/")
    check(R, "newproject", (p / ".git").is_dir(), "git initialized")


def t_skill_dict(e, R):
    lib = e.work / "skills-library"
    lib.mkdir()
    rc, last, secs = e.codex("skill-dict", f"$skill-dict sync\nThe library lives at {lib}. It is empty; "
                             "create what the skill needs, then sync the installed Codex skills and "
                             "plugins into it. Record unknown values as unknown.", e.work,
                             extra_env={"SKILL_LIBRARY_DIR": str(lib)})
    check(R, "skill-dict", rc == 0, f"codex exited 0 ({secs}s)")
    index = list(lib.rglob("INDEX.md"))
    check(R, "skill-dict", index, "library INDEX.md created")
    text = index[0].read_text() if index else ""
    check(R, "skill-dict", re.search(r"grill-me", text) and re.search(r"putdown", text),
          "installed skills (grill-me, putdown) catalogued")
    rc2, last2, secs2 = e.codex("skill-dict-show", "$skill-dict show pickup", e.work,
                                extra_env={"SKILL_LIBRARY_DIR": str(lib)}, sandbox="read-only")
    check(R, "skill-dict", rc2 == 0 and re.search(r"pickup", last2, re.I), f"show pickup prints its entry ({secs2}s)")


SCEN = {"grill-me": t_grill_me, "takenotes": t_takenotes, "putdown": t_putdown,
        "pickup": t_pickup, "newproject": t_newproject, "skill-dict": t_skill_dict}


def main():
    argv = sys.argv[1:]
    key_file = None
    if "--api-key-from" in argv:  # e.g. --api-key-from path/to/.env (uses its OPENAI_API_KEY line)
        i = argv.index("--api-key-from")
        key_file = argv[i + 1]
        del argv[i:i + 2]
    args = [a for a in argv if not a.startswith("--")]
    keep = "--keep" in argv
    want = [s for s in ORDER if not args or s in args]
    if "pickup" in want and "putdown" not in want:
        want.insert(want.index("pickup"), "putdown")
    if not (REPO / "codex").is_dir():
        sys.exit("codex/ not built — run scripts/build-codex.py first")
    e = Env(keep, key_file)
    R = []
    print(f"test root: {e.root}", flush=True)
    try:
        for s in want:
            try:
                SCEN[s](e, R)
            except UsageLimit as ex:
                print(f"\nBLOCKED: {ex}")
                R.append((s, False, f"BLOCKED (usage limit), not a skill result"))
                break
            except Exception as ex:
                R.append((s, False, f"harness error: {ex}"))
            for n, ok, what in [r for r in R if r[0] == s]:
                print(f"  {'PASS' if ok else 'FAIL'}  {n:11} {what}", flush=True)
    finally:
        e.close()
    passed = sum(ok for _, ok, _ in R)
    print(f"\n{passed}/{len(R)} checks passed" + (f"; logs kept in {e.logs}" if keep else ""))
    (REPO / "tests" / "codex" / "last-run.json").write_text(json.dumps(
        [{"scenario": n, "pass": ok, "check": w} for n, ok, w in R], indent=1) + "\n")
    return 0 if passed == len(R) else 1


if __name__ == "__main__":
    sys.exit(main())
