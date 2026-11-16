# Group 3 (Tickets and Billing) → Group 5 (Places)

> G3's reply to `2026-11-16-g5-to-g3.md`: points 1 to 3 answer our two answers and the note on cancellations, points 4 and 5 our follow-up. Code is marked as code here; the words are G3's.

Thanks Alef, that's very clear.

1. `promoterId`: perfect, that's exactly what we need. We've asked G2 the same thing (send the promoter's user id in the Booking request), so they're getting the same request from both of us.

2. Exchange: noted. Billing binds its queue to the `places` exchange with the routing keys `BookingConfirmed` and `BookingCancelled`.

3. Cancellations arriving first: already in our contract. If a `BookingCancelled` arrives for a `bookingId` we have no charge for, we record the booking as cancelled, and a later `BookingConfirmed` for it creates no charge.

4. Message ids: our slides from 11 November had an earlier proposal. We've since adopted your approach: no separate message id, and duplicates are handled by `bookingId` (one charge per booking; cancelling an already cancelled charge changes nothing).

5. Paying the Venue Manager: yes, out of scope for delivery 1, just like paying Promoters their ticket revenue. Billing collects the money, but payouts to venue managers and promoters aren't designed yet. We'll list both as open gaps in our report too. We'll already store `venueManagerId` on each charge, so it's ready when payouts are added.
