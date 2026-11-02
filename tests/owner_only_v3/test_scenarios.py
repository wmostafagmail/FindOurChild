"""90 frozen V3 record/runtime scenarios. Six additional designs execute in official browsers.

Hosted mode requires real private PostgreSQL and actual Linux benign isolation
probes. Unit mode is explicitly reported separately and is not hosted evidence.
"""

import copy
import json
import os
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from pathlib import Path
from uuid import uuid4

import jwt
import psycopg
import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519, rsa

from tests.owner_only_v3.helpers import Environment, fixture_plan
from tools.phase2e.owner_only_v3 import fixtures, processing
from tools.phase2e.owner_only_v3.dispatcher import Dispatcher, select_policy
from tools.phase2e.owner_only_v3.fencing import Fencing
from tools.phase2e.owner_only_v3.identity import authenticate_token, claims_session
from tools.phase2e.owner_only_v3.plans import catalog, inventory
from tools.phase2e.owner_only_v3.receipts import RECEIPT_DOMAIN, Producer, Verifier, chain
from tools.phase2e.owner_only_v3.records import (
    DESIGN,
    DOMAIN,
    Denied,
    canonical,
    decode,
    digest,
    require,
    reviewed_digest,
    sha,
    validate,
)

CASES = [r["case_id"] for r in json.loads((DESIGN / "TEST_MATRIX.json").read_bytes())["cases"]]
CASES = [c for c in CASES if not c.startswith("OD3-B")]


def denied(operation):
    with pytest.raises((Denied, psycopg.Error)):
        operation()


def frozen(env, plan=None):
    plan = plan or fixture_plan()
    plan = fixtures.validate_plan(canonical(plan))
    derivatives = {r["image_ref"]: digest("benign-derivative:" + r["image_ref"]) for r in plan["images"]}
    with env.engine.tx() as tx:
        return fixtures.freeze(tx, plan, derivatives)


def lease(env, **kwargs):
    fence = Fencing(env.engine, lambda *_: env.grants)
    token = fence.issue(env.session, env.body["record_id"], kwargs.get("action", "verify_bytes"),
                        {"plan": digest(fixture_plan())}, job=str(uuid4()),
                        receipt_expiry=env.clock.now() + 60, hard_deadline=env.clock.now() + 60)
    return fence, token, {"plan": digest(fixture_plan())}


def valid_receipt():
    key = ed25519.Ed25519PrivateKey.generate()  # Untrusted ephemeral service fixture, never a human key.
    now = int(time.time())
    row = {"domain": RECEIPT_DOMAIN, "producer": "synthetic-measurement", "source": digest("source"),
           "build": digest("build"), "tool": digest("tool"), "job": str(uuid4()), "stage": "source",
           "evidence_class": "engineering_generated_buffer", "inputs": {"source": digest("source")},
           "outputs": {"buffer": digest("actual-generated-buffer")}, "limits": {"wall_ms": 1, "cpu_ms": 1,
           "rss_bytes": 4096, "wall_limit_ms": 3000, "cpu_limit_ms": 2000, "memory_limit_bytes": 67108864},
           "exit_code": 0, "started_at": now - 1, "finished_at": now, "expires_at": now + 60,
           "dependencies": {}, "audit_digest": digest("audit")}
    producer = Producer(key.public_key().public_bytes_raw(), row["source"], row["build"], row["tool"],
                        row["evidence_class"])
    verifier = Verifier({row["producer"]: producer}, engineering=True)

    def verify(value, *, target=verifier, signature=None):
        return target.verify(canonical(value), signature or key.sign(canonical(value)), expected_job=row["job"],
                             expected_inputs=row["inputs"], measured_outputs=row["outputs"], now=now)

    assert verify(row) == row
    return key, row, producer, verify


def renew(env):
    env.claims.update(auth_time=env.clock.now(), iat=env.clock.now(), exp=env.clock.now() + 1800)
    env.claims["sid"] = str(uuid4())
    env.session = claims_session(env.claims, env.binding, env.session_token, env.clock.now(), lambda *_: env.alive)


