# Application requirements

Places is the subsystem of the Event Management system that group 5 builds. It keeps the catalogue of Venues that Promoters can hold Events in, and the calendar of which Venue is booked on which days. The other groups build the rest of the system: Reviews (G1), Promoters and Events (G2), Tickets and Billing (G3), and Users, the message broker and the Gateway (G4).

This report follows the process Richardson gives for defining a microservice architecture [@richardson2019, sec. 2.2]^["Figure 2.5 A three-step process for defining an application’s microservice architecture" (p. 44); "The first step in defining an application’s architecture is to define the system operations. The starting point is the application’s requirements, including user stories and their associated user scenarios." (p. 45); "The second step in the process is to determine the decomposition into services." (p. 45); "The third step in defining the application’s architecture is to determine each service’s API. To do that, you assign each system operation identified in the first step to a service." (p. 45); "In that case, you determine how the services collaborate, which typically requires services to support additional operations." (p. 45)]. It starts from the application requirements in this section, derives the system operations from them, groups those operations into services, and then defines the service APIs and the collaborations between services. This section states the requirements the way Wiegers and Beatty recommend [@wiegers2013]^["Rather than thinking of “the user” in singular, spend some time identifying the multiple user classes and their roles and privileges for your product." (p. 102); "The user class—which need not be a human being—in a user story corresponds to the primary actor in a use case." (p. 145); "As a chemist, I want to request a chemical so that I can perform experiments." (p. 145); "The simplest approach gives every requirement a unique sequence number, such as UC-9 or FR-26." (p. 187); "“The system shall” or “The user shall,” followed by an action verb, followed by the observable result." (p. 207); "Can a tester devise tests or other verification approaches to determine whether each requirement is properly implemented?" (p. 205); "Such characteristics, collectively known as quality attributes, quality factors, quality requirements, quality of service requirements, or the “–ilities,” constitute a major portion of the system’s nonfunctional requirements." (p. 261); "Indicate the scale or units of measure for each attribute and the target, minimum, and maximum values." (p. 267); "Similarly, a software project should define its scope and limitations. You need to state both what the solution being developed is and what it is not." (p. 88)]: the actors, what they want to do as user stories, the functional requirements as numbered "shall" statements that can each be tested, the non-functional requirements with how each is measured, and what is in and out of scope.

## Vocabulary

The report uses these terms with these meanings only.

| Term | Meaning |
|------------|------------------------------------------------------------------------|
| Venue | A physical site submitted to the platform, with an address, images and a Rating. It is the unit a Promoter books for an Event. |
| Room | A named part of a Venue, shown in the Venue's description with its own capacity, area and layout. A Room is never booked on its own. |
| Promoter | A user who organises Events and books Venues for them. |
| Venue Manager | The user who submits a Venue to the platform and the only one allowed to change it and its Rooms. The same person may also be a Promoter. |
| Listed | A Venue that appears in search and accepts new Bookings. A Venue is Listed as soon as it is submitted. |
| Unlisted | A Venue its Venue Manager has taken out of search. It accepts no new Bookings, but its existing Bookings stand. |
| Booking | A Venue reserved for one Event over consecutive whole days. An Event holds at most one Booking, and a Venue is available exactly when no Booking overlaps the requested days. |
| Rating | The average of a Venue's reviews, as Places last read it from Reviews (G1). |

## Actors

Wiegers and Beatty separate the classes of people who use a system from the other systems it exchanges data with [@wiegers2013, chs. 5–6]^["The external entities in the rectangles can represent user classes (Chemist, Buyer), organizations (Health and Safety Department), other systems (Training Database), or hardware devices (Bar Code Reader)." (p. 93)]. Places has two classes of user and four collaborating services. Users never reach Places directly: they go through the Gateway, which tells Places who they are.

