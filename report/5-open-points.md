# Open points

Delivery 1 leaves some points open, and this section collects them: a gap that no group covers, what delivery 1 leaves out, and the questions we have asked the professor and the other groups. Wiegers and Beatty advise marking each piece of information that is still missing, rather than leaving the gap unstated, and resolving it before the requirements it affects are implemented [@wiegers2013, chs. 10–11]. For each question, this section gives the position the report takes until the answer comes.

## No group handles refunds

Billing (G3) creates the bill from *Booking confirmed* and ignores *Booking cancelled*, so the bill for a cancelled Booking still stands, whoever cancelled it. It matters most when a Venue Manager cancels: the Promoter has lost the Venue and still owes the amount. Places can't close the gap on its own, because bills belong to Billing (Table \ref{tab:ownership}).

## Out of scope for delivery 1

Delivery 1 leaves out Venue approval, transferring a Venue to another Venue Manager, hourly or seasonal pricing, distance search, keyword and equipment filters, blocking days outside Bookings, and refunds and cancellation fees. The Scope in the Application requirements section says where each stands. Two of them are open rather than settled: blocking days waits on question L1 below, and refunds are the gap above.

## Questions for later

Table \ref{tab:questions} lists the questions, whom we asked, and the position this report takes until they answer.

| # | Asked of | Question | Position meanwhile |
|----|--------------|------------------------------------|------------------------------------------------|
| L1 | The professor | Can a Venue Manager block days for maintenance or for rentals outside the platform? | Not in delivery 1: only Bookings take a Venue's days (FR-12, FR-15). |
| L2 | The professor | Will later deliveries deploy all groups to one shared cluster, and is the broker or the stack mandated? | Deploying Places is for later deliveries. Places needs its own PostgreSQL database (NFR-11); a mandated stack without it would mean replacing the exclusion constraint that the Services section chose to prevent overlapping Bookings. For the broker, see L7. |
| L3 | G2 | Will you rename `Room_request` to Booking request on the shared diagram? | This report says Booking request: Events asks for a whole Venue (FR-16), and a Room is never booked on its own. |
| L4 | G2 and G4 | Which messages go on the Log topic? | Places reads only *Event cancelled* from the Log topic and ignores every other message there (FR-26, FR-27). |
| L5 | G3 | Does Tickets read a Venue's name and address with a REST GET? | We assume so: `GET /venues/{venueId}` (flow 3 in Table \ref{tab:flows}), which returns Unlisted Venues too (FR-10, US-12). |
| L6 | G1 | Will Reviews enforce "only the Promoter who booked may rate" from our Booking messages, and publish *Rating changed* with the Venue id, average, review count and timestamp? | We assume so, as the Messaging and collaborations section describes. Places reads the Venue id, the average and the timestamp, and doesn't keep the review count. Until the first *Rating changed* for a Venue arrives, the Venue has no Rating, and a search with a minimum Rating leaves it out (FR-14). |
| L7 | G4 | Which broker will you run, and is delivery at-least-once? | Any broker with publish-subscribe channels: each message names its own type, so Places relies on no feature of a particular broker. We assume at-least-once delivery and nothing more: Places' handlers are safe to run twice (NFR-5), and we ask consumers to drop a second message by its Booking id (NFR-6). |

: The questions open at delivery 1. \label{tab:questions}
