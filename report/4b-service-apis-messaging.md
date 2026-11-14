<!-- Continues "Service APIs and collaborations" from 4a-service-apis-rest.md; split so both halves can be written in parallel. -->

## Messaging and collaborations

Besides its REST API, Places talks to the other groups through messages on the broker that G4 runs. Richardson describes such an asynchronous API by its message channels, its message types and their formats [@richardson2018, sec. 3.3.3]. This section does that for the four messages Places publishes or consumes, justifies what they carry, explains how their delivery stays reliable, and ends with a diagram of every flow, REST and broker, between Places and the other groups.

### Messages

All four are what Richardson calls *event* messages: each states that something has happened in the domain of the group that sends it, and the sender doesn't need to know who acts on it [@richardson2018, sec. 3.3.1]. Each goes on a publish-subscribe channel, so every group that subscribes gets its own copy. Places publishes on a channel of its own, called the *Places topic* here. It reads *Event cancelled* from the *Log topic*, on which Promoters and Events (G2) publishes its Event messages, and *Rating changed* from a channel of Reviews (G1), called the *Reviews topic* here. G4 will name the channels and choose the broker.

Messages are JSON, a text format every group's stack can read and write [@richardson2018, sec. 3.1.4], and follow the conventions of NFR-9: UUIDs for ids, ISO 8601 for dates and times, whole days in the Europe/Lisbon time zone, and amounts in EUR. Each has a `type` field naming the message, so that a consumer can tell the messages on a channel apart without relying on a feature of a broker no one has chosen yet. Every message Places sends carries the Booking id (NFR-6).

Places reads only the fields it needs from a message, and ignores any others, along with messages of types it doesn't handle, such as *Event scheduled* on the Log topic (FR-27). This is the Robustness principle Richardson recommends for evolving an API [@richardson2018, sec. 3.1.3]. We ask the consumers of Places' messages to read them the same way, so that Places can add a field without breaking them.

#### *Booking confirmed* {.unnumbered .unlisted}

Channel
:   The Places topic.

Producer
:   Places, from `requestBooking`.

Consumers
:   Billing (G3), which creates the bill for the Booking, and Reviews (G1), which records that the Promoter booked the Venue.

Sent when
:   Places has created a Booking (FR-24). Places saves the message with the Booking and publishes it shortly after, as Reliable delivery below explains.

| Field | Type | Meaning |
|------------------|-----------|---------------------------------------------------------------|
| `type` | string | `BookingConfirmed`. |
| `bookingId` | UUID | The Booking. Consumers drop a second message with the same Booking id. |
| `eventId` | UUID | The Event the Venue is booked for. |
| `promoterId` | UUID | The Event's Promoter, whom Billing bills and who may rate the Venue. |
| `venueId` | UUID | The Venue booked. |
| `venueManagerId` | UUID | The Venue's Venue Manager. |
| `firstDay` | date | The first day of the Booking. |
| `lastDay` | date | The last day of the Booking, included. |
| `amount` | number | The number of days × the Venue's price per day when the Booking was created, in EUR (FR-22). |

: The fields of *Booking confirmed*. \label{tab:booking-confirmed}

#### *Booking cancelled* {.unnumbered .unlisted}

Channel
:   The Places topic.

Producer
:   Places, from `cancelBooking`, `cancelVenueBooking` and `handleEventCancelled`.

Consumers
:   Events (G2), which learns that its Event no longer has the Venue; when the Venue Manager cancelled, this message is the only way Events learns it. Reviews (G1), which records that the Promoter no longer holds the Booking. Billing (G3) receives it on the Places topic and ignores it.

Sent when
:   Places has cancelled a Booking, whoever cancelled it (FR-32).

| Field | Type | Meaning |
|------------------|-----------|---------------------------------------------------------------|
| `type` | string | `BookingCancelled`. |
| `bookingId` | UUID | The Booking cancelled. |
| `eventId` | UUID | The Event that held it. |
| `promoterId` | UUID | The Event's Promoter. |
| `venueId` | UUID | The Venue that was booked. |
| `cancelledBy` | string | `events` when Events cancelled it, with a Booking cancellation or through *Event cancelled*; `venueManager` when the Venue's Venue Manager did. |
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

