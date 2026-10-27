---
name: research-brief-lite
description: Free check for a Markdown research brief. Finds a missing question, search budget, stop rule or findings section, a claim with no label ([V] verified, [I] inferred, [U] unverified, [X] not found) and a verified claim with no source. Use when an agent researches a market, a tool or a question, when the user asks for a research brief or a fact-checked summary, or before sharing research. Search words: research brief, fact check, source check, citations, search budget, stop rule, deep research.
license: MIT. LICENSE has complete terms.
compatibility: Designed for Claude Code; works with any agent that reads files. Needs python3 (3.8+). No network access.
metadata:
  version: "1.0.0"
  edition: "free"
---

# Research brief (lite)

You run research as a brief: one question, a budget and a stop rule first, then a label on every claim. The script checks the brief before it is shared.

## Step 1: Set up the brief with the user

Before any search, agree on one question, a search budget (for example "Searches: 8") and a stop rule (for example "Stop when 3 independent sources agree, or when the budget is spent"). Write them in the layout in `references/format.md`. Stop searching when the stop rule says so.

## Step 2: Label every claim

One claim per item under `## Findings`: `[V, source, date]` if you read it in the source, `[I]` if worked out, `[U]` if not checked, `[X]` if not found (say what you tried). `references/labels.md` explains each label. Never invent a source.

## Step 3: Check the brief

```bash
python3 <skill-folder>/scripts/brief_lint.py BRIEF.md
```

ERROR for a missing question, budget, stop rule or findings, and for a claim with no label. WARN for a verified claim with no source and for more than one question. `--json` prints JSON. Exit code 1 means errors.

## Limits
- A file with no brief sections is read as research notes: every labelled line is checked for a source.
- The check reads Markdown with level-2 headings. It cannot tell whether a source supports the claim.
- This edition does not count searches against the budget, check dates or listed sources, or compare before and after. The full edition does.
