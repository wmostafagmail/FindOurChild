"""Private immutable S3 versions and bounded ClamAV streaming; no remote image imports."""

import hashlib
import io
import os
import secrets
import socket
import struct
import warnings
from uuid import UUID

import boto3
from botocore.config import Config
from botocore.exceptions import BotoCoreError, ClientError
from cryptography.exceptions import InvalidTag
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from PIL import Image, ImageOps, UnidentifiedImageError

FAILURES = (OSError, ValueError, BotoCoreError, ClientError, InvalidToken, InvalidTag)

MAX_BYTES = 5 * 1024 * 1024
MAX_PIXELS = 12_000_000


def s3(role):
    if role not in {"API", "WORKER", "GATEWAY", "ADMIN"}:
        raise ValueError("Invalid role")
    return boto3.client(
        "s3",
        endpoint_url="http://storage:8333",
        aws_access_key_id=os.environ[f"FOC_S3_{role}_KEY"],
        aws_secret_access_key=os.environ[f"FOC_S3_{role}_SECRET"],
        region_name="us-east-1",
        config=Config(
            signature_version="s3v4",
            s3={"addressing_style": "path"},
            connect_timeout=3,
            read_timeout=10,
            retries={"max_attempts": 0},
        ),
    )


def cipher():
    return Fernet(os.environ["FOC_REPORT_KEY"].encode())


def new_key():
    key = AESGCM.generate_key(bit_length=256)
    return cipher().encrypt(key).decode()


def encrypt(data, wrapped, key_id):
    nonce = secrets.token_bytes(12)
    return nonce + AESGCM(cipher().decrypt(wrapped.encode())).encrypt(
        nonce, data, str(UUID(str(key_id))).encode()
    )


def decrypt(data, wrapped, key_id):
    if len(data) > MAX_BYTES + 128 or len(data) < 28:
        raise ValueError("Invalid encrypted object")
    return AESGCM(cipher().decrypt(wrapped.encode())).decrypt(
        data[:12], data[12:], str(UUID(str(key_id))).encode()
    )


def put(role, bucket, key, data, wrapped):
    encrypted = encrypt(data, wrapped, key)
    response = s3(role).put_object(
        Bucket=bucket,
        Key=str(UUID(str(key))),
        Body=encrypted,
        ContentType="application/octet-stream",
        IfNoneMatch="*",
        Metadata={"envelope": "aes256gcm-v1"},
    )
    version = response.get("VersionId")
    if not version or version == "null":
        raise ValueError("Versioned storage required")
    return version


def get(role, bucket, key, version, wrapped):
    response = s3(role).get_object(Bucket=bucket, Key=str(UUID(str(key))), VersionId=version)
    try:
        if response["ContentLength"] > MAX_BYTES + 128:
            raise ValueError("Object too large")
        data = response["Body"].read(MAX_BYTES + 129)
    finally:
        response["Body"].close()
    return decrypt(data, wrapped, key)


def scan(data):
    if not 0 < len(data) <= MAX_BYTES:
        raise ValueError("Invalid media size")
    with socket.create_connection(("scanner", 3310), timeout=5) as sock:
        sock.settimeout(20)
        sock.sendall(b"zINSTREAM\0")
        for start in range(0, len(data), 65536):
            block = data[start : start + 65536]
            sock.sendall(struct.pack("!I", len(block)) + block)
        sock.sendall(struct.pack("!I", 0))
        response = bytearray()
        while b"\0" not in response:
            part = sock.recv(1024)
            if not part or len(response) > 2048:
                raise ValueError("Incomplete scanner response")
            response.extend(part)
    status = bytes(response).split(b"\0")[0]
    with socket.create_connection(("scanner", 3310), timeout=5) as sock:
        sock.settimeout(5)
        sock.sendall(b"zVERSION\0")
        version = sock.recv(1024).decode("ascii").strip("\0\n")
    if not version.startswith("ClamAV 1.5.4/"):
        raise ValueError("Unverified scanner version")
    # Never infer clean from a generic success/empty/unknown/error reply.
    if status == b"stream: OK":
        return "clean", version
    if status.startswith(b"stream: ") and status.endswith(b" FOUND"):
        return "infected", version
    raise ValueError("Scanner did not establish safety")


def sanitize(data, expected_mime):
    Image.MAX_IMAGE_PIXELS = MAX_PIXELS
    formats = {"image/jpeg": "JPEG", "image/png": "PNG", "image/webp": "WEBP"}
    with warnings.catch_warnings():
        warnings.simplefilter("error", Image.DecompressionBombWarning)
        try:
            with Image.open(io.BytesIO(data), formats=list(formats.values())) as probe:
                if (
                    probe.format != formats.get(expected_mime)
                    or probe.width * probe.height > MAX_PIXELS
                    or max(probe.size) > 6000
                    or getattr(probe, "n_frames", 1) != 1
                ):
                    raise ValueError("Invalid image bounds or format")
                probe.verify()
            with Image.open(io.BytesIO(data), formats=list(formats.values())) as source:
                source.load()
                oriented = ImageOps.exif_transpose(source).convert("RGB")
                # Rebuild from pixel bytes. No EXIF/GPS/ICC/comments/thumbnails/animation copied.
                flat = Image.frombytes("RGB", oriented.size, oriented.tobytes())
                flat.thumbnail((1600, 1600))
                output = io.BytesIO()
                flat.save(output, format="PNG", optimize=False)
        except (
            UnidentifiedImageError,
            OSError,
            SyntaxError,
            Image.DecompressionBombError,
            Image.DecompressionBombWarning,
        ) as exc:
            raise ValueError("Invalid image") from exc
    result = output.getvalue()
    if len(result) > MAX_BYTES:
        raise ValueError("Derivative too large")
    return result


def checksum(data):
    return hashlib.sha256(data).hexdigest()


def put_once(bucket, key, data, wrapped, role="WORKER"):
    """Recover an immutable worker write after process loss without overwriting evidence."""
    if not (
        (role == "WORKER" and bucket in {"foc-original", "foc-derivative"})
        or (role == "API" and bucket == "foc-quarantine")
    ):
        raise ValueError("Invalid recovery bucket")
    try:
        return put(role, bucket, key, data, wrapped)
    except ClientError as exc:
        if exc.response.get("Error", {}).get("Code") not in {"PreconditionFailed", "412"}:
            raise
    head = s3(role).head_object(Bucket=bucket, Key=str(UUID(str(key))))
    version = head.get("VersionId")
    if not version or version == "null":
        raise ValueError("Immutable recovery version required")
    existing = get(role, bucket, key, version, wrapped)
    if checksum(existing) != checksum(data):
        raise ValueError("Immutable recovery mismatch")
    return version


def erase_versions(bucket, key):
    """Exact opaque-key erasure, including an upload lost before database bind; verify before ack."""
    if bucket not in {"foc-quarantine", "foc-original", "foc-derivative"}:
        raise ValueError("Invalid cleanup bucket")
    key = str(UUID(str(key)))
    client = s3("WORKER")
    for page in client.get_paginator("list_object_versions").paginate(Bucket=bucket, Prefix=key):
        for item in page.get("Versions", []) + page.get("DeleteMarkers", []):
            if item["Key"] == key:
                client.delete_object(Bucket=bucket, Key=key, VersionId=item["VersionId"])
    remaining = client.list_object_versions(Bucket=bucket, Prefix=key)
    if any(item["Key"] == key for item in remaining.get("Versions", []) + remaining.get("DeleteMarkers", [])):
        raise ValueError("Storage cleanup not acknowledged")
