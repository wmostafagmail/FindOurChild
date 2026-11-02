"""Technical service attestations bind actual measured bytes, source, job and tools.

No human-review signatures and no caller pass flag. Producer keys are private service
trust, unprovisioned in this milestone; test keys never enter a deployed trust store.
"""

import fcntl
import hashlib
import os
from dataclasses import dataclass

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

from tools.phase2e.demo_governance.artifacts import SEALS

from .records import canonical, decode, digest, require

RECEIPT_DOMAIN = "FOC-PHASE2E-DEMO-TECHNICAL-MEASUREMENT-V3"
DEPENDENCIES = {
    "source": (), "quarantine": ("source",), "bytes": ("quarantine",),
    "processed": ("bytes",), "load": ("processed",), "ready": ("load",), "result": ("ready",),
}


@dataclass(frozen=True)
class Producer:
    public_key: bytes
    source: str
    build: str
    tool: str
    evidence_class: str


class Verifier:
    def __init__(self, producers, *, engineering=False):
        self._producers = dict(producers)
        self._engineering = engineering

    def verify(self, raw, signature, *, expected_job, expected_inputs, measured_outputs, now):
        row = decode(raw)
        require(type(row) is dict and set(row) == {"domain", "producer", "source", "build", "tool",
                "job", "stage", "evidence_class", "inputs", "outputs", "limits", "exit_code",
                "started_at", "finished_at", "expires_at", "dependencies", "audit_digest"}, "receipt_closed")
        require(row["domain"] == RECEIPT_DOMAIN and type(row["producer"]) is str
                and row["producer"] in self._producers, "receipt_producer")
        require(type(signature) is bytes and len(signature) == 64, "receipt_signature_encoding")
        require(type(row["inputs"]) is dict and type(row["outputs"]) is dict
                and 0 < len(row["inputs"]) <= 8 and 0 < len(row["outputs"]) <= 8, "receipt_io_closed")
        trusted = self._producers[row["producer"]]
        try:
            Ed25519PublicKey.from_public_bytes(trusted.public_key).verify(signature, raw)
        except (ValueError, InvalidSignature, TypeError):
            require(False, "receipt_signature")
        require((row["source"], row["build"], row["tool"], row["evidence_class"])
                == (trusted.source, trusted.build, trusted.tool, trusted.evidence_class), "receipt_provenance")
        require(self._engineering or row["evidence_class"] == "actual_isolated_measurement", "receipt_test_substitution")
        require(row["job"] == expected_job and row["inputs"] == expected_inputs
                and row["outputs"] == measured_outputs, "receipt_measurement")
        require(type(row["exit_code"]) is int and row["exit_code"] == 0, "receipt_failure")
        for field in ["started_at", "finished_at", "expires_at"]:
            require(type(row[field]) is int, "receipt_time_type")
        require(row["started_at"] <= row["finished_at"] <= now < row["expires_at"]
                and row["expires_at"] - row["started_at"] <= 14400, "receipt_time")
        require(type(row["limits"]) is dict and set(row["limits"]) == {"wall_ms", "cpu_ms", "rss_bytes",
                "wall_limit_ms", "cpu_limit_ms", "memory_limit_bytes"}, "receipt_limits")
        limits = row["limits"]
        require(all(type(v) is int and v > 0 for v in limits.values())
                and limits["wall_ms"] <= limits["wall_limit_ms"]
                and limits["cpu_ms"] <= limits["cpu_limit_ms"]
                and limits["rss_bytes"] <= limits["memory_limit_bytes"], "receipt_resource_failure")
        require(type(row["stage"]) is str and row["stage"] in DEPENDENCIES and type(row["dependencies"]) is dict
                and set(row["dependencies"]) == set(DEPENDENCIES[row["stage"]]), "receipt_dependencies")
        for item in [*row["inputs"].values(), *row["outputs"].values(), *row["dependencies"].values(),
                     row["audit_digest"]]:
            require(type(item) is str and len(item) == 64 and all(c in "0123456789abcdef" for c in item),
                    "receipt_digest")
        return row


def chain(rows, stage, *, job, inputs, now):
    """Only previously verified records from the protected journal, never raw browser receipts."""
    require(stage in DEPENDENCIES and len(rows) <= 7, "stage_bound")
    required = []
    current = stage
    while True:
        required.append(current)
        dependencies = DEPENDENCIES[current]
        if not dependencies:
            break
        current = dependencies[0]
    for name in reversed(required):
        require(name in rows, "stage_missing")
        row = rows[name]
        require(row["stage"] == name and row["job"] == job and row["inputs"] == inputs
                and now < row["expires_at"], "stage_binding")
        for parent in DEPENDENCIES[name]:
            require(row["dependencies"][parent] == digest(rows[parent]), "stage_lineage")
    return min(rows[name]["expires_at"] for name in required)


def signing_bytes(row):
    # Utility for privileged measurement producers, not an approval issuing endpoint.
    return canonical(row)


def measure_sealed_outputs(outputs):
    """Only kernel-sealed generated/approved snapshots; never reopen a caller pathname."""
    require(type(outputs) is dict and 0 < len(outputs) <= 8, "measurement_outputs")
    measured = {}
    for name, fd in outputs.items():
        require(type(name) is str and name in {"buffer", "source", "build", "scan", "derivative", "load", "result"}
                and type(fd) is int and fd >= 0, "measurement_closed")
        require(fcntl.fcntl(fd, getattr(fcntl, "F_GET_SEALS", 1034)) & SEALS == SEALS, "measurement_unsealed")
        size = os.fstat(fd).st_size
        require(0 < size <= 64 * 1024 * 1024, "measurement_size")
        value, offset = hashlib.sha256(), 0
        while offset < size:
            block = os.pread(fd, min(size - offset, 65536), offset)
            require(block, "measurement_truncated")
            value.update(block)
            offset += len(block)
        measured[name] = value.hexdigest()
    return measured


class Ingestor:
    def __init__(self, confirmation, verifier):
        self.confirmation, self.verifier = confirmation, verifier

    def accept(self, raw, signature, session, record_id, job, expected_inputs, sealed_outputs):
        measured = measure_sealed_outputs(sealed_outputs)
        now = self.confirmation.clock.now()
        row = self.verifier.verify(raw, signature, expected_job=job, expected_inputs=expected_inputs,
                                   measured_outputs=measured, now=now)
        with self.confirmation.tx() as tx:
            self.confirmation.authorization(tx, record_id, session)
            parents = {}
            for name in DEPENDENCIES[row["stage"]]:
                prior = tx.get("receipt", job + ":" + name)
                require(prior is not None, "receipt_parent_missing")
                parents[name] = prior
                require(row["dependencies"][name] == digest(prior), "receipt_parent_digest")
            tx.put("receipt", job + ":" + row["stage"], row)
            tx.audit("technical_receipt_ingested", digest(row))
            self.confirmation.authorization(tx, record_id, session)
        return digest(row)
