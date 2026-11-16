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

## Out of scope for delivery 1

Venue approval, transferring a Venue to another Venue Manager, hourly or seasonal pricing, distance search, keyword and equipment filters, blocking days outside Bookings, refunds and cancellation fees.
