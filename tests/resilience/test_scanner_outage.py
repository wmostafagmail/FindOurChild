"""Executed only while the real scanner service is deliberately stopped by the host orchestrator."""

import socket

from foc_api import worker

from tests.reporting.helpers import admin, create_report, make_client, upload, verify_reporter


def test_actual_scanner_outage_keeps_media_quarantined_and_retries_bounded():
    try:
        with socket.create_connection(("scanner", 3310), timeout=1):
            raise AssertionError("Outage precondition not established")
    except OSError:
        pass
    with make_client() as client:
        receipt, body = create_report(client)
        verify_reporter(client, receipt, body["reporter"]["encrypted_transport_contact"])
        iid, _ = upload(client)
        # Isolate the fixture's due job without discarding earlier evidence or modifying other cases.
        with admin() as conn:
            conn.execute("UPDATE app.jobs SET next_attempt_at='1990-01-01' WHERE aggregate_id=%s", (iid,))
        assert worker.once()
        with admin() as conn:
            state, attempts, error = conn.execute(
                "SELECT state,attempts,error_code FROM app.jobs WHERE aggregate_id=%s", (iid,)
            ).fetchone()
            assert (state, attempts, error) == ("pending", 1, "SCANNER_UNAVAILABLE")
            assert (
                conn.execute(
                    "SELECT count(*) FROM app.objects WHERE case_id=(SELECT case_id FROM app.upload_intents WHERE id=%s)",
                    (iid,),
                ).fetchone()[0]
                == 0
            )
            assert (
                conn.execute("SELECT state FROM app.upload_intents WHERE id=%s", (iid,)).fetchone()[0]
                == "scanning"
            )
            # Repeated unavailability reaches a visible dead letter rather than release.
            conn.execute(
                "UPDATE app.jobs SET attempts=4,next_attempt_at='1990-01-01' WHERE aggregate_id=%s", (iid,)
            )
        assert worker.once()
        with admin() as conn:
            assert (
                conn.execute("SELECT state FROM app.jobs WHERE aggregate_id=%s", (iid,)).fetchone()[0]
                == "dead"
            )
            assert (
                conn.execute("SELECT state FROM app.upload_intents WHERE id=%s", (iid,)).fetchone()[0]
                == "rejected"
            )
