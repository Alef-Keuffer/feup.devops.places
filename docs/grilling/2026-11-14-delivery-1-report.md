# Grilling record: DCN Delivery 1 report (2026-11-14)

Goal: settle what the 2026-11-11 presentation left open, using `docs/notes/nov-11th-presentation-notes.md`, ahead of the report due 2026-11-18. This record supersedes the decisions and open questions in `2026-11-11-delivery-1-presentation.md`.

Vocabulary: see `GLOSSARY.md`. Decisions: see `docs/adr/0001` to `0006`.

## Decisions

1. **The Venue is the bookable unit.** A Promoter books a whole Venue. A Venue has an address, coordinates, images, capacity, area, price per day, equipment, type and Rating. Rooms are structured entries in the Venue's description (name, capacity, area, layout image), with no price, and are never booked; the number of rooms is the count of entries.
2. **Venue type** is one field from a fixed list: open-air, stadium, pavilion, auditorium, conference centre, other.
3. **Places owns the catalogue.** A Venue Manager submits a Venue, and it is Listed immediately, with no approval step. Each Venue has exactly one Venue Manager, its submitter, and that can't be transferred. The Venue Manager can unlist and relist it at any time. An Unlisted Venue drops out of search and takes no new Bookings, but its existing Bookings stand. Deleting a Venue is refused while it has future Bookings.
4. **Identity.** The Gateway (G4) checks the token, and Places trusts the user id and roles it forwards. Places checks that the role allows the operation and, for changes to a Venue, that the caller is that Venue's Venue Manager. One person may be both a Promoter and a Venue Manager.
5. **Bookings** (ADR-0001, ADR-0003). A Booking covers consecutive whole days. An Event holds at most one Booking: the professor ruled out an Event at several places, and separate days are separate Events. A Booking's days never change; to move, cancel and book again. A Booking request is not checked against capacity: capacity is a search filter, and the Promoter sets the ticket cap, which can change after booking anyway.
6. **Cancellation** can come from either side.
   - Events cancels a Booking with a synchronous REST `DELETE`, so a rebooking sent straight after can't hit the old Booking.
   - *Event cancelled* on the Log topic removes the Event's Booking.
   - A Venue Manager may cancel a Booking for an unforeseen reason. They find it through a REST list of their Venue's Bookings, open only to them.
   - Every cancellation, whoever made it, publishes *Booking cancelled*, saying who cancelled and with an optional reason.
7. **Pricing.** Price per day only. The amount for a Booking is days × the Venue's price per day.
8. **Billing** (ADR-0004, confirmed). Places publishes *Booking confirmed* with the amount, and Billing (G3) creates the bill. Billing ignores cancellations.
9. **Rating** (ADR-0002). Ratings are per Venue and come from Promoters. Only the Promoter who booked a Venue may rate it; Reviews (G1) enforces this, learning who booked what from *Booking confirmed* and *Booking cancelled*. *Rating changed* carries a timestamp, and Places drops one older than the Rating it holds.
10. **Search filters:**
    - a date window and a number of days: a Venue matches when it has at least that many consecutive free days inside the window
    - minimum capacity
    - maximum price per day
    - city
    - minimum Rating
    - Venue type

    The Promoter then checks exact days with the single-Venue availability check. There is no keyword or equipment filter.
11. **The Log box**, as we read the professor's answer, is Places' subscription to the topic G2 publishes Event messages on. Places acts on *Event cancelled* and ignores *Event scheduled*. Places no longer consumes *Event ended*.
12. **Collaborations:**
    - Events → Places: the Booking request (`Room_request` on the shared diagram) and Booking cancellation, over synchronous REST.
    - Events → Log topic → Places: *Event cancelled*.
    - Reviews → broker → Places: *Rating changed*.
    - Places → broker: *Booking confirmed* (Billing, Reviews) and *Booking cancelled* (Events, Reviews; Billing ignores it).
    - Tickets (G3) → Places: REST GET on a Venue for its name and address.
    - Promoters and Venue Managers → Gateway → Places: REST.
