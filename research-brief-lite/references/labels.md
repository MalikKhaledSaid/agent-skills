# The four labels

Every item under `## Findings` carries one label in square brackets at the start.

| Label | Means | Needs |
|---|---|---|
| `[V]` | Verified: you read it in the source | A source (link, file name or source name) and the date you read it. The link goes in `## Sources` too |
| `[I]` | Inferred: worked out from other findings | Which findings it comes from |
| `[U]` | Unverified: one source you could not check, or something you were told | Who said it, if known |
| `[X]` | Not found: you looked and could not find it | What you tried: searches, pages, people asked |

## Examples

- `[V, https://vendor.example/fees, 26 Oct 2026] The vendor charges a fee per sale, shown on its fees page.`
- `[V: pricing page of the vendor, read 26 Oct 2026] The free plan allows 3 seats.`
- `[I] The tool costs more than its rival for teams over 10 seats, from findings 2 and 4.`
- `[U] A forum post says the API limit is 100 calls a minute. The vendor docs do not say.`
- `[X] Not found: searched "vendor SOC 2 report" and read the vendor trust page; no report is listed.`

## Rules
- Read the source before you write `[V]`. A search result snippet is `[U]` until you open the page.
- One claim per item. Split a claim that rests on two sources with different labels.
- A date can be on the item or in an "as of <date>" line at the top of the brief.
- An `[X]` is a result. Keep it. It tells the reader where not to look again.
