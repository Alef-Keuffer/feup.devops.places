<!-- Continues "Service APIs and collaborations" from 4a-service-apis-rest.md; split so both halves can be written in parallel. -->

## Messaging and collaborations

Besides its REST API, Places talks to the other groups through messages on the broker that G4 runs. Richardson describes such an asynchronous API by its message channels, its message types and their formats [@richardson2018, sec. 3.3.3]. This section does that for the three messages Places publishes or consumes, justifies what they carry and why Places reads Ratings from Reviews over REST instead, explains how their delivery stays reliable, and ends with a diagram of every flow, REST and broker, between Places and the other groups.

### Messages

All three are what Richardson calls *event* messages: each states that something has happened in the domain of the group that sends it, and the sender doesn't need to know who acts on it [@richardson2018, sec. 3.3.1]. Each goes on a publish-subscribe channel, so every group that subscribes gets its own copy. Places publishes on a channel of its own, the *Places topic*: a durable topic exchange named `places`, on which each message's routing key is its type, `BookingConfirmed` or `BookingCancelled`, so that a consumer binds only to the types it handles. It reads *Event cancelled* from the *Log topic*, G2's durable topic exchange `events`, on which Promoters and Events (G2) publishes its Event messages with each message's type as its routing key (L4). G3 tells us that G4 runs RabbitMQ, which question L7 asks G4 to confirm.

Messages are JSON, a text format every group's stack can read and write [@richardson2018, sec. 3.1.4], and follow the conventions of NFR-9 that the REST API section proposes (Table \ref{tab:conventions}): UUIDs for ids, ISO 8601 for dates and times, whole days in the Europe/Lisbon time zone, and amounts in EUR as decimal strings with two decimals. Each has a `type` field naming the message, so that a consumer can tell the messages on a channel apart without relying on the routing key. Every message Places sends carries the Booking id (NFR-6).

Places reads only the fields it needs from a message, and ignores any others, along with messages of types it doesn't handle, such as *Event scheduled* on the Log topic (FR-27). This is the Robustness principle Richardson recommends for evolving an API [@richardson2018, sec. 3.1.3]. We ask the consumers of Places' messages to read them the same way, so that Places can add a field without breaking them.

#### *Booking confirmed* {.unnumbered .unlisted}

Channel
:   The Places topic.

Producer
:   Places, from `requestBooking`.

Consumers
:   Billing (G3), which creates the bill for the Booking, and for a Rebooking carries a paid bill over from the Booking it replaces.

Sent when
:   Places has created a Booking (FR-24). Places saves the message with the Booking and publishes it shortly after, as Reliable delivery below explains.

| Field | Type | Meaning |
|------------------|-----------|---------------------------------------------------------------|
| `type` | string | `BookingConfirmed`. |
| `bookingId` | UUID | The Booking. Consumers drop a second message with the same Booking id. |
| `eventId` | UUID | The Event the Venue is booked for. |
| `promoterId` | UUID | The Event's Promoter, whom Billing bills, by user id: the value the Gateway forwards as `X-User-Id` (Table \ref{tab:identity}). |
| `venueId` | UUID | The Venue booked. |
| `venueManagerId` | UUID | The Venue's Venue Manager. Billing stores it on each bill, for paying the Venue Manager in a later delivery. |
| `firstDay` | date | The first day of the Booking. |
| `lastDay` | date | The last day of the Booking, included. |
| `amount` | string | The number of days × the Venue's price per day when the Booking was created (FR-22): an amount in EUR as a decimal string with two decimals, such as `"800.00"`. |
| `replacesBookingId` | UUID | For a Rebooking, the Booking it replaces; left out otherwise. Billing reads it to carry a paid bill over to the new Booking, so that a Promoter who postpones doesn't pay twice. |

: The fields of *Booking confirmed*. \label{tab:booking-confirmed}

#### *Booking cancelled* {.unnumbered .unlisted}

Channel
:   The Places topic.

Producer
:   Places, from `cancelBooking`, `cancelVenueBooking`, `handleEventCancelled`, and `requestBooking` for the Booking a Rebooking replaces.

Consumers
:   Events (G2), which matches the message to its Event by `bookingId` and ignores it when `cancelledBy` is `events`; when the Venue Manager cancelled, this message is the only way Events learns that its Event no longer has the Venue (L15). Billing (G3), which cancels the Booking's bill if the Promoter hasn't paid it yet.

Sent when
:   Places has cancelled a Booking, whoever cancelled it (FR-32).

