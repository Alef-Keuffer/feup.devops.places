# System operations

Richardson's first step turns the requirements into *system operations*: the requests Places handles, each either a *command*, which creates, changes or removes data, or a *query*, which only reads it [@richardson2018, sec. 2.2.1]. He first draws a high-level domain model to give the operations a vocabulary, then specifies each operation by its parameters, its result, the preconditions that must hold when it is called and the postconditions that hold once it has run. This section does the same for Places. It says what each operation does, not how the request arrives: the Service APIs and collaborations section maps each operation to a REST endpoint, a broker message or, for `refreshRatings`, Places' own timer. In this report, "system operations" means these commands and queries, not the work of deploying and running Places.

## Domain model

Figure \ref{fig:domain} shows the domain model. Its classes are the nouns of the user stories, which is where Richardson finds them [@richardson2018, sec. 2.2.1], and it uses the terms of the Vocabulary in the Application requirements section.

```{=latex}
\begin{figure}[htbp]
\centering
\begin{tikzpicture}[
    node distance=1.3cm and 2.2cm,
    class/.style={draw, rectangle split, rectangle split parts=2, rectangle split part align={center, left}, align=left, font=\small, inner sep=3pt},
    byid/.style={draw, dashed, align=center, font=\small, inner sep=4pt},
    mult/.style={font=\scriptsize, inner sep=2pt},
    part/.style={{Diamond[length=3mm, width=2mm]}-}]
  \node[class] (venue) {\textbf{Venue}\nodepart{second}id\\name\\address, city\\coordinates\\capacity\\area\\price per day\\type\\images\\equipment\\Listed or Unlisted};
  \node[class, right=of venue] (room) {\textbf{Room}\nodepart{second}name\\capacity\\area\\layout image};
  \node[class, left=of venue] (rating) {\textbf{Rating}\nodepart{second}average\\stamped at};
  \node[class, below=of venue] (booking) {\textbf{Booking}\nodepart{second}id\\first day\\last day\\amount};
  \node[byid, above=of venue] (manager) {\textbf{Venue Manager}\\{\scriptsize id only}};
  \node[byid, right=of booking] (promoter) {\textbf{Promoter}\\{\scriptsize id only}};
  \node[byid, left=of booking] (event) {\textbf{Event}\\{\scriptsize id only}};

  \draw[part] (venue) -- node[mult, pos=0.12, above] {1} node[mult, pos=0.88, above] {0..*} (room);
  \draw[part] (venue) -- node[mult, pos=0.12, above] {1} node[mult, pos=0.88, above] {0..1} (rating);
  \draw (manager) -- node[mult, pos=0.15, right] {1} node[mult, pos=0.85, right] {0..*} (venue);
  \draw (venue) -- node[mult, pos=0.12, right] {1} node[mult, pos=0.85, right] {0..*} (booking);
  \draw (booking) -- node[mult, pos=0.12, above] {0..*} node[mult, pos=0.88, above] {1} (promoter);
  \draw (booking) -- node[mult, pos=0.12, above] {0..1} node[mult, pos=0.88, above] {1} (event);
\end{tikzpicture}
\caption{Domain model of Places. Dashed boxes belong to other groups, and Places keeps only their ids. A diamond marks a part that is removed with its Venue.}
\label{fig:domain}
\end{figure}
```

- **Venue** is what a Promoter books. It has the details of FR-1 and is either Listed or Unlisted (FR-4, FR-7).
- **Room** is part of a Venue's description. It has no price and is never booked on its own (FR-3).
- **Booking** reserves a Venue for one Event and its Promoter, from a first to a last day, both included (FR-16). Its amount is fixed when it is created (FR-22), and its days never change (FR-23); a Rebooking replaces it with a new Booking (FR-19). Cancelling a Booking removes it, so its days are free at once (FR-31); who cancelled it and why travel in *Booking cancelled* (FR-32). A Booking that has ended stays until its Venue is removed.
- **Rating** is Places' copy of the average Reviews computes for a Venue, with the time Reviews stamped it with, so that an older answer from Reviews can't replace a newer one (FR-33, FR-34). A Venue has no Rating until Places first reads one for it, and loses it when Reviews no longer lists the Venue.
- **Event**, **Promoter** and **Venue Manager** belong to other groups: Events and Promoters to Promoters and Events (G2), users to Users (G4). Places keeps only their ids, the way Richardson's aggregates refer to what they don't own [@richardson2018, ch. 5]. It takes the Event and Promoter ids from Events' Booking requests and the Venue Manager's from the identity the Gateway forwards, and never asks the other groups about them.