| Actor | Kind | What it needs from Places |
|----------------|-------------|----------------------------------------------------------|
| Promoter | User | Find Venues that suit an Event and check their days. Books and cancels through Events. |
| Venue Manager | User | Submit Venues and keep them up to date, unlist and relist them, see their Bookings, and cancel a Booking when something unforeseen happens. |
| Events (G2) | Service | Read Venues, book a Venue for an Event, and read and cancel that Booking. Tells Places when an Event is cancelled, and learns when Places cancels a Booking. |
| Reviews (G1) | Service | Nothing. Reviews decides who may rate a Venue and computes each Venue's Rating, which Places reads from it. |
| Billing and Tickets (G3) | Service | Billing bills the Promoter for each Booking, and cancels the bill if the Booking is cancelled before it is paid. Tickets reads a Venue's name and address to print on tickets. |
| Gateway (G4) | Service | Checks each user's token and forwards the user's id to Places. G4 also runs the message broker. |

Figure \ref{fig:context} shows these actors around Places in a context diagram [@wiegers2013, ch. 5]^["The context diagram visually illustrates this boundary. It identifies external entities (also called terminators) outside the system that interface to it in some way, as well as data, control, and material flows between the terminators and the system." (p. 92); "The entire system is depicted as a single circle; the context diagram deliberately provides no visibility into the system’s internal objects, processes, or data." (p. 93)]. It shows what flows between them, not how: the Service APIs and collaborations section says which flows are REST calls and which are messages through the broker.

```{=latex}
\begin{figure}[htbp]
\centering
\begin{tikzpicture}[
    node distance=1.8cm and 2.6cm,
    actor/.style={draw, rounded corners, align=center, minimum width=2.6cm, minimum height=1cm, font=\small},
    system/.style={draw, circle, very thick, align=center, minimum size=2.4cm, font=\bfseries},
    flow/.style={-{Stealth[length=2.4mm]}},
    label/.style={font=\scriptsize, align=center}]
  \node[system] (places) {Places\\(G5)};
  \node[actor, left=of places] (gateway) {Gateway\\(G4)};
  \node[actor, above=of gateway] (promoter) {Promoter};
  \node[actor, below=of gateway] (manager) {Venue Manager};
  \node[actor, above=of places] (events) {Events\\(G2)};
  \node[actor, right=of places] (reviews) {Reviews\\(G1)};
  \node[actor, below=of places] (g3) {Billing and Tickets\\(G3)};

  \draw[flow] (promoter) -- node[label, left] {searches,\\availability checks} (gateway);
  \draw[flow] (manager) -- node[label, left] {Venue changes,\\Booking lists,\\cancellations} (gateway);
  \draw[flow] (gateway) -- node[label, above] {requests with\\user id} (places);

  \draw[flow] ([xshift=-4mm]events.south) -- node[label, left] {Venue reads,\\Booking requests,\\Booking reads,\\Booking cancellations,\\\emph{Event cancelled}} ([xshift=-4mm]places.north);
  \draw[flow] ([xshift=4mm]places.north) -- node[label, right] {\emph{Booking cancelled}} ([xshift=4mm]events.south);

  \draw[flow] (reviews) -- node[label, above] {Venue Ratings} (places);

  \draw[flow] (places) -- node[label, right] {\emph{Booking confirmed},\\\emph{Booking cancelled} (Billing),\\Venue name and address (Tickets)} (g3);
\end{tikzpicture}
\caption{Context diagram of Places. Names in italics are messages.}
\label{fig:context}
\end{figure}
```

## User stories

Richardson starts from user stories and their scenarios, and he writes a scenario as *given*, *when*, *then* [@richardson2019, sec. 2.2.1]^["The starting point is the application’s requirements, including user stories and their associated user scenarios." (p. 45); "Given a consumer And a restaurant And a delivery address/time that can be served by that restaurant And an order total that meets the restaurant's order minimum When the consumer places an order for the restaurant Then consumer's credit card is authorized" (p. 47)]. Wiegers and Beatty describe a user story as a short description of what someone needs, and say that it sometimes stands for a single scenario [@wiegers2013, ch. 8]^["As used on agile development projects, a user story is a “short, simple description of a feature told from the perspective of the person who desires the new capability, usually a user or customer of the system”" (p. 145); "In the agile world, a user story sometimes covers the same scope as an entire use case, but in other cases a user story represents just a single scenario or alternative flow." (p. 152)]. Each story ends with the functional requirements that implement it. The dates are examples.

