# Grilling record: the report points back to the repository (2026-11-18)

Goal: the report refers to "the group's repository" (revision history, REST API, appendix) but never says where it is, so a reader can't follow it. The repository is public at `https://github.com/Alef-Keuffer/feup.devops.places`, and the draft tags are pushed.

Vocabulary: see `GLOSSARY.md`, unchanged. Decisions: no ADR, since the change is cheap to reverse and weighed no real alternatives.

## Decisions

1. **The title page gives the address.** A line under `Version …` gives `https://github.com/Alef-Keuffer/feup.devops.places`, linked to the repository's root, on every build. We rejected putting it only in the revision history's sentence, and putting it in both: the title page is where the reader already finds the version.
2. **The version links to its tag when the build is exactly a tag.** When `git describe --tags --always --dirty` prints a bare tag, with no `-N-g<hash>` and no `-dirty`, the version links to `https://github.com/Alef-Keuffer/feup.devops.places/tree/<tag>`. Any other build keeps the version as plain text, since GitHub has no page for it. Whether the tag is pushed isn't checked: the order is tag, push, build.
3. **The `openapi.yaml` mentions stay as they are.** "At the root of the repository" (REST API) and the appendix keep their wording, without a link. The appendix reproduces the file as built, and a link to `main` would drift from it.

## For the report

- `report/version.lua`: add the repository line to the title page's date line, and make the version a link when it is a bare tag.
- Revision history, the opening paragraph: say that the title page also gives the repository's address.
- Revision history, a row under the next version: "The title page gives the repository's address and links the version to its tag." Why: "The report referred to the repository without saying where it is."