Two invariants hold at all times, even when requests arrive at the same moment. The database enforces both; for the first, that is the exclusion constraint of NFR-11.

1. No two Bookings of one Venue overlap (FR-18, NFR-3).
2. An Event has at most one Booking (FR-19).

## Operations

Table \ref{tab:operations} lists every operation, with the actor that calls it, the user story it comes from, and the requirements it implements. With the rules that follow the table, which carry FR-35 and FR-38, they cover every functional requirement, FR-1 to FR-38. Richardson's tables of commands and queries follow the same shape [@richardson2018, sec. 2.2.1].

| Operation | Kind | Actor | Story | Requirements |
|----------------------------|------------|--------------------------|----------|----------------------------------|
| `submitVenue` | Command | Venue Manager | US-5 | FR-1 to FR-5, FR-36 |
| `updateVenue` | Command | Venue Manager | US-6 | FR-2, FR-5, FR-6, FR-22, FR-37 |
| `unlistVenue` | Command | Venue Manager | US-7 | FR-7, FR-8, FR-37, NFR-2 |
| `relistVenue` | Command | Venue Manager | US-7 | FR-7, FR-8, FR-37, NFR-2 |
| `deleteVenue` | Command | Venue Manager | US-8 | FR-9, FR-37 |
| `requestBooking` | Command | Events | US-3, US-4, US-10 | FR-8, FR-16 to FR-22, FR-24, FR-30, FR-32, NFR-2 to NFR-4 |
| `cancelBooking` | Command | Events | US-4 | FR-23, FR-25, FR-30 to FR-32, NFR-2, NFR-4 |
| `cancelVenueBooking` | Command | Venue Manager | US-9 | FR-29 to FR-32, FR-37, NFR-2, NFR-4 |
| `searchVenues` | Query | Any user, Events | US-1 | FR-8, FR-11 to FR-14, NFR-1, NFR-7 |
| `checkAvailability` | Query | Any user | US-2 | FR-15, NFR-1, NFR-7 |
| `getVenue` | Query | Any user, Events, Tickets | US-12 | FR-3, FR-10, FR-33, NFR-7 |
| `listVenueBookings` | Query | Venue Manager | US-9 | FR-28, FR-37 |
| `handleEventCancelled` | Command | Events, through the Log topic | US-4 | FR-26, FR-27, FR-30 to FR-32, NFR-4, NFR-5 |
| `refreshRatings` | Command | Places itself, every five minutes | US-11 | FR-33, FR-34, NFR-7 |

: The system operations of Places. \label{tab:operations}

These rules apply to every operation, so the specifications below don't repeat them:

- Every operation a user calls carries the caller's user id and roles, which the Gateway forwards. Places rejects a user request without them as unauthenticated (FR-35). The specifications call this user the *caller*. A user who holds both the Promoter and the Venue Manager roles may do everything either role allows (FR-38). `requestBooking` and `cancelBooking` are for Events alone; the REST API section says how Places tells a call from Events apart from a user's.
- When a precondition doesn't hold, Places rejects the operation and changes nothing. Where a requirement names the rejection (a conflict, or forbidden), the precondition says so; the REST API section maps every rejection to an error response.
- A command that creates or cancels a Booking saves *Booking confirmed* or *Booking cancelled* with the change, in one database transaction, and Places publishes it to the broker afterwards. The specifications call this *queuing* the message: it is queued exactly when the change is saved, so it can't be lost (NFR-4). The Messaging and collaborations section explains how.
- Every change is seen by the availability checks and searches Places answers after it (NFR-2).
- Queries read only Places' own data, so they keep working while Reviews or Events is down (NFR-7).

## Commands

#### `submitVenue` {.unnumbered .unlisted}

Parameters
:   The caller, and the Venue's details: a name; an address, including its city; coordinates; a capacity in persons; an area in square metres; a price per day in EUR; a type; images; equipment, as items with quantities; and Rooms, each with a name, a capacity, an area and a layout image (FR-1, FR-3).

Result
:   The new Venue's id.

Preconditions
:   - The caller has the Venue Manager role; otherwise the submission is forbidden (FR-36).
    - The type is open-air, stadium, pavilion, auditorium, conference centre or other (FR-2).

Postconditions
:   - A Venue exists with the given details and Rooms (FR-1, FR-3).
    - It is Listed, so it appears in search and accepts Booking requests at once (FR-4).
    - The caller is its Venue Manager, for as long as the Venue exists (FR-5).
    - It has no Bookings and no Rating.

