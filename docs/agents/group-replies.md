# Group replies

Other groups keep answering our questions until the **cutoff**. Until then, sessions only record the replies, and the report changes once, through tickets cut at the cutoff. Questions still unanswered at the cutoff stay in the report as open points, with the position the report takes meanwhile.

Delivery 1's cutoff: the afternoon of 2026-11-17.

## Recording a reply

1. Save the reply in `docs/groups/` as `<date>-g<N>-to-g5.md`, or as the file the group sent under a name starting `<date>-g<N>-`, where `<date>` is the day it was sent, with a note at its top saying how it arrived. A live document, such as a Google Doc, can change after it is sent, so save it as PDF, name it by the day you exported it, and give the export time where you record it. A draft of ours that has been sent moves out of `docs/groups/drafts/`, as its README says.
2. Record what the reply settles, and why: in a grilling record when we grill on it, otherwise as a dated entry under "Since the session" in the latest grilling record. Update ADRs and `GLOSSARY.md` as `docs/agents/domain.md` says.
3. List each edit the reply calls for in `report/` or `openapi.yaml` under "For the report" in that grilling record, naming the requirement, operation, section or table it touches. Add the heading if the record has none. The tickets make these edits, so `report/` and `openapi.yaml` stay as they are.
4. Commit on `main` and push it. These records change no part of `report/` or `openapi.yaml`, so they need no PR. Other sessions start from commits, not from this working tree. Done when `git status` lists none of the files this session touched.

## Cutting tickets

At the cutoff, or earlier if every group has settled, the user runs `/to-tickets`. Read every "For the report" list in `docs/grilling/` that no ticket covers yet. Draw each ticket around one decision, through every report section and `openapi.yaml` part it touches. Add a last ticket that runs the consistency check over the whole report, to finish before #8, the human sign-off.