| Field | Type | Meaning |
|------------------|-----------|---------------------------------------------------------------|
| `type` | string | `BookingCancelled`. |
| `bookingId` | UUID | The Booking cancelled. |
| `eventId` | UUID | The Event that held it. |
| `promoterId` | UUID | The Event's Promoter, by user id. |
| `venueId` | UUID | The Venue that was booked. |
| `cancelledBy` | string | `events` when Events cancelled it, with a Booking cancellation, a Rebooking or through *Event cancelled*; `venue-manager` when the Venue's Venue Manager did. `events` is Events' `X-Service-Name` (Table \ref{tab:identity}). |
| `reason` | string | The reason given, left out when none was. |

: The fields of *Booking cancelled*. \label{tab:booking-cancelled}

#### *Event cancelled* {.unnumbered .unlisted}

Channel
:   The Log topic.

Producer
:   Promoters and Events (G2).

Consumers
:   Places, which runs `handleEventCancelled` (FR-26), and any other group that subscribes.

Sent when
:   An Event is cancelled. G2 also publishes *Event scheduled* and other messages on the Log topic, which Places ignores (FR-27).

G2 designs this message, so the table lists only the fields Places relies on. Its routing key on the Log topic is its type, `EventCancelled` (L4).

| Field | Type | Meaning |
|------------------|-----------|---------------------------------------------------------------|
| `type` | string | `EventCancelled`. |
| `eventId` | UUID | The cancelled Event: the same id Events sent in its Booking request. |

: The fields of *Event cancelled* that Places reads. \label{tab:event-cancelled}

### Why these messages and calls

#### Places keeps a copy of each Venue's Rating {.unnumbered .unlisted}

Reviews computes each Venue's Rating, and Places needs it for the minimum Rating filter of search (FR-11, FR-14) and to return with the Venue (FR-10). We considered three options.

- **Ask Reviews for the Ratings on each search.** Rejected. A search with a minimum Rating would find the Venues that match its other filters, ask Reviews for the Rating of each, and drop those below the minimum in memory, so the filter couldn't be part of the SQL query that does the rest of the search. Every such search would wait on a call to Reviews, which puts the 2-second target of NFR-1 at risk, and would fail while Reviews is down, against NFR-7. Richardson's point is general: each synchronous call to another service while handling a request lowers the availability of the operation [@richardson2018, sec. 3.4.1].
- **Keep a copy, updated from a *Rating changed* message.** Rejected, though it was our first choice. Richardson's remedy is for a service to replicate the data it needs from another service, kept up to date by the events that service publishes [@richardson2018, sec. 3.4.2]. That needs Reviews to publish the message. G1 first declined, then said it might, pending a decision within its group, once it had agreed to return every Venue's Rating in one call. We told G1 that call is enough (L6). A refresh is one call every five minutes, and it corrects itself: each refresh reads every Rating again, so an answer that failed or was saved out of order is put right by the next one. A lost message, by contrast, would leave a Venue's Rating wrong until its next review, unless Reviews sent its messages as reliably as Places does through its outbox (Reliable delivery below), which we can't require of G1. All the message would add is freshness.
- **Keep a copy, refreshed from Reviews' REST API (chosen).** Places keeps the copy and keeps it up to date by asking Reviews for every Venue's Rating, in one call every five minutes. Places then answers every search and `getVenue` from its own database, whether Reviews is up or not, and the minimum Rating filter stays in the SQL query. The cost is that a Venue's Rating can lag behind its latest review by up to five minutes, which matters little for a search filter, and that a Venue has no Rating until a refresh reads one for it, and loses it when Reviews no longer lists the Venue (FR-14).

#### Refreshing the Ratings {.unnumbered .unlisted}

Every five minutes, Places runs `refreshRatings`, which makes one call, Reviews' `GET /api/v1/ratings/venues`. The answer lists the `venueId`, `average`, `count` and `stampedAt` of every Venue with at least one review, and Places saves each entry's `average` and `stampedAt` as that Venue's Rating, whether the Venue is Listed or Unlisted (FR-33). A Venue missing from the answer has no reviews, including one whose last review was removed by its author or by an administrator of Reviews. It loses the Rating it holds, and a search with a minimum Rating leaves it out (FR-14). When Reviews doesn't answer, every Venue keeps the Rating it holds until the next refresh, and search goes on using it (NFR-7).

Two refreshes can overlap, when several copies of Places run or a refresh takes longer than five minutes, and the answer Reviews gave first could then be saved last, replacing a newer Rating with an older one, or clearing it. So Places replaces the Rating it holds only with one stamped no earlier (FR-34). A Venue missing from the answer has no `stampedAt`, so Places compares its Rating with the answer's `Date` header instead: the time Reviews sent the answer, which a server with a clock must send on every successful answer [@rfc9110, sec. 6.6.1]. Places clears only a Rating stamped no later. Every stamp comes from Reviews' clock, so the rule doesn't depend on Places' clock agreeing with Reviews'. Places applies the rule with two statements, the first run for each entry in the answer, which also change nothing for a Venue removed in the meantime:

