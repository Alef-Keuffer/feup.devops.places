# Grilling record: DCN Delivery 1 presentation (2026-11-11)

> Superseded by `2026-11-14-delivery-1-report.md`: its decisions and questions for later replace the ones below.

Goal: prepare the Places subsystem (group 5) for presentation in today's lecture. The report is due 2026-11-18 and covers application requirements, system operations, services, and service APIs and collaborations, with every architectural decision justified.

Vocabulary: see `GLOSSARY.md`. Decisions: see `docs/adr/0001` to `0003`.

## Decisions

1. **Venue → Rooms.** "Place" is only an umbrella word. A Venue has its address, coordinates, images and Rating. A Room has its capacity, area, layout, equipment and price per day. The Room is the proposed bookable unit (still open, see O2).
2. **Places owns the catalogue.** It owns create, update and delete for Venues and Rooms. Venue Managers submit their own Venues and only they may change them. Users/Gateway (G4) authenticates callers and passes on their identity and role.
3. **Places owns Bookings and availability** (ADR-0001). A Booking is confirmed in one step: an accepted `Room_request` creates it, and it is removed when the Event is cancelled. There is no hold or expiry.
4. **The Venue Rating is cached** from a *Rating changed* message published by Reviews (G1) (ADR-0002).
5. **Stack:** a private PostgreSQL database with an exclusion constraint against overlapping Bookings, and a REST API documented in OpenAPI (ADR-0003).
6. **Collaborations (proposed):**
   - Events → Places `Room_request`: synchronous REST.
   - Events → broker → Places: *Event cancelled* (remove the Booking) and *Event ended*.
   - Reviews → broker → Places: *Rating changed*.
   - Promoters and Venue Managers → Gateway → Places: REST.
   - Places publishes no messages in this delivery.
7. **Proposed Booking and pricing model:** Bookings cover whole days (start and end dates inclusive). A quote is the number of days × the Room's price per day.
8. **Proposed search filters:** city, date range, minimum capacity, maximum price per day, minimum Rating, required equipment.

## Open questions to ask in the presentation

- O1: Is a submitted Venue listed immediately, or does it need admin approval first?
- O2: Does a Booking reserve a Room or a whole Venue? Can one Event hold several Bookings? (G2)
- O3: Are whole-day Bookings with a price per day enough, or are hourly or seasonal prices needed?
- O4: Do G1, G2 and G4 agree with the communication split in decision 6?
- O5: Which search filters do Promoters need? Alternatives: distance from coordinates, venue type, accessibility.
- O6: What does the "Log" box inside G5 in the shared diagram draft mean?

## Gap to name

No subsystem bills venue rent. G3 bills tickets, and Places does not handle payments.

## Out of scope

Venue moderation, hourly or seasonal pricing, distance search, and venue rent payment.
