"""Versioned stage boundaries; the only executable adapter is synthetic and weight-free."""

import hashlib
import io
import json
import math
from dataclasses import asdict, dataclass

from PIL import Image, ImageDraw


class QualificationError(ValueError):
    pass


def digest(value):
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    ).hexdigest()


@dataclass(frozen=True)
class Space:
    code_revision: str
    weights_sha256: str
    detector_version: str
    alignment_version: str
    quality_version: str
    preprocessing_version: str
    dimension: int = 128
    metric: str = "cosine"
    normalization: str = "unit-l2"
    data_class: str = "synthetic"
    schema_version: str = "research-space-1"

    def __post_init__(self):
        if (
            self.dimension != 128
            or self.metric != "cosine"
            or self.normalization != "unit-l2"
            or self.data_class != "synthetic"
        ):
            raise QualificationError("unsupported synthetic space")
        for field, value in asdict(self).items():
            if field == "dimension":
                continue
            if not isinstance(value, str) or not value or len(value) > 128:
                raise QualificationError("invalid space provenance")
        if len(self.weights_sha256) != 64 or any(c not in "0123456789abcdef" for c in self.weights_sha256):
            raise QualificationError("invalid artifact digest")

    @property
    def id(self):
        return digest(asdict(self))


SYNTHETIC_SPACE = Space(
    "synthetic-grid-v1",
    hashlib.sha256(b"no-weights:synthetic-grid-v1").hexdigest(),
    "declared-fixture-region-v1",
    "integer-crop-v1",
    "pixel-range-v1",
    "rgb-grid-8x8-v1",
)


def validate_vector(vector, space=SYNTHETIC_SPACE):
    if not isinstance(vector, (list, tuple)) or len(vector) != space.dimension:
        raise QualificationError("invalid dimension")
    if any(type(x) not in (int, float) or not math.isfinite(x) for x in vector):
        raise QualificationError("nonfinite vector")
    norm = math.sqrt(sum(x * x for x in vector))
    if not math.isfinite(norm) or abs(norm - 1) > 1e-5:
        raise QualificationError("nonunit vector")
    return tuple(float(x) for x in vector)


def fixture(index):
    """Procedural geometric patterns only; no faces or model-generated child images."""
    if type(index) is not int or not 0 <= index < 32:
        raise QualificationError("unknown fixture")
    image = Image.new("RGB", (32, 32), (index * 7, 20, 100))
    ImageDraw.Draw(image).rectangle((8, 8, 23, 23), fill=(20, index * 5, 220))
    out = io.BytesIO()
    image.save(out, format="PNG")
    return out.getvalue()


@dataclass(frozen=True)
class Stage:
    schema_version: str
    adapter_version: str
    input_sha256: str
    value: object
    warnings: tuple = ("synthetic_only_not_face_recognition",)


class SyntheticAdapter:
    space = SYNTHETIC_SPACE

    def __init__(self):
        self.allowed = {hashlib.sha256(fixture(i)).hexdigest() for i in range(32)}

    def detect(self, data):
        if (
            type(data) is not bytes
            or len(data) > 4096
            or hashlib.sha256(data).hexdigest() not in self.allowed
        ):
            raise QualificationError("unapproved synthetic input")
        return Stage(
            "stage-1", self.space.detector_version, hashlib.sha256(data).hexdigest(), ((8, 8, 24, 24),)
        )

    def align(self, data, region, *, subject_approved=False):
        detected = self.detect(data)
        if subject_approved is not True or region not in detected.value:
            raise QualificationError("subject selection required")
        with Image.open(io.BytesIO(data)) as image:
            crop = image.convert("RGB").crop(region)
            out = io.BytesIO()
            crop.save(out, format="PNG")
        return Stage("stage-1", self.space.alignment_version, detected.input_sha256, out.getvalue())

    def quality(self, data):
        detected = self.detect(data)
        with Image.open(io.BytesIO(data)) as image:
            values = list(image.convert("RGB").get_flattened_data())
        ranges = [max(v[c] for v in values) - min(v[c] for v in values) for c in range(3)]
        return Stage(
            "stage-1",
            self.space.quality_version,
            detected.input_sha256,
            {"pixel_ranges": ranges, "face_quality": "not_measured"},
        )

    def embed(self, data, *, subject_approved=False):
        selected = self.align(data, (8, 8, 24, 24), subject_approved=subject_approved)
        with Image.open(io.BytesIO(selected.value)) as image:
            pixels = list(image.resize((8, 8)).get_flattened_data())
        raw = [float(p[c] + 1) for p in pixels for c in (0, 1)]
        norm = math.sqrt(sum(v * v for v in raw))
        vector = validate_vector([v / norm for v in raw])
        return Stage(
            "stage-1",
            self.space.preprocessing_version,
            selected.input_sha256,
            {"space_id": self.space.id, "vector": vector, "quality": self.quality(data).value},
        )


def load_recognition_backend(*args, **kwargs):
    # No environment variable, URL, path, pickle, torch checkpoint or dynamic import can activate a backend.
    raise QualificationError("real model loading is not authorized in Phase 2A")


def capabilities():
    return {
        "phase": "2A",
        "data_class": "synthetic",
        "operational_activation": False,
        "public_biometric_search": False,
        "automatic_identity_confirmation": False,
        "custody_disclosure": False,
        "recognition_backend": "none",
    }
