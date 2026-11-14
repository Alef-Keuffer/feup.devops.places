---
name: consistency-check
description: Consistency check of the report against GLOSSARY.md, the ADRs and the latest grilling record. Use when asked to check the report, or before a delivery.
---

# Consistency check

Report only: every file stays as it is.

## 1. Run the script

From the repo root, run `.agents/skills/consistency-check/check.sh`. Each `FAIL` or `Avoid word` line it prints is a finding. Done when the script has exited and its findings are noted.

## 2. Read the sources of truth

- `GLOSSARY.md`
- every ADR in `docs/adr/`
- the latest grilling record in `docs/grilling/` (file names start with the date); it supersedes older records
- the report: the files in `report/pandoc.yaml`'s `input-files`, in that order, and `openapi.yaml` if it exists

Done when every file listed has been read in full.

## 3. Review

Apply every check to every report file:

- **Contradictions**: each statement agrees with the ADRs and the latest grilling record. Something the record lists as out of scope or as a question for later, written as decided or delivered, is a contradiction too.
- **Glossary meaning**: each glossary term is used in its defined meaning. The script skips any *Avoid* word that has a condition in parentheses in some entry, so judge each such word against every entry that lists it, with or without a condition.
- **Justified decisions**: each architectural decision states its reason and cites a reference (`[@key]` from `report/references.bib`).
- **Required sections**: every stage the delivery's assignment requires has a section with real content; a *To be written* placeholder counts as missing. Delivery 1's assignment is `docs/assets/delivery-assignment.pdf`, and its stages are Application requirements, System operations, Services, and Service APIs and collaborations.

Done when every check has been applied to every report file.

## 4. Report

List every finding, script and review alike, one per line:

```
- `report/3-services.md:12` — <problem, naming the ADR, record decision or glossary entry it breaks> — Fix: <suggested change>
```

With no findings, say the report is clean.
