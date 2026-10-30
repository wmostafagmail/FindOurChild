"""Atomic publication into isolated demo-control DB; no operational candidate API."""

from .records import require


class Fence:
    def __init__(self, conn):
        self.conn = conn

    def publish(self, job, token, epoch, revision, now, *, instance, organization, snapshot):
        # now is caller metadata only. Database clock is authoritative; no clock
        # supplied by a browser/worker can extend the deadline.
        require(now.tzinfo is not None, "clock_untrusted")
        with self.conn.transaction():
            return self.conn.execute(
                "SELECT demo_governance.publish(%s,%s,%s,%s,%s,%s,%s)",
                (job, token, epoch, revision, instance, organization, snapshot),
            ).fetchone()[0]
