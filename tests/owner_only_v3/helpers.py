import copy
import json
import os
import threading
import time
from contextlib import contextmanager
from uuid import uuid4

import psycopg
from psycopg.types.json import Jsonb

from tools.phase2e.owner_only_v3.confirmation import Confirmation
from tools.phase2e.owner_only_v3.identity import Binding, claims_session
from tools.phase2e.owner_only_v3.plans import catalog
from tools.phase2e.owner_only_v3.records import ACTIONS, DESIGN, DOMAIN, POLICY, digest, require
from tools.phase2e.owner_only_v3.store import Store


class TestClock:
    __test__ = False

    def __init__(self):
        self.value = int(time.time())

    def now(self):
        return self.value


def fixture_plan():
    weights, data = catalog()
    images, pairs = [], []
    for group in data["groups"]:
        for image in group["photos"]:
            unknown = {"status": "unknown", "lower": None, "upper": None, "basis": "not_known"}
            images.append({"image_ref": image["path"], "expected_git_pointer_blob": image["git_pointer_blob"],
                           "expected_lfs_sha256": image["publisher_sha256"], "expected_bytes": image["bytes"],
                           "fictional_group": group["fictional_group"], "intended_use": "both",
                           "partition": "calibration" if group["planned_partition"] == "calibration" else "evaluation",
                           "enrollment": "enrolled" if group["planned_enrollment"] == "enrolled" else "absent_gallery",
                           "provenance_note": "Publisher metadata only; no image acquired or reviewed",
                           "capture_date": unknown.copy(), "capture_age_months": unknown.copy(),
                           "uncertainty_note": "Fictional linkage; no child identity or age claim"})
        pairs.append({"fictional_group": group["fictional_group"], "left_image_ref": group["photos"][0]["path"],
                      "right_image_ref": group["photos"][1]["path"],
                      "relationship": "fictional_publisher_link_no_biological_identity_claim",
                      "basis_note": "Synthetic engineering metadata; not a human fixture approval"})
    return {"schema_version": 1, "data_class": "synthetic_demo_only", "source_repository": data["repository"],
            "source_commit": data["commit"], "source_plan_sha256": digest(data), "model_plan_sha256": digest(weights),
            "evaluation_plan_sha256": digest("synthetic-evaluation"),
            "preprocessing_contract_sha256": digest("synthetic-no-neural-preprocessing"),
            "metadata_version": 1, "prior_score_exposure": "unknown", "freeze_before": "any_model_image_call",
            "failure_policy": "retain_all_selected_outcomes_no_substitution", "images": images, "pairings": pairs}


def template(binding, instance, tenant):
    schema = json.loads((DESIGN / "authorization-record.schema.json").read_bytes())
    props = schema["properties"]
    plan = fixture_plan()
    scope = {k: v["const"] for k, v in props["scope"]["properties"].items() if "const" in v}
    scope.update({k: digest("synthetic:" + k) for k in props["scope"]["properties"] if k.endswith("sha256")})
    scope["fixture_plan_sha256"] = digest(plan)
    scope["actions"] = sorted(ACTIONS)
    return {"domain": DOMAIN, "schema_version": 1, "record_id": str(uuid4()), "policy_digest": POLICY,
            "project": "find-our-child", "decision": "authorize_bounded_isolated_demo",
            "owner": {"issuer": binding.issuer, "audience": binding.audience, "subject": binding.subject},
            "deployment": {"namespace": "isolated-fictional-demo", "instance_id": instance, "tenant_id": tenant,
                           "activation_epoch": 1, "authority_epoch": 1},
            "source": {"application_commit": "1" * 40, "application_tree": "2" * 40,
                       "worker_build_manifest_sha256": digest("benign-build-only"),
                       "source_projection_sha256": digest("benign-projection-only"),
                       "dependency_sbom_sha256": digest("benign-sbom-only"),
                       "native_interface_version": "foc-dlib-closed-interface-v1"},
            "scope": scope, "exceptions": {k: v["const"] for k, v in props["exceptions"]["properties"].items()},
            "prohibitions": {k: v["const"] for k, v in props["prohibitions"]["properties"].items()}}


class SyntheticCheckpoint:
    """Only tests instantiate this, never a production trust default."""

    def __init__(self):
        self.states, self.seals = {}, {}
        self.lock = threading.RLock()

    def current(self, instance):
        with self.lock:
            return self.states.get(instance)

    def advance(self, instance, expected, new):
        with self.lock:
            require(self.states.get(instance) == expected, "synthetic_checkpoint_cas")
            self.states[instance] = new

    def frozen(self, key):
        return self.seals.get(key)

    def seal(self, key, value):
        with self.lock:
            require(key not in self.seals or self.seals[key] == value, "synthetic_external_freeze")
            self.seals[key] = value


