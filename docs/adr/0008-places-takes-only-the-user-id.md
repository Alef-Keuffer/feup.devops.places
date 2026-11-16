# Places takes only the user id from the Gateway

The Gateway (G4) forwards each user's id in `X-User-Id`, and Places takes nothing else from it: no roles. The id is all Places needs, because a Venue's Venue Manager is the user who submitted it (FR-5), and every check Places makes on a user compares the caller's id with that. Any signed-in user may submit a Venue. Until 2026-11-16 the Gateway was also to forward `X-User-Roles`, holding `promoter`, `venue-manager`, both or none, and Places refused a Venue submission from a user without `venue-manager` (FR-36). We dropped it while reviewing our draft to G4 (`docs/groups/drafts/g5-to-g4.md`; `docs/grilling/2026-11-16-g4-identity.md`).

## Considered options

- **The Gateway forwards roles, `promoter` and `venue-manager` (what we had).** Rejected, for four reasons.
  - Places used one role, once. `venue-manager` gated `submitVenue` alone. Every other Venue Manager operation checks that the caller is that Venue's Venue Manager (FR-37), which the role adds nothing to. `promoter` gated nothing: any user may search and read Venues, and Promoters book through Events, which calls Places directly. FR-38, which lets a user with both roles do what either allows, existed only because roles did.
  - G4 probably can't know who is a Promoter. In G2's report, a user becomes a Promoter by registering with G2's own Promoter Service: "An authenticated user registers as a promoter, providing a tax ID (NIF) and a contact email" (their FR1, `docs/groups/2026-11-16-g2-promoters-and-events-report.pdf`). G4 would have to learn it from G2.
  - Nobody said who grants `venue-manager`. We never asked G4 to keep roles or said how a user gets one. If G4 keeps none, nobody can submit a Venue; if a user gets the role by asking for it, the role vets no one.
  - An empty header doesn't survive every gateway. A user with neither role had to get `X-User-Roles` empty, because Places answered `401` to a user request without both user headers. A Gateway built on nginx drops it: "If the value of a header field is an empty string then this field will not be passed to a proxied server" (nginx, `proxy_set_header`, <https://nginx.org/en/docs/http/ngx_http_proxy_module.html#proxy_set_header>, checked 2026-11-16). Such a user would be refused even a search.
- **The Gateway forwards `venue-manager` alone.** Rejected. It still asks G4 to keep a role for Places and to decide who gets it, for one check that FR-5 already makes, and a user without the role still needs either an empty header or a rule that a missing header means no role.
- **Only the user id (chosen).** Being a Venue Manager is a relation between a user and a Venue, which Places already stores (FR-5), not a kind of user that G4 must know about. G4 keeps nothing for Places, and forwards one header it has anyway.

## Consequences

- Any signed-in user can submit a Venue, and it is Listed at once (FR-4). Someone could list a Venue that doesn't exist, or many of them. We accept this for delivery 1: the role never vetted anyone, and Venue approval, already out of scope, is the fix for a later delivery.
- FR-36 and FR-38 go, and FR-37 becomes FR-36. FR-1 lets any user submit a Venue, and FR-35 takes only the user id.
- Places rejects a request with neither `X-User-Id` nor `X-Service-Name` as unauthenticated, with `401`. The Gateway removes those two headers from whatever a user sends, and Places ignores any `X-User-Roles`.
- The user id must never change and never be given to another user, since Places stores it as a Venue's Venue Manager, and Billing (G3) compares it with `promoterId`. L11 asks G4.
- *Booking cancelled* keeps `cancelledBy: venue-manager`, which G2 already has (`docs/groups/2026-11-16-g5-to-g2.md`). It says the Venue's Venue Manager cancelled, and no longer echoes a header value.
- If G4 forwards a signed token instead of the header, Richardson's Access token pattern, which the report's Identity and access section names, Places reads the user id from it, and nothing else changes.