```sql
-- each Venue in the answer
UPDATE venue
SET    rating_average = :average, rating_stamped_at = :stamped_at
WHERE  id = :venue_id
AND    (rating_stamped_at IS NULL OR rating_stamped_at <= :stamped_at);

-- every Venue missing from the answer
UPDATE venue
SET    rating_average = NULL, rating_stamped_at = NULL
WHERE  id <> ALL (:answer_venue_ids)
AND    rating_stamped_at <= :answer_date;
```

When two copies of Places run these for one Venue at once, the second waits for the first to commit, then checks its `WHERE` clause against the Rating the first wrote [@postgresql-isolation, sec. 13.2.1], so an older answer saved last can't replace a newer Rating or clear it. Two cases slip through, and the next refresh puts both right. `Date` counts whole seconds [@rfc9110, sec. 5.6.7], so a clearing within a second of a Rating's stamp can be refused or let through wrongly. And a Venue cleared by a newer answer has no Rating, so an older answer saved after it gives the Venue its old Rating back.

#### Billing creates the bill from *Booking confirmed* {.unnumbered .unlisted}

The professor expects Places to emit a billing for each Booking: something that lets Billing (G3) bill the Promoter. We considered three ways.

- **Places calls Billing's REST API to create the bill.** Rejected. `requestBooking` would then succeed only while Billing is up, the loss of availability Richardson warns of [@richardson2018, sec. 3.4.1]. A call that failed after the Booking was saved would leave a Booking with no bill, the failure the transactional outbox below exists to prevent.
- **Places publishes *Bill issued*.** Rejected. A bill is Billing's concept, so Places would be modelling another group's domain, and the message would serve only Billing.
- **Places publishes *Booking confirmed*, and Billing creates the bill (chosen).** The message states a fact in Places' own domain, so it serves any group that needs that fact, not only Billing. It carries everything a bill needs, the Promoter, the days and the amount, so Billing never has to call Places back; Richardson calls this *event enrichment* [@richardson2018, sec. 5.3]. Places computes the amount because only Places knows the Venue's price per day, and fixes it when the Booking is created (FR-22).

When *Booking cancelled* arrives, Billing cancels the Booking's bill if the Promoter hasn't paid it yet, and refunds no paid bill, whoever cancelled the Booking. G3 has told us this is deliberate for delivery 1. The Open points section says what it means when a Venue Manager cancels.

A Rebooking publishes *Booking cancelled* (`cancelledBy: events`) for the old Booking, then *Booking confirmed* for the new one, both written to the outbox in the transaction that replaces the Booking. Without a link between them, Billing would cancel the old bill only if it were unpaid and bill the new Booking in full, so a Promoter who paid and then postponed would pay twice. *Booking confirmed* therefore carries `replacesBookingId`, and G3 has told us that Billing reads it and carries the old Booking's paid bill over to the new Booking.

### Reliable delivery

We assume the broker delivers each message at least once: it keeps a message until the consumer acknowledges it, and delivers it again if no acknowledgement comes, for instance because the consumer stopped while handling it. No message is lost, but one can arrive twice, and a redelivered message can arrive after messages sent later. G3 tells us that G4 runs RabbitMQ, and question L7 asks G4 to confirm it. We propose to every group how to get at-least-once delivery from it. A publisher sends persistent messages and waits for the broker to confirm each one, which RabbitMQ does for a durable queue only once the message is on disk. A consumer reads from a durable queue of its own and acknowledges a message only after handling it, so that RabbitMQ requeues any message whose consumer stops before acknowledging it [@rabbitmq-confirms]. RabbitMQ also confirms a message that matches no queue, and keeps it nowhere, so each consumer must bind its queue before the first message it needs is sent. Nothing below depends on more than at-least-once delivery. Reliability then has two sides: Places must get each of its messages to the broker (NFR-4), and every consumer, Places included, must cope with receiving a message twice (NFR-5, NFR-6).

#### Publishing through a transactional outbox {.unnumbered .unlisted}

When a command creates or cancels a Booking, its message must reach the broker exactly when the change is saved. We considered three ways.

