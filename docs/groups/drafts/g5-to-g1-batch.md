# Group 5 (Places) → Group 1 (Reviews)

> A WhatsApp message to G1, our reply to `../2026-11-16-g1-to-g5-ratings.md`, as `../../grilling/2026-11-14-delivery-1-report.md` (Since the session) settled it. Paste it from below this note.

Thanks, that answers all three questions, and the attendance rule is clear.

On the queue: the batch call is enough for us, so you don't need to publish anything. With it, each refresh is one call every five minutes. Each refresh reads every Rating again, so an update we miss is put right by the next one, while a lost message would leave a Venue's Rating wrong until its next review. A delay of up to five minutes is fine for a search filter.

For the batch call, one answer with every Venue's Rating is all we need, each entry as your single-Venue GET returns it (`venueId`, `average`, `count`, `stampedAt`). We'll read a `count` of 0 as "no Rating", whatever `average` holds.
