# Group 5 (Places) → Group 2 (Promoters and Events)

## 1. What we need from you

**Booking request: `POST /bookings`** (our report, sections 4.1.1 and 4.1.4)

Events books a Venue for an Event by calling us directly, not through the Gateway, with the header `X-Service-Name: events`.
Body: `eventId`, `promoterId`, `venueId`, `firstDay`, `lastDay`, with dates such as `2027-06-08` and both days included.

`promoterId` must be the Promoter's user id: the id the Gateway has for the Promoter, which it sends as `X-User-Id`, not the id of your Promoter entity. We pass it on unchanged in our messages, and Billing (G3) and Reviews (G1) compare it with `X-User-Id`.

We answer:

- `201` with the Booking: what you sent, plus its `id` and `amount` (EUR as a decimal string, such as `"800.00"`).
- `409` when the Booking can't be made: `/problems/days-taken`, `/problems/event-already-booked` or `/problems/venue-unlisted`. These are a normal outcome to show the Promoter, not errors to retry.
- `422` with `/problems/unknown-venue` when no Venue has that `venueId`.
- `400` when the body is malformed, `lastDay` is before `firstDay`, or `firstDay` has passed.

**Booking cancellation: `DELETE /bookings/{bookingId}`**

Optionally with `?reason=...`, which we pass on in `BookingCancelled`. We answer `204` only once the days are free, so you can book again straight after, for instance to move an Event to other days. `404` if no Booking has that id, which is also the answer when the Booking is already gone: cancelled by the Venue Manager, or through Event cancelled. `409` with `/problems/booking-ended` if the Booking has ended.

**Event cancelled** (section 4.2.1)

When an Event is cancelled, we cancel its Booking, so you don't need to cancel it yourselves too.
Fields we use: `type` and `eventId`, the same id you sent in the Booking request. We ignore every other message on your exchange.

**Conventions** (section 4.1.3)

UUIDs for ids, ISO 8601 dates, whole days in the Europe/Lisbon time zone, amounts in EUR as decimal strings with two decimals, and errors as RFC 9457 `problem+json`. G3 has adopted them.

## 2. What we send you

**`BookingCancelled`** on our exchange `places`, routing key `BookingCancelled` (section 4.2.1)

We publish it for every cancellation, whoever made it. When the Venue Manager cancels, it is the only way you learn that your Event has lost its Venue.
Fields: `type`, `bookingId`, `eventId`, `promoterId`, `venueId`, `cancelledBy` (`events` or `venue-manager`), and `reason`, left out when none was given.

Please key what you store on `bookingId`, not `eventId` (section 4.2.3). Delivery is at-least-once, so a late copy of an old cancellation could otherwise seem to cancel a newer Booking for the same Event.

You don't need `BookingConfirmed`: our answer to your Booking request already tells you the Booking exists.

## 3. Questions

1. **`promoterId`:** will you put the Promoter's user id in the Booking request, as above?
2. **Your exchange:** our report calls the channel you publish Event messages on the Log topic. Following the broker rule we sent to everyone, what is that exchange called, and what routing key does Event cancelled use? We suggest `EventCancelled`. What else do you publish there?
3. **Calls and conventions:** will you call us directly with `X-Service-Name: events`, and do you adopt the conventions above?
4. **Naming:** could you rename `Room_request` to Booking request on the shared diagram? Events always books a whole Venue, never a room.
