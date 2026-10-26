#!/usr/bin/env python3
"""Check that every number in a Markdown report has a label, a source and a time.

A number is a claim. Each claim line needs:
  - a label: [V] verified, [I] inferred, [U] unverified, [X] not found or not checkable
  - for [V]: a source (a link, URL, file name or a word after the label, like [V, Polar API])
  - for [V]: a time (a date, or a clock time) on the line, or in an 'as of' line above it in the file

Skips list numbers, dates, clock times, versions, years, URLs, file names and code spans. Plain single digits
are skipped unless --include-small is given. Read-only. Python 3.8+, standard library only.

Exit codes: 0 no errors, 1 errors found, 3 usage error.
"""
import argparse
import json
import os
import re
import sys


ERROR, WARN, INFO = "ERROR", "WARN", "INFO"
LABEL = re.compile(r"\[(V|I|U|X)(?:\s*[,:;]\s*([^\]]*))?\]")
MONTHS = r"(?:jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)[a-z]*"
DATE = re.compile(rf"\b\d{{4}}-\d{{2}}-\d{{2}}\b|\b\d{{1,2}}\s+{MONTHS}\b(?:\s+\d{{4}})?|\b{MONTHS}\s+\d{{1,2}}\b|\btoday\b", re.I)
CLOCK = re.compile(r"\b\d{1,2}:\d{2}(?::\d{2})?\s*(?:UTC|GMT|am|pm)?\b", re.I)
AS_OF = re.compile(r"(?i)\b(as of|read on|read at|numbers at|checked|measured|fetched|live read|snapshot)\b")
URL = re.compile(r"https?://\S+")
LINK = re.compile(r"\[[^\]]*\]\([^)]*\)")
CODE = re.compile(r"`[^`]*`")
FILE_REF = re.compile(r"\b[\w./-]+\.(?:md|py|json|csv|txt|ts|js|yml|yaml|html|pdf)\b", re.I)
IGNORE_PATTERNS = [
    re.compile(r"\bv?\d+\.\d+\.\d+\b"),                      # versions
    re.compile(r"\bv\d+(?:\.\d+)?\b", re.I),                  # v2, v1.1
    re.compile(r"\b(?:19|20)\d{2}\b"),                        # years
    re.compile(r"\b[0-9a-f]{7,40}\b"),                        # commit hashes and ids
    re.compile(r"\b(?:L|T|P|S|R|Q)\d+\b"),                    # rule, task and row ids such as L12, T3
    re.compile(r"\b(?:run|issue|pr|#)\s*#?\d{6,}\b", re.I),   # run and issue ids
]
NUMBER = re.compile(r"(?<![\w.])[$€£]?\d[\d,]*(?:\.\d+)?(?:[eE][+-]?\d+)?%?(?![\w])")
LIST_NUM = re.compile(r"^\s*(?:[-*]\s+)?\d+[.)]\s")
HEADING_NUM = re.compile(r"^#+\s*\d+[.)]?\s")


def strip_noise(line):
    for pat in (CODE, LINK, URL, FILE_REF, DATE, CLOCK, LABEL):
        line = pat.sub(" ", line)
    for pat in IGNORE_PATTERNS:
        line = pat.sub(" ", line)
    return line


def claims_in(line, include_small=False):
    if LIST_NUM.match(line) or HEADING_NUM.match(line):
        line = re.sub(r"^(\s*(?:[-*]\s+)?\d+[.)]\s|#+\s*\d+[.)]?\s)", "", line)
    found = []
    for m in NUMBER.finditer(strip_noise(line)):
        tok = m.group(0)
        plain = re.fullmatch(r"\d", tok)
        if plain and not include_small:
            continue
        found.append(tok)
    return found


