# Group 5 (Places) → Group 1 (Reviews)

> Sent to G1 over WhatsApp. Our reply to `2026-11-16-g1-to-g5.md`, in G1's order, as `../grilling/2026-11-14-delivery-1-report.md` (Since the session) settled it. It asks question L13.

Thanks, that's clear. Our replies, in your order:

1. Fine. We've taken Reviews off the consumers of our messages.
2. Who may rate a Venue is your rule, so we've taken it out of our report. A suggestion: only a Promoter whose Event at that Venue has ended. Your `event.ended`, with `venueId` and `promoterId`, already tells you that, and it matches what the professor told us, that Promoters review Venues. If anyone may rate, a Venue Manager could rate their own Venue.
3. We'll use it. We keep a copy of each Venue's Rating for our search filter, and refresh it by calling your GET for every Venue every five minutes. Three questions:
   - What does it answer for a Venue with no reviews: `404`, or a `count` of 0?
   - We'd call you directly, not through the Gateway, with the header `X-Service-Name: places`, as Events and Tickets call us. Does that work for you?
   - Optional: could you add one call that returns the Ratings of many Venues, such as all of them, or those changed since a given time? Then each refresh is one call instead of one per Venue.