- **Publish to the broker after the commit.** Rejected. If Places stops between committing a Booking and publishing *Booking confirmed*, the message is lost and Billing never bills the Booking. Publishing before the commit fails the other way: if the commit then fails, Billing bills a Booking that doesn't exist.
- **One distributed transaction across the database and the broker.** Rejected. A two-phase commit would make the two writes atomic, but many brokers don't support it, and Richardson advises against distributed transactions for modern applications [@richardson2018, sec. 3.3.7].
- **A transactional outbox with a polling relay (chosen).** The command writes the message as a row of an *outbox* table in the same database transaction that saves the change, so the row exists exactly when the change does. A relay then reads the rows and publishes them. These are Richardson's Transactional outbox and Polling publisher patterns [@richardson2018, sec. 3.3.7], and they need nothing beyond Places' own PostgreSQL database. His other relay, Transaction log tailing, reads the rows from the database's transaction log instead of polling for them; it saves the polling queries but adds a tool such as Debezium to run, and at Places' load polling costs little.

The relay runs inside Places. Every second it reads the outbox rows not yet sent, in the order they were inserted, publishes each to the Places topic, and marks a row as sent once the broker has accepted it. If the broker refuses a row, the relay stops there and tries again a second later. Three details matter.

1. If Places stops after the broker accepts a message but before the row is marked, the relay publishes the message again when Places restarts. This is how Places itself can send a message twice, and why consumers deduplicate.
2. The relay marks each row rather than remembering the last row it sent. Rows are numbered as they are inserted, but transactions can commit in a different order, so a row can appear after a row with a higher number has been sent. A relay that only looked past the highest number it had sent would skip it.
3. If several copies of Places run, only one of them runs the relay at a time. A Booking's *Booking confirmed* then always leaves before its *Booking cancelled*.

The relay adds up to a second between a change and its message. Billing doesn't need the message sooner, and Events doesn't wait for it: it learns the result of its own Booking requests and cancellations from Places' REST answers.

#### Consumers deduplicate by Booking id {.unnumbered .unlisted}

Richardson gives a consumer two ways to cope with a duplicate: make its handler idempotent, so that handling a message twice has the effect of handling it once, or record the ids of the messages it has handled and discard those it sees again [@richardson2018, sec. 3.3.6]. A Booking is confirmed once and cancelled at most once, so a message's type and Booking id identify it, and consumers need no separate message id. We ask each consumer to key what it keeps on the Booking id, and G3 has adopted this for Billing.

- **Billing** keeps one bill per Booking id, so a second *Booking confirmed* for a Booking creates nothing, and cancelling a cancelled bill changes nothing. If *Booking cancelled* arrives for a Booking with no bill, Billing records the Booking as cancelled, and a later *Booking confirmed* for it creates no bill, so Billing never bills a Booking that no longer exists.
- **Events** reads *Booking cancelled* as news about the Booking it names, not about the Event. Keyed on the Event, a duplicate would do harm: a Rebooking replaces an Event's Booking with a new one (US-4), and a late copy of the first Booking's *Booking cancelled* would then seem to cancel the new one. Keyed on the Booking id, the copy matches no Booking Events holds, and changes nothing.

#### Places' handlers are safe to run twice {.unnumbered .unlisted}

Places takes the first of Richardson's two ways: its only handler, `handleEventCancelled`, is idempotent (NFR-5), so Places keeps no table of the messages it has handled and doesn't depend on G2 giving its messages unique ids. Places acknowledges a message only after the transaction that handles it has committed, so if Places stops while handling one, the broker delivers it again rather than losing it.

- **`handleEventCancelled`** removes the Event's Booking, if it has one that hasn't ended, and queues *Booking cancelled*, in one transaction. A second delivery finds no Booking and does nothing. The removal is a single `DELETE`, so if two copies of Places handle the same message at once, or Events cancels the same Booking over REST at that moment, the second `DELETE` waits for the first to commit, finds the row gone, and removes nothing [@postgresql-isolation, sec. 13.2.1]. Only one *Booking cancelled* is queued per Booking, whichever way it was cancelled.

### Collaborations

Figure \ref{fig:collaborations} draws every flow between Places and the other groups, and Table \ref{tab:flows} says what each carries and why it is a REST call or a message. A flow is a synchronous REST call when the caller needs the answer before it can go on. It goes through the broker when the sender only states a fact, which any number of groups may act on in their own time. Messages also keep each group's availability its own: Places books Venues while Billing is down, and its messages wait on the broker [@richardson2018, sec. 3.4].