G2 designs this message, so the table lists only the fields Places relies on. We have asked G2 and G4 which messages go on the Log topic.

| Field | Type | Meaning |
|------------------|-----------|---------------------------------------------------------------|
| `type` | string | Names the message as *Event cancelled*, with whatever value G2 chooses. |
| `eventId` | UUID | The cancelled Event: the same id Events sent in its Booking request. |

: The fields of *Event cancelled* that Places reads. \label{tab:event-cancelled}

#### *Rating changed* {.unnumbered .unlisted}

Channel
:   The Reviews topic.

Producer
:   Reviews (G1).

Consumers
:   Places, which runs `handleRatingChanged` (FR-33, FR-34).

Sent when
:   The average of a Venue's reviews changes.

The table lists the fields Places reads. We have asked Reviews to publish them, along with the number of reviews behind the average, which Places doesn't keep.

| Field | Type | Meaning |
|------------------|-----------|---------------------------------------------------------------|
| `type` | string | `RatingChanged`. |
| `venueId` | UUID | The Venue rated. |
| `average` | number | The Venue's new Rating: the average of its reviews. |
| `stampedAt` | date-time | When Reviews computed the average, by Reviews' clock. Places keeps the Rating with the latest stamp (FR-34). |

: The fields of *Rating changed*. \label{tab:rating-changed}

### Why these messages

#### Places keeps a copy of each Venue's Rating {.unnumbered .unlisted}

Reviews computes each Venue's Rating, and Places needs it for the minimum Rating filter of search (FR-11, FR-14) and to return with the Venue (FR-10). We considered two options.

- **Ask Reviews for the Ratings on each search.** Rejected. A search with a minimum Rating would find the Venues that match its other filters, ask Reviews for the Rating of each, and drop those below the minimum in memory, so the filter couldn't be part of the SQL query that does the rest of the search. Every such search would wait on a call to Reviews, which puts the 2-second target of NFR-1 at risk, and would fail while Reviews is down, against NFR-7. Richardson's point is general: each synchronous call to another service while handling a request lowers the availability of the operation [@richardson2018, sec. 3.4.1].
- **Keep a copy, updated from *Rating changed* (chosen).** Richardson's remedy is for a service to replicate the data it needs from another service, kept up to date by the events that service publishes [@richardson2018, sec. 3.4.2]. Places then answers every search and `getVenue` from its own database, whether Reviews is up or not. The cost is that a Venue's Rating can lag behind its latest review for as long as *Rating changed* takes to arrive, which matters little for a search filter, and that a Venue has no Rating until the first message for it arrives (FR-14). Messages can also arrive out of order, which the Rating timestamp rule below deals with. The option depends on Reviews agreeing to publish *Rating changed*, which we have asked.

#### Billing creates the bill from *Booking confirmed* {.unnumbered .unlisted}

The professor expects Places to emit a billing for each Booking: something that lets Billing (G3) bill the Promoter. We considered three ways.

- **Places calls Billing's REST API to create the bill.** Rejected. `requestBooking` would then succeed only while Billing is up, the loss of availability Richardson warns of [@richardson2018, sec. 3.4.1]. A call that failed after the Booking was saved would leave a Booking with no bill, the failure the transactional outbox below exists to prevent.
- **Places publishes *Bill issued*.** Rejected. A bill is Billing's concept, so Places would be modelling another group's domain, and the message would serve only Billing.
- **Places publishes *Booking confirmed*, and Billing creates the bill (chosen).** The message states a fact in Places' own domain, so one message serves every group that needs it: Billing bills from it, and Reviews learns from it who booked which Venue. It carries everything a bill needs, the Promoter, the days and the amount, so Billing never has to call Places back; Richardson calls this *event enrichment* [@richardson2018, sec. 5.3]. Places computes the amount because only Places knows the Venue's price per day, and fixes it when the Booking is created (FR-22).

