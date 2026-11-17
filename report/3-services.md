# Services

Richardson's second step identifies the services and assigns the system operations to them [@richardson2019, secs. 2.2.2–2.2.4]. The course has already made the first cut: giving each group one subsystem of the Event Management system is a decomposition by business capability [@richardson2019, sec. 2.2.2], and Places is group 5's. This section settles what is left inside Places: how many services it is, which data it owns and which it leaves to other groups, and how it keeps its data. Places is one service. It owns the Venue catalogue, the Bookings and the Ratings, and keeps them in a private PostgreSQL database that enforces both invariants of the domain model.

## Places is one service

Places is built and deployed as one service, with all fifteen operations of Table \ref{tab:operations} and one database (NFR-12). The obvious alternative splits it along its two subdomains [@richardson2019, sec. 2.2.3]:

- a *Venue Catalogue* service, with the Venues, their Rooms, whether each is Listed, and its Rating: `submitVenue`, `updateVenue`, `unlistVenue`, `relistVenue`, `deleteVenue`, `getVenue` and `refreshRatings`;
- a *Booking* service, with the Bookings, availability and the messages about Bookings: `requestBooking`, `cancelBooking`, `cancelVenueBooking`, `listVenueBookings`, `findEventBooking`, `checkAvailability` and `handleEventCancelled`.

`searchVenues` fits in neither, because it filters on a Venue's details and on its free days at once. We rejected the split because several operations need Venues and Bookings in one transaction or one query. Table \ref{tab:split} compares what they cost in each design.

| What the operation needs | One service | Venue Catalogue + Booking |
|------------------------------|----------------|----------------------------------------|
| `requestBooking` checks that the Venue is Listed and reads its price per day and its Venue Manager, for the amount and *Booking confirmed* (FR-17, FR-22, FR-24). `listVenueBookings` and `cancelVenueBooking` check that the caller is the Venue's Venue Manager (FR-36). | One transaction reads the Venue and writes the Booking. | The Booking service calls the Catalogue service on each of these requests, so no Booking can be made while the Catalogue service is down. Or it keeps a copy of every Venue, fed by the Catalogue service's messages; the copy lags, so it can accept a request for a Venue that was just unlisted (FR-8) or price it at the old price (FR-22). |
| `deleteVenue` is refused while the Venue has a Booking that has not ended (FR-9). | One transaction checks the Bookings and removes the Venue. | The Catalogue service asks the Booking service, and a Booking can still arrive between the answer and the removal: the race that Places owning the Bookings exists to prevent. Closing it takes a saga, with countermeasures for a saga's lack of isolation [@richardson2019, ch. 4]. |
| `searchVenues` combines filters on the Venue's details with *N* consecutive free days (FR-11, FR-12). | One SQL query. | A third service holding a CQRS view of both, which lags behind them and so breaks NFR-2; or API composition, two calls whose results are merged in memory [@richardson2019, ch. 7], which puts the 2-second target of NFR-1 at risk. |

: What the operations that need both Venues and Bookings cost in one service and in two. \label{tab:split}

The split runs into four of the obstacles Richardson lists for decomposing an application: network latency, availability lost to synchronous calls, keeping data consistent across services, and obtaining a consistent view of the data [@richardson2019, sec. 2.2.5]. In return it would buy four of the advantages Newman gives for microservices: scaling each part on its own, containing a failure in one part, deploying each part on its own, and aligning each with its own team [@newman2021, ch. 1]. None of them applies to Places:

