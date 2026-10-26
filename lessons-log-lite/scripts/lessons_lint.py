#!/usr/bin/env python3
"""Lint a LESSONS.md file of standing rules.

Each rule is a level-2 heading with an id and one line, then short fields:

    ## L12: Run the release gate before every tag
    - Evidence: commit a1b2c3d, incident 2026-10-02
    - Date: 2026-10-02
    - Review by: 2027-01-02
    - Owner: Dana

Checks: rule without evidence, missing or invalid dates, review date passed, rule line too long,
rule body too long, duplicate ids or titles, file over the size cap. A file of plain bullets gets one
warning and a size and length check. Read-only.
Python 3.8+, standard library only.

Exit codes: 0 no errors, 1 errors found, 3 usage error.
"""
import argparse
import json
import os
import re
import sys
from datetime import date, datetime


ERROR, WARN, INFO = "ERROR", "WARN", "INFO"
HEADING = re.compile(r"^##\s+(L?\d+)\s*[:.\-]\s*(.+?)\s*$", re.I)
FIELD = re.compile(r"^\s*[-*]\s*(Evidence|Date|Review by|Owner)\s*:\s*(.*?)\s*$", re.I)
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
VAGUE = {"", "n/a", "na", "none", "tbd", "todo", "see above", "unknown", "-", "?"}
MAX_TITLE = 160
MAX_BODY_LINES = 12
DEFAULT_MAX_LINES = 150
DEFAULT_MAX_BYTES = 15000
DEFAULT_MAX_RULES = 40


def parse(text):
    """Return a list of rules: {id, title, line, fields, body_lines}."""
    rules, cur = [], None
    for n, line in enumerate(text.splitlines(), 1):
        m = HEADING.match(line)
        if m:
            cur = {"id": m.group(1).upper() if m.group(1)[0] in "lL" else "L" + m.group(1),
                   "title": m.group(2), "line": n, "fields": {}, "body_lines": 0}
            rules.append(cur)
            continue
        if line.startswith("#"):
            cur = None
            continue
        if cur is None:
            continue
        f = FIELD.match(line)
        if f:
            cur["fields"][f.group(1).lower()] = f.group(2)
        if line.strip():
            cur["body_lines"] += 1
    return rules


BULLET = re.compile(r"^(?:[-*]|\d+[.)])\s+(\S.*)$")


def bullets(text):
    """Plain bullet lines at the start of a line, for files that do not use the '## L1:' format.
    Returns [{line, text, area, notes}]. Indented lines under a bullet are its notes."""
    out, area, cur = [], "", None
    for n, line in enumerate(text.splitlines(), 1):
        if line.startswith("#"):
            area, cur = line.lstrip("#").strip(), None
            continue
        m = BULLET.match(line)
        if m:
            cur = {"line": n, "text": m.group(1).strip(), "area": area, "notes": []}
            out.append(cur)
        elif cur is not None and line.strip() and line[0] in " \t":
            cur["notes"].append(line.strip())
        elif not line.strip():
            continue
        else:
            cur = None
    return out


def to_date(value):
    if not DATE.match(value or ""):
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None


