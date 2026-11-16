# Group 5 (Places) → Group 3 (Tickets and Billing): Rebooking

> Draft, not sent. Tells G3 about the Rebooking we offer G2 (ADR-0007, `docs/grilling/2026-11-16-g2-report.md`), and asks whether Billing carries a paid bill over. Send it in G3's chat. G1 was to get it too, but reads none of our messages (`docs/groups/2026-11-16-g1-to-g5.md`). When sent, move it to `docs/groups/<date>-g5-to-g3-rebooking.md`. Paste from the next line on.

One change to our Booking messages, after reading G2's report. When Events (G2) postpones an Event, or moves it to another Venue, it can now replace the Event's Booking in one request, which we call a Rebooking: we either cancel the old Booking and create the new one, or do neither. You'll see it as two messages you already handle:

- `BookingCancelled` for the old Booking, with `cancelledBy: events`;
- `BookingConfirmed` for the new Booking, with its own `bookingId`, days and amount, plus one new optional field, `replacesBookingId`: the id of the Booking it replaces.

We publish them in that order, but like any two messages they can reach you in either order.

Without the new field, a Promoter who paid and then postpones or changes Venue pays twice, because the old bill isn't refunded and the new one is billed in full. With `replacesBookingId` you can tell a Rebooking from a new Booking, and carry the payment over if you choose. The new amount is worked out from the new days at today's price per day, so it can differ from the old one. That choice is yours: will you carry it over?