#### `updateVenue` {.unnumbered .unlisted}

Parameters
:   The caller, a Venue id, and new values for any of the details in FR-1, Rooms included (FR-6).

Result
:   Nothing.

Preconditions
:   - The Venue exists.
    - The caller is its Venue Manager; otherwise the change is forbidden (FR-37).
    - A new type, if given, is one of those in FR-2.

Postconditions
:   - The Venue has the new values, and its other details are unchanged (FR-6).
    - Its Venue Manager, whether it is Listed, its Bookings and its Rating are unchanged (FR-5).
    - The amounts of its existing Bookings are unchanged; a new price per day applies only to Bookings created from now on (FR-22).

#### `unlistVenue` {.unnumbered .unlisted}

Parameters
:   The caller and a Venue id.

Result
:   Nothing.

Preconditions
:   - The Venue exists and is Listed (FR-7).
    - The caller is its Venue Manager; otherwise the change is forbidden (FR-37).

Postconditions
:   - The Venue is Unlisted: it drops out of search, and Booking requests for it are rejected (FR-8).
    - Its existing Bookings stand (FR-8).

#### `relistVenue` {.unnumbered .unlisted}

Parameters
:   The caller and a Venue id.

Result
:   Nothing.

Preconditions
:   - The Venue exists and is Unlisted (FR-7).
    - The caller is its Venue Manager; otherwise the change is forbidden (FR-37).

Postconditions
:   - The Venue is Listed: it appears in search and accepts Booking requests again (FR-7, FR-8).

#### `deleteVenue` {.unnumbered .unlisted}

Parameters
:   The caller and a Venue id.

Result
:   Nothing.

Preconditions
:   - The Venue exists.
    - The caller is its Venue Manager; otherwise the change is forbidden (FR-37).
    - Every Booking at the Venue has ended (FR-9).

Postconditions
:   - The Venue is removed, together with its Rooms, its Rating and its Bookings, all of which have ended. Operations that name it now fail their first precondition, and `refreshRatings` no longer reads its Rating.

No operation changes a Booking's days (FR-23): Events replaces a Booking with a Rebooking, a `requestBooking` that names the Booking it replaces (FR-19).

#### `requestBooking` {.unnumbered .unlisted}

Parameters
:   An Event id, the id of the Event's Promoter, a Venue id, a first and a last day, both included, and, optionally, the id of the Booking it replaces, which makes the request a Rebooking (FR-16).

Result
:   The new Booking's id and amount.

Preconditions
:   - The request comes from Events (FR-16).
    - The Venue exists and is Listed (FR-8, FR-17).
    - The last day is not before the first day, and the first day is not before today in the Europe/Lisbon time zone (FR-20).
    - No Booking of the Venue overlaps any of the days, apart from the Booking a Rebooking replaces, which doesn't count against them; otherwise the request is a conflict (FR-18).
    - Without a Booking to replace, the Event has no Booking, at this Venue or any other; otherwise the request is a conflict (FR-19).
    - For a Rebooking, the Booking it replaces exists and is the Event's (FR-19), and has not ended (FR-30).

Postconditions
:   - For a Rebooking, the Booking it replaces is removed, and *Booking cancelled* is queued for it with Events as who cancelled it (FR-32, NFR-4), in the same transaction as the rest.
    - A Booking exists for the Event, its Promoter and the Venue, on those days (FR-16).
    - Its amount is the number of days × the Venue's price per day at this moment, and stays so (FR-22), for a Rebooking too.
    - *Booking confirmed* is queued with the Booking, the Event, the Promoter, the Venue, the Venue Manager, the days, the amount and, for a Rebooking, the Booking it replaces (FR-24, NFR-4).

A Rebooking that fails any precondition changes nothing, so the Event keeps the Booking it names. Places doesn't compare the Venue's capacity with the Event (FR-21). When two requests for overlapping days at one Venue arrive together, the first invariant lets exactly one of them create its Booking, and the other is rejected as a conflict (NFR-3).

#### `cancelBooking` {.unnumbered .unlisted}

Parameters
:   A Booking id and, optionally, a reason (FR-25).

Result
:   Nothing. Places answers only once the Booking is cancelled (FR-25).

Preconditions
:   - The request comes from Events (FR-25).
    - The Booking exists, so it has not been cancelled already.
    - It has not ended (FR-30).

Postconditions
:   - The Booking is removed and its days are free at once (FR-31).
    - *Booking cancelled* is queued with the Booking, the Event, the Promoter, the Venue, Events as who cancelled it, and the reason if one was given (FR-32, NFR-4).

