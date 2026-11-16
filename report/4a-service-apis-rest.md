# Service APIs and collaborations

Richardson's third step defines each service's API: the operations it offers and the messages it publishes [@richardson2018, sec. 2.2.6]. He first assigns each system operation to a service, then works out the collaborations between services that the operations need. Places is one service, so every operation of Table \ref{tab:operations} is Places'. Twelve of them are requests from a user, Events or Tickets, who waits for the answer, and they are REST endpoints, described in this section. The other two start from messages, and the Messaging and collaborations section describes them with the messages Places sends.

## REST API

Places' REST API is described in one OpenAPI 3.1 document [@openapi], `openapi.yaml` at the root of the repository, which Appendix \ref{openapi-specification} reproduces in full. Richardson names OpenAPI as the most popular language for specifying REST APIs [@richardson2018, sec. 3.2.1]. Other groups can read the document, test against it and generate code from it, and `npx @redocly/cli lint openapi.yaml` passes with no errors (NFR-8). Each endpoint's `operationId` is the name of the system operation it implements, so the document traces back to the operations and, through them, to the requirements.

These operations are REST calls, not messages, because each caller needs the answer before it goes on. A Promoter waits for search results. Events needs to know whether Places accepted a Booking request, and at what amount, or rejected it as a conflict. And a cancellation must be complete before Events sends its next Booking request, so that the new request can't collide with the old Booking (US-4). Richardson calls this the request/response interaction style: the caller sends a request and waits for the reply [@richardson2018, sec. 3.1.1].

### Endpoints

Table \ref{tab:endpoints} maps each operation to its endpoint. *Any user* means any user the Gateway forwards, whatever their roles. Where the last column says yes, the caller must also be the Venue's Venue Manager.

| Endpoint | Operation | Success | Who may call it | Venue Manager only |
|-----------------------------------------------|---------------------|--------|---------------|---------|
| `GET /venues` | `searchVenues` | 200 | Any user | No |
| `POST /venues` | `submitVenue` | 201 | Venue Manager role | No |
| `GET /venues/{venueId}` | `getVenue` | 200 | Any user, Tickets | No |
| `PATCH /venues/{venueId}` | `updateVenue` | 204 | Venue Manager role | Yes |
| `DELETE /venues/{venueId}` | `deleteVenue` | 204 | Venue Manager role | Yes |
| `POST /venues/{venueId}/unlist` | `unlistVenue` | 204 | Venue Manager role | Yes |
| `POST /venues/{venueId}/relist` | `relistVenue` | 204 | Venue Manager role | Yes |
| `GET /venues/{venueId}/availability` | `checkAvailability` | 200 | Any user | No |
| `GET /venues/{venueId}/bookings` | `listVenueBookings` | 200 | Venue Manager role | Yes |
| `POST /bookings` | `requestBooking` | 201 | Events | No |
| `DELETE /bookings/{bookingId}` | `cancelBooking` | 204 | Events | No |
| `DELETE /venues/{venueId}/bookings/{bookingId}` | `cancelVenueBooking` | 204 | Venue Manager role | Yes |

: The REST endpoints of Places. \label{tab:endpoints}

The endpoints are built around Places' two resources, Venues and Bookings. `GET` reads and changes nothing, `POST` creates, and `DELETE` removes [@rfc9110, sec. 9.3], while `PATCH` changes some of a Venue's details. This is level 2 of the REST maturity model that Richardson describes [@richardson2018, sec. 3.2.1]. `submitVenue` and `requestBooking` answer 201 with the new Venue or Booking; the other commands return nothing, so they answer 204 with no content. Three choices need a reason.

