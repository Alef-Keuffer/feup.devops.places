# Places publishes *Booking confirmed*; Billing creates the bill

When a Booking is confirmed, Places publishes a *Booking confirmed* message on the broker carrying the Booking, Event, Promoter, Venue, Venue Manager, the booked days and the amount (days × the Venue's price per day). Billing (G3) turns it into the bill; Places never creates bills itself. The professor expects Places to "emit a billing", and this message is how it does: it carries everything a bill needs, including the amount, which only Places can compute because it owns the price.

## Considered options

- **Places calls Billing's REST API to create the bill.** Rejected: a Booking request would then succeed only while Billing is up, and a call that fails after the Booking is saved leaves a Booking with no bill, the failure ADR-0006 exists to prevent. Each synchronous call to another service while handling a request lowers that operation's availability (Richardson, *Microservices Patterns* §3.4.1).
- **Places publishes a *Bill issued* message.** Rejected: a bill is Billing's concept, so Places would be modelling another group's domain, and the message would serve only G3.
- **Places publishes *Booking confirmed* (chosen).** It states a fact about Places' own domain, so one message serves every group that needs it: Billing bills from it, and Reviews (G1) learns which Promoter booked which Venue, which it needs because only that Promoter may rate the Venue. Reviews keeps its own copy instead of calling Places at runtime, the same trade we made for Ratings in ADR-0002.

## Consequences

- Billing also consumes *Booking cancelled*: it cancels the Booking's bill if the Promoter hasn't paid it yet, and refunds no paid bill, whoever cancelled the Booking. G3 told us this on 2026-11-16 and calls it deliberate for delivery 1 (`docs/groups/2026-11-16-g3-to-g5.md`), replacing our earlier assumption that Billing ignores cancellations. A Promoter whose Booking the Venue Manager cancels after they paid loses the amount.
- The Booking request from Events must carry the Promoter's user id, the value the Gateway forwards as `X-User-Id`: Billing compares it with `X-User-Id` to check that the person paying a bill is its Promoter (`docs/groups/2026-11-16-g3-to-g5.md`). G2 has still to agree to send that id rather than the id of its own Promoter entity.
