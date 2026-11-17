# Group 5 (Places) → Group 2 (Promoters and Events): your two questions

Thanks, that settles every point we raised. Our answers:

**a) Recovery after a 201.** Yes, we'll add `GET /bookings?eventId={eventId}`. Call it directly with `X-Service-Name: events`, as you call `POST /bookings`. It answers `200` with a list holding the Event's Booking, with the same fields as the `201`, or an empty list when the Event has none. A Booking that has ended is still listed. Without `eventId` the answer is `400`, and any caller other than Events gets `403`. After a failure, read the Booking with it and save its `id`. You can also use it to check your Event against our Booking at any time. We chose it over an idempotency key, which would mean storing keys and their answers on our side.

**b) EventCancelled with no Booking.** Confirmed. When *EventCancelled* names an Event with no Booking, or one whose Booking has ended, we acknowledge it and do nothing: no error and no *BookingCancelled*. A repeated message has no further effect either.

Both will be in our report for the delivery on 18 November.
