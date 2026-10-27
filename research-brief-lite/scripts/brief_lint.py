#!/usr/bin/env python3
"""Check a Markdown research brief: one question, a search budget, a stop rule, and a label on every finding.

A brief has these sections (level-2 headings, any case):
  ## Question     one question
  ## Budget       the number of searches, for example "Searches: 8" (page reads optional: "Reads: 12")
  ## Stop rule    when to stop searching
  ## Search log   one list item per search; an item that starts with "read" is a page read
  ## Findings     one list item per claim, each with a label:
                  [V] verified (with a source), [I] inferred, [U] unverified, [X] not found
  ## Sources      the links the findings rest on

Read-only. Python 3.8+, standard library only.

Exit codes: 0 no errors, 1 errors found, 3 usage error.
"""
import argparse
import json
import os
import re
import sys


ERROR, WARN, INFO = "ERROR", "WARN", "INFO"
SECTIONS = {
    "question": "question", "research question": "question",
    "budget": "budget", "search budget": "budget",
    "stop rule": "stop", "stop": "stop", "stopping rule": "stop",
    "search log": "log", "log": "log",
    "findings": "findings", "claims": "findings",
    "sources": "sources",
}
HEADING = re.compile(r"^##\s+(.+?)\s*#*\s*$")
ITEM = re.compile(r"^(?:[-*+]|\d+[.)])\s+(.*)$")
LABEL = re.compile(r"\[(V|I|U|X)(?:\s*[,:;]\s*([^\]]*))?\]", re.I)
MONTHS = r"(?:jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)[a-z]*"
DATE = re.compile(rf"\b\d{{4}}-\d{{2}}-\d{{2}}\b|\b\d{{1,2}}\s+{MONTHS}\b(?:\s+\d{{4}})?|\b{MONTHS}\s+\d{{1,2}}\b|\btoday\b", re.I)
CLOCK = re.compile(r"\b\d{1,2}:\d{2}(?::\d{2})?\s*(?:UTC|GMT|am|pm)?\b", re.I)
URL = re.compile(r"https?://[^\s)\]>]+")
LINK = re.compile(r"\[[^\]]*\]\([^)]*\)")
FILE_REF = re.compile(r"\b[\w./-]+\.(?:md|py|json|csv|txt|ts|js|yml|yaml|html|pdf)\b", re.I)
SEARCHES = re.compile(r"(?i)\bsearch(?:es)?\s*[:=]?\s*(\d+)\b|\b(\d+)\s+(?:web\s+)?search(?:es)?\b")
READS = re.compile(r"(?i)\b(?:page\s+)?reads?\s*[:=]?\s*(\d+)\b|\b(\d+)\s+(?:page\s+)?reads?\b")


def parse(text):
    """Split the brief into sections. Returns {key: {"line": n, "lines": [(n, text)], "items": [(n, text)]}}."""
    secs, cur, in_fence = {}, None, False
    for n, raw in enumerate(text.splitlines(), 1):
        line = raw.rstrip()
        if line.strip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        h = HEADING.match(line)
        if h:
            key = SECTIONS.get(re.sub(r"[^a-z ]", "", h.group(1).lower()).strip())
            cur = None
            if key and key not in secs:
                cur = secs[key] = {"line": n, "lines": [], "items": []}
            continue
        if line.startswith("# "):
            cur = None
            continue
        if cur is None or not line.strip():
            continue
        cur["lines"].append((n, line.strip()))
        m = ITEM.match(line.strip())
        if m and not line[:1].isspace():
            cur["items"].append([n, m.group(1)])
        elif cur["items"] and line[:1].isspace():
            cur["items"][-1][1] += " " + line.strip()
    return secs


def body(sec):
    return " ".join(t for _, t in sec["lines"]) if sec else ""


def first_number(pattern, text):
    m = pattern.search(text)
    return int(m.group(1) or m.group(2)) if m else None


def has_source(item, labels):
    texts = [DATE.sub(" ", CLOCK.sub(" ", t or "")) for k, t in labels if k.upper() == "V"]
    if item.lstrip().startswith("|"):  # a table row: a later cell may hold the source
        cells = item.strip().strip("|").split("|")
        at = next((i for i, c in enumerate(cells) if LABEL.search(c)), len(cells))
        if any(re.search(r"[^\W\d_]", c) for c in cells[at + 1:]):
            return True
    return (any(re.search(r"[^\W\d_]", t) for t in texts) or bool(URL.search(item)) or bool(LINK.search(item))
            or bool(FILE_REF.search(item)) or bool(re.search(r"(?i)\bsource\s*:", item)))