**US-1 Find a Venue.** As a Promoter, I want to search the Listed Venues by dates, capacity, price, city, Rating and type, so that I only look at Venues that could host my Event.

*Scenario: a Venue with enough free days matches.*

| **Given** a Listed Venue in Porto for 300 people at 800 EUR per day, with Bookings on 3–5 June and 9–10 June 2027
| **When** a Promoter searches for 3 consecutive days between 1 and 12 June 2027, in Porto, for at least 200 people, at no more than 1,000 EUR per day
| **Then** the Venue is in the results, because 6–8 June are free

*Scenario: too few consecutive free days.*

| **Given** the same Venue
| **When** the Promoter searches for 4 consecutive days in the same window
| **Then** the Venue is not in the results, because its longest free stretch is 3 days

*Scenario: Unlisted Venues are left out.*

| **Given** an Unlisted Venue that matches every filter
| **When** a Promoter searches
| **Then** the Venue is not in the results

Requirements: FR-8, FR-11 to FR-14.

**US-2 Check a Venue's days.** As a Promoter, I want to check whether a Venue is free on the exact days of my Event, so that I can settle the days before I ask Events to book it.

*Scenario: a day is taken.*

| **Given** a Venue with a Booking on 9–10 June 2027
| **When** a Promoter checks the Venue for 8–9 June 2027
| **Then** Places answers that the Venue is not available and that 9 June is taken

Requirements: FR-10, FR-15.

**US-3 Book a Venue for an Event.** As a Promoter, I want Events to book a Venue for my Event's days, so that no other Event can take the Venue on those days.

*Scenario: the days are free.*

| **Given** a Listed Venue at 800 EUR per day with no Booking on 6–8 June 2027, and an Event with no Booking
| **When** Events sends a Booking request for that Event, its Promoter, the Venue and 6–8 June 2027
| **Then** Places creates the Booking with an amount of 2,400 EUR (3 days × 800 EUR)
| **And** Places publishes *Booking confirmed*

*Scenario: the days overlap a Booking.*

| **Given** a Venue with a Booking on 9–10 June 2027
| **When** Events sends a Booking request for the Venue on 10–11 June 2027
| **Then** Places rejects the request as a conflict and creates no Booking

*Scenario: the Event already has a Booking.*

| **Given** an Event that already has a Booking
| **When** Events sends another Booking request for that Event, at any Venue, that doesn't name that Booking
| **Then** Places rejects the request

Requirements: FR-16 to FR-24.

**US-4 Cancel or replace a Booking.** As a Promoter, I want to cancel my Event's Booking, or replace it with a Rebooking on other days or at another Venue, so that the Venue's days are freed when my plans change, and my Event never goes without a Venue in between.

*Scenario: a Rebooking.*

| **Given** an Event booked at a Venue on 6–8 June 2027
| **When** Events sends a Booking request for the same Event and Venue on 7–9 June 2027 that names the Event's Booking as the one it replaces
| **Then** the request succeeds, because the old Booking doesn't count against the new days, and Places cancels the old Booking and creates the new one in one transaction
| **And** Places publishes *Booking cancelled*, then *Booking confirmed*

*Scenario: a Rebooking that fails.*

| **Given** an Event booked at a Venue on 6–8 June 2027, and another Event's Booking at a second Venue on 10 June 2027
| **When** Events sends a Rebooking of the first Event to the second Venue on 9–10 June 2027
| **Then** Places rejects the request as a conflict, and the Event keeps its Booking on 6–8 June 2027

*Scenario: the Event is cancelled.*

| **Given** an Event with a Booking
| **When** *Event cancelled* for that Event arrives on the Log topic
| **Then** Places cancels the Booking and publishes *Booking cancelled*

*Scenario: nothing left to cancel.*