def check(text, include_small=False):
    out = []

    def add(level, name, detail, fix="", claim=""):
        out.append({"level": level, "check": name, "detail": detail, "fix": fix, "claim": claim})

    as_of = False
    in_fence = False
    counted = 0
    for n, raw in enumerate(text.splitlines(), 1):
        line = raw.rstrip()
        if line.strip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence or not line.strip() or re.match(r"^\s*\|?\s*:?-{3,}", line):
            continue
        if AS_OF.search(line) and (DATE.search(line) or CLOCK.search(line)):
            as_of = True
        nums = claims_in(line, include_small)
        if not nums:
            continue
        counted += len(nums)
        labels = LABEL.findall(line)
        where = f"line {n}: {nums[0]}" + (f" (+{len(nums) - 1} more)" if len(nums) > 1 else "")
        if not labels:
            add(ERROR, "No label", f"{where}. Add [V], [I], [U] or [X].",
                "Say how you know the number: [V] verified with a source, [I] inferred, [U] unverified, [X] not found.", line.strip())
            continue
        kinds = {k for k, _ in labels}
        if "V" in kinds:
            texts = [DATE.sub(" ", CLOCK.sub(" ", t or "")) for k, t in labels if k == "V"]
            has_source = (any(re.search(r"[A-Za-z]", t) for t in texts) or bool(URL.search(line)) or bool(LINK.search(line))
                          or bool(FILE_REF.search(line)) or bool(re.search(r"(?i)\bsource\s*:", line)))
            has_time = bool(DATE.search(line)) or bool(CLOCK.search(line)) or as_of
            if not has_source:
                add(WARN, "No source", f"{where}. A [V] number needs a source.",
                    "Add a link, a file name, or a word after the label, like [V, Polar API].", line.strip())
            if not has_time:
                add(WARN, "No time", f"{where}. A [V] number needs the time it was read.",
                    "Add the date or time, or an 'as of <date and time>' line above it.", line.strip())
    if not out:
        add(INFO, "Numbers", f"{counted} numbers, all labelled" + ("." if counted else ". No number found."))
    return out


def to_markdown(results):
    errors = sum(r["level"] == ERROR for r in results)
    warns = sum(r["level"] == WARN for r in results)
    lines = [f"# Numbers check: {errors} errors, {warns} warnings", "", "| Level | Check | Detail |", "|---|---|---|"]
    order = {ERROR: 0, WARN: 1, INFO: 2}
    for r in sorted(results, key=lambda r: order[r["level"]]):
        lines.append(f"| {r['level']} | {r['check']} | {r['detail'].replace('|', '/')} |")
    fixes = []
    seen = set()
    for r in results:
        if r["fix"] and r["level"] != INFO and r["check"] not in seen:
            seen.add(r["check"])
            fixes.append(f"{r['check']}: {r['fix']}")
    if fixes:
        lines += ["", "## Fixes", ""] + [f"{i}. {t}" for i, t in enumerate(fixes, 1)]
    return "\n".join(lines)


FOOTER = "\nFull edition, numbers-check $9: re-fetch changing numbers with a command you give and compare them, a fix guide for each finding, a CLAUDE.md block, a worked example and a before-and-after check. https://buy.polar.sh/polar_cl_Ls5Jzr8nGz1CyxFFYtIKXRYPlFC9ZGks6mqeL1s1ujI"


def main(argv=None):
    ap = argparse.ArgumentParser(description="Check that every number in a report has a label, a source and a time.")
    ap.add_argument("file", help="the Markdown report")
    ap.add_argument("--include-small", action="store_true", help="also check plain single digits")
    ap.add_argument("--json", action="store_true", help="print JSON")
    args = ap.parse_args(argv)
    if not os.path.isfile(args.file):
        print(f"No file at {args.file}.", file=sys.stderr)
        return 3
    with open(args.file, encoding="utf-8") as fh:
        text = fh.read()
    results = check(text, args.include_small)
    print(json.dumps(results, indent=2) if args.json else to_markdown(results))
    if not args.json:
        print(FOOTER)
    return 1 if any(r["level"] == ERROR for r in results) else 0


if __name__ == "__main__":
    sys.exit(main())
