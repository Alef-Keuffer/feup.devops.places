# Group 5 (Places) → Group 2 (Promoters and Events): your two questions

Hi Group 2, thanks. Your answers settle every point we raised, and our report for the 18 November delivery will say so. Here are our answers to your two questions.

**a) Recovery after a 201.** We'll add `GET /bookings?eventId={eventId}`.

- Call it directly with `X-Service-Name: events`, as you call `POST /bookings`. Any other caller gets `403`, and a request without `eventId` gets `400`.
- It answers `200` with a list. The list holds the Event's Booking, with the same fields as our `201` (`id`, `eventId`, `promoterId`, `venueId`, `firstDay`, `lastDay`, `amount`), or is empty when the Event has no Booking. A Booking that has ended is still listed.
- After a failure between our `201` and your save, read the Booking with this call and save its `id`. You can also use it whenever you want to check your Event against our Booking.

We chose this over an idempotency key, which would mean storing keys and their answers on our side, and deciding how long to keep them.

**b) EventCancelled with no Booking.** Confirmed. If an `EventCancelled` names an Event with no Booking, or one whose Booking has ended, we acknowledge it and do nothing. There is no error and no `BookingCancelled`. A repeated `EventCancelled` likewise has no further effect.

Your point on postponements is right too: a Booking is whole days, so a change of time that keeps the same days needs no Rebooking.
