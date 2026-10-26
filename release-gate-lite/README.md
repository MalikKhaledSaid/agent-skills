# release-gate-lite

A free pre-release check for a git repository. One verdict: PASS, HOLD or FAIL.

## Install

```bash
npx skills add MalikKhaledSaid/agent-skills
```

As a Claude Code plugin, from inside Claude Code:

```text
/plugin install release-gate-lite --marketplace MalikKhaledSaid/agent-skills
```

Or copy this folder into `~/.claude/skills/` (personal) or `.claude/skills/` in a project. Then ask your agent: "Run the release gate on this repo."

You can also run the script by hand:

```bash
python3 scripts/gate.py .
```

## What it checks
- Secrets in tracked files: AWS, GitHub, Slack, Stripe, OpenAI, Anthropic and Google keys, private key blocks, hard-coded passwords and tokens, tracked `.env` and key files.
- Version agreement across package.json, pyproject.toml, Cargo.toml and similar files.
- Version bump since the last tag.
- Changelog entry for the version.
- Merge conflict markers.
- Clean working tree.

The check reads only your repository. It sends nothing anywhere. Secret values are masked in the report.

## Sample output

```
# Release gate: FAIL

- Version: 1.1.0. Last tag: v1.0.0.

| Check | Result | Detail |
|---|---|---|
| Secrets in tracked files | FAIL | 1 found: config.py:1: AWS access key (AKIA...) |
| Changelog entry | HOLD | CHANGELOG.md has no entry for 1.1.0. |
| Clean working tree | PASS | No uncommitted changes. |
| Version matches everywhere | PASS | package.json=1.1.0 |
| Version bumped since last tag | PASS | v1.0.0 -> 1.1.0. |
| Merge conflict markers | PASS | None in 2 changed-since-v1.0.0 files. |
```

## Full edition
The full edition, release-gate, adds:
- The exact fix commands for each finding, including key rotation and history clean-up.
- More checks: debug leftovers, large files, broken README links, tests, remote behind, and secrets in past commits.
- A before-and-after comparison: save the findings, fix, compare.
- A release-notes draft from the commits since the last tag.
- Rules for CLAUDE.md, a GitHub Actions workflow and a pre-push hook.

## Requirements
Python 3.8 or later and git. Standard library only.

## License
MIT. See LICENSE.
