# agent-skills

Practical skills for Claude Code and other agents that use the Agent Skills format (SKILL.md).

| Skill | What it does | Edition |
|---|---|---|
| [agent-token-auditor-lite](agent-token-auditor-lite/) | Reads your local Claude Code logs and shows where your tokens went, with the costly patterns and a fix for each. | Free, MIT |
| agent-token-auditor (full) | Adds the fix playbook, ready CLAUDE.md rules and a guided workflow that applies the fixes. | [$9 one-time]
| agent-team-ops | Runs several AI agent sessions as one team: creates ORG.md and TEAM_PLAN.md, then checks for idle roles, broken reporting lines and tasks with no purpose. Includes 11 operating rules. | [$12 one-time](https://buy.polar.sh/polar_cl_0RUUUFGvqGayeWXaK1PxhAuQSrHMRDJHEkuoZ0xJOV3) |(https://buy.polar.sh/polar_cl_a3PsNiRzvZ4szsrbQS1eHOvKSEymZvFHIGegX0Q2rJT) |

## Install

```bash
npx skills add MalikKhaledSaid/agent-skills
```

Or copy a skill folder into `~/.claude/skills/`.

## Principles
- Each skill runs locally and states exactly what it reads.
- No telemetry and no network calls, unless a skill says otherwise.
- Scripts use the Python standard library only.
