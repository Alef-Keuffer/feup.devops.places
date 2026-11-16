# Group 5 (Places) → Group 3 (Tickets and Billing): Rebooking

> Sent to G3 in their chat. Tells G3 about the Rebooking we offer G2 (ADR-0007, `../grilling/2026-11-16-g2-report.md`), and asks whether Billing carries a paid bill over. G1 was to get it too, but reads none of our messages (`2026-11-16-g1-to-g5.md`).

One change to our Booking messages, after reading G2's report. When Events (G2) postpones an Event, or moves it to another Venue, it can now replace the Event's Booking in one request, which we call a Rebooking: we either cancel the old Booking and create the new one, or do neither. You'll see it as two messages you already handle:

- `BookingCancelled` for the old Booking, with `cancelledBy: events`;
- `BookingConfirmed` for the new Booking, with its own `bookingId`, days and amount, plus one new field, `replacesBookingId`: the id of the Booking it replaces, left out on any other Booking.

We publish them in that order, but like any two messages they can reach you in either order, so the new `BookingConfirmed` can arrive before the old charge is cancelled.

Without the new field, a Promoter who paid and then postpones or changes Venue pays twice: the old charge isn't refunded, and the new one is charged in full. With `replacesBookingId` you can tell a Rebooking from a new Booking and carry the payment over. The new amount comes from the new days at today's price per day, so it can differ from the old one. That choice is yours: will you carry the payment over?
