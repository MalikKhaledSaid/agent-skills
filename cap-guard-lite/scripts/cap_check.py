#!/usr/bin/env python3
"""Keep an agent's spend inside a cap: read a spend log, give one verdict, OK, WARN or STOP.

  python3 cap_check.py spend.csv --cap 100 --cycle-end 2026-11-30 [--today DATE] [--warn 0.8] [--unit USD] [--json]

The log is a CSV with a header row `date,amount`: one row per charge or per day, ISO dates, a dot as the decimal mark,
for the current cycle only. STOP is spend at or above the cap. WARN is spend at or above the warn share of the cap.
Exit codes: 0 OK, 1 WARN, 2 STOP, 3 unreadable or impossible input (one line on stderr).
Reads the one file you name. Makes no network call and runs no command. Python 3.8+, standard library only.
"""
import argparse
import csv
import json
import math
import os
import statistics
import sys
from collections import defaultdict
from datetime import date, timedelta

OK, WARN, STOP = "OK", "WARN", "STOP"
EXIT = {OK: 0, WARN: 1, STOP: 2}


class InputError(Exception):
    """Input that cannot be used. The message is one line for the user."""


def parse_date(text, what):
    try:
        return date.fromisoformat(str(text).strip())
    except ValueError:
        raise InputError(f"{what} '{text}' is not a date like 2026-11-30.")


def read_log(path, today):
    """Return a list of (date, amount) from the CSV log. Raises InputError with one clear line."""
    try:
        with open(path, encoding="utf-8") as fh:
            lines = fh.read().splitlines()
    except OSError:
        raise InputError(f"No file at {path}.")
    numbered = [(n, l) for n, l in enumerate(lines, 1) if l.strip()]
    if not numbered:
        raise InputError("The log is empty.")
    header = [c.strip().lower() for c in next(csv.reader([numbered[0][1]]))]
    if header != ["date", "amount"]:
        raise InputError("The first row must be the header 'date,amount'.")
    rows = []
    for n, line in numbered[1:]:
        cells = next(csv.reader([line]))
        if len(cells) != 2:
            raise InputError(f"Line {n}: expected 'date,amount' with a dot as the decimal mark, found {len(cells)} fields.")
        day = parse_date(cells[0], f"Line {n}: the date")
        try:
            amount = float(cells[1].strip())
        except ValueError:
            raise InputError(f"Line {n}: the amount '{cells[1].strip()}' is not a number with a dot as the decimal mark.")
        if not math.isfinite(amount):
            raise InputError(f"Line {n}: the amount '{cells[1].strip()}' is not a finite number.")
        if amount < 0:
            raise InputError(f"Line {n}: the amount {amount} is negative.")
        if day > today:
            raise InputError(f"Line {n}: the date {day.isoformat()} is after today ({today.isoformat()}).")
        rows.append((day, amount))
    if len(rows) < 2:
        raise InputError("The log needs at least 2 rows.")
    return rows


def verdict_for(spent, cap, warn):
    if spent >= cap:
        return STOP
    if spent >= warn * cap:
        return WARN
    return OK


def analyse(rows, cap, cycle_end, today, warn, days=7):
    spent = sum(a for _, a in rows)
    days_left = (cycle_end - today).days
    res = {"spent": round(spent, 2), "cap": cap, "days_left": days_left, "warn_at": warn,
           "verdict": verdict_for(spent, cap, warn)}
    return res


def to_markdown(res, unit=""):
    u = f" {unit}" if unit else ""
    pct = res["spent"] / res["cap"] * 100
    lines = [f"# Cap guard: {res['verdict']}", "",
             f"- Spent: {res['spent']:.2f}{u} of {res['cap']:.2f}{u} ({pct:.0f}%).",
             f"- Days left in the cycle: {res['days_left']}.",
             f"- Warn level: {res['warn_at'] * 100:.0f}% of the cap. Stop level: the cap."]
    return "\n".join(lines)


FOOTER = "\nFull edition, cap-guard $7: a forecast from your spend log (days left to the warn level and to the cap, burst days left out), the daily spend that lasts to the cycle end, a one-page status file, a fix guide, a CLAUDE.md block, a worked example and a before-and-after check. https://buy.polar.sh/polar_cl_Lb5HMDxvRd6RmWT9hUkX61Dc36Egqi7OnPCmi22BcKs?utm_source=github&utm_medium=script&utm_campaign=cap-guard"


def main(argv=None):
    ap = argparse.ArgumentParser(description="Keep an agent's spend inside a cap: OK, WARN or STOP from a spend log.")
    ap.add_argument("log", help="CSV spend log with the header date,amount")
    ap.add_argument("--cap", type=float, required=True, help="the cap for the cycle, in the log's unit")
    ap.add_argument("--cycle-end", required=True, help="last day of the cycle, YYYY-MM-DD")
    ap.add_argument("--today", help="today's date, YYYY-MM-DD (default: the local date)")
    ap.add_argument("--warn", type=float, default=0.8, help="share of the cap that gives WARN (default 0.8)")
    ap.add_argument("--unit", default="", help="a label for the amounts, for example USD")
    ap.add_argument("--json", action="store_true", help="print JSON")
    args = ap.parse_args(argv)
    try:
        if not args.cap > 0:
            raise InputError("--cap must be above 0.")
        if not 0 < args.warn < 1:
            raise InputError("--warn must be between 0 and 1, for example 0.8.")
        today = parse_date(args.today, "--today") if args.today else date.today()
        cycle_end = parse_date(args.cycle_end, "--cycle-end")
        if cycle_end < today:
            raise InputError(f"--cycle-end {cycle_end.isoformat()} is before today ({today.isoformat()}).")
        rows = read_log(args.log, today)
    except InputError as exc:
        print(str(exc), file=sys.stderr)
        return 3
    days = 7
    res = analyse(rows, args.cap, cycle_end, today, args.warn, days)
    print(json.dumps(res, indent=2) if args.json else to_markdown(res, args.unit))
    if not args.json:
        print(FOOTER)
    return EXIT[res["verdict"]]


if __name__ == "__main__":
    sys.exit(main())
