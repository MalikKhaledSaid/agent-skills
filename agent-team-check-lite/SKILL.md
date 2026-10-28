---
name: agent-team-check-lite
description: Free health check for a team of AI agent sessions that share ORG.md, TEAM_PLAN.md and DECISIONS.md. Finds a role that has no queue, a broken reporting line, more than one voice to the human, tasks with no goal or receiver, template text left in the plan, a stale plan or decision log, and missing session ids. Use when the user runs several Claude Code sessions as a team and asks whether the team files are healthy. Search words: agent team setup, multi-agent team, agent org chart, team plan check, decision log, agent handoff, parallel Claude Code sessions.
license: MIT. LICENSE has complete terms.
compatibility: Designed for Claude Code with several sessions; works with any agent that reads files. Needs python3 (3.8+). No network access.
metadata:
  version: "1.0.1"
  edition: "free"
---

# Agent team check (lite)

You check the team files of a group of agent sessions. The script gives the findings. You explain each one in plain words. You change nothing until the user agrees.

## Step 1: Run the check

From the folder that holds ORG.md and TEAM_PLAN.md, with the path to this skill's folder:

```bash
python3 <skill-folder>/scripts/team_check.py --dir .
```

`--json` prints JSON. `--stale-days N` sets the age at which a plan counts as stale (default 7). Exit code 1 means at least one ERROR.

## Step 2: Explain the findings

List ERRORs first, then WARNs. For each, say what is wrong and name the file and line to edit. Use the Fixes list the script prints.

`references/templates.md` shows the file formats the check reads. Use it when a file is missing or in the wrong shape.

## Step 3: Edit after approval

Propose each edit as a short before and after. Make the edits only after the user says yes.

## Limits
- The check reads the files. It cannot tell whether the work in them is good.
- This edition has no set-up mode and no before-and-after comparison. The full edition has both.