- **Unlisting and relisting are sub-resources.** They change one aspect of a Venue, and each has its own precondition: only a Listed Venue can be unlisted, and only an Unlisted one relisted (FR-7). For operations that don't map onto an HTTP method, Richardson defines a sub-resource that takes a `POST`, as in his `POST /orders/{orderId}/cancel` [@richardson2018, sec. 3.2.1]. We rejected a `PATCH` that sets `listed` to false: `updateVenue` leaves whether the Venue is Listed unchanged, and one endpoint would then carry two operations with different preconditions.
- **A Booking request names its Venue in the body.** `POST /bookings` carries the Event, its Promoter, the Venue, and the first and last days (FR-16), which are the parameters of `requestBooking`. A Booking then has a path of its own, `/bookings/{bookingId}`, by which Events cancels it (FR-25). A Booking request for a Venue that doesn't exist (FR-17) is answered 422 rather than 404, because the path it was sent to, `/bookings`, does exist: 422 means that Places understood the request but can't carry it out [@rfc9110, sec. 15.5.21].
- **Cancellation is a `DELETE`, answered once it is done.** Events cancels its Event's Booking by the Booking's id alone (FR-25), with `DELETE /bookings/{bookingId}`. A Venue Manager cancels a Booking under the Venue, at `DELETE /venues/{venueId}/bookings/{bookingId}`, beside the list of the Venue's Bookings they found it in (FR-28, FR-29). Who cancelled, which *Booking cancelled* reports (FR-32), follows from the endpoint, so no caller can set it wrongly. Places answers only once the Booking's days are free, so a Booking request that Events sends straight after can take them (FR-25, US-4). The optional reason is a query parameter, because content in a `DELETE` request has no defined meaning, and some implementations reject the request [@rfc9110, sec. 9.3.5].

### Identity and access

The Gateway checks each user's token and forwards the request with the user's id and roles (FR-35), so Places never handles tokens: authenticating requests at the edge is one of the jobs Richardson gives an API gateway [@richardson2018, ch. 8]. Events and Tickets don't go through the Gateway, which serves users. They call Places directly on the platform's network and name themselves. This is how Places tells a call from Events apart from a user's, which the System operations section left to this one. Table \ref{tab:identity} lists the three headers.

| Header | Set by | Value |
|------------------|-------------------|------------------------------------------------------|
| `X-User-Id` | The Gateway | The user's id. |
| `X-User-Roles` | The Gateway | The user's roles, comma-separated: `promoter`, `venue-manager`, or both. |
| `X-Service-Name` | Events or Tickets | `events` or `tickets`. |

: The headers that identify the caller. \label{tab:identity}

Places checks every request in three steps:

1. A request that carries neither both `X-User-Id` and `X-User-Roles` nor `X-Service-Name` is rejected as unauthenticated, with 401 (FR-35).
2. A request from a role or service that Table \ref{tab:endpoints} doesn't allow is rejected as forbidden, with 403 (FR-36). Places looks for the role it needs in the user's list, so a user with both roles may do whatever either role allows (FR-38).
3. Where only the Venue's Venue Manager may call the endpoint, Places compares the caller's id with the Venue's Venue Manager, and rejects any other user as forbidden, with 403 (FR-37).

In `openapi.yaml`, the three headers are security schemes, and each operation's `security` lists the roles or the service it allows. OpenAPI 3.1 allows role names there for schemes other than OAuth [@openapi, sec. 4.8.30]. Each operation's description also says whether the caller must be the Venue's Venue Manager.

Places trusts these headers without checking them. That is safe only because users can reach Places through the Gateway alone (NFR-10), and because the Gateway removes all three headers from whatever a user sends before it sets its own. We ask G4 for both (L12). The headers still let any service inside the platform's network claim to be Events. Richardson's Access token pattern closes that gap: the Gateway passes each service a signed token, such as a JWT, holding the user's identity and roles, and the service checks the signature [@richardson2018, ch. 11]. We chose plain headers for delivery 1 because every group can set and read them without sharing keys. If G4 issues signed tokens, Places will check them instead, and the endpoints and the access rules stay the same.

### Conventions

We propose these conventions to every group, so that ids, days, amounts and errors mean the same in every service's API and messages (NFR-9). Table \ref{tab:conventions} gives each with its reason.