- **Scaling.** The load is low: NFR-1 assumes 20 requests per second over 1,000 Venues, our own assumption, since no group has stated an expected load. Neither half needs to scale apart from the other, and Newman notes that running more copies of one service behind a load balancer is often a simpler way to scale than splitting it [@newman2021, ch. 3].
- **Robustness.** A service boundary can stop a failure from spreading, so the rest of the system carries on [@newman2021, ch. 1]. This boundary wouldn't: the Booking service depends on the Catalogue service for every Booking, as Table \ref{tab:split} shows, so when the Catalogue service fails, Bookings either stop or go on from a stale copy of the Venues.
- **Deployment and teams.** One team of five builds Places, so the two services would be deployed by the same people, mostly together. Richardson's measure of a well-sized service is one that a small team can develop with little lead time and little collaboration with other teams [@richardson2019, sec. 2.1.3]^["A much better goal is to define a well-designed service to be a service capable of being developed by a small team with minimal lead time and with minimal collaboration with other teams." (p. 43)], and Places as one service meets it.
- **Change.** The two halves change together, because a Venue's details drive both search and the amount on *Booking confirmed*. Hourly or seasonal pricing, out of scope today, would change the Venue's prices, the amount `requestBooking` sets and the price filter of `searchVenues` at once. Richardson's Common Closure Principle puts what changes for the same reason in the same service [@richardson2019, sec. 2.2.4]. His other guideline, the Single Responsibility Principle, doesn't argue for the split either: every operation serves one responsibility, which Venue can be booked on which days.

Newman asks for a goal before splitting a system: microservices are a means to an outcome, not the outcome [@newman2021, ch. 3]. He advises drawing boundaries around larger, coarser-grained contexts first, and subdividing them only when the benefits of the finer split are wanted [@newman2021, ch. 2]. We want none of them yet. A reader may expect a subsystem in a microservices course to show several services, and Table \ref{tab:split} is our answer. If one of the advantages above comes to apply, for instance search load far above Booking load, or a second team taking over the catalogue, this split is the first candidate, and the table lists what it would then cost.

## What Places owns

A microservice owns its data and decides what of it to share; other services get that data from the microservice, never from its database [@newman2021, ch. 1]. Table \ref{tab:ownership} lists the data Places works with, the group it belongs to, and what Places holds of it. Of other groups' data, Places keeps only ids, as the domain model shows, and the Rating, which Places reads from Reviews.

| Data | Belongs to | What Places holds or does |
|------------------------|---------------------|------------------------------------------------|
| Venues, their Rooms and details, Listed or Unlisted | Places | The source of truth. Other groups read a Venue by its id. |
| Bookings, and so availability | Places | The source of truth. Events asks for a Booking, and Places accepts or rejects it. |
| Rating | Places, as a copy of the average Reviews computes | Each Venue's Rating as Places last read it from Reviews, every five minutes, so that search never calls Reviews. The Messaging and collaborations section gives the reasons. |
| Users and authentication | Users and the Gateway (G4) | Each Venue's Venue Manager by user id. Places trusts the user id the Gateway forwards with each request. |
| Events | Promoters and Events (G2) | The Event id and Promoter id on each Booking, taken from Events' Booking request. |
| Bills | Billing (G3) | Nothing. Places publishes *Booking confirmed* with the amount, and Billing creates the bill; on *Booking cancelled*, Billing cancels the bill if it is unpaid. |
| Tickets | Tickets (G3) | Nothing. Tickets reads a Venue's name and address from Places. |
| Reviews, and who may rate a Venue | Reviews (G1) | Nothing. Reviews decides who may rate a Venue without Places' messages. |
| Refunds and cancellation fees | Billing (G3) | Nothing. For delivery 1, Billing refunds no paid bill and charges no fee, whoever cancelled the Booking. |

: The data Places works with and the group each belongs to. \label{tab:ownership}

## Where the Bookings live

Events asks Places to book a Venue with a Booking request, and Places accepts it or rejects it as a conflict (FR-16, FR-18). We considered two options for where the Bookings live.

