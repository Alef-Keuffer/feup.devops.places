## Agent skills

### Issue tracker

Issues are tracked in GitHub Issues via the `gh` CLI. See `docs/agents/issue-tracker.md`.

### Triage labels

Default five-role vocabulary (`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`). See `docs/agents/triage-labels.md`.

### Domain docs

Single-context: one `GLOSSARY.md` and `docs/adr/` at the repo root. See `docs/agents/domain.md`.

### Group replies

To record a reply from another group, or to cut tickets for the report, follow `docs/agents/group-replies.md`.

### Consistency check

To check the report, before a delivery or when asked, follow `.agents/skills/consistency-check/SKILL.md`.

### Citation check

To check the report's citations against the cited sources, follow the citation-check skill at `~/.claude/skills/citation-check`. That skill is a checkout of https://github.com/Alef-Keuffer/citation-check. This repo keeps no copy of the tool.
