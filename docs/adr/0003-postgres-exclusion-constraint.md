# Places has its own PostgreSQL database; overlapping Bookings are prevented by an exclusion constraint

Places owns a private PostgreSQL database (database per service), and no other service reads it directly. We chose Postgres so that a range exclusion constraint on (Room, booked period) prevents double-booking even when requests arrive concurrently, which is what ADR-0001 depends on. The alternative was to check for overlaps in application code, which can let two concurrent requests both pass. The rest of the system reaches Places only through its REST API, documented in OpenAPI.
