# Places

Group 5's work on the Places subsystem of the Event Management system (DevOps and Cloud Computing): the catalogue of Venues and the calendar of their Bookings.

- `report/`: the Delivery 1 report, one Markdown file per section.
- `GLOSSARY.md`: the terms the report and the code use.
- `docs/adr/`: architecture decisions and their reasons.
- `docs/grilling/`: the decision records the ADRs and tickets come from.

## Build the report

You need pandoc 3 and a TeX distribution with xelatex (MacTeX or TeX Live). From the repo root:

```sh
pandoc -d report/pandoc.yaml
```

This writes `report/places-delivery-1.pdf`. `report/pandoc.yaml` lists the section files in order, so add any new file there.

## Write the report

- **Citations**: add the entry to `report/references.bib` and cite it as `[@key]` or `[@key, ch. 3]`. Pandoc's citeproc formats the citation and the reference list.
- **Diagrams**: draw them in TikZ, inside a raw LaTeX block (```` ```{=latex} ````). TikZ needs nothing beyond xelatex and gives vector figures. Copy the context diagram in `report/1-application-requirements.md` as a starting point, and add any TikZ library you need to `report/preamble.tex`.
- **Terms**: use the terms in `GLOSSARY.md`, and none of the words it lists under *Avoid*.
