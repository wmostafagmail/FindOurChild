"""Least-privilege leased media worker. No network route to the Internet or model provider."""

import json
import os
import time
from pathlib import Path
from urllib.parse import urlparse
from uuid import NAMESPACE_URL, uuid5

import psycopg

from . import media


def connection():
    url = os.environ["FOC_WORKER_DATABASE_URL"]
    parsed = urlparse(url)
    if (
        os.environ.get("FOC_DATA_CLASS") != "synthetic"
        or parsed.hostname != "db"
        or parsed.path != "/foc_synthetic"
        or parsed.username != "foc_worker"
    ):
        raise RuntimeError("Synthetic worker database required")
    return psycopg.connect(url, connect_timeout=3)


def once():
    with connection() as conn:
        job = conn.execute("SELECT platform.media_lease()").fetchone()[0]
    if job is None:
        return False
    outcome = "error"
    version = None
    ov = None
    dv = None
    dkey = None
    sha = None
    size = None
    try:
        data = media.get(
            "WORKER", "foc-quarantine", job["quarantine_key"], job["quarantine_version"], job["wrapped_key"]
        )
        if media.checksum(data) != job["expected_hash"][2:] or len(data) != job["expected_bytes"]:
            outcome = "invalid"
        else:
            outcome, version = media.scan(data)
            if outcome == "clean":
                try:
                    derivative = media.sanitize(data, job["expected_mime"])
                except ValueError:
                    outcome = "invalid"
                if outcome == "clean":
                    ov = media.put_once("foc-original", job["quarantine_key"], data, job["wrapped_key"])
                    dkey = str(uuid5(NAMESPACE_URL, "foc-synthetic-derivative:" + job["intent_id"]))
                    dv = media.put_once("foc-derivative", dkey, derivative, job["wrapped_key"])
                    sha = bytes.fromhex(media.checksum(derivative))
                    size = len(derivative)
    except (*media.FAILURES, psycopg.Error):
        # No exception text, file bytes, credentials, S3 URLs or claimed names in logs.
        outcome = "error"
    with connection() as conn:
        conn.execute(
            "SELECT platform.media_finish(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            (
                job["job_id"],
                job["lease_token"],
                outcome,
                "ClamAV 1.5.4" if version else None,
                version,
                ov,
                dv,
                dkey,
                sha,
                size,
            ),
        ).fetchone()[0]
    # A stale lease must not erase immutable versions that a successful retry may have adopted.
    # The separate cleanup sweep checks committed publication metadata before deleting orphan versions.
    return True


def maintain():
    with connection() as conn:
        conn.execute("SELECT platform.reporting_reconcile()")
        conn.execute("SELECT platform.draft_expire()")
        orphan = conn.execute("SELECT platform.quarantine_cleanup_next()").fetchone()[0]
    if orphan is not None:
        media.erase_versions("foc-quarantine", orphan["key"])
        if not orphan["published"]:
            media.erase_versions("foc-original", orphan["key"])
            media.erase_versions(
                "foc-derivative", str(uuid5(NAMESPACE_URL, "foc-synthetic-derivative:" + orphan["id"]))
            )
        with connection() as conn:
            conn.execute("SELECT platform.quarantine_cleanup_ack(%s)", (orphan["id"],))
    with connection() as conn:
        event = conn.execute("SELECT platform.outbox_next()").fetchone()[0]
    if not event or event.get("cancelled"):
        return
    for recipient in event["recipients"]:
        with connection() as conn:
            allowed = conn.execute(
                "SELECT platform.outbox_recipient_current(%s,%s,%s)",
                (event["event_id"], recipient, event["attempt"]),
            ).fetchone()[0]
        if not allowed:
            continue
        # Dedicated private development sink; no external messaging account or child data.
        path = Path("/notifications") / (event["event_id"] + "-" + recipient + ".json")
        value = json.dumps(
            {
                "task_id": event["event_id"],
                "recipient_ref": recipient,
                "template": "neutral-task-v1",
                "task_link": "/en/reporting",
            },
            sort_keys=True,
        ).encode()
        try:
            fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            with os.fdopen(fd, "wb") as stream:
                stream.write(value)
        except FileExistsError:
            if path.read_bytes() != value:
                raise ValueError("Notification deduplication conflict")
        with connection() as conn:
            current = conn.execute(
                "SELECT platform.outbox_recipient_current(%s,%s,%s)",
                (event["event_id"], recipient, event["attempt"]),
            ).fetchone()[0]
        if not current:
            path.unlink(missing_ok=True)
    with connection() as conn:
        conn.execute("SELECT platform.outbox_finish(%s,%s)", (event["event_id"], event["attempt"]))


if __name__ == "__main__":
    while True:
        try:
            worked = once()
            maintain()
        except (*media.FAILURES, psycopg.Error):
            worked = False
        time.sleep(0.5 if worked else 2)
