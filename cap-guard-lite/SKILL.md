---
name: cap-guard-lite
description: Free check of an agent's spend against a cap. Reads a spend log (a CSV of dates and amounts), a cap and a cycle end date and gives one verdict, OK, WARN or STOP, with exit codes 0, 1 and 2 so a hook can stop an agent. Use before a costly agent step, or when the user asks "how much budget is left" or "are we near the spending cap". Search words: spending cap, budget guard, agent budget, usage limit, stop at limit.
license: MIT
compatibility: Designed for Claude Code; works with any agent that reads files. Needs python3 (3.8+). Reads only the log file you name; no network, no commands run.
metadata:
  version: "1.0.0"
---

# Cap guard (free)

You check an agent's spend against a cap. The script reads the log and gives one verdict.

## Step 1: Get the three inputs

- A CSV log with the header `date,amount`: one row per charge or per day, ISO dates, a dot as the decimal mark, current cycle only.
- The cap for the cycle, in the same unit as the log.
- The last day of the cycle.

If the user has no log, say so and stop. Do not invent amounts.

## Step 2: Run the check

```bash
python3 <skill>/scripts/cap_check.py spend.csv --cap 100 --cycle-end 2026-11-30 --unit USD
```

It prints the spend against the cap, the days left and the verdict. Add `--warn 0.9` to move the warn level (default 0.8 of the cap). Add `--json` for a script.

Exit codes: 0 OK, 1 WARN, 2 STOP, 3 input it cannot use (one line says why).

## Step 3: Act on the verdict

- OK: carry on and check again before the next costly step.
- WARN: look before any costly step and name who may spend the rest.
- STOP: stop. Start nothing costly until a person raises the cap or the cycle resets.

## Limits

- It reads a log you supply and cannot tell whether the log is complete.
- It does not forecast. It checks the spend so far.
- It does not stop a run by itself; the agent or a hook must act on the exit code.

Full edition: cap-guard $7: a forecast from your spend log (days left to the warn level and to the cap, burst days left out), the daily spend that lasts to the cycle end, a one-page status file, a fix guide, a CLAUDE.md block, a worked example and a before-and-after check. https://buy.polar.sh/polar_cl_Lb5HMDxvRd6RmWT9hUkX61Dc36Egqi7OnPCmi22BcKs?utm_source=github&utm_medium=skill&utm_campaign=cap-guard
