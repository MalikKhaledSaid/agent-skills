# Formats

## LESSONS.md

```markdown
# Lessons

## L1: <the rule, one plain sentence, 160 characters or fewer>
- Evidence: <file, commit, incident or URL that shows why the rule exists>
- Date: <YYYY-MM-DD, the day the rule was set>
- Review by: <YYYY-MM-DD, ninety days later is a good default>
- Owner: <name>
```

Rules for the file:
- One rule per `##` heading. The id is `L` and a number. Ids never repeat and never change.
- The rule line says what to do. The story lives in the evidence.
- Keep the body to the four fields. The lint warns above 12 lines.
- Keep the file under 150 lines and 40 rules. Retire rules whose review date has passed.

## LESSONS_ARCHIVE.md
Written by `scripts/lessons_tool.py archive --apply`. It keeps each retired rule with its text and an `Archived` line.

## From an incident to a rule
1. Write what happened in one or two sentences, with the date.
2. Ask what the team does differently next time. That sentence is the rule.
3. Name the evidence: the commit, file or log that shows it.
4. Add it with `lessons_tool.py new`. Set the review date.
