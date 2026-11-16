# Group 5 (Places) → Group 4 (Users, broker, Gateway)

## 1. What we need from you

**Routing user requests**

Forward users' requests for `/venues` and every path under it to Places. `/bookings` is only for Events, which calls us directly (see the endpoints in our report, section 4.1.1), so the Gateway doesn't need to route it.

**Identity headers** (our report, section 4.1.2)

You check the user's token; Places never sees it. On every request you forward, set:

- `X-User-Id`: the user's id.
- `X-User-Roles`: the user's roles, comma-separated: `promoter`, `venue-manager`, both, or none. We ignore any other role.

Set both for every user, with `X-User-Roles` empty for a user who has neither role: any user may search and read Venues, and we answer `401` to a request without both headers.

Before setting them, remove `X-User-Id`, `X-User-Roles` and `X-Service-Name` from whatever the user sent. We trust these headers without checking them, so users must reach Places only through the Gateway.

**The broker** (our report, section 4.2.3)

RabbitMQ, with the broker rule we sent to everyone. Places:

- declares the durable topic exchange `places`, and publishes `BookingConfirmed` and `BookingCancelled` there as persistent messages, waiting for the broker's confirmation;
- declares its own durable queue and binds it to G2's exchange for Event cancelled, declaring that exchange first, as the rule asks of every consumer, and acknowledges a message only after handling it.

So Places needs a RabbitMQ user that may declare `places`, G2's exchange and its own queue, bind its queue to G2's exchange, publish to `places`, and read its own queue. Every group that consumes needs the same on the exchanges it reads from.

## 2. What we send you

Nothing. Places calls none of your APIs, and you don't need any of our messages.

## 3. Questions

1. **Broker:** can you confirm you run RabbitMQ? Does the broker rule we sent to everyone work for you, or would you rather create the exchanges and queues yourselves?
2. **Headers:** is `X-User-Id` a UUID? Are the roles in `X-User-Roles` named `promoter` and `venue-manager`, and can you send it empty for a user with neither?
3. **Only way in:** can users reach Places only through the Gateway, and will the Gateway remove the three headers from whatever a user sends, as above?
