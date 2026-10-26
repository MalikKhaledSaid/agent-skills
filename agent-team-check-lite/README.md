# agent-team-check-lite

A free health check for a team of AI agent sessions. It reads your team files and lists what is broken.

## Install

```bash
npx skills add MalikKhaledSaid/agent-skills
```

As a Claude Code plugin, from inside Claude Code:

```text
/plugin install agent-team-check-lite --marketplace MalikKhaledSaid/agent-skills
```

Or copy this folder into `~/.claude/skills/` (personal) or `.claude/skills/` in a project. Then ask your agent: "Check my team files."

You can also run the script by hand, from the folder that holds ORG.md and TEAM_PLAN.md:

```bash
python3 scripts/team_check.py --dir .
```

## What it checks
- ERROR: no role, or several roles, that talk to the human; a manager name that matches no role; a reporting loop; a missing ORG.md or TEAM_PLAN.md.
- WARN: a role with no queue or no open items; tasks that name no goal or receiver; template text left in a task, such as `<task>` or "output to: Nobody"; a plan or decision log older than 7 days; missing session ids or approvals list.

`references/templates.md` shows the file formats the check reads.

## Sample output
This is the real output for a fresh template with three roles, before anyone edits it:

```
# Team check: 0 errors, 6 warnings

| Level | Check | Detail |
|---|---|---|
| WARN | Session id | Lead has no session id. |
| WARN | Session id | Builder has no session id. |
| WARN | Session id | Research has no session id. |
| WARN | Placeholder task | Lead: 1 of 1 open items are template text or name nobody to receive the output. |
| WARN | Placeholder task | Builder: 1 of 1 open items are template text or name nobody to receive the output. |
| WARN | Placeholder task | Research: 1 of 1 open items are template text or name nobody to receive the output. |
```

## Full edition
The full edition, agent-team-ops, adds:
- Set-up in one command: ORG.md, TEAM_PLAN.md, DECISIONS.md and a hand-over folder.
- The 11 operating rules and the start briefs for each role.
- The exact edit for each finding, with a before and after snippet.
- A before-and-after comparison: save the findings, fix, compare.
- A CLAUDE.md block and a session-start hook that runs the check.
- A worked example team.

## Requirements
Python 3.8 or later. Standard library only.

## License
MIT. See LICENSE.
