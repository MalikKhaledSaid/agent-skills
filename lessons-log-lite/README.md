# lessons-log-lite

A free check for a LESSONS.md file of standing rules. It finds rules with no evidence and rules nobody has re-read.

A lessons file helps only while its rules are short, backed by evidence and still current. This check shows which ones are not.

## Install

```bash
npx skills add MalikKhaledSaid/agent-skills
```

As a Claude Code plugin, from inside Claude Code:

```text
/plugin install lessons-log-lite --marketplace MalikKhaledSaid/agent-skills
```

Or copy this folder into `~/.claude/skills/` (personal) or `.claude/skills/` in a project. Then ask your agent: "Check my LESSONS.md."

You can also run the script by hand:

```bash
python3 scripts/lessons_lint.py LESSONS.md
```

## The file format
One rule per `##` heading, with an id, one line, and four fields. See `references/templates.md`.

```markdown
## L1: Run the release gate before every tag
- Evidence: incident 2026-09-14, commit 4f2a9c1
- Date: 2026-09-14
- Review by: 2026-12-14
- Owner: Lead
```

## What it checks
- ERROR: a rule with no evidence, or two rules with one id.
- A file of plain bullets gets one warning, plus checks for size and for bullets over 160 characters.
- WARN: a review date that passed, a missing date or review date, a rule line over 160 characters, a rule body over 12 lines, two rules with the same title (case and punctuation ignored), and a file over 150 lines or 40 rules.

## Sample output
Real output on a two-rule file, run on 26 Oct 2026:

```
# Lessons lint: 1 errors, 1 warnings

| Level | Check | Detail |
|---|---|---|
| ERROR | No evidence | L2: the rule has no evidence. |
| WARN | Review overdue | L1: review date 2026-10-01 passed 25 days ago. |
| INFO | No owner | L1: no Owner field. |
| INFO | No owner | L2: no Owner field. |

## Fixes

1. Review overdue: Re-read the rule. Renew it with a new date, or retire it.
```

## Full edition
The full edition, lessons-log, adds:
- `lessons_tool.py`: add a rule from an incident, renew a review date, archive overdue rules to LESSONS_ARCHIVE.md (nothing is deleted), and convert a file of plain bullets into rules.
- The exact edit for each finding, with a before and after snippet.
- A before-and-after comparison: save the findings, clean up, compare.
- A CLAUDE.md block and a session-start hook that shows the lint.
- A worked example file.

## Requirements
Python 3.8 or later. Standard library only. No network.

## License
MIT. See LICENSE.