def labelled_lines(text):
    """Every line outside code fences that carries a label: list items, table rows and prose. Used for notes."""
    out, in_fence = [], False
    for n, raw in enumerate(text.splitlines(), 1):
        line = raw.strip()
        if line.startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence or line.startswith("#") or not LABEL.search(line):
            continue
        if len({k.upper() for k, _ in LABEL.findall(line)}) >= 3:  # a legend that explains the labels
            continue
        m = ITEM.match(line)
        out.append([n, m.group(1) if m else line])
    return out


def check(text):
    out = []

    def add(level, name, detail, fix=""):
        out.append({"level": level, "check": name, "detail": detail, "fix": fix})

    secs = parse(text)
    notes = not any(k in secs for k in ("question", "budget", "stop", "findings"))
    question = secs.get("question")
    if notes:
        found = labelled_lines(text)
        if found:
            add(WARN, "Not a brief", f"No Question, Budget, Stop rule or Findings section. Read as research notes: {len(found)} labelled lines checked.",
                "To check the budget and every claim, start a brief with these sections (references/format.md).")
        else:
            add(WARN, "No labels", "No brief sections and no line with [V], [I], [U] or [X].",
                "Label each claim, or start a brief with '## Question', '## Budget', '## Stop rule' and '## Findings'.")
    elif not body(question):
        add(ERROR, "No question", "No '## Question' section, or it is empty.",
            "Write the one question the research must answer under '## Question'.")
    elif body(question).count("?") > 1:
        add(WARN, "More than one question", f"line {question['line']}: the question section asks {body(question).count('?')} questions.",
            "Keep one question per brief. Move the others to a new brief or to open questions.")
    budget = secs.get("budget")
    max_searches = first_number(SEARCHES, body(budget))
    if max_searches is None and not notes:
        add(ERROR, "No budget", "No '## Budget' section with a number of searches, like 'Searches: 8'.",
            "Set a search budget before you search, for example 'Searches: 8. Reads: 12.'")
    stop = secs.get("stop")
    if not body(stop) and not notes:
        add(ERROR, "No stop rule", "No '## Stop rule' section, or it is empty.",
            "Say when to stop, for example 'Stop when 3 independent sources agree, or when the budget is spent.'")
    findings = secs.get("findings")
    items = findings["items"] if findings else []
    if notes:
        items = labelled_lines(text)
    elif not items:
        add(ERROR, "No findings", "No '## Findings' section with list items.",
            "List each claim as one item under '## Findings', with a label.")
    counts = {"V": 0, "I": 0, "U": 0, "X": 0}
    for n, item in items:
        labels = LABEL.findall(item)
        short = item if len(item) <= 60 else item[:57] + "..."
        if not labels:
            add(ERROR, "No label", f"line {n}: {short}",
                "Say how you know the claim: [V] verified with a source, [I] inferred, [U] unverified, [X] not found.")
            continue
        kinds = {k.upper() for k, _ in labels}
        for k in kinds:
            counts[k] += 1
        if "V" in kinds and not has_source(item, labels):
            add(WARN, "No source", f"line {n}: {short}",
                "Add the link, file or source name to the [V] claim, or relabel it [U].")
    if items:
        add(INFO, "Findings", f"{len(items)} findings: {counts['V']} [V], {counts['I']} [I], {counts['U']} [U], {counts['X']} [X].")
    return out


def to_markdown(results):
    errors = sum(r["level"] == ERROR for r in results)
    warns = sum(r["level"] == WARN for r in results)
    lines = [f"# Research brief check: {errors} errors, {warns} warnings", "", "| Level | Check | Detail |", "|---|---|---|"]
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


FOOTER = "\nFull edition, research-brief $9: start a brief, log each search against the budget and stop when it is spent, checks for dates, listed sources and over-budget logs, a fix guide for each finding, a CLAUDE.md block, a worked example and a before-and-after check. https://buy.polar.sh/polar_cl_c3IMazGk7ocx6JpKwmUcGP8WPms58i1pAnAbz2QTI43"


def main(argv=None):
    ap = argparse.ArgumentParser(description="Check a research brief: question, budget, stop rule and a label on every finding.")
    ap.add_argument("file", help="the Markdown brief")
    ap.add_argument("--json", action="store_true", help="print JSON")
    args = ap.parse_args(argv)
    if not os.path.isfile(args.file):
        print(f"No file at {args.file}.", file=sys.stderr)
        return 3
    with open(args.file, encoding="utf-8") as fh:
        text = fh.read()
    results = check(text)
    print(json.dumps(results, indent=2) if args.json else to_markdown(results))
    if not args.json:
        print(FOOTER)
    return 1 if any(r["level"] == ERROR for r in results) else 0


if __name__ == "__main__":
    sys.exit(main())