| **Given** an Event whose Booking Events has already cancelled
| **When** *Event cancelled* for that Event arrives, once or twice
| **Then** Places changes nothing and publishes nothing

*Scenario: Events lost the answer.*

| **Given** Events sent a Booking request for Event 100 and Places answered `201`, but Events failed before saving the Booking's id
| **When** Events asks Places for Event 100's Booking
| **Then** it gets that Booking, with its id

Requirements: FR-16, FR-19, FR-22, FR-23, FR-25 to FR-27, FR-30 to FR-32, FR-38.

**US-5 Submit a Venue.** As a Venue Manager, I want to submit my Venue with its address, capacity, area, price per day, type, equipment, images and Rooms, so that Promoters can find and book it.

*Scenario: the Venue is Listed at once.*

| **Given** a user
| **When** they submit a Venue of type auditorium with three Rooms
| **Then** the Venue is Listed and appears in search straight away, with 3 Rooms
| **And** that user is its Venue Manager

*Scenario: an unknown type.*

| **Given** a user
| **When** they submit a Venue of type "barn"
| **Then** Places rejects the submission

Requirements: FR-1 to FR-5, FR-35.

**US-6 Keep a Venue up to date.** As a Venue Manager, I want to change my Venue's description, Rooms and price per day, so that Promoters see current information.

*Scenario: a new price applies to new Bookings only.*

| **Given** a Venue at 800 EUR per day with a Booking whose amount is 2,400 EUR
| **When** its Venue Manager changes the price to 900 EUR per day
| **Then** new Bookings are priced at 900 EUR per day
| **And** the existing Booking's amount stays 2,400 EUR

*Scenario: only the Venue Manager may change a Venue.*

| **Given** a Venue
| **When** any other user tries to change it
| **Then** Places refuses the change as forbidden

Requirements: FR-6, FR-22, FR-36.

**US-7 Take a Venue out of search.** As a Venue Manager, I want to unlist my Venue and relist it later, so that it takes no new Bookings while I can't host Events.

*Scenario: unlist.*

| **Given** a Listed Venue with a Booking on 6–8 June 2027
| **When** its Venue Manager unlists it
| **Then** the Venue drops out of search, and Booking requests for it are rejected
| **And** the Booking on 6–8 June 2027 stands

*Scenario: relist.*

| **Given** an Unlisted Venue
| **When** its Venue Manager relists it
| **Then** it appears in search again and accepts Booking requests

Requirements: FR-7, FR-8, FR-36.

**US-8 Remove a Venue.** As a Venue Manager, I want to delete a Venue I no longer offer, so that it leaves the platform.

*Scenario: no Bookings to come.*

| **Given** a Venue whose Bookings have all ended
| **When** its Venue Manager deletes it
| **Then** Places removes the Venue

*Scenario: a Booking still to come.*

| **Given** a Venue with a Booking that has not ended
| **When** its Venue Manager tries to delete it
| **Then** Places refuses, and the Venue and its Booking stay

Requirements: FR-9, FR-36.

**US-9 Cancel a Booking at my Venue.** As a Venue Manager, I want to see my Venue's Bookings and cancel one when something unforeseen happens, so that the Promoter learns in time that the Venue is no longer theirs on those days.

*Scenario: the Venue Manager cancels.*

| **Given** a Venue with a Booking that has not ended
| **When** its Venue Manager lists the Venue's Bookings and cancels that one, giving a reason
| **Then** Places cancels the Booking
| **And** Places publishes *Booking cancelled*, saying that the Venue Manager cancelled it and why

*Scenario: other users can't see a Venue's Bookings.*

| **Given** a Venue
| **When** a user who is not its Venue Manager asks for its Bookings
| **Then** Places refuses as forbidden

Requirements: FR-28 to FR-32, FR-36.

**US-10 Bill a Booking.** As Billing (G3), I want to learn about each new Booking and its amount, so that I can bill the Promoter without knowing Venue prices.

*Scenario: a Booking is created.*

