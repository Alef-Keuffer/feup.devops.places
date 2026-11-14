# Places publishes *Booking confirmed*; Billing creates the bill

When a Booking is confirmed, Places publishes a *Booking confirmed* message on the broker carrying the Booking, Event, Promoter, Venue, Venue Manager, the booked days and the amount (days × the Venue's price per day). Billing (G3) turns it into the bill; Places never creates bills itself. The professor expects Places to "emit a billing", and this message is how it does: it carries everything a bill needs, including the amount, which only Places can compute because it owns the price.

## Considered options

- **Places publishes a *Bill issued* message.** Rejected: a bill is Billing's concept, so Places would be modelling another group's domain, and the message would serve only G3.
- **Places publishes *Booking confirmed* (chosen).** It states a fact about Places' own domain, so one message serves every group that needs it: Billing bills from it, and Reviews (G1) learns which Promoter booked which Venue, which it needs because only that Promoter may rate the Venue. Reviews keeps its own copy instead of calling Places at runtime, the same trade we made for Ratings in ADR-0002.

## Consequences

- Cancellations are not billed or refunded. Places publishes *Booking cancelled* for other groups, and Billing ignores it, so a Promoter whose Booking the Venue Manager cancels still owes the amount. Refunds are a named gap.
- The Booking request from Events must carry the Promoter id.