13. **API conventions**, which we propose to all groups and explain as our choice in the report: UUID ids, ISO 8601 dates, Europe/Lisbon as the timezone for whole-day Bookings, EUR, errors as RFC 9457 `problem+json`, and one OpenAPI spec per service. We assume at-least-once delivery on the broker, so every message handler is safe to run twice.
14. **Stack** (ADR-0003). A private PostgreSQL database with an exclusion constraint against overlapping Bookings, and a REST API documented in OpenAPI.
15. **Places is one service** (ADR-0005), not separate catalogue and Booking services.
16. **Outgoing messages go through a transactional outbox** (ADR-0006), so a saved or cancelled Booking never loses its *Booking confirmed* or *Booking cancelled* message.
17. **The report follows Richardson's process** (*Microservices Patterns* ch. 2 §2.2): application requirements, then system operations (commands and queries with preconditions and postconditions), then services, then service APIs and collaborations. "System operations" means those commands and queries, not DevOps operations. References: Wiegers & Beatty for requirements, Newman and Richardson for services, Richardson for APIs and collaborations. *The DevOps Handbook* is kept for later deliveries.

## Questions for later

- L1 (professor): Can a Venue Manager block days for maintenance or for rentals outside the platform? Our position: not in delivery 1.
- L2 (professor): Will later deliveries deploy all groups to one shared cluster, and is the broker or the stack mandated?
- L3 (G2): Will you rename `Room_request` to Booking request on the shared diagram?
- L4 (G2, G4): Which messages go on the Log topic?
- L5 (G3): Does Tickets read a Venue's name and address with a REST GET?
- L6 (G1): Will Reviews enforce "only the Promoter who booked may rate" from our Booking messages, and publish *Rating changed* with the Venue id, average, review count and timestamp?
- L7 (G4): Which broker will you run, and is delivery at-least-once?

## Gap to name

No group handles refunds. If a Venue Manager cancels a Booking, the Promoter's bill still stands.

## Since the session

- 2026-11-16, G3 (`docs/groups/2026-11-16-g3-to-g5.md`): Billing cancels an unpaid bill on *Booking cancelled* and refunds no paid one, deliberately for delivery 1. This replaces "Billing ignores cancellations" in decisions 8 and 12 and the gap above; see ADR-0004. G3 also answered L5: yes.
- 2026-11-16, our replies to G3 (`docs/groups/2026-11-16-g5-to-g3.md`) and G1 (`docs/groups/2026-11-16-g5-to-g1.md`):
  - `promoterId` is the Promoter's user id, the value the Gateway forwards as `X-User-Id`, so Billing can check who pays a bill and Reviews who may rate a Venue. Events must put that id in its Booking request rather than the id of G2's own Promoter entity; new question L8 to G2.
  - The Places topic is a durable topic exchange named `places`, and each message's routing key is its type. G3 says G4 runs RabbitMQ; L7 still asks G4.
  - We asked G1 which exchange carries *Rating changed* and suggested the routing key `RatingChanged` (L6).
  - We asked G3 whether paying the Venue Manager the Booking's amount is out of scope for delivery 1, since Billing doesn't read `venueManagerId`; new question L9.