| **Given** a Booking request that Places accepts
| **When** Places creates the Booking
| **Then** Billing receives *Booking confirmed* with the Promoter, the Venue, the days and the amount

*Scenario: a Booking is cancelled.*

| **Given** a Booking that Billing has billed
| **When** Places cancels the Booking, whoever asked
| **Then** Billing receives *Booking cancelled* with the Booking id, and cancels the bill if it is unpaid

Requirements: FR-22, FR-24, FR-32.

**US-11 See a Venue's Rating.** As a Promoter, I want each Venue to show the Rating Reviews (G1) has computed for it, so that I can compare Venues and search by Rating.

*Scenario: a new Rating.*

| **Given** a Venue whose Rating is 4.2, stamped 10:00
| **When** a refresh reads 4.4, stamped 10:05, from Reviews
| **Then** Places shows 4.4 and searches use it

*Scenario: a late answer.*

| **Given** the same Venue, now rated 4.4 as of 10:05
| **When** an overlapping refresh saves 4.2, stamped 10:00, after it
| **Then** Places keeps 4.4

*Scenario: the last review removed.*

| **Given** a Venue rated 4.4, stamped 10:05
| **When** a refresh answered at 10:10 no longer lists it, because its last review was removed
| **Then** the Venue has no Rating, and a search with a minimum Rating leaves it out

*Scenario: Reviews is down.*

| **Given** a Venue rated 4.4
| **When** a refresh gets no answer from Reviews
| **Then** Places keeps 4.4, and searches use it

Requirements: FR-33, FR-34, NFR-7.

**US-12 Print a Venue on tickets.** As Tickets (G3), I want to read a Venue's name and address, so that tickets show where the Event is held.

*Scenario: the Venue has been unlisted since it was booked.*

| **Given** a Booking at a Venue that is now Unlisted
| **When** Tickets asks Places for the Venue by its id
| **Then** Places returns the Venue, with its name and address

Requirements: FR-10.

## Functional requirements

Each requirement is a single "shall" statement that a test can pass or fail [@wiegers2013, ch. 11]^["“The system shall” or “The user shall,” followed by an action verb, followed by the observable result." (p. 207); "Can a tester devise tests or other verification approaches to determine whether each requirement is properly implemented?" (p. 205)]. They are grouped by feature [@wiegers2013, ch. 10]^["The template in Figure 10-2 shows functional requirements organized by system feature, which is just one possible way to arrange them." (p. 194)]. A Booking *has ended* once its last day is past, in the Europe/Lisbon time zone.

#### Venue catalogue {.unnumbered .unlisted}

| ID | Requirement |
|-------|------------------------------------------------------------------------------|
| FR-1 | Places shall let a user submit a Venue with: a name; an address, including its city; coordinates (latitude and longitude); a capacity in persons; an area in square metres; a price per day in EUR; a type; images; equipment, as items with quantities; and Rooms. |
| FR-2 | Places shall accept only these Venue types: open-air, stadium, pavilion, auditorium, conference centre, other. |
| FR-3 | Places shall keep each Room with a name, a capacity, an area and a layout image, and no price, and shall give a Venue's number of Rooms as the count of its Rooms. |
| FR-4 | Places shall make a submitted Venue Listed at once, with no approval step. |
| FR-5 | Places shall make the user who submits a Venue its Venue Manager, and shall offer no way to change a Venue's Venue Manager. |
| FR-6 | Places shall let a Venue's Venue Manager change any of the Venue's details listed in FR-1. |
| FR-7 | Places shall let a Venue's Venue Manager unlist the Venue when it is Listed and relist it when it is Unlisted, at any time. |
| FR-8 | Places shall leave Unlisted Venues out of search results and reject Booking requests for them, while keeping their existing Bookings. |
| FR-9 | Places shall let a Venue's Venue Manager delete the Venue, and shall refuse to while the Venue has a Booking that has not ended. |
| FR-10 | Places shall return any Venue, Listed or Unlisted, by its id, with its details, its Rooms and its Rating. |

#### Search and availability {.unnumbered .unlisted}

