#!/usr/bin/env python3
"""List the connector and MCP servers a Claude Code setup can reach, and say which a deny rule covers.

  python3 connector_audit.py [--settings FILE ...] [--tools FILE] [--json]

--settings   a Claude Code settings.json (project or user); repeat for several. The permissions.deny rules that
             start with mcp__ and the PreToolUse hooks that match mcp__ tools are read from it.
--tools      a text file with one tool name per line, as shown in your session (for example mcp__shop__list_orders).
Reads only the files you name. Makes no network call and runs no command. Python 3.8+, standard library only.
Exit codes: 0 every server seen is covered, 1 at least one server is open, 3 input it cannot use.
"""
import argparse
import fnmatch
import json
import os
import sys


class InputError(Exception):
    """Input that cannot be used. The message is one line for the user."""


def server_of(tool):
    parts = tool.split("__")
    return parts[1] if len(parts) >= 3 and parts[0] == "mcp" else None


def rule_matches(rule, tool):
    """True when a permissions.deny rule such as mcp__shop, mcp__shop__*, mcp__shop__list_orders or mcp__* covers the tool."""
    rule = rule.strip()
    if not rule.startswith("mcp__") or "(" in rule or ")" in rule:
        return False
    if "__" not in rule[5:] and "*" not in rule:
        return server_of(tool) == rule[5:]
    return fnmatch.fnmatchcase(tool, rule)


def load_settings(paths):
    deny, hooks = [], []
    for path in paths:
        try:
            with open(path, encoding="utf-8") as fh:
                data = json.load(fh)
        except OSError:
            raise InputError(f"No file at {path}.")
        except ValueError:
            raise InputError(f"{path} is not valid JSON.")
        if not isinstance(data, dict):
            raise InputError(f"{path} must hold one JSON object.")
        for rule in (data.get("permissions") or {}).get("deny") or []:
            if isinstance(rule, str):
                deny.append(rule)
        for entry in (data.get("hooks") or {}).get("PreToolUse") or []:
            if isinstance(entry, dict) and "mcp__" in str(entry.get("matcher", "")):
                hooks.append(str(entry["matcher"]))
    return deny, hooks


def load_tools(path):
    try:
        with open(path, encoding="utf-8") as fh:
            names = [l.strip() for l in fh if l.strip() and not l.strip().startswith("#")]
    except OSError:
        raise InputError(f"No file at {path}.")
    return names


def audit(deny, hooks, tools):
    """One row per server seen in the tool list: the tools, whether a deny rule covers all of them, and the hook."""
    servers = {}
    for t in tools:
        s = server_of(t)
        if s is None:
            raise InputError(f"'{t}' is not a tool name like mcp__server__tool.")
        servers.setdefault(s, []).append(t)
    rows = []
    for s, names in sorted(servers.items()):
        covered = [n for n in names if any(rule_matches(r, n) for r in deny)]
        deny_state = "all" if len(covered) == len(names) else ("some" if covered else "none")
        hook = any(h in ("mcp__.*", "mcp__", ".*") or s in h for h in hooks)
        status = "COVERED" if deny_state == "all" else "OPEN"
        rows.append({"server": s, "tools": len(names), "deny": deny_state, "hook": "yes" if hook else "no", "status": status})
    return rows


def to_markdown(rows, deny, hooks):
    open_n = sum(r["status"] == "OPEN" for r in rows)
    lines = [f"# Connector audit: {len(rows)} servers, {open_n} open", "",
             f"- Deny rules for mcp__ tools: {len([r for r in deny if r.strip().startswith('mcp__')])}. PreToolUse hooks for mcp__ tools: {len(hooks)}.", ""]
    if rows:
        lines += ["| Server | Tools seen | Deny rule | Hook | Status |", "|---|---|---|---|---|"]
        lines += [f"| {r['server']} | {r['tools']} | {r['deny']} | {r['hook']} | {r['status']} |" for r in rows]
    else:
        lines.append("No tool list was given, so no server was checked. Pass --tools FILE.")
    if open_n:
        lines += ["", "OPEN means a deny rule does not cover every tool of that server. Add `mcp__SERVER__*` to permissions.deny, or list the server in a locks file."]
    return "\n".join(lines)


FOOTER = "\nFull edition, connector-lock $9: a PreToolUse hook that blocks the servers you lock, a deny list for settings.json written from a locks file by account, one test per rule, a CLAUDE.md block and a before-and-after check. https://buy.polar.sh/polar_cl_qw3HAkiABUy617ASbmgPUT1tHn6e0iHKe2NTm0WgaR0?utm_source=github&utm_medium=script&utm_campaign=connector-lock"


def main(argv=None):
    ap = argparse.ArgumentParser(description="Audit connector and MCP tool coverage in Claude Code settings.")
    ap.add_argument("--settings", action="append", default=[], metavar="FILE", help="a settings.json to read (repeatable)")
    ap.add_argument("--tools", metavar="FILE", help="a text file with one tool name per line")
    ap.add_argument("--json", action="store_true", help="print JSON")
    args = ap.parse_args(argv)
    try:
        deny, hooks = load_settings(args.settings)
        tools = load_tools(args.tools) if args.tools else []
        rows = audit(deny, hooks, tools)
    except InputError as exc:
        print(str(exc), file=sys.stderr)
        return 3
    result = {"servers": rows, "deny_rules": len([r for r in deny if r.strip().startswith("mcp__")]), "hooks": len(hooks)}
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(to_markdown(rows, deny, hooks))
    if not args.json:
        print(FOOTER)
    return 1 if any(r["status"] == "OPEN" for r in rows) else 0


if __name__ == "__main__":
    sys.exit(main())