def lint(text, today=None, max_lines=DEFAULT_MAX_LINES, max_bytes=DEFAULT_MAX_BYTES, max_rules=DEFAULT_MAX_RULES):
    today = today or date.today()
    out = []

    def add(level, check, detail, fix=""):
        out.append({"level": level, "check": check, "detail": detail, "fix": fix})

    rules = parse(text)
    lines = len(text.splitlines())
    size = len(text.encode("utf-8"))
    if not rules:
        found = bullets(text)
        if not found:
            add(ERROR, "Rules", "No rule found. A rule starts with a line like '## L1: one-line rule'.",
                "Use the format in the header of this script and in references/templates.md.")
            return out
        add(WARN, "Bullet-style file", f"{len(found)} bullet lines, no '## L1:' rules. The evidence and review checks need the L format.",
            "Rewrite each bullet as '## L1: rule' with Evidence, Date and Review by lines. See references/templates.md.")
        if lines > max_lines or size > max_bytes:
            add(WARN, "File size", f"{lines} lines and {size} bytes; the cap is {max_lines} lines and {max_bytes} bytes.",
                "Merge bullets with the same title and retire the ones nobody needs.")
        if len(found) > max_rules:
            add(WARN, "Rule count", f"{len(found)} bullets; the cap is {max_rules}.", "Retire the weakest first.")
        longest = [b for b in found if len(b["text"]) > MAX_TITLE]
        if longest:
            add(WARN, "Rule too long", f"{len(longest)} bullet line(s) are over {MAX_TITLE} characters (first on line {longest[0]['line']}).",
                "Cut each to one plain sentence. Move the story to its own file.")
        return out
    if lines > max_lines or size > max_bytes:
        add(WARN, "File size", f"{lines} lines and {size} bytes; the cap is {max_lines} lines and {max_bytes} bytes.",
            "Retire rules whose review date passed, and merge rules with the same title.")
    if len(rules) > max_rules:
        add(WARN, "Rule count", f"{len(rules)} rules; the cap is {max_rules}.", "Retire the weakest rules first.")
    seen_ids, seen_titles = {}, {}
    for r in rules:
        rid, f = r["id"], r["fields"]
        if rid in seen_ids:
            add(ERROR, "Duplicate id", f"{rid} appears on lines {seen_ids[rid]} and {r['line']}.", "Give each rule its own id.")
        seen_ids.setdefault(rid, r["line"])
        key = re.sub(r"\W+", " ", r["title"].lower()).strip()
        if key in seen_titles:
            add(WARN, "Duplicate rule", f"{rid} has the same title as {seen_titles[key]}.", "Merge the two rules.")
        seen_titles.setdefault(key, rid)
        if len(r["title"]) > MAX_TITLE:
            add(WARN, "Rule too long", f"{rid}: the rule line is {len(r['title'])} characters; the cap is {MAX_TITLE}.",
                "Cut the rule to one plain sentence. Move the story to the evidence.")
        if r["body_lines"] > MAX_BODY_LINES:
            add(WARN, "Rule body too long", f"{rid}: {r['body_lines']} lines under the heading; the cap is {MAX_BODY_LINES}.",
                "Keep the fields only. Move the incident write-up to a file and link it as the evidence.")
        if f.get("evidence", "").strip().lower() in VAGUE:
            add(ERROR, "No evidence", f"{rid}: the rule has no evidence.",
                "Name the file, commit, incident or URL that shows why the rule exists.")
        d = to_date(f.get("date"))
        if "date" not in f:
            add(WARN, "No date", f"{rid}: no Date field.", "Add '- Date: YYYY-MM-DD' (the day the rule was set).")
        elif d is None:
            add(WARN, "Bad date", f"{rid}: Date '{f['date']}' is not YYYY-MM-DD.", "Write the date as YYYY-MM-DD.")
        rv = to_date(f.get("review by"))
        if "review by" not in f:
            add(WARN, "No review date", f"{rid}: no 'Review by' field.", "Add '- Review by: YYYY-MM-DD'. Ninety days is a good default.")
        elif rv is None:
            add(WARN, "Bad review date", f"{rid}: Review by '{f['review by']}' is not YYYY-MM-DD.", "Write the date as YYYY-MM-DD.")
        else:
            if rv < today:
                add(WARN, "Review overdue", f"{rid}: review date {rv} passed {(today - rv).days} days ago.",
                    "Re-read the rule. Renew it with a new date, or retire it.")
            if d and rv < d:
                add(WARN, "Review before date", f"{rid}: Review by {rv} is before Date {d}.", "Fix one of the two dates.")
        if not f.get("owner", "").strip():
            add(INFO, "No owner", f"{rid}: no Owner field.", "")
    if not any(x["level"] in (ERROR, WARN) for x in out):
        add(INFO, "Rules", f"{len(rules)} rules, all with evidence and a review date in the future.")
    return out


def to_markdown(results):
    errors = sum(r["level"] == ERROR for r in results)
    warns = sum(r["level"] == WARN for r in results)
    lines = [f"# Lessons lint: {errors} errors, {warns} warnings", "", "| Level | Check | Detail |", "|---|---|---|"]
    order = {ERROR: 0, WARN: 1, INFO: 2}
    for r in sorted(results, key=lambda r: order[r["level"]]):
        lines.append(f"| {r['level']} | {r['check']} | {r['detail'].replace('|', '/')} |")
    fixes, seen = [], set()
    for r in results:
        if r["fix"] and r["level"] != INFO and r["check"] not in seen:
            seen.add(r["check"])
            fixes.append(f"{r['check']}: {r['fix']}")
    if fixes:
        lines += ["", "## Fixes", ""] + [f"{i}. {t}" for i, t in enumerate(fixes, 1)]
    return "\n".join(lines)


FOOTER = "\nFull edition, lessons-log $7: add a rule from an incident, renew and archive overdue rules, a fix guide for each finding, a CLAUDE.md block, a worked example and a before-and-after check. https://buy.polar.sh/polar_cl_Kh5u3AuxemqQUYOrHAhyxVtoHx8xcgWQvDvzU1SuEPo"


def main(argv=None):
    ap = argparse.ArgumentParser(description="Lint a LESSONS.md file of standing rules.")
    ap.add_argument("file", nargs="?", default="LESSONS.md", help="the lessons file (default: LESSONS.md)")
    ap.add_argument("--max-lines", type=int, default=DEFAULT_MAX_LINES, help="line cap for the file")
    ap.add_argument("--max-rules", type=int, default=DEFAULT_MAX_RULES, help="rule cap for the file")
    ap.add_argument("--json", action="store_true", help="print JSON")
    args = ap.parse_args(argv)
    if not os.path.isfile(args.file):
        print(f"No file at {args.file}.", file=sys.stderr)
        return 3
    with open(args.file, encoding="utf-8") as fh:
        text = fh.read()
    results = lint(text, max_lines=args.max_lines, max_rules=args.max_rules)
    print(json.dumps(results, indent=2) if args.json else to_markdown(results))
    if not args.json:
        print(FOOTER)
    return 1 if any(r["level"] == ERROR for r in results) else 0


if __name__ == "__main__":
    sys.exit(main())