| ID | Requirement |
|-------|------------------------------------------------------------------------------|
| FR-11 | Places shall let any user search the Listed Venues with any combination of these filters, and return the Venues that match every filter given: a date window and a number of days; a minimum capacity; a maximum price per day; a city; a minimum Rating; a Venue type. |
| FR-12 | Given a date window and a number of days *N*, Places shall match a Venue when it has at least *N* consecutive days inside the window that no Booking covers. |
| FR-13 | Places shall reject a search whose number of days is less than 1 or longer than its date window. |
| FR-14 | Given a minimum Rating, Places shall not match a Venue that has no Rating yet. |
| FR-15 | Places shall let any user check one Venue for a first and a last day, and answer either that the Venue is available, because no Booking for it overlaps those days, or which of those days are taken. |

#### Bookings {.unnumbered .unlisted}

| ID | Requirement |
|-------|------------------------------------------------------------------------------|
| FR-16 | Places shall accept a Booking request from Events that names an Event, its Promoter, a Venue, and a first and a last day, both included, and, for a Rebooking, the Event's Booking it replaces. |
| FR-17 | Places shall reject a Booking request for a Venue that is Unlisted or does not exist. |
| FR-18 | Places shall reject a Booking request as a conflict when a Booking for the same Venue overlaps any of its days. |
| FR-19 | Places shall reject a Booking request for an Event that already has a Booking, unless the request is a Rebooking that names that Booking, which Places then cancels in the transaction that creates the new one, so that either both happen or nothing changes. |
| FR-20 | Places shall reject a Booking request whose last day is before its first day, or whose first day is before today in the Europe/Lisbon time zone. |
| FR-21 | Places shall not check a Booking request against the Venue's capacity. |
| FR-22 | Places shall set a Booking's amount, when it creates the Booking, to its number of days × the Venue's price per day, and shall not change the amount when the price changes later. |
| FR-23 | Places shall offer no way to change a Booking's days. |
| FR-24 | When it creates a Booking, Places shall publish *Booking confirmed* with the Booking, the Event, the Promoter, the Venue, the Venue Manager, the days and the amount. |

#### Cancellation {.unnumbered .unlisted}

| ID | Requirement |
|-------|------------------------------------------------------------------------------|
| FR-25 | Places shall let Events cancel a Booking by its id, with an optional reason, and shall answer only once the Booking is cancelled. |
| FR-38 | Places shall let Events read an Event's Booking by the Event's id, and answer with no Booking when the Event has none. |
| FR-26 | When *Event cancelled* arrives on the Log topic, Places shall cancel that Event's Booking if it has one, and otherwise do nothing. |
| FR-27 | Places shall ignore *Event scheduled* and every other message on the Log topic. |
| FR-28 | Places shall let a Venue's Venue Manager list the Venue's Bookings. |
| FR-29 | Places shall let a Venue's Venue Manager cancel a Booking at that Venue, with an optional reason. |
| FR-30 | Places shall refuse to cancel a Booking that has ended. |
| FR-31 | Places shall count a cancelled Booking's days as free from the moment the Booking is cancelled. |
| FR-32 | For every cancellation, whoever made it, Places shall publish *Booking cancelled* with the Booking, the Event, the Promoter, the Venue, who cancelled it (Events or the Venue Manager), and the reason if one was given. |

#### Rating {.unnumbered .unlisted}

| ID | Requirement |
|-------|------------------------------------------------------------------------------|
| FR-33 | Every five minutes, Places shall read each Venue's Rating from Reviews, keep it, and use it in search and when returning the Venue. A Venue that Reviews no longer lists shall lose its Rating. When Reviews doesn't answer, Places shall keep the Rating it holds. |
| FR-34 | Places shall not replace a Venue's Rating with one stamped earlier than the Rating it holds, nor clear a Rating stamped later than the answer that no longer lists the Venue. |

#### Access {.unnumbered .unlisted}

