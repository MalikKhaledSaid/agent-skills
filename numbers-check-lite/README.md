# numbers-check-lite

A free check that every number in a report says how it is known.

A report that mixes measured figures with guesses cannot be trusted. This check scans a Markdown report and asks three things of each number: a label, a source and a time.

## Install

```bash
npx skills add MalikKhaledSaid/agent-skills
```

As a Claude Code plugin, from inside Claude Code:

```text
/plugin install numbers-check-lite --marketplace MalikKhaledSaid/agent-skills
```

Or copy this folder into `~/.claude/skills/` (personal) or `.claude/skills/` in a project. Then ask your agent: "Check the numbers in this report."

You can also run the script by hand:

```bash
python3 scripts/numbers_check.py report.md
```

## The four labels
`[V]` verified, with a source and a time. `[I]` inferred. `[U]` unverified. `[X]` not found. See `references/labels.md`.

## What it checks
- ERROR: a number with no label.
- WARN: a verified number with no source, or with no time.
- It skips list numbers, dates, clock times, versions, years, commit hashes, ids, URLs, file names and code.

## Sample
A small report:

```markdown
# Weekly update

Numbers as of 26 Oct 2026 09:00 UTC.

- 120 people signed up this week [V, signup dashboard].
- Revenue is $840 [V].
- Churn is about 4% [I, from 5 cancellations out of 120].
- Support tickets: 37.
```

The real output for it:

```
# Numbers check: 1 errors, 1 warnings

| Level | Check | Detail |
|---|---|---|
| ERROR | No label | line 8: 37. Add [V], [I], [U] or [X]. |
| WARN | No source | line 6: $840. A [V] number needs a source. |

## Fixes

1. No source: Add a link, a file name, or a word after the label, like [V, Polar API].
2. No label: Say how you know the number: [V] verified with a source, [I] inferred, [U] unverified, [X] not found.
```

## Full edition
The full edition, numbers-check, adds:
- `numbers_recheck.py`: re-fetch a changing number with a command you list, and compare it with the report (MATCH or DIFFERENT, with a tolerance).
- The exact edit for each finding, with a before and after snippet.
- A before-and-after comparison: save the findings, fix the report, compare.
- A CLAUDE.md block and a worked example with a checks file.

## Requirements
Python 3.8 or later. Standard library only. No network.

## License
MIT. See LICENSE.
