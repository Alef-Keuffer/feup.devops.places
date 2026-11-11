# Venue Rating is cached from Reviews events, not fetched per search

Places keeps each Venue's Rating locally and updates it from a "rating changed" message that Reviews (G1) publishes on the broker. We rejected calling Reviews synchronously on every search: filtering by minimum Rating would then depend on Reviews being up and would put the 2-second p95 availability target at risk. The cost is a Rating that may lag slightly behind the latest reviews. This relies on G1 agreeing to publish the message.
