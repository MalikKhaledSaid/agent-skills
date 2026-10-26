# agent-skills

Free Claude Code skill that shows where your tokens go. It reads your own local session logs and prints a ranked report. No network access.

![Sample run of agent-token-auditor-lite](docs/demo.gif)

Real run on the author's own multi-agent workload, 26 Oct 2026, last 3 days. Session names replaced. Weighted tokens: 301.6M over 57 sessions. 64% came from turns above 150k context. 27% ran inside subagents. 41 tool results were longer than 20,000 characters.

## Free and full edition

| | Free: agent-token-auditor-lite | Full: agent-token-auditor, $9 |
|---|---|---|
| Token report by session, day and model | Yes | Yes |
| Costly patterns, each with a one-line fix | Yes | Yes |
| Fix playbook for each finding | No | Yes |
| Ready-to-paste CLAUDE.md rules | No | Yes |
| Guided workflow where your agent applies the fixes | No | Yes |

[Get the full edition ($9, one-time)](https://buy.polar.sh/polar_cl_a3PsNiRzvZ4szsrbQS1eHOvKSEymZvFHIGegX0Q2rJT)

All three full editions together, [All 3 packs for $19](https://buy.polar.sh/polar_cl_0NhKpsS3Zs6kOUrxkurweJd57GdowIOfceWDR2Rq94C) (bought separately: $28). The three are agent-token-auditor, release-gate and agent-team-ops.

Launch code `LAUNCH30` takes 30% off any single pack at checkout. It ends 8 Nov 2026 23:59 UTC and works for the first 50 uses. LAUNCH30 applies to single packs; the bundle is already discounted.

Skills in this repo work with any agent that reads SKILL.md. The install line below is for Claude Code.

| Skill | What it does | Edition |
|---|---|---|
| [agent-token-auditor-lite](agent-token-auditor-lite/) | Reads your local Claude Code logs and shows where your tokens went, with the costly patterns and a fix for each. | Free, MIT |
| [release-gate-lite](release-gate-lite/) | One PASS, HOLD or FAIL verdict before a release: secrets, version, changelog, merge markers, clean tree. | Free, MIT |
| [agent-team-check-lite](agent-team-check-lite/) | Checks the team files of a group of agent sessions for idle roles, broken reporting lines and template text left in tasks. | Free, MIT |
| agent-token-auditor (full) | Adds the fix playbook, ready CLAUDE.md rules and a guided workflow that applies the fixes. | [$9 one-time](https://buy.polar.sh/polar_cl_a3PsNiRzvZ4szsrbQS1eHOvKSEymZvFHIGegX0Q2rJT) |
| release-gate | One PASS, HOLD or FAIL verdict before a release. Checks secrets, versions, changelog, debug leftovers, large files, README links, tests and remote status, then your agent reviews the diff and drafts release notes. | [$7 one-time](https://buy.polar.sh/polar_cl_zGKv60a7zfftMDwtEse3Gq4Bsx5Gd5wDiXnm01q51F4) |
| agent-team-ops | Runs several AI agent sessions as one team: creates ORG.md and TEAM_PLAN.md, then checks for idle roles, broken reporting lines and tasks with no purpose. Includes 11 operating rules. | [$12 one-time](https://buy.polar.sh/polar_cl_0RUUUFGvqGayeWXaK1PxhAuQSrHMRDJHEkuoZ0xJOV3) |

## Install

```bash
npx skills add MalikKhaledSaid/agent-skills
```

As a Claude Code plugin, from inside Claude Code:

```text
/plugin install agent-token-auditor-lite --marketplace MalikKhaledSaid/agent-skills
/plugin install release-gate-lite --marketplace MalikKhaledSaid/agent-skills
/plugin install agent-team-check-lite --marketplace MalikKhaledSaid/agent-skills
```

Or copy a skill folder into `~/.claude/skills/`.

## Principles
- Each skill runs locally and states exactly what it reads.
- No telemetry and no network calls, unless a skill says otherwise.
- Scripts use the Python standard library only.
