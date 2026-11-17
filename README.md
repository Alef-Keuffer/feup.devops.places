# Places

Group 5's work on the Places subsystem of the Event Management system (DevOps and Cloud Computing): the catalogue of Venues and the calendar of their Bookings.

- `report/`: the Delivery 1 report, one Markdown file per section.
- `GLOSSARY.md`: the terms the report and the code use.
- `openapi.yaml`: Places' REST API. Check it with `npx @redocly/cli lint openapi.yaml`; the report's appendix includes it as it is.
- `docs/adr/`: architecture decisions and their reasons.
- `docs/grilling/`: the decision records the ADRs and tickets come from.

## Build the report

You need pandoc 3 and a TeX distribution with xelatex (MacTeX or TeX Live). From the repo root:

```sh
pandoc -d report/pandoc.yaml -o "report/$(git describe --tags --always --dirty).pdf"
```

This writes the PDF next to the sources, named with the version the title page prints. On the commit you tag, that name is the tag. `report/pandoc.yaml` lists the section files in order, so add any new file there.

CI (`.github/workflows/report.yml`) builds the same PDF on each push to main and each pull request. To get it without building, open the run in the repo's Actions tab and download it under Artifacts.

To hand in a delivery, tag the commit and push the tag, e.g. `git tag delivery-1 && git push origin delivery-1`. CI builds the PDF and attaches it to a release of that tag, named with the tag, so this link works for anyone, without a GitHub account, and doesn't expire: `https://github.com/Alef-Keuffer/feup.devops.places/releases/download/delivery-1/delivery-1.pdf`. Artifact links need a GitHub login and expire after 90 days, so share this one instead. The release notes list the pull requests merged since the previous tag.

Each version of the report is a tag: `delivery-1-draft-0.2` and so on for drafts, `delivery-1` for the version handed in. Before tagging, add the version's row to `report/0-revision-history.md`, in the commit you tag. The title page prints `git describe` of the checkout: the tag on a tagged commit, otherwise the nearest tag, the number of commits since it and the commit (`-dirty` if there are uncommitted changes).

## Write the report

- **Citations**: add the entry to `report/references.bib` and cite it as `[@key]` or `[@key, ch. 3]`. Pandoc's citeproc formats the citation and the reference list.
- **Diagrams**: draw them in TikZ, inside a raw LaTeX block (```` ```{=latex} ````). TikZ needs nothing beyond xelatex and gives vector figures. Copy the context diagram in `report/1-application-requirements.md` as a starting point, and add any TikZ library you need to `report/preamble.tex`.
- **Terms**: use the terms in `GLOSSARY.md`, and none of the words it lists under *Avoid*.

## Check the report

Ask your coding agent to run the consistency check (in Claude Code, `/consistency-check`). The skill lives in `.agents/skills/consistency-check/`, where Codex, Cursor, Gemini CLI and Copilot look for skills; Claude Code only reads `.claude/skills/`, so `.claude/skills/consistency-check` is a symlink to it, and `AGENTS.md` points any other agent at it. On Windows, Git checks the symlink out as a plain file unless symlinks are on: turn on Developer Mode and clone with `git clone -c core.symlinks=true`. Without an agent, `SKILL.md` also reads as a checklist. It runs the mechanical checks, then reviews the report against `GLOSSARY.md`, the ADRs and the latest grilling record, and lists each finding with its file and line, the problem and a suggested fix. It changes nothing.

The mechanical checks also run on their own, from the repo root (they need pandoc and xelatex as above, and Node for `npx` once `openapi.yaml` exists):

```sh
.agents/skills/consistency-check/check.sh             # Avoid words, OpenAPI lint, PDF build and citations
.agents/skills/consistency-check/check.sh --self-test # the script's own test
```
