# Team file templates

Write these files by hand. `scripts/team_check.py` reads the formats below, so keep the table columns and the heading style.

## ORG.md

```markdown
# Team structure

Owner: <lead name>. Every agent reads this file at the start of each session.

## The one rule
Only <lead name> talks to <human name>. Other agents send anything for <human name> to <lead name>.

## Roles

| Name | Role | Session | Reports to | Talks to human | Model |
|---|---|---|---|---|---|
| Lead | Lead and coordinator | (session id) | Human | yes | large |
| Builder | Builds and tests | (session id) | Lead | no | large |
| Research | Finds facts and sources | (session id) | Lead | no | small |

## Approvals only the human gives
1. Spending money.
2. Creating accounts, keys or payment setup.
3. Anything public: posts, releases, listings, emails.

## Working rules
1. Every task names the goal it serves and the teammate who will use its output.
2. Messages go only to a teammate who must act or decide. Status goes in files.
3. Each message stays under 150 words. Its first line says what it is about.
4. One round summary per role per round, sent to the role's manager.
5. Blocked work goes to the manager the same round, with what was tried.
6. Rejected work goes back to its owner with the reason. Nothing is deleted silently.
7. When a session's context passes about 150k tokens, it writes a hand-over in `handovers/` and a fresh session starts from it.
8. Numbers carry their source and time. Unknowns are marked unknown.
```

## TEAM_PLAN.md

```markdown
# Team plan

Goal: <one measurable goal with a date>.
Updated: <YYYY-MM-DD> by <name>.

## Lead
1. <task> (goal: <goal>; output to: <name>)

## Builder
1. <task> (goal: <goal>; output to: <name>)

## Research
1. <task> (goal: <goal>; output to: <name>)
```

Rules for the plan:
- One `##` section per role name in ORG.md.
- Open items are numbered lines. Done items move to `DECISIONS.md` or are marked `[done]`.
- Each open item names its goal and who uses the output.

## DECISIONS.md

```markdown
# Decision log

## <YYYY-MM-DD>: <decision in one line>
- Decided by: <name>
- Why: <evidence>
- Before: <number or state>. After: <number or state>.
```

## handovers/<role>-<YYYY-MM-DD>.md

```markdown
# Hand-over: <role>, <YYYY-MM-DD>

- Open items, in order:
- Files and paths:
- Decisions made and why:
- Numbers, with source and time:
- Waiting on (who, what, since when):
- First action for the new session:
```

## Round summary (message to the manager)

```text
<Name> (<role>) round <n>: <one-line result>.
Done: <items, with file or commit>.
Blocked: <item, what was tried> | none.
Needs <human> via lead: <approval> | none.
Next: <item>.
```
