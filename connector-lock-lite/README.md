# connector-lock-lite

A free audit of which connector and MCP servers a Claude Code setup can reach, and which a deny rule covers.

## Use
Copy this folder into `~/.claude/skills/` (personal) or `.claude/skills/` in a project, then ask your agent: "Audit my MCP deny rules." Or run it by hand:

```bash
python3 scripts/connector_audit.py --settings .claude/settings.json --tools tools.txt
```

`tools.txt` holds one tool name per line, such as `mcp__shop__list_orders`. Exit codes: 0 every server is covered, 1 a server is open, 3 input it cannot use.

## What it checks
- Each server in the tool list: how many tools a deny rule covers, whether a PreToolUse hook matches, COVERED or OPEN.

## Requirements
Python 3.8 or later. Standard library only. No network.

## Status
The full edition adds a hook that blocks locked servers, a deny list written from a locks file by account, tests and a before-and-after check. https://buy.polar.sh/polar_cl_qw3HAkiABUy617ASbmgPUT1tHn6e0iHKe2NTm0WgaR0?utm_source=github&utm_medium=readme&utm_campaign=connector-lock

## License
MIT. See LICENSE.
