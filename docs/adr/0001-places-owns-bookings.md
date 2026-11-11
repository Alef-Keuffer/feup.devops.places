# Places owns Bookings and is the source of truth for availability

Events asks Places to book a Room (`Room_request`), and Places accepts the request or rejects it as a conflict. Availability means no overlapping Booking. We rejected deriving availability by querying Events, because only the service that owns a Room's calendar can serialise two competing requests for the same Room and dates. Without that, double-booking is possible, Places depends on Events at runtime, and we can't meet the requirement that confirmed changes are reflected in later availability queries.
