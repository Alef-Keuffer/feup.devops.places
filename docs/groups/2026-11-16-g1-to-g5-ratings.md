# Group 1 (Reviews) → Group 5 (Places)

> G1's follow-up to `2026-11-16-g5-to-g1-ratings.md`, answering its points 2 and 3 in the same numbering. Code is marked as code here; the words are G1's. Their message breaks off after `"average`, so it doesn't say what `average` holds for a Venue with no reviews.

2. We explained ourselves badly: only users who attended the Event will be able to review it (and its Venue). Since reviews reach us as a POST, we'll call the Tickets service at that moment to check whether the user attended. So a Venue Manager can't rate their own Venue unless they actually attended.

3. Given your search use case, publishing rating changes on a queue might make more sense than polling. We thought that it would only be for showing. I need to discuss with my group. In the meantime, the answers that don't depend on that decision:
   - A Venue with no reviews returns `200` with `"count": 0` and `"average`.
   - Calling us directly with `X-Service-Name: places` works for the rating GETs, since they're read-only and public.
   - Batch endpoint is ok. We'll share how it will be in the report today if everything goes well.
