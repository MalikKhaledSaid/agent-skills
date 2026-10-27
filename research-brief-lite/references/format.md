# Brief layout

Use level-2 headings. The check accepts any case.

```markdown
# Research brief: <short title>

Started 2026-10-26.

## Question

One question, written so a yes, a no, a number or a short list answers it.

## Budget

Searches: 8. Reads: 12.

## Stop rule

Stop when 3 independent sources agree on the answer, or when the budget is spent, whichever comes first.

## Search log

- search: "the query" (2026-10-26): what it gave
- read: https://example.com/page (2026-10-26): what it says

## Findings

- [V, https://example.com/page, 26 Oct 2026] A claim read in the source.
- [I] A claim worked out from findings 1 and 2.
- [U] A claim from one source that could not be checked.
- [X] Not found: searched "query one" and "query two", read the vendor pricing page.

## Sources

- https://example.com/page

## Open questions

- What the brief could not answer inside the budget.
```

Section names the check also accepts: "Research question", "Search budget", "Stop" and "Stopping rule", "Log", "Claims".

A log item that starts with `read` counts as a page read. Every other log item counts as a search.

This edition does not count the log against the budget. The full edition does, and refuses a search once the budget is spent.
