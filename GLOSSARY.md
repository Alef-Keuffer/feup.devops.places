# Places

The Places subsystem (group 5) of the Event Management system: the catalogue of venues promoters can hold events in, and the calendar of which rooms are taken when.

## Language

**Place**:
Umbrella word used in requirements for "somewhere an event can happen"; in the model it is always either a Venue or a Room.
_Avoid_: Location, space (when a precise term is meant)

**Venue**:
A physical site submitted to the platform, with an address, images and a Rating, containing one or more Rooms.
_Avoid_: Place (when the site specifically is meant), building

**Room**:
The bookable unit of a Venue, with its own capacity, area, layout, equipment and price.
_Avoid_: Hall, space

**Venue Manager**:
The person who submits a Venue to the platform and is the only one allowed to change it and its Rooms.
_Avoid_: Owner, landlord, admin

**Booking**:
A Room reserved for one Event over a period; Rooms are available exactly when no Booking overlaps the requested period.
_Avoid_: Reservation, schedule entry

**Rating**:
A Venue's average review score, as last reported by the Reviews subsystem.
_Avoid_: Reputation, score
