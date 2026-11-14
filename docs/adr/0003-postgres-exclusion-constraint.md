# Places has its own PostgreSQL database; overlapping Bookings are prevented by an exclusion constraint

Places owns a private PostgreSQL database (database per service), and no other service reads it directly. We chose Postgres so that a range exclusion constraint on (Venue, booked days) prevents double-booking even when requests arrive concurrently, which is what ADR-0001 depends on. The rest of the system reaches Places only through its REST API, documented in OpenAPI, and its broker messages.

## Considered options

- **Check, then insert, in application code.** Rejected. At Postgres's default isolation level, Read Committed, each statement sees the data committed when it starts, so two requests for overlapping days can both check before either inserts, and both insert. Repeatable Read doesn't prevent this either (PostgreSQL docs §13.2.1–13.2.2).
- **Check, then insert, after locking the Venue's row (`SELECT … FOR UPDATE`).** Rejected, although it works: a second request for the same Venue waits for the first to commit, then sees its Booking. The invariant then depends on every code path that saves a Booking taking the lock, and the database can't detect one that doesn't. Today only the Booking request saves Bookings, but a later path (blocking days for maintenance, open question L1) or a manual data fix could forget.
- **Check, then insert, at the Serializable isolation level.** Rejected, although it works: Postgres aborts one of two conflicting transactions with SQLSTATE 40001. Every transaction that saves a Booking must then run Serializable and retry on 40001 ("applications using this level must be prepared to retry transactions", §13.2.3). It also aborts transactions that don't conflict, because predicate locks can cover a whole table: "A sequential scan will always necessitate a relation-level predicate lock" (§13.2.3).
- **Exclusion constraint (chosen).** The database states the invariant and enforces it on every write, from any code path, with no lock discipline and no retry loop. A second overlapping insert waits for the first to commit and is then refused, and that refusal is the business answer: a conflict.

We ran each option on Postgres 18 (2026-11-14) with two concurrent sessions, A booking 9–10 June and B booking 10–11 June at the same Venue, each pausing 1 s between check and insert:

| Option | Result | Bookings saved |
|---|---|---|
| Check, then insert (Read Committed) | A and B both booked | 2 (double-booked) |
| Lock the Venue's row first | B waited, then saw A's Booking and was rejected | 1 |
| Serializable | B aborted with 40001, to be retried | 1 |
| Serializable, A and B at different Venues, no index | B aborted with 40001 though nothing conflicted | 1 (should be 2) |
| Exclusion constraint, no application check | B waited, then was refused by the constraint | 1 |

Sources: PostgreSQL 18 documentation, §13.2 Transaction Isolation (<https://www.postgresql.org/docs/18/transaction-iso.html>) and §5.5.6 Exclusion Constraints (<https://www.postgresql.org/docs/18/ddl-constraints.html#DDL-CONSTRAINTS-EXCLUSION>).

## Consequences

- The second invariant, that an Event has at most one Booking, is enforced the same way, by a unique constraint on the Booking's Event.
- A refusal by either constraint is a normal outcome of a Booking request, answered as a rejection, not an error to retry.
- Places depends on a Postgres feature (range types with a GiST exclusion constraint, via the `btree_gist` extension), so moving to another database would mean re-solving this.
