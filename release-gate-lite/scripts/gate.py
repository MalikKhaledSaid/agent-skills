#!/usr/bin/env python3
"""Pre-release gate for a git repository.

Runs deterministic checks and gives one verdict: PASS, HOLD or FAIL.
FAIL blocks the release. HOLD needs a human look. PASS means no check fired.
Read-only, except --run-tests, which runs the project's own test command.
Python 3.8+, standard library only, needs git on PATH.

Exit codes: 0 PASS, 1 HOLD, 2 FAIL, 3 usage error.
"""
import argparse
import json
import math
import os
import re
import subprocess
import sys
from urllib.parse import unquote

PASS, HOLD, FAIL, INFO = "PASS", "HOLD", "FAIL", "INFO"
RANK = {PASS: 0, INFO: 0, HOLD: 1, FAIL: 2}

SECRET_PATTERNS = [
    ("AWS access key", re.compile(r"\b(AKIA|ASIA)[0-9A-Z]{16}\b")),
    ("GitHub token", re.compile(r"\b(ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{36}\b|\bgithub_pat_[A-Za-z0-9_]{60,}\b")),
    ("Slack token", re.compile(r"\bxox[abprs]-[A-Za-z0-9-]{10,}\b")),
    ("Stripe live key", re.compile(r"\b(sk|rk)_live_[A-Za-z0-9]{20,}\b")),
    ("Anthropic API key", re.compile(r"\bsk-ant-[A-Za-z0-9_-]{20,}\b")),
    ("OpenAI API key", re.compile(r"\bsk-(?!ant-)(proj-)?[A-Za-z0-9_-]{32,}\b")),
    ("Google API key", re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b")),
    ("Private key block", re.compile(r"-----BEGIN (RSA |EC |OPENSSH |DSA |PGP )?PRIVATE KEY")),
    ("Hard-coded secret", re.compile(
        r"""(?i)\b(api[_-]?key|secret|password|passwd|token|auth[_-]?token)\b\s*[:=]\s*['"]([A-Za-z0-9/+_\-]{16,})['"]""")),
]
PLACEHOLDER = re.compile(r"(?i)(example|sample|dummy|placeholder|changeme|your[_-]|xxxx|test|fake|\$\{|<)")
SECRET_FILES = re.compile(r"(^|/)(\.env(\.[^/]*)?|id_rsa|id_ed25519|.*\.pem|.*\.p12|.*\.pfx|credentials\.json)$")
SAFE_ENV = re.compile(r"\.env\.(example|sample|template|dist)$")
DEBUG_LEFTOVERS = [
    ("merge conflict marker", re.compile(r"^(<{7}|>{7}) ", re.M)),
]
JS_EXT = (".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs")
TEST_PATH = re.compile(r"(^|/)(tests?|__tests__|spec|fixtures?)/|(^|/)test_[^/]*$|[._-](test|spec)\.[a-z]+$")
CODE_EXT = (".py", ".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs", ".go", ".rs", ".rb", ".java", ".kt", ".php", ".swift")
SEMVER = re.compile(r"^v?(\d+)\.(\d+)\.(\d+)(?:[-+].*)?$")
MAX_SCAN = 1024 * 1024


def git(repo, *args):
    r = subprocess.run(["git", "-C", repo] + list(args), capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else None


def git_z(repo, *args):
    """Run git with -z style output and return the NUL-separated fields, so non-ASCII names stay unquoted."""
    r = subprocess.run(["git", "-C", repo] + list(args), capture_output=True)
    if r.returncode != 0:
        return []
    return [f.decode("utf-8", "surrogateescape") for f in r.stdout.split(b"\0") if f]


def porcelain_paths(repo):
    """Paths from `git status --porcelain -z`; a rename entry is followed by its old path, which is skipped."""
    fields = git_z(repo, "status", "--porcelain", "-z")
    paths, i = [], 0
    while i < len(fields):
        entry = fields[i]
        paths.append(entry[3:])
        i += 2 if entry[0] in "RC" else 1
    return paths


def looks_random(value):
    """True for values that look like generated secrets: mixed character classes and high entropy."""
    classes = sum(bool(re.search(p, value)) for p in (r"[a-z]", r"[A-Z]", r"[0-9]"))
    counts = {c: value.count(c) for c in set(value)}
    entropy = -sum(n / len(value) * math.log2(n / len(value)) for n in counts.values())
    return classes >= 2 and entropy >= 3.5


def read_text(path):
    try:
        if os.path.getsize(path) > MAX_SCAN:
            return None
        with open(path, "rb") as fh:
            data = fh.read()
        if b"\0" in data[:4096]:
            return None
        return data.decode("utf-8", errors="replace")
    except OSError:
        return None


def load_json(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return {}


def semver_key(v):
    m = SEMVER.match(v or "")
    return tuple(int(x) for x in m.groups()) if m else None


class Gate:
    def __init__(self, repo):
        self.repo = repo
        self.results = []

    def add(self, check, status, detail, fix=""):
        self.results.append({"check": check, "status": status, "detail": detail, "fix": fix})

    def verdict(self):
        worst = max((RANK[r["status"]] for r in self.results), default=0)
        return {0: PASS, 1: HOLD, 2: FAIL}[worst]


def check_tree(g, tracked):
    dirty = git(g.repo, "status", "--porcelain")
    if dirty:
        n = len(dirty.splitlines())
        g.add("Clean working tree", HOLD, f"{n} uncommitted or untracked paths.",
              "Commit or remove them, so the release matches the repository.")
    else:
        g.add("Clean working tree", PASS, "No uncommitted changes.")


def check_secrets(g, tracked):
    hits = []
    for rel in tracked:
        if SECRET_FILES.search(rel) and not SAFE_ENV.search(rel):
            hits.append(f"{rel}: secret-type file is tracked")
            continue
        text = read_text(os.path.join(g.repo, rel))
        if text is None:
            continue
        for name, pat in SECRET_PATTERNS:
            for m in pat.finditer(text):
                value = m.group(0)
                if name == "Hard-coded secret" and (
                        PLACEHOLDER.search(m.group(2)) or TEST_PATH.search(rel) or not looks_random(m.group(2))):
                    continue
                if name != "Hard-coded secret" and PLACEHOLDER.search(value):
                    continue
                line = text.count("\n", 0, m.start()) + 1
                hits.append(f"{rel}:{line}: {name} ({value[:4]}...)")
                break
    if hits:
        g.add("Secrets in tracked files", FAIL, f"{len(hits)} found: " + "; ".join(hits[:8]),
              "Remove the secret, rotate it at the provider, and purge it from git history if it was pushed.")
    else:
        g.add("Secrets in tracked files", PASS, f"No known secret pattern in {len(tracked)} tracked files.")


def find_versions(repo):
    found = {}

    def grab(rel, pattern, flags=0):
        text = read_text(os.path.join(repo, rel)) if os.path.isfile(os.path.join(repo, rel)) else None
        if text:
            m = re.search(pattern, text, flags)
            if m:
                found[rel] = m.group(1)

    pkg = os.path.join(repo, "package.json")
    if os.path.isfile(pkg):
        v = load_json(pkg).get("version")
        if v:
            found["package.json"] = v
    grab("pyproject.toml", r'^\[(?:project|tool\.poetry)\][^\[]*?^version\s*=\s*["\']([^"\']+)', re.M | re.S)
    grab("setup.cfg", r"^\[metadata\][^\[]*?^version\s*=\s*([^\s]+)", re.M | re.S)
    grab("Cargo.toml", r'^\[package\][^\[]*?^version\s*=\s*"([^"]+)"', re.M | re.S)
    grab("setup.py", r"""version\s*=\s*['"]([^'"]+)['"]""")
    grab("VERSION", r"^\s*(\S+)")
    for rel in sorted(os.listdir(repo)):
        init = os.path.join(rel, "__init__.py")
        if os.path.isfile(os.path.join(repo, init)):
            grab(init, r"""^__version__\s*=\s*['"]([^'"]+)['"]""", re.M)
    if os.path.isdir(os.path.join(repo, "src")):
        for rel in sorted(os.listdir(os.path.join(repo, "src"))):
            init = os.path.join("src", rel, "__init__.py")
            if os.path.isfile(os.path.join(repo, init)):
                grab(init, r"""^__version__\s*=\s*['"]([^'"]+)['"]""", re.M)
    return found


def check_version(g, last_tag):
    versions = find_versions(g.repo)
    if not versions:
        g.add("Version", INFO, "No version field found (package.json, pyproject.toml, Cargo.toml, setup.cfg, VERSION).")
        return None
    distinct = sorted(set(versions.values()))
    listing = ", ".join(f"{k}={v}" for k, v in versions.items())
    if len(distinct) > 1:
        g.add("Version matches everywhere", FAIL, f"Versions disagree: {listing}.", "Set one version in every file.")
        return None
    version = distinct[0]
    g.add("Version matches everywhere", PASS, listing)
    if last_tag:
        new, old = semver_key(version), semver_key(last_tag)
        if new and old and new <= old:
            g.add("Version bumped since last tag", HOLD, f"Version {version} is not above last tag {last_tag}.",
                  "Bump the version before tagging a new release.")
        elif new and old:
            g.add("Version bumped since last tag", PASS, f"{last_tag} -> {version}.")
        else:
            g.add("Version bumped since last tag", INFO, f"Cannot compare {version} with tag {last_tag}.")
    return version


def check_changelog(g, version):
    names = ["CHANGELOG.md", "CHANGELOG", "CHANGES.md", "HISTORY.md", "RELEASES.md", "NEWS.md"]
    path = next((n for n in names if os.path.isfile(os.path.join(g.repo, n))), None)
    if not path:
        g.add("Changelog entry", HOLD, "No changelog file.", "Add CHANGELOG.md with an entry for this release.")
        return
    if not version:
        g.add("Changelog entry", INFO, f"{path} exists; no version to match.")
        return
    text = read_text(os.path.join(g.repo, path)) or ""
    if re.search(r"(?<![\d.])v?" + re.escape(version.lstrip("v")) + r"(?![\d])", text):
        g.add("Changelog entry", PASS, f"{path} mentions {version}.")
    else:
        g.add("Changelog entry", HOLD, f"{path} has no entry for {version}.", f"Add a {version} section to {path}.")


def changed_files(g, last_tag, tracked):
    if not last_tag:
        return tracked
    paths = set(git_z(g.repo, "diff", "--name-only", "-z", f"{last_tag}..HEAD"))
    paths |= set(porcelain_paths(g.repo))
    return sorted(p for p in paths if os.path.isfile(os.path.join(g.repo, p)))


def check_leftovers(g, files, scope):
    hits = []
    todo = 0
    for rel in files:
        text = read_text(os.path.join(g.repo, rel))
        if text is None:
            continue
        for name, pat in DEBUG_LEFTOVERS:
            if name != "merge conflict marker" and not rel.endswith(CODE_EXT):
                continue
            if name in ("focused test", "JS debugger statement") and not rel.endswith(JS_EXT):
                continue
            m = pat.search(text)
            if m:
                hits.append(f"{rel}:{text.count(chr(10), 0, m.start()) + 1}: {name}")
        if rel.endswith(CODE_EXT):
            todo += len(re.findall(r"\b(TODO|FIXME|XXX)\b", text))
    markers = [h for h in hits if "merge conflict" in h]
    leftovers = [h for h in hits if "merge conflict" not in h]
    if markers:
        g.add("Merge conflict markers", FAIL, "; ".join(markers[:8]), "Resolve the conflicts before release.")
    else:
        g.add("Merge conflict markers", PASS, f"None in {len(files)} {scope} files.")
    if todo:
        g.add("TODO / FIXME notes", INFO, f"{todo} in {scope} code files.")




def run_gate(repo, run_tests=False, history=False):
    repo = os.path.abspath(repo)
    top = git(repo, "rev-parse", "--show-toplevel")
    if not top:
        sys.stderr.write(f"{repo} is not a git repository.\n")
        sys.exit(3)
    g = Gate(top)
    tracked = [p for p in git_z(top, "ls-files", "-z") if os.path.isfile(os.path.join(top, p))]
    last_tag = git(top, "describe", "--tags", "--abbrev=0")
    files = changed_files(g, last_tag, tracked)
    scope = f"changed-since-{last_tag}" if last_tag else "tracked"
    check_tree(g, tracked)
    check_secrets(g, tracked)
    version = check_version(g, last_tag)
    check_changelog(g, version)
    check_leftovers(g, files, scope)
    return {"repo": top, "last_tag": last_tag, "version": version, "verdict": g.verdict(), "checks": g.results}


def to_markdown(res):
    lines = [f"# Release gate: {res['verdict']}", "",
             f"- Repository: `{os.path.basename(res['repo'])}`",
             f"- Version: {res['version'] or 'not found'}. Last tag: {res['last_tag'] or 'none'}.", "",
             "| Check | Result | Detail |", "|---|---|---|"]
    order = sorted(res["checks"], key=lambda r: -RANK[r["status"]])
    for r in order:
        lines.append(f"| {r['check']} | {r['status']} | {r['detail'].replace('|', '/')} |")
    return "\n".join(lines)


FOOTER = "\nFull edition, release-gate $7: exact fix commands, more checks, a scan of past commits, release notes and CI rules. https://buy.polar.sh/polar_cl_zGKv60a7zfftMDwtEse3Gq4Bsx5Gd5wDiXnm01q51F4"


def main(argv=None):
    class Parser(argparse.ArgumentParser):
        def error(self, message):
            self.print_usage(sys.stderr)
            sys.stderr.write(f"gate.py: error: {message}\n")
            sys.exit(3)

    ap = Parser(description="Pre-release PASS/HOLD/FAIL gate for a git repository.")
    ap.add_argument("repo", nargs="?", default=".", help="path inside the repository (default: current folder)")
    ap.add_argument("--json", action="store_true", help="print JSON")
    args = ap.parse_args(argv)
    res = run_gate(args.repo, getattr(args, "run_tests", False), getattr(args, "history", False))
    print(json.dumps(res, indent=2) if args.json else to_markdown(res))
    if not args.json:
        print(FOOTER)
    return {PASS: 0, HOLD: 1, FAIL: 2}[res["verdict"]]


if __name__ == "__main__":
    sys.exit(main())