#### `cancelVenueBooking` {.unnumbered .unlisted}

Parameters
:   The caller, a Venue id, a Booking id and, optionally, a reason (FR-29).

Result
:   Nothing.

Preconditions
:   - The Venue exists.
    - The caller is its Venue Manager; otherwise the cancellation is forbidden (FR-37).
    - The Booking exists and is at that Venue.
    - It has not ended (FR-30).

Postconditions
:   - The Booking is removed and its days are free (FR-31).
    - *Booking cancelled* is queued with the Booking, the Event, the Promoter, the Venue, the Venue Manager as who cancelled it, and the reason if one was given (FR-32, NFR-4).

## Queries

#### `searchVenues` {.unnumbered .unlisted}

Parameters
:   The caller and any combination of these filters (FR-11): a date window, from a first to a last day, with a number of days *N*; a minimum capacity; a maximum price per day; a city; a minimum Rating; a Venue type.

Result
:   The Listed Venues that match every filter given (FR-8, FR-11). A Venue matches

    - the date window when at least *N* consecutive days inside it are free of its Bookings (FR-12);
    - the minimum capacity when its capacity is at least that, and the maximum price when its price per day is at most that;
    - the city and the type when they are its own;
    - the minimum Rating when it has a Rating of at least that, so a Venue with no Rating doesn't match (FR-14).

Preconditions
:   - *N* is at least 1 and no longer than the date window (FR-13).

Postconditions
:   - Nothing has changed.

#### `checkAvailability` {.unnumbered .unlisted}

Parameters
:   The caller, a Venue id, and a first and a last day, both included (FR-15).

Result
:   Either that the Venue is available, because none of its Bookings overlaps those days, or which of the days are taken (FR-15).

Preconditions
:   - The Venue exists.
    - The last day is not before the first day.

Postconditions
:   - Nothing has changed.

#### `getVenue` {.unnumbered .unlisted}

Parameters
:   A Venue id. The caller is a user, Events or Tickets (US-12).

Result
:   The Venue, Listed or Unlisted, with its details, its Rooms, its number of Rooms and its Rating if it has one (FR-3, FR-10, FR-33).

Preconditions
:   - The Venue exists.

Postconditions
:   - Nothing has changed.

#### `listVenueBookings` {.unnumbered .unlisted}

Parameters
:   The caller and a Venue id (FR-28).

Result
:   The Venue's Bookings, each with its id, its Event, its Promoter, its days and its amount.

Preconditions
:   - The Venue exists.
    - The caller is its Venue Manager; otherwise the request is forbidden (FR-37).

Postconditions
:   - Nothing has changed.

## Operations triggered by messages

Two operations start not from a request but from a message another group sends through the broker. Places ignores *Event scheduled* and every other message on the Log topic (FR-27). The broker delivers each message at least once, so each operation has the same effect whether its message arrives once or twice (NFR-5). They have no preconditions: there is no caller to reject a message to, so a message that doesn't apply changes nothing.

#### `handleEventCancelled` {.unnumbered .unlisted}

Parameters
:   An *Event cancelled* message from the Log topic, naming the Event (FR-26).

Result
:   Nothing.

Preconditions
:   - None.

Postconditions
:   - If the Event had a Booking that had not ended, that Booking is removed and its days are free (FR-26, FR-30, FR-31), and *Booking cancelled* is queued with Events as who cancelled it (FR-32, NFR-4).
    - Otherwise nothing has changed and nothing is queued (FR-26). This is the case when the message arrives a second time, so the second delivery has no effect (NFR-5).

#### `refreshRatings` {.unnumbered .unlisted}

Parameters
:   None. Places runs it every five minutes (FR-33).

Result
:   Nothing.

Preconditions
:   - None.

Postconditions
:   - Places has asked Reviews once for every Venue's Rating. The answer lists each Venue with reviews, with its average and the time Reviews stamped it with, and carries the time Reviews sent it in its `Date` header.
    - A Venue in the answer whose entry is stamped no earlier than the Rating it holds, or that had no Rating, now has the entry's average and stamp as its Rating, and search and `getVenue` use it (FR-33).
    - A Venue missing from the answer, whose Rating is stamped no later than the answer's `Date`, now has no Rating, so a search with a minimum Rating leaves it out (FR-14).
    - Every other Venue keeps the Rating it holds, if any: when its entry or the answer is stamped earlier (FR-34), and when Reviews didn't answer (FR-33). A Venue removed meanwhile gets no Rating.
