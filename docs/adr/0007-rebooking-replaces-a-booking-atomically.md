# A Rebooking replaces an Event's Booking in one transaction

A Booking request may name the Event's current Booking in `replacesBookingId`. Places then cancels that Booking and creates the new one in one transaction, so either both happen or nothing changes. We call this a Rebooking. It lets Events postpone an Event, or give a published Event another Venue, without ever leaving the Event with no Venue, while a Booking's days still never change (FR-23) and an Event still holds at most one Booking (FR-19).

G2's report (`docs/groups/2026-11-16-g2-promoters-and-events-report.pdf`, received 2026-11-16) needs exactly this guarantee in two flows of its §4.3. `postponeEvent` asks Places to "move the reservation to the new dates. If Group 5 refuses, the command fails with 409 and nothing changes." `updateEvent`, on a published Event, "reserves the new place with Group 5 first and releases the old reservation only after the event is saved". What we offered until now couldn't do either: a second Booking for the Event is rejected (FR-19), and a Booking's days can't change (FR-23), so Events had to cancel and book again.

## Considered options

- **Cancel, then book again (what we offered before).** Rejected. Between Places answering the cancellation and receiving the new Booking request, another Promoter's request can take the old days. If the new days are taken as well, the Event has lost its Venue and can't get it back. Events could check availability first (FR-15), but a check is a read, and nothing stops another request from taking the days between the check and the Booking. ADR-0001 rests on this point: only the service that owns a Venue's calendar can serialise two competing requests. Asking G2 to accept the race would contradict our own reason for owning Bookings, and G2's flows explicitly require that nothing changes on failure.
- **Change a Booking's days in place (`PATCH /bookings/{bookingId}`), as G2's report assumes.** Rejected. It reverses FR-23. *Booking confirmed* has already given Billing (G3) and Reviews (G1) the days and the amount (FR-24), so a change needs a new message, such as *Booking changed*, that both groups must consume, and Billing would have to change a bill's amount. It also doesn't cover a change of Venue: the new days are in another Venue's calendar, so the `PATCH` would have to move the Booking between Venues as well.
- **Rebooking (chosen).** One optional field in the Booking request, and the messages we already publish. FR-19 and FR-23 hold at every commit. One mechanism covers postponing, changing a published Event's Venue, and changing the Venue of a draft Event, which G2's `bookPlace` also does.

## How the database enforces it

Within the transaction, Places deletes the old Booking before it inserts the new one. Both constraints from ADR-0003 are checked as each row is inserted, and a row the same transaction has deleted takes no part in the check. So the new Booking may overlap the old one's days, which a postponement by one day at the same Venue needs, and the Event's one Booking stays unique. We ran this on Postgres 18 (2026-11-16): Venue 7 booked 8–10 June for Event 100 and 12–13 June for Event 200.

| In one transaction | Result |
|---|---|
| Delete Event 100's Booking, insert 9–11 June for it | Committed: the new days overlap the old ones |
| Insert 10–11 June for Event 100 before deleting its Booking | Refused by the unique constraint on the Event |
| Delete Event 100's Booking, insert 12 June for it | Refused by the exclusion constraint; after rollback the old Booking stands |

## Consequences

- A Rebooking is rejected with `422 /problems/unknown-booking` when the Booking it names doesn't exist or belongs to another Event, and with `409 /problems/booking-ended` when that Booking has ended (FR-30). If a Venue Manager cancels the same Booking at the same moment, whichever transaction commits second finds no Booking. A Rebooking that comes second gets `unknown-booking`, and Events learns of the cancellation from *Booking cancelled*.
- Every other rejection of the new Booking (`days-taken`, `venue-unlisted`, `unknown-venue`, `400`) rolls the transaction back and leaves the old Booking standing.
- A Booking request without `replacesBookingId` for an Event that has a Booking is still rejected as `409 /problems/event-already-booked` (FR-19).
- Events can't undo a Rebooking. Once Places answers, the old Booking is gone and its days may be taken, so Events must make its own checks on the Venue before the request, and if saving its Event fails afterwards, save it again rather than cancel the new Booking. G2's `updateEvent` releases the old reservation only after saving the Event to cover that failure; retrying the save takes its place.
- The new Booking's amount is set at today's price per day (FR-22). A postponement at the same Venue costs more or less if its Venue Manager has changed the price since the first Booking.
- A Rebooking writes two messages to the outbox in its transaction (ADR-0006): *Booking cancelled* for the old Booking, with `cancelledBy: events`, then *Booking confirmed* for the new one. Consumers handle both as they handle any other Booking. Each message still has its own Booking id, so the message type and the Booking id still identify each message.
- *Booking confirmed* gains an optional `replacesBookingId`. Without it, Billing can't tell a Rebooking from an unrelated Booking. Billing refunds no paid bill (ADR-0004), so a Promoter who paid and then postpones would pay twice. With the field, Billing can carry the payment over to the new bill if it chooses. That choice is G3's.