Billing ignores *Booking cancelled*, so cancellations are neither billed nor refunded: if a Venue Manager cancels a Booking, the Promoter's bill still stands. No group handles refunds, a gap the Scope in the Application requirements section names.

#### How Reviews knows who may rate a Venue {.unnumbered .unlisted}

Only the Promoter who booked a Venue may rate it. Reviews enforces the rule, since it takes the reviews, but Places is the one that knows who booked which Venue: it holds the Bookings and sees every cancellation, the Venue Manager's included. Reviews learns what it needs from the two Booking messages:

1. *Booking confirmed* says that a Promoter holds a Booking at a Venue. Reviews records the Booking id with the Promoter and the Venue.
2. *Booking cancelled* says that the Booking no longer stands, whoever cancelled it. Reviews marks its record of the Booking as cancelled, creating the record if *Booking confirmed* hasn't arrived yet.
3. When a Promoter submits a review of a Venue, Reviews accepts it only if it holds a record of a Booking by that Promoter at that Venue that is not cancelled. Reviews then recomputes the Venue's Rating and publishes *Rating changed*, which brings the new Rating back to Places.

Reviews could instead ask Places, for each review, whether the Promoter had booked the Venue. Keeping its own record is the same trade Places makes for the Rating: Reviews takes reviews while Places is down. The rule assumes that the Promoter id Events puts in its Booking request is the id Reviews knows the Promoter by when the review arrives. We have asked Reviews to confirm that it enforces the rule this way.

### Reliable delivery

We assume the broker delivers each message at least once: it keeps a message until the consumer acknowledges it, and delivers it again if no acknowledgement comes, for instance because the consumer stopped while handling it. No message is lost, but one can arrive twice, and a redelivered message can arrive after messages sent later. G4 hasn't chosen the broker yet, and we have asked whether it delivers at least once; nothing below depends on more than that. Reliability then has two sides: Places must get each of its messages to the broker (NFR-4), and every consumer, Places included, must cope with receiving a message twice (NFR-5, NFR-6).

#### Publishing through a transactional outbox {.unnumbered .unlisted}

When a command creates or cancels a Booking, its message must reach the broker exactly when the change is saved. We considered three ways.

- **Publish to the broker after the commit.** Rejected. If Places stops between committing a Booking and publishing *Booking confirmed*, the message is lost and Billing never bills the Booking. Publishing before the commit fails the other way: if the commit then fails, Billing bills a Booking that doesn't exist.
- **One distributed transaction across the database and the broker.** Rejected. A two-phase commit would make the two writes atomic, but many brokers don't support it, and Richardson advises against distributed transactions for modern applications [@richardson2018, sec. 3.3.7].
- **A transactional outbox with a polling relay (chosen).** The command writes the message as a row of an *outbox* table in the same database transaction that saves the change, so the row exists exactly when the change does. A relay then reads the rows and publishes them. These are Richardson's Transactional outbox and Polling publisher patterns [@richardson2018, sec. 3.3.7], and they need nothing beyond Places' own PostgreSQL database. His other relay, Transaction log tailing, reads the rows from the database's transaction log instead of polling for them; it saves the polling queries but adds a tool such as Debezium to run, and at Places' load polling costs little.

The relay runs inside Places. Every second it reads the outbox rows not yet sent, in the order they were inserted, publishes each to the Places topic, and marks a row as sent once the broker has accepted it. If the broker refuses a row, the relay stops there and tries again a second later. Three details matter.

1. If Places stops after the broker accepts a message but before the row is marked, the relay publishes the message again when Places restarts. This is how Places itself can send a message twice, and why consumers deduplicate.
2. The relay marks each row rather than remembering the last row it sent. Rows are numbered as they are inserted, but transactions can commit in a different order, so a row can appear after a row with a higher number has been sent. A relay that only looked past the highest number it had sent would skip it.
3. If several copies of Places run, only one of them runs the relay at a time. A Booking's *Booking confirmed* then always leaves before its *Booking cancelled*.