@pytest.mark.parametrize("case", CASES)
def test_scenario(case, tmp_path, monkeypatch):
    hosted = os.environ.get("FOC_V3_TEST_MODE") == "hosted-real-postgres"
    env = Environment(postgres=hosted)
    env.authorized()  # Matched positive control with actual durable confirmation in hosted mode.
    result = env.engine.confirm(env.session, env.body)
    assert result == env.result and result["execution_available"] is False
    record = env.draft["record"]

    if case in {"OD3-R01", "OD3-R06", "OD3-S03"}:
        denied(lambda: claims_session(dict(env.claims, sub="self-asserted-owner"), env.binding,
                                      env.session_token, env.clock.now(), lambda *_: True))
    elif case in {"OD3-R02", "OD3-X18"}:
        fence, token, inputs = lease(env)
        denied(lambda: Dispatcher(fence).execute(token, env.session, inputs, job=token.job, action=token.action))
        denied(lambda: processing.process_assets(enabled=True, owner=True))
    elif case in {"OD3-R03", "OD3-X04"}:
        wrong = replace(env.session, session_digest=digest("other-session"))
        denied(lambda: env.engine.confirm(wrong, env.body))
        denied(lambda: env.engine.confirm(env.session, dict(env.body, reviewed_draft_sha256="f" * 64)))
        denied(lambda: env.engine.confirm(env.session, dict(env.body, nonce="wrong")))
    elif case in {"OD3-R04", "OD3-P02"}:
        env.prepared()
        with ThreadPoolExecutor(2) as pool:
            results = list(pool.map(lambda _: env.engine.confirm(env.session, env.body), range(2)))
        assert results[0] == results[1]
        with env.engine.tx() as tx:
            assert tx.get("authorization", env.body["record_id"]) == env.draft["record"]
        env.prepared()
        env.clock.value += 301
        renew(env)
        # New auth event cannot consume an older challenge, even with a fresh token.
        denied(lambda: env.engine.confirm(env.session, env.body))
    elif case == "OD3-R05":
        private = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        public = private.public_key().public_bytes(serialization.Encoding.PEM,
                                                   serialization.PublicFormat.SubjectPublicKeyInfo)
        binding = replace(env.binding, public_key=public)
        token = jwt.encode(env.claims, private, algorithm="RS256")
        assert authenticate_token(token, binding, env.session_token, time.time(), lambda *_: True)
        denied(lambda: authenticate_token(jwt.encode(env.claims, b"untrusted-synthetic-secret-only-32", algorithm="HS256"),
                                         binding, env.session_token, time.time(), lambda *_: True))
        denied(lambda: authenticate_token(token + "x", binding, env.session_token, time.time(), lambda *_: True))
    elif case == "OD3-R07":
        denied(lambda: env.engine.confirm(env.session, dict(env.body, reviewer="invented-reviewer")))
    elif case in {"OD3-R08", "OD3-S08", "OD3-X08", "OD3-X09"}:
        key, row, producer, verify = valid_receipt()
        denied(lambda: verify(dict(row, passed=True)))
        denied(lambda: verify(dict(row, producer="owner")))
        denied(lambda: verify(dict(row, source="b" * 64)))
        denied(lambda: verify(row, signature=ed25519.Ed25519PrivateKey.generate().sign(canonical(row))))
        denied(lambda: verify(row, target=Verifier({row["producer"]: producer})))
        denied(lambda: chain({"source": row}, "ready", job=row["job"], inputs=row["inputs"], now=int(time.time())))
    elif case in {"OD3-R09", "OD3-S13", "OD3-X11", "OD3-X12", "OD3-W15"}:
        original = frozen(env)
        changed = fixture_plan()
        changed["evaluation_plan_sha256"] = digest("changed-after-scores")
        assert fixtures.lineage_key(changed) == original
        denied(lambda: frozen(env, changed))
        renewed = copy.deepcopy(env.engine.template)
        renewed["deployment"]["instance_id"] = str(uuid4())
        # Mutable labels and deployment IDs cannot enter the stable lookup key.
        assert fixtures.lineage_key(changed) == fixtures.lineage_key(fixture_plan())
        assert frozen(env) == original
    elif case in {"OD3-R10", "OD3-S14", "OD3-X14", "OD3-P08"}:
        fence, token, inputs = lease(env)
        env.grants = False  # Owner confirmation never creates case/media/purpose rights.
        denied(lambda: Dispatcher(fence).check(token, env.session, inputs, job=token.job, action=token.action))
        denied(lambda: fence.issue(env.session, env.body["record_id"], "child_release", inputs, job=str(uuid4()),
                                   receipt_expiry=env.clock.now() + 10, hard_deadline=env.clock.now() + 10))
    elif case in {"OD3-R11", "OD3-X03"}:
        env.alive = False
        denied(lambda: env.engine.confirm(env.session, env.body))
        denied(lambda: env.engine.prepare(env.session))
    elif case in {"OD3-R12", "OD3-S07", "OD3-X07"}:
        for section, key, value in [("deployment", "namespace", "operational"),
                                    ("deployment", "authority_epoch", 2), ("source", "application_tree", "f" * 40)]:
            wrong = copy.deepcopy(record)
            wrong[section][key] = value
            wrong["confirmation"]["reviewed_draft_sha256"] = reviewed_digest(wrong)
            if key != "namespace":
                env.tamper("authorization", env.body["record_id"], wrong, matching_digest=True)
                with env.engine.tx() as tx:
                    denied(lambda: env.engine.authorization(tx, env.body["record_id"], env.session))
            else:
                denied(lambda wrong=wrong: validate(canonical(wrong), env.clock.now()))
    elif case == "OD3-R13":
        denied(lambda: env.engine.confirm(env.session, dict(env.body, store_path="/tmp/forged")))
        assert select_policy() == DOMAIN
    elif case in {"OD3-R14", "OD3-R16", "OD3-W12"}:
        env.prepared()
        from tools.phase2e.owner_only_v3.store import Transaction

        if hosted:
            original = Transaction.audit

            def fail(self, *args):
                original(self, *args)
                raise Denied("synthetic_audit_failure")

            monkeypatch.setattr(Transaction, "audit", fail)
        else:
            env.store.audit_hook = lambda _: require(False, "synthetic_audit_failure")
        denied(lambda: env.engine.confirm(env.session, env.body))
        with env.engine.tx() as tx:
            assert tx.get("authorization", env.body["record_id"]) is None
    elif case in {"OD3-R15", "OD3-W14", "OD3-P07"}:
        if hosted:
            with psycopg.connect(os.environ["FOC_V3_TEST_ADMIN_URL"]) as conn:
                conn.execute("UPDATE owner_only_demo.authority SET enabled=false WHERE instance=%s", (env.instance,))
        else:
            env.store.active = False
        denied(lambda: env.engine.confirm(env.session, env.body))
    elif case == "OD3-S01":
        from tests.demo_governance.helpers import World
        from tools.phase2e.demo_governance.records import Denied as V2Denied

        denied(lambda: validate(canonical(dict(record, domain="FOC-PHASE2E-DEMO-APPROVAL-V2")), env.clock.now()))
        with pytest.raises(V2Denied):
            world = World()
            identity = sha(canonical(record))
            world.records[identity] = canonical(record)
            world.verify(root=identity)  # V2 has no V3 schema/policy fallback.
    elif case == "OD3-S02":
        denied(lambda: env.engine.confirm(env.session, dict(env.body, reviewed_draft_sha256="0" * 64)))
    elif case == "OD3-S04":
        for raw in [b'{"a":1,"a":1}', b'{"z":1,"a":2}', canonical(record) + b'{}', b'{ "a":1}']:
            denied(lambda raw=raw: decode(raw))
        denied(lambda: validate(canonical(dict(record, unknown=True)), env.clock.now()))
    elif case == "OD3-S05":
        for raw in [b'{"a":NaN}', b'{"a":1.0}', b'{"a":9007199254740992}', b'{"a":-1}']:
            denied(lambda raw=raw: decode(raw))
        wrong = copy.deepcopy(record)
        wrong["deployment"]["activation_epoch"] = True
        denied(lambda wrong=wrong: validate(canonical(wrong), env.clock.now()))
    elif case == "OD3-S06":
        start = time.monotonic()
        for raw in [b'[' * 16000, b'"' + b'x' * 20000 + b'"', b'{"a":' + b'[],' * 40 + b'[]}']:
            denied(lambda raw=raw: decode(raw))
        assert time.monotonic() - start < 1
    elif case in {"OD3-S09", "OD3-X01", "OD3-X02"}:
        for changes in [{"auth_time": env.clock.now() - 301}, {"auth_time": env.clock.now() + 1},
                        {"auth_time": True}, {"amr": "pwd,otp"}, {"amr": ["pwd", ["otp"]]}]:
            denied(lambda changes=changes: claims_session(dict(env.claims, **changes), env.binding, env.session_token,
                                          env.clock.now(), lambda *_: True))
    elif case in {"OD3-S10", "OD3-W13"}:
        fence, token, inputs = lease(env)
        env.clock.value += 31
        denied(lambda: fence.publish(token, env.session, inputs, digest("late")))
    elif case == "OD3-S11":
        denied(lambda: env.engine.confirm(env.session, dict(env.body, nonce="changed-replay")))
        assert env.engine.confirm(env.session, env.body) == result
    elif case in {"OD3-S12", "OD3-X15"}:
        fence, token, inputs = lease(env, action="load_qualification")
        denied(lambda: Dispatcher(fence).check(token, env.session, inputs, job=token.job,
                                              action="private_image_inference"))
        denied(lambda: select_policy("public_biometric_search"))
    elif case in {"OD3-S15", "OD3-W10"}:
        fence, token, inputs = lease(env)
        from tools.phase2e.owner_only_v3.store import Transaction

        if hosted:
            original = Transaction.audit

            def revoke_while_waiting(self, *args):
                original(self, *args)
                env.alive = False

            monkeypatch.setattr(Transaction, "audit", revoke_while_waiting)
        else:
            env.store.audit_hook = lambda _: setattr(env, "alive", False)
        denied(lambda: fence.publish(token, env.session, inputs, digest("late")))
    elif case == "OD3-S16":
        _, row, producer, verify = valid_receipt()
        denied(lambda: verify(row, target=Verifier({row["producer"]: producer}, engineering=False)))
    elif case == "OD3-A01":
        denied(lambda: processing.process_assets(owner=True, gate="approved"))
        denied(lambda: chain({}, "source", job="synthetic", inputs={}, now=int(time.time())))
    elif case == "OD3-A02":
        weights, data = catalog()
        rows = [{"ref": p["path"], "source_commit": weights["commit"], "source_blob": p["sha"], "bytes": p["size"]}
                for p in weights["files"]]
        rows += [{"ref": p["path"], "source_commit": data["commit"], "source_blob": p["git_pointer_blob"],
                  "bytes": p["bytes"]} for g in data["groups"] for p in g["photos"]]
        assert len(inventory(rows)) == 51
        for wrong in [rows[:-1], rows + rows[:1], rows[:-1] + rows[:1], [dict(r, url="https://bad.invalid") for r in rows]]:
            denied(lambda wrong=wrong: inventory(wrong))
    elif case.startswith("OD3-A"):
        # Identical approved immutable-byte/parser primitives, exercised on benign buffers only.
        from tests.demo_governance import test_artifacts as old

        functions = {
            "OD3-A03": lambda: old.test_dg_a03_exact_bytes_size_git_and_sha(),
            "OD3-A04": lambda: old.test_dg_a04_type_links_and_permissions_before_read(),
            "OD3-A05": lambda: old.test_dg_a05_no_pathname_reopen(tmp_path),
            "OD3-A06": lambda: old.test_dg_a06_copy_mutation_denied_before_parser(tmp_path),
            "OD3-A07": lambda: old.test_dg_a07_kernel_seals_prevent_write_grow_shrink(tmp_path),
            "OD3-A08": lambda: old.test_dg_a08_sealing_failure_never_falls_back(tmp_path, monkeypatch),
            "OD3-A09": lambda: old.test_dg_a09_malformed_concatenated_or_truncated_bzip(),
            "OD3-A10": lambda: old.test_dg_a10_bounded_output_and_ratio(),
            "OD3-A11": lambda: old.test_dg_a11_scanner_missing_stale_dirty_or_timeout(),
            "OD3-A12": lambda: old.test_dg_a12_decoder_failure_or_format_and_pixels(),
            "OD3-A13": lambda: old.test_dg_a13_lineage_or_permission_changed(),
            "OD3-A14": lambda: old.test_dg_a14_quarantine_aad_tag_and_key(),
            "OD3-A15": lambda: old.test_dg_a15_space_and_build_not_dimension_or_filename(tmp_path),
            "OD3-A16": lambda: old.test_dg_a16_build_outputs_required_not_receipts(),
        }
        functions[case]()
        denied(lambda: processing.process_assets(component="cnn_detector"))
    elif case in {f"OD3-W{i:02}" for i in range(1, 8)}:
        from tests.demo_governance import test_linux as old

        names = ["test_dg_w01_docker_client_death_does_not_cancel_watchdog",
                 "test_dg_w02_no_control_plane_dependency_after_admission", "test_dg_w03_supervisor_death_kills_namespace",
                 "test_dg_w04_independent_cpu_and_wall_limits", "test_dg_w05_memory_exhaustion_fails_job",
                 "test_dg_w06_descendants_fd_output_and_watchdog_attack", "test_dg_w07_stable_container_identity_and_unknown_probe_denied"]
        getattr(old, names[int(case[-2:]) - 1])()
    elif case in {"OD3-W08", "OD3-W09"}:
        fence, token, inputs = lease(env)
        fence.cancel(env.session, token.job)
        denied(lambda: fence.publish(token, env.session, inputs, digest("late")))
    elif case == "OD3-W11":
        if hosted:
            with psycopg.connect(os.environ["FOC_V3_TEST_DATABASE_URL"]) as conn:
                assert conn.execute("SELECT count(*) FROM owner_only_demo.journal").fetchone()[0] == 0
                with pytest.raises(psycopg.errors.InsufficientPrivilege):
                    conn.execute("UPDATE owner_only_demo.authority SET enabled=true")
        else:
            fence, token, inputs = lease(env)
            denied(lambda: Dispatcher(fence).check(replace(token, tenant=str(uuid4())), env.session, inputs,
                                                  job=token.job, action=token.action))
    elif case in {"OD3-W16", "OD3-X16"}:
        from tools.phase2e.owner_only_v3.evidence import enforce_inventory, public_report

        denied(lambda: public_report({"token": "private"}))
        denied(lambda: enforce_inventory([], CASES, {}))
    elif case in {"OD3-X05", "OD3-P04"}:
        wrong = copy.deepcopy(record)
        wrong["owner"]["subject"] += "\u202e"
        denied(lambda wrong=wrong: validate(canonical(wrong), env.clock.now()))
        ui = Path("apps/web/app/[locale]/demo-authorization/panel.tsx").read_text()
        assert 'dir="ltr"' in ui and 'data-testid="draft-digest"' in ui
    elif case == "OD3-X06":
        denied(lambda: select_policy("FOC-PHASE2E-DEMO-APPROVAL-V2"))
    elif case == "OD3-X10":
        # First call commitment is durable before any invocation; diagnostics have the same rule.
        assert frozen(env)
        fence, token, inputs = lease(env, action="private_image_inference")
        denied(lambda: Dispatcher(fence).execute(token, env.session, inputs, job=token.job, action=token.action))
    elif case in {"OD3-X13", "OD3-P05"}:
        plan = fixture_plan()
        rows = [{"ref": p["image_ref"], "outcome": "no_face" if i % 2 else "failed"} for i, p in enumerate(plan["images"])]
        assert len(fixtures.outcomes(plan, rows)) == 48
        denied(lambda: fixtures.outcomes(plan, rows[:-1]))
        denied(lambda: fixtures.outcomes(plan, rows[:-1] + rows[:1]))
    elif case == "OD3-X17":
        assert record["exceptions"]["database_p95_target_ms"] == 1000
        _, row, _, verify = valid_receipt()
        row["limits"]["wall_ms"] = 3001
        denied(lambda: verify(row))
    elif case == "OD3-P01":
        assert validate(canonical(record), env.clock.now())["domain"] == DOMAIN
        assert result["record_id"] == record["record_id"]
    elif case == "OD3-P03":
        _, row, _, _ = valid_receipt()
        assert chain({"source": row}, "source", job=row["job"], inputs=row["inputs"], now=int(time.time())) > time.time()
    elif case == "OD3-P06":
        key = frozen(env)
        env.clock.value += 14401
        renew(env)
        env.authorized()
        assert frozen(env) == key
    else:
        pytest.fail("Unimplemented mandatory V3 scenario: " + case)