| Convention | Choice | Reason |
|--------------|--------------------------------|------------------------------------------------------|
| Ids | UUIDs [@rfc9562]. | Every group creates its own ids, and Places stores other groups' ids (the Event, the Promoter, the Venue Manager) as they store ours. A UUID is unique without a counter shared between services, so each service creates ids on its own, and one group's ids can't clash with another's. |
| Dates and times | ISO 8601: calendar dates such as `2027-06-06`, and timestamps with their offset from UTC. In OpenAPI these are the `date` and `date-time` formats, RFC 3339's profile of ISO 8601 [@rfc3339]. | One text form that every language parses, that sorts as text in date order, and that can't be misread the way `06/07/2027` can, as 6 July or as June 7. |
| Time zone | A day is a whole day in the Europe/Lisbon time zone, and is sent with no zone of its own. | A day starts at a different instant in each time zone, so `2027-06-06` names the same day in every service only if they agree on one zone. Places needs it to decide what *today* is (FR-20) and when a Booking has ended (FR-30). Europe/Lisbon is the Time Zone Database's zone for mainland Portugal, Porto included, where the system is built [@tzdb]. As a named zone, unlike a fixed offset from UTC, it follows the change between winter and summer time. |
| Money | EUR, as a decimal string with two decimals, such as `"800.00"`. | One currency, so amounts need no currency field and no conversion. A string, because JSON parsers commonly read numbers as binary floating point [@rfc8259, sec. 6], which can't hold most amounts in cents exactly, and Billing must receive the exact amount. |
| Errors | RFC 9457 problem details, as `application/problem+json` [@rfc9457]. | One error format for every service, so a caller handles errors from any group the same way. The problem's `type` tells apart rejections with the same status, such as the three conflicts of a Booking request, without parsing text. |
| API description | One OpenAPI document per service [@openapi]. | Every group can read the others' APIs in one format, check them with the same tools, and generate code from them. |

: The conventions we propose to every group. \label{tab:conventions}

### Errors

Every rejection that the System operations section names maps to one error response, listed in Table \ref{tab:errors}. A problem has its own `type` only where the caller may need to act on it. Every other problem has the type `about:blank`, whose `title` is the HTTP status phrase, such as "Not Found" [@rfc9457, sec. 4.2.1]. The types are relative URIs that start with their full path, as RFC 9457 recommends for a type that isn't an absolute URI [@rfc9457, sec. 3.1.1]. They are relative because Places has no address outside the platform yet; once it has one, they can become absolute URIs under it.

| Status | Problem type | When |
|--------|-----------------------------------|----------------------------------------------------|
| 400 | `about:blank` | A parameter or the body is malformed or out of range: for instance, a search whose number of days is less than 1 or longer than its window (FR-13), or a Booking request whose last day is before its first day, or whose first day has passed (FR-20). |
| 401 | `about:blank` | The request names neither a user nor a service (FR-35). |
| 403 | `about:blank` | The caller's role or service isn't allowed, or the caller isn't the Venue's Venue Manager (FR-36, FR-37). |
| 404 | `about:blank` | No Venue or Booking has the id in the path, or the Booking isn't at that Venue. |
| 409 | `/problems/days-taken` | A Booking of the Venue overlaps the requested days (FR-18). |
| 409 | `/problems/event-already-booked` | The Event already has a Booking (FR-19). |
| 409 | `/problems/venue-unlisted` | A Booking request for an Unlisted Venue, or `unlistVenue` on one (FR-7, FR-8). |
| 409 | `/problems/venue-listed` | `relistVenue` on a Listed Venue (FR-7). |
| 409 | `/problems/venue-has-bookings` | `deleteVenue` on a Venue with a Booking that has not ended (FR-9). |
| 409 | `/problems/booking-ended` | A cancellation of a Booking that has ended (FR-30). |
| 422 | `/problems/unknown-venue` | A Booking request for a Venue that doesn't exist (FR-17). |

: The error responses of Places. \label{tab:errors}

The conflicts `days-taken` and `event-already-booked` are how Places answers when the exclusion constraint or the unique constraint of the Services section refuses a Booking. They are a normal outcome of a Booking request, which Events shows the Promoter, not an error to retry.
