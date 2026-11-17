# Grilling record: when a Venue loses its Rating (2026-11-17)

Goal: settle what ticket #23 left open on clearing a Rating, found by its review: what a clearing leaves behind, what the records say about the cases the stamp rule misses, and which requirement says a Venue loses its Rating. This record adds to `2026-11-14-delivery-1-report.md` and doesn't supersede it.

Vocabulary: see `GLOSSARY.md`, unchanged. Decisions: see ADR-0002.

## Decisions

1. **Why the report rejects *Rating changed*.** We switched to the refresh because G1 refused to publish (`docs/groups/2026-11-16-g1-to-g5.md`). When G1 then said it might, pending a decision within its group (`docs/groups/2026-11-16-g1-to-g5-ratings.md`), we kept the refresh for ADR-0002's reasons: a refresh corrects itself, while a lost message would leave a Rating wrong unless Reviews published as reliably as our outbox, which we can't require of G1. The report keeps that framing, with G1's refusal and its maybe as history. We rejected leading with G1's lack of a guarantee: the argument holds even if G1 decides to publish.
2. **A clearing leaves no stamp.** Clearing sets both the average and the stamp to NULL. An older answer saved after a clearing finds no Rating and restores the old one, until the next refresh clears it again. We accept this, as ADR-0002 accepts the one-second `Date` case. We rejected keeping the answer's `Date` as the stamp of a cleared Venue: it closes the slip, but a Venue would have no Rating yet a stamp, which bends the model, for a case the next refresh corrects.
3. **ADR-0002 names both cases the stamp rule misses**, each put right by the next refresh: a clearing within a second of a Rating's stamp, refused or let through wrongly because `Date` counts whole seconds and may be generated at any time while the answer is sent; and an older answer saved after a clearing. The report's Messaging section already says both, since #23.
4. **A requirement for losing a Rating.** FR-33 and FR-34 cover clearing too, and US-11 gets a scenario for it, below.

## For the report

`openapi.yaml` needs no edit, since it doesn't describe Reviews' API.

- Application requirements, FR-33: add that a Venue Reviews no longer lists loses its Rating.
- Application requirements, FR-34: add "nor clear a Rating stamped later than the answer that no longer lists the Venue".
- Application requirements, US-11: add a scenario, after "a late answer":

  *Scenario: the last review removed.*

  | **Given** a Venue rated 4.4, stamped 10:05
  | **When** a refresh answered at 10:10 no longer lists it, because its last review was removed
  | **Then** the Venue has no Rating, and a search with a minimum Rating leaves it out

- System operations, the domain model's Rating (`2-system-operations.md`, "A Venue has no Rating until Places first reads one for it"), and Messaging, the chosen Rating option ("a Venue has no Rating until a refresh reads one for it"): each adds that a Venue loses its Rating when Reviews no longer lists it.
- The `delivery-1-draft-0.2` row of the revision history says so.
