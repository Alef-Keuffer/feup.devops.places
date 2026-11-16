# Group 5 (Places) → all groups: binding queues

> Draft, not sent. Adds to the broker rule in `../2026-11-16-g5-to-all.md` the two points it left out: bind before the first message is published, and declare the publisher's exchange before binding. When sent, move it to `docs/groups/<date>-g5-to-all-binding.md`. Paste from the next line on.

Two additions to our broker rule:

- Bind your queue before the first message you need is published. RabbitMQ confirms a message that matches no queue and then drops it, so the publisher never sends it again.
- Before binding, declare the publisher's exchange yourselves, with the same settings: durable, topic, named after the publisher. RabbitMQ refuses a binding to an exchange that doesn't exist yet, and declaring one that already exists with the same settings changes nothing. So it doesn't matter which group starts first.

For our messages, declare `places` and bind your queue to it before we start publishing.