| ID | Requirement |
|-------|------------------------------------------------------------------------------|
| FR-35 | Places shall take the caller's user id from what the Gateway forwards with each user request, and shall reject a user request that carries none as unauthenticated. |
| FR-36 | Places shall reject as forbidden any change to a Venue (update, unlist, relist or delete), any request for its Bookings, and any cancellation of its Bookings, from a user who is not that Venue's Venue Manager. |
| FR-37 | Places shall reject as forbidden a Booking request or a cancellation of a Booking by its id from a user, and any request from Events or Tickets for an operation not theirs: Events may search and read Venues, request Bookings, read an Event's Booking and cancel a Booking by its id, and Tickets may read a Venue. |

## Non-functional requirements

Each non-functional requirement comes with the measure that decides whether Places meets it [@wiegers2013, ch. 14]^["Such characteristics, collectively known as quality attributes, quality factors, quality requirements, quality of service requirements, or the “–ilities,” constitute a major portion of the system’s nonfunctional requirements." (p. 261); "Indicate the scale or units of measure for each attribute and the target, minimum, and maximum values." (p. 267)]. The load figures in NFR-1 are our own assumption, since no group has stated an expected load.

#### Performance {.unnumbered .unlisted}

| ID | Requirement | How it is measured |
|--------|------------------------------------------|----------------------------------------|
| NFR-1 | Places shall answer 95% of availability checks and searches with a date window within 2 seconds under normal operating conditions. | 95th percentile of response time at Places' REST API over a 10-minute load test, with 1,000 Venues, 50 Bookings per Venue and 20 requests per second. |

#### Consistency and integrity {.unnumbered .unlisted}

| ID | Requirement | How it is measured |
|--------|------------------------------------------|----------------------------------------|
| NFR-2 | Once Places has answered a Booking request, a Booking cancellation, or an unlist or relist, every availability check and search it answers afterwards shall reflect that change. | A test runs each change followed at once by a check, 1,000 times: no answer may be out of date. |
| NFR-3 | No two Bookings of one Venue shall overlap, even when Booking requests arrive at the same time. | 50 concurrent Booking requests for overlapping days at one Venue: exactly 1 succeeds and 49 are rejected as conflicts. |

#### Reliability {.unnumbered .unlisted}

| ID | Requirement | How it is measured |
|--------|------------------------------------------|----------------------------------------|
| NFR-4 | Every Booking that Places creates or cancels shall reach the broker as *Booking confirmed* or *Booking cancelled* at least once, even if Places stops between saving the change and sending the message. | Places is stopped right after the database commit and restarted: the message reaches the broker. No message may be lost. |
| NFR-5 | Handling *Event cancelled* twice shall have the same effect as handling it once, since the broker delivers each message at least once. | The message is delivered twice in a test: the stored data and the messages sent are the same as after one delivery. |
| NFR-6 | Every message Places sends shall carry the Booking id, so that consumers can drop a message they receive twice. | Inspection of the message schemas. |
| NFR-7 | Search, availability checks and getting a Venue shall keep working, and keep to NFR-1, while Reviews or Events is unavailable. | The NFR-1 load test is rerun with Reviews and Events stopped. |

#### Interoperability {.unnumbered .unlisted}

| ID | Requirement | How it is measured |
|--------|------------------------------------------|----------------------------------------|
| NFR-8 | Places' REST API shall be described in one OpenAPI document, a single document that conforms to the OpenAPI Specification [@openapi]^["The OpenAPI Specification (OAS) defines a standard, programming language-agnostic interface description for HTTP APIs, which allows both humans and computers to discover and understand the capabilities of a service without requiring access to source code, additional documentation, or inspection of network traffic."; "An OpenAPI Document is a single JSON or YAML document that conforms to the OpenAPI Specification."]. It shall lint without errors. | `npx @redocly/cli lint openapi.yaml` exits with status 0. |
| NFR-9 | Places' API and messages shall use UUIDs for ids, ISO 8601 for dates and times, the Europe/Lisbon time zone for whole days, and EUR for amounts. Errors shall be problem details, which use the `application/problem+json` media type [@rfc9457]^["This specification's aim is to define common error formats for applications that need one so that they aren't required to define their own"; "The canonical model for problem details is a JSON [JSON] object. When serialized in a JSON document, that format is identified with the “application/problem+json” media type."]. | Inspection of the OpenAPI document and message schemas, and a test of each error response. |