- 2026-11-16, questions drafted for G2 and G4 (`docs/groups/drafts/`) but not sent, because we don't yet know who represents them. They carry L3, L4, L7 and L8, and add L10 (G2: call directly with `X-Service-Name: events`, adopt our conventions), L11 (G4: `X-User-Id` a UUID, role names) and L12 (G4: the Gateway removes the identity headers users send, and is the only way in). L4 now also asks for the exchange and routing key of *Event cancelled*, suggesting `EventCancelled`, and L7 asks who creates the exchanges. We sent every group a rule for the broker (`docs/groups/2026-11-16-g5-to-all.md`): each publisher declares a durable topic exchange named after itself, with the message type as routing key, sends persistent messages and waits for the broker's confirms; each consumer declares its own durable queue, binds it by routing key and acknowledges a message only after handling it. RabbitMQ confirms and drops a message that matches no queue, so a consumer must bind its queue before the first message it needs is published; the rule as sent leaves this out, and a drafted follow-up adds it. The report now says "question Ln asks" rather than "we have asked" for questions not yet sent.
- 2026-11-16, G2's report (`docs/groups/2026-11-16-g2-promoters-and-events-report.pdf`) and our answer to it, settled in `2026-11-16-g2-report.md`. A Booking can now be replaced by a Rebooking (ADR-0007), which amends decision 5: a Booking's days still never change, but to move, Events rebooks in one request instead of cancelling and booking again. *Booking confirmed* gains an optional `replacesBookingId`. G2 answered L8 against our assumption, and we ask them to key their Promoter by the user id. We decline G2's request for a *Venue updated* message.
- 2026-11-16, we sent G2 our answer (`docs/groups/2026-11-16-g5-to-g2.md`), which asks L3, L4, L8 and L10 and the new questions of `2026-11-16-g2-report.md`, and sent every group the follow-up to the broker rule (`docs/groups/2026-11-16-g5-to-all-binding.md`).
- 2026-11-16, G1 (`docs/groups/2026-11-16-g1-to-g5.md`) answered L6, no to both parts. Reviews won't bind to `places`: it learns where an Event was held from G2's `event.ended`, and will ask G2 to add `venueId` to it. Reviews would let anyone rate a Venue, but is open to changing that. Reviews publishes nothing, and offers `GET /api/v1/ratings/venues/{venueId}`, answering `venueId`, `average`, `count` and `stampedAt`. Decided:
  - Places still keeps a copy of each Venue's Rating (ADR-0002, rewritten), but refreshes it every five minutes by calling that GET for every Venue, Listed or Unlisted. The timestamp rule stays, now because two refreshes can overlap. *Rating changed* is gone, and `refreshRatings`, run by Places' own timer, replaces `handleRatingChanged`. This replaces the message in decision 9 and the Reviews line of decision 12. We rejected dropping the Rating from Places: the minimum Rating filter was our proposal, not the professor's, but the refresh is little to build.
  - Who may rate a Venue is Reviews' rule, not a requirement of Places, which replaces "only the Promoter who booked a Venue may rate it" in decision 9. We suggest to G1 a Promoter whose Event at that Venue has ended: G2's `event.ended` already tells G1 that, it matches the professor's note that Promoters review Venues, and if anyone may rate, a Venue Manager could rate their own Venue. Reviews drops out as a consumer of *Booking confirmed* and *Booking cancelled* in decision 12. ADR-0004 and ADR-0007 now name Billing alone where they named Reviews too.
  - New question L13 (G1): what the GET answers for a Venue with no reviews, whether Places may call it directly with `X-Service-Name: places`, and whether Reviews could return many Ratings in one call. The report assumes a `404` or a `count` of 0 means no Rating, and a direct call. We sent it to G1 with our reply (`docs/groups/2026-11-16-g5-to-g1-ratings.md`). The Rebooking message went to G3 alone (`docs/groups/2026-11-16-g5-to-g3-rebooking.md`), and the G4 draft no longer binds a queue to a G1 exchange.
  - G1 calls G2's messages `event.ended` and `event.cancelled`. If those are G2's routing keys, the `EventCancelled` that L4 suggests is wrong; L4 still asks G2.
- 2026-11-16, reviewing the G4 draft: the Gateway sends `X-User-Roles` for every user, empty for one with neither role, because any user may search and read Venues and Places answers `401` to a request without both user headers. L11 now also asks G4 whether it can send the header empty. L4 is now for G2 alone: under the broker rule G2 names its own exchange, and our answer to G2 asks it.
- 2026-11-16, G1's follow-up (`docs/groups/2026-11-16-g1-to-g5-ratings.md`) to our reply:
  - Reviews lets a user review an Event and its Venue only if they attended the Event, which it checks with Tickets (G3) when the review is posted. A Venue Manager can rate their own Venue only after attending an Event there, which answers our concern. Ratings no longer "come from Promoters" (decision 9). Places is unaffected, since it reads only the average. The rule departs from the professor's "Promoter gives reviews to places" (`docs/notes/nov-11th-presentation-notes.md`), which we pointed out to G1 before; the rule is theirs to defend.
  - L13 answered. For a Venue with no reviews, Reviews answers `200` with a `count` of 0. G1's message breaks off before saying what `average` then holds, so Places reads a `count` of 0 as no Rating, whatever `average` says, and the `404` assumption goes. Places may call the Rating GETs directly with `X-Service-Name: places`, since they are read-only and public. Reviews will add a call that returns many Ratings, and will give its shape in its report.
  - G1 now offers to publish rating changes on the broker, given our search, and will decide within its group. Decided: we tell G1 the batch call is enough, and Reviews needn't publish. With the batch call, a refresh is one call every five minutes. Each refresh reads every Rating again, so an answer that failed or was saved out of order is put right by the next one, while a lost message would leave a Venue's Rating wrong until its next review, unless Reviews publishes as reliably as our outbox (ADR-0006). All the message would add is freshness, and ADR-0002 already accepts a five-minute lag for a search filter. G1 then builds only the batch call, and the report keeps the refresh it describes. ADR-0002 now gives this argument. We sent G1 this reply (`docs/groups/2026-11-16-g5-to-g1-batch.md`).
