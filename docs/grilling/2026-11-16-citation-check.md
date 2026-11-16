# Grilling record: checking the report's citations (2026-11-16)

Goal: decide how this report's citations get checked. The checking tool itself became its own project, `/Users/alef/Documents/repos/citation-check`, whose glossary, ADRs and grilling record hold the design. This record keeps only what this repo acts on. It doesn't supersede `2026-11-14-delivery-1-report.md`.

## Decisions

1. **Every citation carries its passages.** Each one is followed by a footnote with one or more verbatim passages from the cited source, each with its location: `[@richardson2019, sec. 2.2.1]^["passage" (p. N)]`, or `(PDF p. N)` for Newman, whose PDF prints no page numbers. A pointer citation, `[see @key]`, carries none. Only we write `see`, never the agent.
2. **The passages go in a quotations appendix.** `enotez` in `report/preamble.tex` turns footnotes into endnotes, and `\printendnotes` under an appendix heading in `report/9-references-and-appendix.md` prints them. The report has no other footnotes.
3. **Retrofit before the 18 Nov delivery**, in its own worktree and `/implement` session, using `cite.py quote` from the citation-check skill: `~/.claude/skills/citation-check/cite.py`, a symlink to a clone of github.com/Alef-Keuffer/citation-check. PR 17, which would have put a copy of the script in this repo, is closed. That is about 75 citations, not the 39 counted on 2026-11-14. The same work adds a `url` to the entries `cite.py list` can't resolve: rfc9457, rfc9110, rfc9562, rfc3339 and rfc8259. Any citation without a passage that carries its claim gets reworded or cut.
4. **Richardson's year is 2019**, as his PDF prints ("©2019"). The key `richardson2018` becomes `richardson2019` in `references.bib` and in every citation.
5. **`docs/books/` becomes `docs/sources/`** once the citation-check tool looks there (its verify ticket). Until then, cite.py reads `docs/books/`.
6. **This repo keeps no copy of the tool.** `AGENTS.md` points agents to the citation-check skill and its repo; the quote work adds that pointer.
