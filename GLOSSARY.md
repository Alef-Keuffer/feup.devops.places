# Places

The Places subsystem (group 5) of the Event Management system: the catalogue of venues promoters can hold events in, and the calendar of which venues are taken when.

## Language

**Place**:
Umbrella word used in requirements for "somewhere an event can happen"; in the model it is always either a Venue or a Room.
_Avoid_: Location, space (when a precise term is meant)

**Venue**:
A physical site submitted to the platform, with an address, images and a Rating; the unit a Promoter books for an Event.
_Avoid_: Place (when the site specifically is meant), building

**Room**:
A space inside a Venue, shown as part of the Venue's description; a Room is never booked on its own.
_Avoid_: Hall, space

**Promoter**:
A user who organises Events and books Venues for them.
_Avoid_: Organiser, client

**Venue Manager**:
The user who submitted a Venue, and the only one allowed to change it and its Rooms; a user is the Venue Manager of each Venue they submitted and of no other, and may also be a Promoter.
_Avoid_: Owner, landlord, admin

**Listed**:
A Venue that appears in search and accepts new Bookings; a Venue is Listed as soon as it is submitted.
_Avoid_: Published, active, approved

**Unlisted**:
A Venue its Venue Manager has taken out of search; it accepts no new Bookings, but its existing Bookings stand.
_Avoid_: Hidden, archived, deleted

**Booking**:
A Venue reserved for one Event over consecutive whole days; an Event holds at most one Booking, and a Venue is available exactly when no Booking overlaps the requested days.
_Avoid_: Reservation, schedule entry

**Rebooking**:
A Booking request that replaces its Event's Booking with a new one: either the old Booking is cancelled and the new one is created, or nothing changes.
_Avoid_: Move, reschedule, postpone (postponing is what happens to the Event)

**Rating**:
A Venue's average review score, as Places last read it from the Reviews subsystem.
_Avoid_: Reputation, score