- **Events keeps the Bookings, and Places asks it.** Rejected. Places would work out a Venue's availability by asking Events which Events hold the Venue on which days. Two Booking requests for the same Venue and days can arrive at the same moment, and only the service that holds the Venue's calendar can serialise them, so that one succeeds and the other is a conflict. With the calendar in Events, Places can't, and a Venue can be booked twice (NFR-3). Search and availability checks would also call Events at runtime, so they would stop while Events is down (NFR-7), which is Richardson's warning that synchronous calls between services reduce availability [@richardson2019, sec. 2.2.5]. And Places couldn't promise that the availability checks after a change reflect it (NFR-2), because the change would be made in another group's service.
- **Places keeps the Bookings (chosen).** A Venue is available when no Booking overlaps the requested days, and Places answers that from its own data. Both invariants of the domain model then constrain only data that Places holds, so Places' own database can enforce them.

## A private database with an exclusion constraint

Places keeps its data in its own PostgreSQL database, which no other service reads or writes (NFR-11). This is Richardson's Database per service pattern: a service keeps its data private, like the fields of a class, so that its team can change the schema without coordinating with other teams, and so that no other service can, for example, hold database locks that block it [@richardson2019, sec. 2.1.3]. Newman makes the same point: services that share a database are coupled through it, so a change to one can break the other [@newman2021, ch. 2]. Other groups depend only on Places' REST API and messages, which the Service APIs and collaborations section describes, and not on its tables. That matters here, because the five groups build their services at the same time. The database holds the Venues with their Rooms, the Bookings, the Ratings, and the outbox from which Places publishes its messages, which the Messaging and collaborations section explains.

The first invariant, that no two Bookings of one Venue overlap, has to hold even when Booking requests arrive together (NFR-3). Places can check for an overlap before it saves a Booking, or leave the database to refuse one. We considered four ways.

- **Check, then insert.** Rejected. Places would read the Venue's Bookings and insert the new one if none overlaps. At PostgreSQL's default isolation level, Read Committed, each statement sees the data committed when it starts [@postgresql-isolation, sec. 13.2.1], so two requests for overlapping days can both read before either inserts, both find the days free, and both insert. The stronger Repeatable Read level doesn't prevent this either [@postgresql-isolation, sec. 13.2.2].
- **Check, then insert, after locking the Venue.** Rejected, although it works. Each request first locks the Venue's row with `SELECT … FOR UPDATE`, so a second request for the same Venue waits until the first commits, and its check then sees the new Booking [@postgresql-isolation, sec. 13.2.3]. But the invariant then holds only as long as every piece of code that saves a Booking takes the lock first, and the database can't tell when one doesn't. Today only `requestBooking` saves Bookings; a later one, such as blocking days for maintenance, or a manual fix to the data, could forget.
- **Check, then insert, at the Serializable level.** Rejected, although it works. PostgreSQL aborts one of two transactions whose reads and writes conflict, so the second request fails and must be retried [@postgresql-isolation, sec. 13.2.3]. Every transaction that saves a Booking must then run at that level and retry on failure. It also aborts transactions that don't conflict: the database may track what a transaction has read for a whole table rather than row by row, so Bookings at two different Venues can abort each other [@postgresql-isolation, sec. 13.2.3].
- **An exclusion constraint (chosen).** PostgreSQL refuses a row that conflicts with an existing row on the columns and operators the constraint names, however many transactions try at once [@postgresql]. A constraint that compares the Venue for equality and the booked days for overlap is exactly the first invariant. The database then holds it for every write, from whatever code, with no lock to remember and no retry, and the request that loses the race gets the answer it should: a conflict (FR-18). This constraint is why Places uses PostgreSQL.

The second invariant, that an Event has at most one Booking (FR-19), is a unique constraint on the Event, for the same reason. The Booking table carries both:

```sql
CREATE EXTENSION btree_gist;  -- lets a GiST index compare uuids with =

CREATE TABLE booking (
    id        uuid PRIMARY KEY,
    venue_id  uuid NOT NULL,
    event_id  uuid NOT NULL UNIQUE,  -- second invariant
    days      daterange NOT NULL,    -- first to last day, both included
    -- the Promoter, the amount and other columns are left out
    EXCLUDE USING gist (venue_id WITH =, days WITH &&)  -- first invariant
);
```
