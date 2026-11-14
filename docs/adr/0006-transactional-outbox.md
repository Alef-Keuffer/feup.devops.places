# Places publishes its messages through a transactional outbox

Places writes each outgoing *Booking confirmed* and *Booking cancelled* message to an outbox table in the same database transaction that creates or cancels the Booking. A relay then polls the table and publishes the rows to the broker. Without this, Places could save a Booking and crash before publishing *Booking confirmed*. Billing creates the bill only from that message (ADR-0004), so the bill would never exist. The same failure on *Booking cancelled* would leave Events believing its Event still has a Venue. This is the Transactional outbox pattern, with a Polling publisher as the relay (Richardson, *Microservices Patterns* ch. 3).

## Considered options

- **Publish right after the commit.** Rejected: a crash between the commit and the publish loses the message.
- **One distributed transaction across the database and the broker (2PC).** Rejected: most brokers don't support it, and Richardson advises against 2PC for microservices.
- **Transactional outbox with a polling relay (chosen).** It needs nothing beyond our own PostgreSQL. Tailing the transaction log would avoid polling but adds a tool such as Debezium.

## Consequences

- The relay can publish a message twice if it crashes after publishing but before marking the row as sent. Consumers deduplicate by Booking id, which fits the at-least-once delivery we already assume.