class MemoryStore:
    """Explicit unit double only. Hosted required scenarios instead use real PostgreSQL Store."""

    def __init__(self):
        self.rows, self.events, self.exposure = {}, [], {}
        self.lock = threading.RLock()
        self.active = True
        self.audit_hook = None
        self.epoch = (1, 1)

    @contextmanager
    def transaction(self, a, b):
        with self.lock:
            require(self.active and (a, b) == self.epoch, "authority_inactive_or_epoch")
            old = copy.deepcopy((self.rows, self.events))
            try:
                yield self
            except BaseException:
                self.rows, self.events = old
                raise

    def get(self, kind, key):
        return copy.deepcopy(self.rows.get((kind, key)))

    def put(self, kind, key, value):
        prior = self.get(kind, key)
        require(prior is None or prior == value, "immutable_record_conflict")
        self.rows[kind, key] = copy.deepcopy(value)

    def audit(self, action, obj):
        if self.audit_hook:
            self.audit_hook(action)
        self.events.append((action, obj))


SHARED_CHECKPOINT = SyntheticCheckpoint()


def postgres_store(instance, tenant, checkpoint):
    admin = os.environ["FOC_V3_TEST_ADMIN_URL"]
    dsn = os.environ["FOC_V3_TEST_DATABASE_URL"]
    with psycopg.connect(admin) as conn:
        conn.execute("INSERT INTO owner_only_demo.authority(instance,tenant,enabled,activation_epoch,authority_epoch,checkpoint) "
                     "VALUES(%s,%s,true,1,1,%s)", (instance, tenant, "0" * 64))
    checkpoint.states[instance] = (1, 1, 0, "0" * 64)
    return Store(dsn, instance, tenant, checkpoint)


class Environment:
    def __init__(self, *, postgres=True, subject=None):
        self.clock = TestClock()
        self.instance, self.tenant = str(uuid4()), str(uuid4())
        self.binding = Binding("https://synthetic.invalid/issuer", "synthetic-v3", subject or str(uuid4()),
                               str(uuid4()), b"untrusted-test-placeholder-not-a-key")
        self.alive, self.grants = True, True
        self.checkpoint = SHARED_CHECKPOINT
        self.store = postgres_store(self.instance, self.tenant, self.checkpoint) if postgres else MemoryStore()
        self.claims = {"iss": self.binding.issuer, "aud": self.binding.audience, "sub": self.binding.subject,
                       "sid": str(uuid4()), "iat": self.clock.now(), "auth_time": self.clock.now(),
                       "exp": self.clock.now() + 1800, "amr": ["pwd", "otp"]}
        self.session_token = "synthetic-session-" + str(uuid4())
        self.session = claims_session(self.claims, self.binding, self.session_token, self.clock.now(),
                                      lambda *_: self.alive)
        self.engine = Confirmation(self.store, template(self.binding, self.instance, self.tenant), self.clock,
                                   lambda _: self.alive)
        self.engine.fixture_plan = fixture_plan()

    def prepared(self):
        draft = self.engine.prepare(self.session)
        self.body = {"record_id": draft["record"]["record_id"], "nonce": draft["nonce"],
                     "reviewed_draft_sha256": draft["record"]["confirmation"]["reviewed_draft_sha256"]}
        self.draft = draft
        return draft

    def authorized(self):
        self.prepared()
        self.result = self.engine.confirm(self.session, self.body)
        return self.result

    def tamper(self, kind, key, value, *, matching_digest=False):
        if isinstance(self.store, MemoryStore):
            self.store.rows[kind, key] = value
            return
        # Explicit privileged adversarial corruption fixture, not a deployed API.
        with psycopg.connect(os.environ["FOC_V3_TEST_ADMIN_URL"]) as conn:
            conn.execute("ALTER TABLE owner_only_demo.journal DISABLE TRIGGER immutable_v3")
            conn.execute("UPDATE owner_only_demo.journal SET value=%s WHERE instance=%s AND kind=%s AND key=%s",
                         (Jsonb(value), self.instance, kind, key))
            if matching_digest:
                conn.execute("UPDATE owner_only_demo.journal SET digest=%s WHERE instance=%s AND kind=%s AND key=%s",
                             (digest(value), self.instance, kind, key))
            conn.execute("ALTER TABLE owner_only_demo.journal ENABLE TRIGGER immutable_v3")
