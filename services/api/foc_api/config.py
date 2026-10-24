"""Phase 1A can only start in a synthetic, loopback development environment."""

import os
from dataclasses import dataclass
from urllib.parse import urlparse


@dataclass(frozen=True)
class Settings:
    database_url: str
    data_class: str = "synthetic"

    @classmethod
    def load(cls):
        if os.environ.get("FOC_DATA_CLASS") != "synthetic":
            raise RuntimeError("FOC_DATA_CLASS must be synthetic")
        url = os.environ.get("FOC_DATABASE_URL", "")
        parsed = urlparse(url)
        if parsed.scheme not in {"postgresql", "postgres"} or parsed.hostname not in {
            "127.0.0.1",
            "localhost",
            "db",
        }:
            raise RuntimeError("An isolated local PostgreSQL URL is required")
        if parsed.path != "/foc_synthetic":
            raise RuntimeError("Only the foc_synthetic database is permitted")
        return cls(url)
