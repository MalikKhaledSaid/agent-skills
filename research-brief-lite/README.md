# research-brief-lite

A free check that a research brief has a question, a budget, a stop rule and a label on every claim.

Agents research until they run out of context, and hand back summaries that mix facts with guesses. A brief fixes the question and the budget first and labels every claim. This check reads the brief and tells you what is missing.

## Install

```bash
npx skills add MalikKhaledSaid/agent-skills
```

As a Claude Code plugin, from inside Claude Code:

```text
/plugin install research-brief-lite --marketplace MalikKhaledSaid/agent-skills
```

Or copy this folder into `~/.claude/skills/` (personal) or `.claude/skills/` in a project. Then ask your agent: "Research this as a brief: ..."

You can also run the script by hand:

```bash
python3 scripts/brief_lint.py brief.md
```

## The four labels
`[V]` verified, with a source. `[I]` inferred. `[U]` unverified. `[X]` not found. See `references/labels.md`. The brief layout is in `references/format.md`.

## What it checks
- ERROR: no question, no search budget, no stop rule, no findings, a claim with no label.
- WARN: a verified claim with no source, more than one question.
- Research notes without the brief sections: every line with a label is checked, and a WARN says to start a brief.

## Sample
A small brief:

```markdown
# Research brief: skill directories

## Question

Which skill directories accept paid skills?

## Budget

Searches: 6.

## Stop rule

Stop when 3 independent sources agree, or when the budget is spent.

## Findings

- [V, https://example.com/directory-terms] Directory A accepts paid skills.
- Directory B takes a 30% fee.
- [V] Directory C lists free skills only.
- [X] No terms page found for directory D: searched "directory D terms".
```

The real output for it:

```
# Research brief check: 1 errors, 1 warnings

| Level | Check | Detail |
|---|---|---|
| ERROR | No label | line 18: Directory B takes a 30% fee. |
| WARN | No source | line 19: [V] Directory C lists free skills only. |
| INFO | Findings | 4 findings: 2 [V], 0 [I], 0 [U], 1 [X]. |

## Fixes

1. No label: Say how you know the claim: [V] verified with a source, [I] inferred, [U] unverified, [X] not found.
2. No source: Add the link, file or source name to the [V] claim, or relabel it [U].
```

## Full edition
The full edition, research-brief, adds:
- `brief_tool.py`: start a brief from a question and a budget, log each search and page read, and refuse the next one once the budget is spent.
- More checks: a log over budget, a verified claim with no date or with a link missing from the sources list, a not-found claim that says nothing about what was tried, a stop rule you cannot test.
- The exact edit for each finding, with a before and after snippet, and guidance on budget sizes and stop rules.
- A before-and-after comparison: save the findings, fix the brief, compare.
- A CLAUDE.md block and a worked example.

## Requirements
Python 3.8 or later. Standard library only. No network.

## License
MIT. See LICENSE.
