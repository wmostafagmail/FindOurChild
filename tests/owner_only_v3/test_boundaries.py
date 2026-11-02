import copy
import os
import time
from uuid import uuid4

import psycopg
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from tests.owner_only_v3.helpers import Environment
from tests.owner_only_v3.test_scenarios import denied, lease, valid_receipt
from tools.phase2e.owner_only_v3.checkpoint import Checkpoint
from tools.phase2e.owner_only_v3.records import Denied, canonical, digest, reviewed_digest, sha, validate


def test_four_hour_and_confirmation_digest_bounds():
    env = Environment(postgres=False)
    row = env.prepared()["record"]
    for changes in [{"lifetime_seconds": 14401}, {"issued_at": "2099-01-01T00:00:00Z"},
                    {"expires_at": "2000-01-01T00:00:00Z"}]:
        wrong = copy.deepcopy(row)
        wrong["time"].update(changes)
        wrong["confirmation"]["reviewed_draft_sha256"] = reviewed_digest(wrong)
        denied(lambda wrong=wrong: validate(canonical(wrong), env.clock.now()))
    assert digest(row) != reviewed_digest(row)


def test_real_checkpoint_file_append_freeze_corruption_and_no_bootstrap(tmp_path):
    parent = tmp_path / "protected"
    parent.mkdir(mode=0o700)
    fd = os.open(parent, os.O_RDONLY | os.O_DIRECTORY)
    with pytest.raises(FileNotFoundError):
        Checkpoint(fd, owner=os.getuid())
    instance = str(uuid4())
    state = (1, 1, 0, "0" * 64)
    # Untrusted test provisioning only; runtime has NO create/bootstrap operation.
    row = {"instance": instance, "previous": "0" * 64, "state": list(state)}
    row["chain"] = digest(row)
    path = parent / "owner-only-v3.checkpoints"
    path.write_bytes(canonical(row) + b"\n")
    path.chmod(0o600)
    checkpoint = Checkpoint(fd, owner=os.getuid())
    try:
        assert checkpoint.current(instance) == state
        checkpoint.advance(instance, state, (1, 1, 1, "a" * 64))
        assert checkpoint.current(instance) == (1, 1, 1, "a" * 64)
        denied(lambda: checkpoint.advance(instance, state, (1, 1, 1, "b" * 64)))
        checkpoint.seal("f" * 64, "a" * 64)
        assert checkpoint.frozen("f" * 64) == "a" * 64
        denied(lambda: checkpoint.seal("f" * 64, "b" * 64))
        with path.open("ab") as stream:
            stream.write(b"partial")
        denied(lambda: checkpoint.current(instance))
    finally:
        checkpoint.close()
        os.close(fd)


def test_private_api_default_denial_csrf_and_closed_confirmation(monkeypatch):
    from foc_api import owner_only_demo as api

    app = FastAPI()
    app.include_router(api.router)
    client = TestClient(app)
    monkeypatch.setattr(api, "authenticate", lambda *_a, **_k: (uuid4(), "synthetic-session"))
    assert client.get("/demo-authorization/status").status_code == 503
    env = Environment(postgres=False)

    class SyntheticBackend:
        def resolve(self, *_):
            return env.engine, env.session

    app.state.owner_only_v3_backend = SyntheticBackend()
    assert client.get("/demo-authorization/status?owner=true").status_code == 403
    assert client.get("/demo-authorization/confirm").status_code == 405
    draft = client.post("/demo-authorization/prepare", content=b"{}").json()
    body = {"record_id": draft["record"]["record_id"], "nonce": draft["nonce"],
            "reviewed_draft_sha256": draft["record"]["confirmation"]["reviewed_draft_sha256"]}
    assert client.post("/demo-authorization/confirm", content=canonical(body)).status_code == 200
    assert client.post("/demo-authorization/confirm", content=canonical(dict(body, owner=True))).status_code == 403
    assert client.post("/demo-authorization/confirm", content=b'{"x":1,"x":1}').status_code == 403
    assert client.post("/demo-authorization/revoke", content=canonical({"record_id": body["record_id"]})).status_code == 200
    assert client.post("/demo-authorization/confirm", content=canonical(body)).status_code == 403


def test_receipt_actual_sealed_measurement_and_unsealed_denial(tmp_path):
    from tools.phase2e.owner_only_v3.processing import snapshot_fd
    from tools.phase2e.owner_only_v3.receipts import measure_sealed_outputs

    path = tmp_path / "benign-buffer"
    path.write_bytes(b"actual-generated-buffer")
    with path.open("rb") as source:
        with pytest.raises((Denied, OSError)):
            measure_sealed_outputs({"buffer": source.fileno()})
        with snapshot_fd(source.fileno(), size=path.stat().st_size, sha256=sha(path.read_bytes())) as sealed:
            assert measure_sealed_outputs({"buffer": sealed}) == {"buffer": sha(path.read_bytes())}


def test_receipt_dag_expiry_exit_and_provenance():
    _, row, _, verify = valid_receipt()
    for key, value in [("exit_code", 1), ("build", "f" * 64), ("tool", "f" * 64),
                       ("expires_at", int(time.time()) - 1), ("dependencies", {"source": "f" * 64})]:
        denied(lambda key=key, value=value: verify(dict(row, **{key: value})))


def test_real_postgres_immutability_epoch_checkpoint_and_append_only():
    env = Environment(postgres=True)
    env.authorized()
    with psycopg.connect(os.environ["FOC_V3_TEST_DATABASE_URL"]) as conn:
        conn.execute("SELECT set_config('foc.v3_instance',%s,true)", (env.instance,))
        conn.execute("SELECT set_config('foc.v3_tenant',%s,true)", (env.tenant,))
        with pytest.raises(psycopg.errors.InsufficientPrivilege):
            conn.execute("DELETE FROM owner_only_demo.journal")
    env.checkpoint.states[env.instance] = (1, 1, 0, "0" * 64)
    denied(lambda: env.engine.confirm(env.session, env.body))


def test_real_postgres_global_fixture_freeze_survives_new_instance():
    from tests.owner_only_v3.test_scenarios import frozen

    a, b = Environment(postgres=True), Environment(postgres=True)
    a.authorized()
    b.authorized()
    assert frozen(a) == frozen(b)
    changed = copy.deepcopy(b.engine.fixture_plan)
    changed["metadata_version"] = 2
    denied(lambda: frozen(b, changed))


def test_v3_benign_worker_adapter_and_stale_publication():
    from tools.phase2e.owner_only_v3.worker import run_benign_job

    env = Environment(postgres=True)
    env.authorized()
    fence, token, inputs = lease(env)
    result = run_benign_job(fence, token, env.session, inputs, os.environ["FOC_GOVERNANCE_PROBE_IMAGE"])
    assert result["inference"] is False
    fence.cancel(env.session, token.job)
    denied(lambda: run_benign_job(fence, token, env.session, inputs, os.environ["FOC_GOVERNANCE_PROBE_IMAGE"]))
