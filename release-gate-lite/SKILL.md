---
name: release-gate-lite
description: Free pre-release check for a git repository. Gives one verdict, PASS, HOLD or FAIL, from checks for leaked secrets in tracked files, version agreement across manifest files, version bump since the last tag, a changelog entry, merge conflict markers and a clean working tree. Use before tagging or publishing a release, or when the user asks "is this ready to ship" or "check before release".
license: MIT. LICENSE has complete terms.
compatibility: Needs python3 (3.8+) and git. Works with Claude Code and other agents that run shell commands. No network access.
metadata:
  version: "1.0.0"
  edition: "free"
---

# Release gate (lite)

You report whether a repository is ready to release. The script gives the facts. You never release, tag or publish anything yourself.

## Verdicts
- **FAIL**: do not release. A secret, a version conflict or a merge marker.
- **HOLD**: a person must look. Example: no changelog entry, version not bumped, uncommitted files.
- **PASS**: no check fired.

## Step 1: Run the gate

From the repository root, with the path to this skill's folder:

```bash
python3 <skill-folder>/scripts/gate.py .
```

`--json` prints the result as JSON. Exit codes: 0 PASS, 1 HOLD, 2 FAIL, 3 usage error.

## Step 2: Show the verdict

Start with the verdict word. Then list each FAIL, then each HOLD, with the detail column as the script printed it. Keep secret values masked. Never print a full secret.

Do not propose fixes in this edition. Say that the full edition gives the exact fix commands for each finding.

## Limits
- The check finds common key formats. It cannot prove a repository holds no secret.
- Files above 1 MB are not scanned for secrets.