The relay adds up to a second between a change and its message. Billing and Reviews don't need the message sooner, and Events doesn't wait for it: it learns the result of its own Booking requests and cancellations from Places' REST answers.

#### Consumers deduplicate by Booking id {.unnumbered .unlisted}

Richardson gives a consumer two ways to cope with a duplicate: make its handler idempotent, so that handling a message twice has the effect of handling it once, or record the ids of the messages it has handled and discard those it sees again [@richardson2018, sec. 3.3.6]. A Booking is confirmed once and cancelled at most once, so a message's type and Booking id identify it, and consumers need no separate message id. We ask each consumer to key what it keeps on the Booking id.

- **Billing** creates at most one bill per Booking id, so a second *Booking confirmed* for a Booking is dropped.
- **Reviews** keeps one record per Booking id. *Booking cancelled* marks it cancelled, creating it from the message's Promoter and Venue if *Booking confirmed* hasn't arrived yet, and a cancelled record stays cancelled whatever arrives after it. Otherwise a *Booking confirmed* redelivered after the cancellation would let the Promoter rate a Venue they no longer hold a Booking at.
- **Events** reads *Booking cancelled* as news about the Booking it names, not about the Event. Keyed on the Event, a duplicate would do harm: Events cancels an Event's Booking and books again at once (US-4), and a late copy of the first Booking's *Booking cancelled* would then seem to cancel the new one. Keyed on the Booking id, the copy matches no Booking Events holds, and changes nothing.

#### Places' handlers are safe to run twice {.unnumbered .unlisted}

Places takes the first of Richardson's two ways: both its handlers are idempotent (NFR-5), so Places keeps no table of the messages it has handled and doesn't depend on G1 and G2 giving their messages unique ids. Places acknowledges a message only after the transaction that handles it has committed, so if Places stops while handling one, the broker delivers it again rather than losing it.

- **`handleEventCancelled`** removes the Event's Booking, if it has one that hasn't ended, and queues *Booking cancelled*, in one transaction. A second delivery finds no Booking and does nothing. The removal is a single `DELETE`, so if two copies of Places handle the same message at once, or Events cancels the same Booking over REST at that moment, the second `DELETE` waits for the first to commit, finds the row gone, and removes nothing [@postgresql-isolation, sec. 13.2.1]. Only one *Booking cancelled* is queued per Booking, whichever way it was cancelled.
- **`handleRatingChanged`** applies the Rating timestamp rule. A second delivery sets the same Rating again.

#### The Rating timestamp rule {.unnumbered .unlisted}

*Rating changed* messages for one Venue can arrive out of order. The broker may redeliver an old message after newer ones, and when several copies of Places consume the Reviews topic side by side, as Richardson's competing receivers [@richardson2018, sec. 3.3.5], they can finish two messages in the opposite order to the one they took them in. Applied as they finish, an old Rating would replace a newer one. So each message carries the time Reviews computed the average, and Places replaces the Rating it holds only with one stamped no earlier (FR-34). Both stamps come from Reviews' clock, so the rule doesn't depend on Places' clock agreeing with Reviews'. Places applies the rule in one statement, which also changes nothing for a Venue that no longer exists:

```sql
UPDATE venue
SET    rating_average = :average, rating_stamped_at = :stamped_at
WHERE  id = :venue_id
AND    (rating_stamped_at IS NULL OR rating_stamped_at <= :stamped_at);
```

When two copies of Places run this for one Venue at once, the second waits for the first to commit, then checks its `WHERE` clause against the Rating the first wrote [@postgresql-isolation, sec. 13.2.1], so the older message can't win the race.

### Collaborations

