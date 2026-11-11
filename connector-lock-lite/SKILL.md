---
name: connector-lock-lite
description: Free audit of which connector and MCP servers a Claude Code setup can reach and which a deny rule covers. Reads your settings.json files and a text file of tool names and lists each server as COVERED or OPEN. Use when the user asks "which connectors can my agent reach", "is this MCP server blocked", or wants to check deny rules for MCP tools. Search words: MCP deny rule, connector audit, block MCP server, Claude Code permissions.
license: MIT
compatibility: Designed for Claude Code (minimum 2.1.7); works with any agent that reads files. Needs python3 (3.8+). Reads only the files you name.
metadata:
  version: "1.0.0"
---

# Connector lock (free audit)

You show the user which connector and MCP servers their setup can reach and which a deny rule covers.

## Step 1: Get the names

Ask the user for the tool names their session shows, one per line in a text file (`mcp__server__tool`), and the path of their settings.json (project and user).

## Step 2: Run the audit

```bash
python3 <skill>/scripts/connector_audit.py --settings .claude/settings.json --tools tools.txt
```

It lists each server, how many of its tools a deny rule covers, whether a PreToolUse hook matches, and COVERED or OPEN. Exit code 1 means a server is open; exit code 3 means input it cannot use.

## Step 3: Report

Name each OPEN server. Suggest adding `mcp__SERVER__*` to `permissions.deny`, and ask before you edit any file. Do not call any connector tool to test it.

## Limits

- It checks the files and names you give it. It does not read your live session.
- It reports coverage. It does not block anything.
- A deny rule with parentheses is skipped by Claude Code for `mcp__` tools, so the audit does not count it.

Full edition: connector-lock $9: a PreToolUse hook that blocks the servers you lock, a deny list for settings.json written from a locks file by account, one test per rule, a CLAUDE.md block and a before-and-after check. https://buy.polar.sh/polar_cl_qw3HAkiABUy617ASbmgPUT1tHn6e0iHKe2NTm0WgaR0?utm_source=github&utm_medium=skill&utm_campaign=connector-lock
