---
name: numbers-check-lite
description: Free check that every number in a Markdown report has a label (verified, inferred, unverified or not found), a source and a time. Use before sending a report, a status update or a decision memo that holds figures, or when the user asks whether the numbers in a document can be trusted.
license: MIT. LICENSE has complete terms.
compatibility: Designed for Claude Code; works with any agent that reads files. Needs python3 (3.8+). No network access.
metadata:
  version: "1.0.0"
  edition: "free"
---

# Numbers check (lite)

You make sure a report can be trusted. A number with no label, no source or no time is a guess that looks like a fact. The script finds them. You fix them with the user.

## Step 1: Scan the report

```bash
python3 <skill-folder>/scripts/numbers_check.py REPORT.md
```

It reports ERROR for a number with no label, and WARN for a verified number with no source or no time. `--json` prints JSON. Exit code 1 means errors. `references/labels.md` explains the labels and what the scan skips.

## Step 2: Fix each finding with the user

For each finding, ask how the user knows the number, then label it: `[V, source, time]` if read from a source, `[I]` if worked out, `[U]` if told or seen once, `[X]` if not found. Never invent a source or a time. Never delete a number you cannot verify. Make the edits after the user agrees.

## Limits
- The scan reads Markdown. A number written as a word is not found.
- It checks that a label, a source and a time are present. It cannot tell whether the source is real.
- This edition does not re-fetch numbers and has no before-and-after comparison. The full edition has both.
