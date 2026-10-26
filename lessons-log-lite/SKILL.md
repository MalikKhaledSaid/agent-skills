---
name: lessons-log-lite
description: Free check for a LESSONS.md file of standing rules. Finds rules with no evidence, repeated ids, review dates that passed, missing dates, rules that are too long, rules with the same title and a file that grew too big. Use when the user asks to check, review or clean up LESSONS.md, or wants to know whether the team's lessons are still current.
license: MIT. LICENSE has complete terms.
compatibility: Designed for Claude Code; works with any agent that reads files. Needs python3 (3.8+). No network access.
metadata:
  version: "1.0.1"
  edition: "free"
---

# Lessons log (lite)

You check a file of standing rules. The script gives the findings. You explain each one in plain words and change nothing until the user agrees.

## Step 1: Run the lint

```bash
python3 <skill-folder>/scripts/lessons_lint.py LESSONS.md
```

`--json` prints JSON. Exit code 1 means at least one ERROR.

## Step 2: Explain the findings

List ERRORs first, then WARNs. For each, say what is wrong, name the rule id, and use the Fixes list the script prints. `references/templates.md` shows the file format the lint reads.

## Step 3: Edit after approval

Propose each edit as a short before and after. Make the edits only after the user says yes. Never invent evidence for a rule. If the user has none, say the rule is an opinion.

## Limits
- Evidence and review dates are checked only in the rule format of `references/templates.md`. A file of plain bullets gets one warning and a size and length check.
- It checks structure and dates. It cannot tell whether a rule is wise or the evidence is real.
- This edition does not add, renew, archive or convert rules and has no before-and-after comparison. The full edition has them.
