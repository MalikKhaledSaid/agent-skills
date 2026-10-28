#!/usr/bin/env python3
"""Check the team files of a group of agent sessions.

Reads ORG.md, TEAM_PLAN.md, DECISIONS.md and handovers/ in one folder and
reports problems: idle roles, broken reporting lines, more than one voice to
the human, tasks with no goal or user, a stale plan or decision log, and old
hand-overs. Read-only. Python 3.8+, standard library only.

Exit codes: 0 no errors, 1 errors found, 3 usage error.
"""
import argparse
import json
import os
import re
import sys
from datetime import date


ERROR, WARN, INFO = "ERROR", "WARN", "INFO"

PLACEHOLDER_TASK = re.compile(r"<[^<>]+>|^\d+\.\s*first task for\b", re.I)
NO_OWNER = re.compile(r"(?i)output to:\s*(nobody|no one|none|n/?a|tbd|-)?\s*[;)]|output to:\s*(nobody|no one|none|n/?a|tbd|-)\s*$")
HUMAN_WORDS = {"human", "owner", "founder", "-", ""}
DATE = re.compile(r"(\d{4}-\d{2}-\d{2})")


def read(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return fh.read()
    except OSError:
        return None


def parse_org(text):
    """Return role rows from the first Markdown table whose header has Name and Reports to."""
    lines = text.splitlines()
    for i, line in enumerate(lines):
        cells = [c.strip().lower() for c in line.strip().strip("|").split("|")]
        if "name" in cells and "reports to" in cells:
            rows = []
            for row in lines[i + 2:]:
                if not row.strip().startswith("|"):
                    break
                vals = [c.strip() for c in row.strip().strip("|").split("|")]
                rows.append(dict(zip(cells, vals + [""] * (len(cells) - len(vals)))))
            return rows
    return []


def parse_plan(text):
    sections, current = {}, None
    for line in text.splitlines():
        m = re.match(r"^##\s+(.+?)\s*(\(.*\))?\s*$", line)
        if m:
            current = m.group(1).strip()
            sections[current] = []
        elif current and re.match(r"^\s*\d+\.\s+\S", line):
            sections[current].append(line.strip())
    return sections


def find_section(sections, role):
    """A plan heading belongs to a role if it names the role, or is the start of its title."""
    name = role["name"].lower()
    title = role.get("role", "").lower()
    for heading in sections:
        words = re.findall(r"[a-z0-9]+", heading)
        if name in words or heading == title:
            return heading
        head = heading.split("(")[0].strip()
        if head and (title.startswith(head + " ") or title == head or title.split(" and ")[0].strip() == head):
            return heading
    return None


def days_old(text_date, today):
    try:
        return (today - date.fromisoformat(text_date)).days
    except ValueError:
        return None


def check(folder, today=None, stale_days=7, human=""):
    today = today or date.today()
    out = []

    def add(level, check_name, detail, fix=""):
        out.append({"level": level, "check": check_name, "detail": detail, "fix": fix})

    org = read(os.path.join(folder, "ORG.md"))
    if org is None:
        add(ERROR, "ORG.md", "Missing.", "Run scripts/team_init.py or write ORG.md from references/templates.md.")
        return out
    roles = parse_org(org)
    if not roles:
        add(ERROR, "Roles table", "No table with Name and Reports to columns in ORG.md.",
            "Use the roles table format in references/templates.md.")
        return out
    names = {r["name"].lower(): r for r in roles if r.get("name")}

    def resolve(boss):
        """Map a 'Reports to' value to a role name: by name, or by the start of a role title."""
        b = boss.strip().lower()
        if b in names:
            return b
        hits = [n for n, r in names.items() if r.get("role", "").lower().split(" and ")[0].strip() == b
                or r.get("role", "").lower().startswith(b + " ")]
        return hits[0] if len(hits) == 1 else None

    external = {}
    for r in roles:
        boss = r.get("reports to", "").strip()
        if resolve(boss) is None:
            external.setdefault(boss, []).append(r["name"])
    humans = {b for b in external if b.lower() in HUMAN_WORDS or b.lower() == human.lower()}
    if not humans and external:
        humans = {max(external, key=lambda b: len(external[b]))}
    for boss, who in external.items():
        if boss not in humans:
            add(ERROR, "Reporting line", f"{', '.join(who)} report(s) to unknown '{boss}'.", "Fix the name in ORG.md.")

    if any("talks to human" in r for r in roles):
        voices = [r["name"] for r in roles if r.get("talks to human", "").lower().startswith("y")]
    else:
        voices = [r["name"] for r in roles if r.get("reports to", "").strip() in humans]
    if len(voices) != 1:
        add(ERROR, "One voice to the human",
            f"{len(voices)} roles talk to the human: {', '.join(voices) or 'none'}.",
            "Make exactly one role (the lead) talk to the human; everyone else reports inside the team.")
    else:
        add(INFO, "One voice to the human", f"{voices[0]}.")

    for r in roles:
        session = r.get("session", r.get("session id", None))
        if session is not None and (not session or session.startswith("(")):
            add(WARN, "Session id", f"{r['name']} has no session id.", "Fill it in, so teammates can message the role.")
    for r in roles:
        seen, cur = set(), r["name"].lower()
        while cur and cur not in seen:
            seen.add(cur)
            cur = resolve(names[cur].get("reports to", ""))
        if cur in seen:
            add(ERROR, "Reporting cycle", f"Reporting line from {r['name']} loops back.", "Make every line end at the human.")
            break

    if not re.search(r"(?im)^##\s+approvals", org):
        add(WARN, "Approvals list", "ORG.md has no Approvals section.",
            "List what only the human approves: money, accounts, anything public.")

    plan = read(os.path.join(folder, "TEAM_PLAN.md"))
    if plan is None:
        add(ERROR, "TEAM_PLAN.md", "Missing.", "Write one section per role with numbered open items.")
    else:
        sections = {k.lower(): v for k, v in parse_plan(plan).items()}
        for r in roles:
            key = find_section(sections, r)
            if key is None:
                add(WARN, "Idle role", f"{r['name']} has no section in TEAM_PLAN.md.", "Add a queue for the role.")
                continue
            items = [i for i in sections[key] if "[done]" not in i.lower()]
            if not items:
                add(WARN, "Idle role", f"{r['name']} has no open items.", "Give the role its next highest-value task.")
            template = [i for i in items if PLACEHOLDER_TASK.search(i) or NO_OWNER.search(i)]
            if template:
                add(WARN, "Placeholder task", f"{r['name']}: {len(template)} of {len(items)} open items are template text or name nobody to receive the output.",
                    "Replace each with a real task and name who receives the output.")
            vague = [i for i in items if not (re.search(r"(?i)goal:", i) and re.search(r"(?i)(output to|for):", i))]
            if vague:
                add(WARN, "Task purpose", f"{r['name']}: {len(vague)} of {len(items)} open items name no goal or user.",
                    "Add '(goal: ...; output to: ...)' to each item.")
        m = re.search(r"(?im)^updated:\s*" + DATE.pattern, plan)
        age = days_old(m.group(1), today) if m else None
        if age is None:
            add(WARN, "Plan date", "TEAM_PLAN.md has no 'Updated: YYYY-MM-DD' line.", "Add one and keep it current.")
        elif age > stale_days:
            add(WARN, "Plan date", f"TEAM_PLAN.md last updated {age} days ago.", "Review the plan and queue order.")
        else:
            add(INFO, "Plan date", f"Updated {age} days ago.")

    decisions = read(os.path.join(folder, "DECISIONS.md"))
    if decisions is None:
        add(WARN, "Decision log", "DECISIONS.md is missing.", "Log each decision with date, owner, evidence, before and after.")
    else:
        dates = [d for d in DATE.findall(decisions) if days_old(d, today) is not None and days_old(d, today) >= 0]
        if dates:
            age = min(days_old(d, today) for d in dates)
            level = WARN if age > stale_days else INFO
            add(level, "Decision log", f"Latest entry {age} days ago, {len(set(dates))} dated entries.")
        else:
            add(WARN, "Decision log", "No dated entries.", "Start each entry with '## YYYY-MM-DD: decision'.")

    hdir = os.path.join(folder, "handovers")
    if os.path.isdir(hdir):
        notes = [f for f in os.listdir(hdir) if f.endswith(".md")]
        old = []
        for f in notes:
            m = DATE.search(f)
            if m and (days_old(m.group(1), today) or 0) > stale_days * 2:
                old.append(f)
        add(INFO, "Hand-overs", f"{len(notes)} notes; {len(old)} older than {stale_days * 2} days (twice --stale-days).",
            "Move used hand-overs to an archive folder." if old else "")
    return out


def to_markdown(results):
    errors = sum(r["level"] == ERROR for r in results)
    warns = sum(r["level"] == WARN for r in results)
    lines = [f"# Team check: {errors} errors, {warns} warnings", "", "| Level | Check | Detail |", "|---|---|---|"]
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


FOOTER = "\nFull edition, agent-team-ops $12: one-command set-up, a fix guide for each finding, a CLAUDE.md block, a worked example team and a before-and-after check. https://buy.polar.sh/polar_cl_0RUUUFGvqGayeWXaK1PxhAuQSrHMRDJHEkuoZ0xJOV3"


def main(argv=None):
    ap = argparse.ArgumentParser(description="Check team files for a group of agent sessions.")
    ap.add_argument("--dir", default=".", help="folder that holds ORG.md and TEAM_PLAN.md")
    ap.add_argument("--stale-days", type=int, default=7, help="days before the plan or log counts as stale")
    ap.add_argument("--human", default="", help="name of the human at the top, if not in ORG.md")
    ap.add_argument("--json", action="store_true", help="print JSON")
    args = ap.parse_args(argv)
    if not os.path.isdir(args.dir):
        print(f"No folder at {args.dir}.", file=sys.stderr)
        return 3
    results = check(args.dir, stale_days=args.stale_days, human=args.human)
    print(json.dumps(results, indent=2) if args.json else to_markdown(results))
    if not args.json:
        print(FOOTER)
    return 1 if any(r["level"] == ERROR for r in results) else 0


if __name__ == "__main__":
    sys.exit(main())