```{=latex}
\begin{figure}[htbp]
\centering
\begin{tikzpicture}[
    box/.style={draw, rounded corners, align=center, minimum width=2cm, minimum height=0.9cm, font=\small},
    system/.style={box, very thick, font=\small\bfseries},
    channel/.style={draw, align=center, minimum width=2cm, minimum height=0.7cm, font=\small},
    rest/.style={-{Stealth[length=2.4mm]}},
    msg/.style={-{Stealth[length=2.4mm]}, dashed},
    num/.style={draw, solid, rounded corners=2pt, fill=white, inner sep=1.5pt, font=\scriptsize}]
  \node[system] (places) at (0,0) {Places\\(G5)};
  \node[box] (gateway) at (-3.2,0) {Gateway\\(G4)};
  \node[box] (promoter) at (-6.2,1) {Promoter};
  \node[box] (manager) at (-6.2,-1) {Venue\\Manager};
  \node[box] (tickets) at (0,-3) {Tickets\\(G3)};
  \node[channel] (log) at (3.3,1.7) {Log topic};
  \node[channel] (ptopic) at (3.3,0) {Places topic};
  \node[draw, dotted, inner sep=7pt, fit=(log) (ptopic), label={[font=\scriptsize]above:Message broker (G4)}] {};
  \node[box] (events) at (6.6,2.4) {Events\\(G2)};
  \node[box] (billing) at (6.6,0) {Billing\\(G3)};
  \node[box] (reviews) at (3.3,-2.2) {Reviews\\(G1)};

  \draw[rest] (promoter.east) -- node[num] {1} (gateway.north west);
  \draw[rest] (manager.east) -- node[num] {1} (gateway.south west);
  \draw[rest] (gateway) -- node[num] {1} (places);
  \draw[rest] (events.north) -- ++(0,0.6) -| node[num, pos=0.25] {2} (places.north);
  \draw[rest] (tickets) -- node[num] {3} (places);
  \draw[rest] (places.south east) -- node[num] {5} (reviews.west);

  \draw[msg] (events.west) -- node[num, pos=0.4] {4} (log.east);
  \draw[msg] (log.west) -- node[num] {4} (places.north east);
  \draw[msg] (places) -- node[num, pos=0.4] {6, 7} (ptopic);
  \draw[msg] (ptopic.east) -- node[num, pos=0.6] {6, 7} (billing);
  \draw[msg] (ptopic.east) -- node[num, pos=0.6] {7} (events.south west);
\end{tikzpicture}
\caption{Collaborations between Places and the other groups. Solid arrows are synchronous REST calls, from the caller to the service it calls. Dashed arrows are messages, from the producer to a channel on the broker and from the channel to each consumer. The numbers refer to Table \ref{tab:flows}.}
\label{fig:collaborations}
\end{figure}
```

| # | Flow | What it carries | Why REST or the broker |
|----|---------------------------|-------------------------------------|--------------------------------------|
| 1 | Promoter or Venue Manager → Gateway → Places | Every user request, with the user id the Gateway forwards: searches, reading a Venue, availability checks, Venue changes, a Venue's Bookings and their cancellation. | REST. A user waits for the answer. |
| 2 | Events → Places | Venues (`searchVenues`, `getVenue`), Booking requests (`requestBooking`) and Booking cancellations (`cancelBooking`). | REST. Events needs each answer before it goes on, for the reasons the REST API section gives. |
| 3 | Tickets → Places | A Venue by its id (`getVenue`), for its name and address. | REST. Tickets reads them once per Event, when Events publishes the Event, and Places publishes no messages about Venues that Tickets could keep a copy from. |
| 4 | Events → Log topic → Places | *Event cancelled* (`handleEventCancelled`). | Broker. Events states the fact once for every group that cares, and needs no answer. |
| 5 | Places → Reviews | Every Venue's Rating, in one call every five minutes (`refreshRatings`). | REST. Each refresh reads every Rating again, so a refresh that fails is put right by the next. Places keeps a copy of the Rating, so search doesn't call Reviews. |
| 6 | Places → Places topic → Billing | *Booking confirmed* (`requestBooking`). | Broker. A Booking doesn't wait for Billing, and any other group that needs the fact can subscribe. |
| 7 | Places → Places topic → Events, Billing | *Booking cancelled* (`cancelBooking`, `cancelVenueBooking`, `handleEventCancelled`, and `requestBooking` for a Rebooking). | Broker. One message serves both groups, and it tells Events of a Venue Manager's cancellation without Events asking. Events consumes it and matches it by `bookingId`. |

: The flows of Figure \ref{fig:collaborations}. \label{tab:flows}

Events and Tickets, in flows 2 and 3, call Places directly rather than through the Gateway, and name themselves with the `X-Service-Name` header (Table \ref{tab:identity}). Places calls Reviews the same way in flow 5, as `places`, which G1 accepts, since its Rating calls only read (L13).
G3 has confirmed that Tickets reads a Venue with a REST GET.