- 2026-11-16, G3's reply (`docs/groups/2026-11-16-g3-to-g5-followup.md`) to our answers and follow-up:
  - `promoterId` as the user id is what Billing needs, and G3 has asked G2 the same, so G2 hears it from both of us. L8 stays open with G2.
  - Billing binds its queue to `places` with the routing keys `BookingConfirmed` and `BookingCancelled`, as the broker rule says.
  - Billing keys its bills on `bookingId` and reads no separate message id, which replaces the message id of G3's slides of 11 November: one bill per Booking, and cancelling a cancelled bill changes nothing. A *Booking cancelled* for a Booking with no bill records the Booking as cancelled, and a later *Booking confirmed* for it creates no bill. What the report asks of Billing under "Consumers deduplicate by Booking id" is now what Billing does. G3 calls a bill a *charge*; the report keeps *bill*.
  - L9 answered: nobody pays the Venue Manager a Booking's amount in delivery 1, just as nobody pays Promoters their ticket revenue. Billing collects the money, and payouts to either aren't designed yet. Billing stores `venueManagerId` on each bill, ready for when payouts are added, and G3's report lists both payouts as open gaps. Ours lists the Venue Manager's.

## For the report

From G1's follow-up of 2026-11-16. `openapi.yaml` needs no edit, since it doesn't describe Reviews' API.

- Application requirements: the Promoter rows of the glossary table ("rates the Venues they booked") and of the stakeholders table ("rates through Reviews") stop saying that Promoters rate. Who may rate a Venue stays Reviews' rule, as the Reviews rows and the Scope table already say.
- Open points, L6: replace "we suggested a Promoter whose Event at that Venue has ended" with G1's rule, a user who attended the Event, checked with Tickets when the review is posted. "Reviews publishes no messages" stays, now because we told G1 the batch call is enough.
- Open points, L13: answered. A `count` of 0 means no Rating, the direct call with `X-Service-Name: places` is accepted, and Reviews will add the batch call.
- Messaging section, the three Rating options: the *Rating changed* option is still rejected, but for our reasons in ADR-0002 (a self-correcting refresh at one call every five minutes), not because G1 declined.
- Messaging section, "Refreshing the Ratings": read a `count` of 0 as no Rating, and use the batch call, with its path and answer from G1's report. If G1's report doesn't give them by the cutoff, keep one call per Venue and say the batch call is agreed, with its shape to come. If the batch call is used, row 5 of the flows table says the Ratings come in one call. The paragraph on direct calls under the flows table says G1 accepts the direct call, instead of "which we have asked G1 to accept (L13)".
- System operations, `refreshRatings`: in its postconditions, "when Reviews has no Rating for it" becomes "when Reviews answers a `count` of 0", and "Places has asked Reviews for the Rating of each Venue" follows whichever call the Messaging section uses.

From G3's reply of 2026-11-16. `openapi.yaml` needs no edit, since it doesn't describe messages.

- Open points, L9: answered. Paying the Venue Manager is out of scope for delivery 1, like paying Promoters their ticket revenue; Billing stores `venueManagerId` on each bill for when payouts are added, and G3's report lists both as gaps.
- Open points, "Out of scope for delivery 1", and the Scope table in Application requirements: add paying the Venue Manager a Booking's amount. Where it stands: Billing (G3) collects the amount but pays no one out in delivery 1, and keeps `venueManagerId` on each bill.
- Messaging section, *Booking confirmed*'s fields: `venueManagerId` says Billing stores it on each bill, for paying the Venue Manager in a later delivery.
- Messaging section, "Consumers deduplicate by Booking id": the paragraph says G3 has adopted keying on the Booking id for Billing, and the Billing bullet says what Billing does, as G3 confirmed, rather than what it must do, including recording a Booking as cancelled when *Booking cancelled* comes first.
- Open points, L7: G3 already binds Billing's queue to `places` by routing key, as the rule says. L8: G3 has asked G2 the same.

## Out of scope for delivery 1

Venue approval, transferring a Venue to another Venue Manager, hourly or seasonal pricing, distance search, keyword and equipment filters, blocking days outside Bookings, refunds and cancellation fees, a *Venue updated* message (added 2026-11-16, see `2026-11-16-g2-report.md`).