#### Security {.unnumbered .unlisted}

| ID | Requirement | How it is measured |
|--------|------------------------------------------|----------------------------------------|
| NFR-10 | Users shall reach Places only through the Gateway, because Places trusts the identity the Gateway forwards. | A request sent to Places from outside the platform's network, bypassing the Gateway, gets no answer. |

#### Constraints {.unnumbered .unlisted}

| ID | Requirement | How it is measured |
|--------|------------------------------------------|----------------------------------------|
| NFR-11 | Places shall keep its data in its own PostgreSQL database, which no other service reads or writes, and shall prevent overlapping Bookings in the database with an exclusion constraint. Exclusion constraints ensure that if any two rows are compared on the specified columns or expressions using the specified operators, at least one of these operator comparisons will return false or null [@postgresql]^["Exclusion constraints ensure that if any two rows are compared on the specified columns or expressions using the specified operators, at least one of these operator comparisons will return false or null."]. Other services reach Places only through its REST API and broker messages. | Inspection of the schema and the deployment: only Places holds the database credentials. |
| NFR-12 | Places shall be built and deployed as one service that owns the Venue catalogue, the Bookings and the Ratings in one database. | Inspection of the deployment. |

## Scope

Delivery 1 covers the Venue catalogue with its Rooms, Listed and Unlisted Venues, search and availability, Bookings and their cancellation from either side, the Ratings Places keeps, and the messages Places exchanges with the other groups.

The following are out of scope. Where another group or a later delivery covers an item, the table says so.

| Out of scope | Where it stands |
|------------------------------------|----------------------------------------------------------|
| Approving Venues before they are Listed | Not needed: a submitted Venue is Listed at once (FR-4). |
| Transferring a Venue to another Venue Manager | Not offered (FR-5). |
| Booking a Room on its own | The Venue is the bookable unit; Rooms are part of its description. |
| One Event at several Venues, or on separate days | Not offered: an Event holds at most one Booking, and separate days are separate Events (FR-19). |
| Changing a Booking's days | Not offered: a Rebooking replaces the Booking with a new one, and a Booking's days never change (FR-19, FR-23). |
| Checking the Event's expected attendance against the Venue's capacity | Capacity is a search filter; the Promoter sets the ticket cap, which can change after booking (FR-21). |
| Hourly, seasonal or per-date pricing | Price per day only (FR-22). |
| Distance search, keyword search and equipment filters | Not offered (FR-11). |
| Blocking days outside Bookings, such as for maintenance or rentals made outside the platform | Not in delivery 1; question L1 asks the professor. |
| Creating bills | Billing (G3) creates the bill from *Booking confirmed* (FR-24). |
| Cancelling bills, refunds and cancellation fees | Billing (G3) cancels an unpaid bill when *Booking cancelled* arrives. For delivery 1 it refunds no paid bill and charges no fee, whoever cancelled the Booking. |
| Paying the Venue Manager a Booking's amount | Billing (G3) collects the amount but pays no one out in delivery 1, and keeps `venueManagerId` on each bill. |
| Deciding who may rate a Venue, and computing Ratings | Reviews (G1), which reads none of Places' messages. Places reads each Venue's Rating from it (FR-33). |
| Authenticating users | The Gateway (G4) checks the token and forwards the user id (FR-35). |
| Acting on *Event scheduled* or *Event ended* | Places ignores them (FR-27). |
| *Venue updated*, a message telling other groups that a Venue's details changed | Not in delivery 1: Events reads a Venue with `GET /venues/{venueId}` when it needs it. A candidate for a later delivery. |
| Deploying and operating Places (DevOps operations) | Later deliveries. In this report, "system operations" means the commands and queries Places handles. |
