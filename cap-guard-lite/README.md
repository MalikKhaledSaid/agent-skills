# cap-guard-lite

A free check of an agent's spend against a cap. One verdict from a spend log: OK, WARN or STOP.

## Use
Copy this folder into `~/.claude/skills/` (personal) or `.claude/skills/` in a project, then ask your agent: "Check my spend against the cap." Or run it by hand:

```bash
python3 scripts/cap_check.py spend.csv --cap 100 --cycle-end 2026-11-30 --unit USD
```

The log is a CSV with the header `date,amount`. Exit codes: 0 OK, 1 WARN, 2 STOP, 3 input it cannot use.

## What it checks
- Spend so far against the cap, and the days left in the cycle.
- The verdict at one warn level (default 80% of the cap).

An empty file, one row, a date after today, a negative amount or a comma decimal gives one clear line and exit code 3.

## Requirements
Python 3.8 or later. Standard library only. No network.

## Status
The full edition adds a forecast from the log, burst days, the daily spend to the cycle end, a status file and a before-and-after check. https://buy.polar.sh/polar_cl_Lb5HMDxvRd6RmWT9hUkX61Dc36Egqi7OnPCmi22BcKs?utm_source=github&utm_medium=readme&utm_campaign=cap-guard

## License
MIT. See LICENSE.
