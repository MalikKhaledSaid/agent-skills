# agent-skills

Practical skills for Claude Code and other agents that use the Agent Skills format (SKILL.md).

| Skill | What it does | Edition |
|---|---|---|
| [agent-token-auditor-lite](agent-token-auditor-lite/) | Reads your local Claude Code logs and shows where your tokens went, with the costly patterns and a fix for each. | Free, MIT |

## Install

```bash
npx skills add MalikKhaledSaid/agent-skills
```

Or copy a skill folder into `~/.claude/skills/`.

## Principles
- Each skill runs locally and states exactly what it reads.
- No telemetry and no network calls, unless a skill says otherwise.
- Scripts use the Python standard library only.
