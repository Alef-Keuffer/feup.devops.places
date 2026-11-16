---
name: citation-check
description: Citation check of the report against the cited books and pages themselves, each claim backed by a verbatim passage from the cited chapter or section. Use when asked to check citations, and after writing or changing one.
---

# Citation check

Report only: every file stays as it is.

A citation's **source** is what `cite.py` gives for it: the book in the main checkout's `docs/books/` that prints the ISBN from `report/references.bib`, or the page at the entry's `url`. Check each citation against its source, and rest each verdict on a **verbatim** passage that `cite.py quote` accepts. When `cite.py` can't give the source, the citation is **unchecked**: report it with the reason the script gave.

The script is `.agents/skills/citation-check/cite.py`. It runs from anywhere in the repo or a worktree, and prints its usage when run with no arguments.

## 1. List the citations

Run `cite.py list`, or `cite.py list FILE...` when asked about only some report files. It prints each citation, the pages of its source it resolves to, and the sentence before it. Each `FAIL` line is a finding. Done when the list has printed and every `FAIL` is noted.

## 2. Judge each citation

Group the citations by key and locator, and save each group's cited text once: `cite.py text KEY "LOCATOR" > <scratchpad>/<key>-<locator>.txt`. Search it for the terms of each claim and read the passages around the matches. The sentence `list` prints ends at the citation; read the report line when the claim runs on past it.

For each citation, pick the shortest passage that carries the claim, from one page, and run `cite.py quote KEY "LOCATOR" "PASSAGE"`. A claim with two parts may need a passage for each. Then give one verdict:

- **Supported**: `quote` prints OK for passages that together say what the claim says.
- **Wrong locator**: `quote` fails and names the page and section where the passage is. The fix is that chapter or section.
- **Overstated**: the passages carry only part of the claim, or a weaker form of it. Name the part with no passage.
- **Not supported**: no passage in the source says it.

Done when every citation from step 1 has a verdict, and every Supported verdict rests on passages that `quote` printed OK for.

## 3. Report

List every citation that isn't Supported, one per line:

```
- `report/3-services.md:22` — `[@newman2021, ch. 1]` — <verdict>: <the passage, quoted, and where it is> — Fix: <the right locator, or how to reword the claim>
```

End with the tally: citations checked, supported, findings, unchecked.
