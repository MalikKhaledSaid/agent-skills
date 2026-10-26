# The four labels

Put one label on every line that holds a number.

| Label | Meaning | What the line needs |
|---|---|---|
| `[V]` | Verified: you read it from a source | A source and a time |
| `[I]` | Inferred: you worked it out from other numbers | Say from what, if it is not obvious |
| `[U]` | Unverified: someone told you, or you saw it once | Nothing more. Check it before you rely on it |
| `[X]` | Not found, or not checkable | Say what you tried |

## A source
A link, a URL, a file name, or words after the label: `[V, Polar API]`, `[V, qa-report.md]`.

## A time
A date (`2026-10-26`, `26 Oct`), a clock time (`14:49 UTC`), or one line above the numbers that says when they were read:

```markdown
Numbers as of 26 Oct 2026 10:30 UTC.
```

That line covers every number below it, until the next such line. Words that start an as-of line: as of, read on, numbers at, checked, measured, fetched, snapshot.

## What the check skips
List numbers (`1.`), heading numbers, dates, clock times, version numbers (`1.2.3`, `v2`), years, commit hashes, ids such as `L12`, URLs, file names, and anything inside backticks or a code block. Plain single digits are skipped unless you pass `--include-small`.

## Why
A report with unlabelled numbers cannot be checked. A reader cannot tell a measured figure from a guess. A number with no time may be a week old. Three words after a number prevent both.
