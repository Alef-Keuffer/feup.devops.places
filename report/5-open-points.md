# Open points

Delivery 1 leaves some points open, and this section collects them: what Billing's choice on refunds means for Promoters, what delivery 1 leaves out, and the questions we have asked the professor and the other groups. Wiegers and Beatty advise marking each piece of information that is still missing, rather than leaving the gap unstated, and resolving it before the requirements it affects are implemented [@wiegers2013, ch. 10]. For each question, this section gives the position the report takes until the answer comes.

## Paid bills are not refunded

Billing (G3) creates the bill from *Booking confirmed*, and cancels it on *Booking cancelled* if the Promoter hasn't paid it yet. A paid bill is not refunded, whoever cancelled the Booking; G3 has told us this is deliberate for delivery 1. It matters most when a Venue Manager cancels after the Promoter has paid: the Promoter has lost both the Venue and the amount. Places can't change this on its own, because bills belong to Billing (Table \ref{tab:ownership}).

## Out of scope for delivery 1

Delivery 1 leaves out Venue approval, transferring a Venue to another Venue Manager, hourly or seasonal pricing, distance search, keyword and equipment filters, blocking days outside Bookings, and refunds and cancellation fees. The Scope in the Application requirements section says where each stands. One of them is open rather than settled: blocking days waits on question L1 below. Refunds are Billing's to decide, and the section above gives its choice.

## Questions for later

Table \ref{tab:questions} lists the questions, whom we asked, and the position this report takes until they answer.

| # | Asked of | Question | Position meanwhile |
|----|--------------|------------------------------------|------------------------------------------------|
| L1 | The professor | Can a Venue Manager block days for maintenance or for rentals outside the platform? | Not in delivery 1: only Bookings take a Venue's days (FR-12, FR-15). |
| L2 | The professor | Will later deliveries deploy all groups to one shared cluster, and is the broker or the stack mandated? | Deploying Places is for later deliveries. Places needs its own PostgreSQL database (NFR-11); a mandated stack without it would mean replacing the exclusion constraint that the Services section chose to prevent overlapping Bookings. For the broker, see L7. |
| L3 | G2 | Will you rename `Room_request` to Booking request on the shared diagram? | This report says Booking request: Events asks for a whole Venue (FR-16), and a Room is never booked on its own. |
| L4 | G2 and G4 | Which messages go on the Log topic? | Places reads only *Event cancelled* from the Log topic and ignores every other message there (FR-26, FR-27). |
| L5 | G3 | Does Tickets read a Venue's name and address with a REST GET? | Answered: yes. G3 confirmed that Tickets calls `GET /venues/{venueId}` (flow 3 in Table \ref{tab:flows}) once per Event, directly with `X-Service-Name: tickets`, and relies on it returning Unlisted Venues too (FR-10, US-12). |
| L6 | G1 | Will Reviews enforce "only the Promoter who booked may rate" from our Booking messages, and publish *Rating changed* with the Venue id, average, review count and timestamp? | We assume so, as the Messaging and collaborations section describes. Places reads the Venue id, the average and the timestamp, and doesn't keep the review count. Until the first *Rating changed* for a Venue arrives, the Venue has no Rating, and a search with a minimum Rating leaves it out (FR-14). |
| L7 | G4 | Which broker will you run, and is delivery at-least-once? | Any broker with publish-subscribe channels: each message names its own type, so Places relies on no feature of a particular broker. We assume at-least-once delivery and nothing more: Places' handlers are safe to run twice (NFR-5), and we ask consumers to drop a second message by its Booking id (NFR-6). |
| L8 | G2 | Will the Promoter id in your Booking requests be the Promoter's user id, the value the Gateway forwards as `X-User-Id`, rather than the id of your Promoter entity? | We assume so, and have told G3 that `promoterId` is the user id: Billing compares it with `X-User-Id` to check who pays a bill, and Reviews to check who may rate a Venue. Places can't check it, because Events calls Places directly, not through the Gateway. |
| L9 | G3 | Billing doesn't read `venueManagerId`, so who pays the Venue Manager a Booking's amount? Is it out of scope for delivery 1, like paying Promoters their ticket revenue? | We assume it is out of scope, and that nobody pays the Venue Manager in delivery 1. *Booking confirmed* carries `venueManagerId` for whichever group takes it on. |

: The questions asked for delivery 1, and the answers so far. \label{tab:questions}
