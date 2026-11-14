# Places is one service, not separate catalogue and Booking services

Places is deployed as a single service that owns the Venue catalogue, the Bookings and the cached Ratings in one database. The obvious split was a Venue Catalogue service (Venues, Rooms, Listed/Unlisted) and a Booking service (Bookings, availability, *Booking confirmed*). We rejected it because three of our decisions need Venues and Bookings in the same transaction or the same query.

## Considered options

- **Venue Catalogue + Booking services.** Rejected. Measured against decisions already made, the split costs:

  | Decision | One service | Catalogue + Booking |
  |---|---|---|
  | A Booking request checks that the Venue is Listed and reads its price per day for the amount on *Booking confirmed* (ADR-0004) | One transaction | A call to Catalogue on every Booking, or a message-fed copy of every Venue inside the Booking service |
  | Deleting a Venue is refused while it has future Bookings | One transaction | Catalogue asks Booking, and a Booking can still arrive between the check and the delete: the race ADR-0001 exists to prevent |
  | Search combines catalogue filters with "N consecutive free days" | One SQL query | A third read model (CQRS, Richardson, *Microservices Patterns* ch. 7) or two calls merged in memory, which puts the 2-second p95 target at risk |

- **One service (chosen).** What a split would buy (independent scaling, independent deploys, separate team ownership) doesn't apply here: one team of five owns Places, load is low, and both halves change together, because a Venue's fields drive both search and the amount on *Booking confirmed*. Richardson's Common Closure Principle (*Microservices Patterns* §2.2.4) puts things that change together in one service, and Newman (*Building Microservices*) advises starting with fewer, larger services and splitting only when there is a concrete reason.

## Consequences

- In a microservices course, a reader may expect each subsystem to show several services. The table above is the argument to defend.