Figure \ref{fig:collaborations} draws every flow between Places and the other groups, and Table \ref{tab:flows} says what each carries and why it is a REST call or a message. A flow is a synchronous REST call when the caller needs Places' answer before it can go on. It goes through the broker when the sender only states a fact, which any number of groups may act on in their own time. Messages also keep each group's availability its own: Places books Venues while Billing or Reviews is down, and their messages wait on the broker [@richardson2018, sec. 3.4].

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
  \node[channel] (rtopic) at (3.3,-1.7) {Reviews topic};
  \node[draw, dotted, inner sep=7pt, fit=(log) (rtopic), label={[font=\scriptsize]above:Message broker (G4)}] {};
  \node[box] (events) at (6.6,2.4) {Events\\(G2)};
  \node[box] (billing) at (6.6,0) {Billing\\(G3)};
  \node[box] (reviews) at (6.6,-2.4) {Reviews\\(G1)};

  \draw[rest] (promoter.east) -- node[num] {1} (gateway.north west);
  \draw[rest] (manager.east) -- node[num] {1} (gateway.south west);
  \draw[rest] (gateway) -- node[num] {1} (places);
  \draw[rest] (events.north) -- ++(0,0.6) -| node[num, pos=0.25] {2} (places.north);
  \draw[rest] (tickets) -- node[num] {3} (places);

  \draw[msg] (events.west) -- node[num, pos=0.4] {4} (log.east);
  \draw[msg] (log.west) -- node[num] {4} (places.north east);
  \draw[msg] (reviews.west) -- node[num, pos=0.4] {5} (rtopic.east);
  \draw[msg] (rtopic.west) -- node[num] {5} (places.south east);
  \draw[msg] (places) -- node[num, pos=0.4] {6, 7} (ptopic);
  \draw[msg] (ptopic.east) -- node[num, pos=0.6] {6} (billing);
  \draw[msg] (ptopic.east) -- node[num, pos=0.6] {6, 7} (reviews.north west);
  \draw[msg] (ptopic.east) -- node[num, pos=0.6] {7} (events.south west);
\end{tikzpicture}
\caption{Collaborations between Places and the other groups. Solid arrows are synchronous REST calls, from the caller to Places. Dashed arrows are messages, from the producer to a channel on the broker and from the channel to each consumer. The numbers refer to Table \ref{tab:flows}.}
\label{fig:collaborations}
\end{figure}
```

| # | Flow | What it carries | Why REST or the broker |
|----|---------------------------|-------------------------------------|--------------------------------------|
| 1 | Promoter or Venue Manager → Gateway → Places | Every user request, with the user id and roles the Gateway forwards: searches, availability checks, Venue changes, a Venue's Bookings and their cancellation. | REST. A user waits for the answer. |
| 2 | Events → Places | Booking requests (`requestBooking`) and Booking cancellations (`cancelBooking`). | REST. Events must know at once whether it has the Venue or the request is a conflict, to tell the Promoter. A cancellation answers only once it is done, so a Booking request sent straight after can't hit the old Booking (FR-25). |
| 3 | Tickets → Places | A Venue by its id (`getVenue`), for its name and address. | REST. Tickets needs them only when it prints tickets, and Places publishes no messages about Venues that Tickets could keep a copy from. |
| 4 | Events → Log topic → Places | *Event cancelled* (`handleEventCancelled`). | Broker. Events states the fact once for every group that cares, and needs no answer. |
| 5 | Reviews → Reviews topic → Places | *Rating changed* (`handleRatingChanged`). | Broker. Places keeps a copy of the Rating, so search doesn't call Reviews. |
| 6 | Places → Places topic → Billing, Reviews | *Booking confirmed* (`requestBooking`). | Broker. One message serves two groups, and a Booking doesn't wait for either. |
| 7 | Places → Places topic → Events, Reviews | *Booking cancelled* (`cancelBooking`, `cancelVenueBooking`, `handleEventCancelled`). Billing receives it too, and ignores it. | Broker. One message serves two groups, and it tells Events of a Venue Manager's cancellation without Events asking. |

: The flows of Figure \ref{fig:collaborations}. \label{tab:flows}

We have asked G3 to confirm that Tickets reads a Venue with a REST GET.
