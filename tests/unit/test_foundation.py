import pytest
from foc_api.config import Settings


@pytest.mark.parametrize("value", [None, "production", "real", "", "Synthetic"])
def test_fnd_config_rejects_non_synthetic(monkeypatch, value):
    monkeypatch.delenv("FOC_DATA_CLASS", raising=False)
    if value is not None:
        monkeypatch.setenv("FOC_DATA_CLASS", value)
    with pytest.raises(RuntimeError, match="synthetic"):
        Settings.load()


@pytest.mark.parametrize(
    "url",
    [
        "postgresql://user@remote.invalid/foc_synthetic",
        "postgresql://user@127.0.0.1/production",
        "https://127.0.0.1/foc_synthetic",
        "postgresql://user@localhost/postgres",
        "",
    ],
)
def test_fnd_config_rejects_untrusted_database(monkeypatch, url):
    monkeypatch.setenv("FOC_DATA_CLASS", "synthetic")
    monkeypatch.setenv("FOC_DATABASE_URL", url)
    with pytest.raises(RuntimeError):
        Settings.load()


def test_fnd_config_accepts_local_synthetic(monkeypatch):
    monkeypatch.setenv("FOC_DATA_CLASS", "synthetic")
    monkeypatch.setenv("FOC_DATABASE_URL", "postgresql://foc_api@127.0.0.1:55439/foc_synthetic")
    assert Settings.load().data_class == "synthetic"


@pytest.mark.parametrize(
    "key",
    [
        "FOC_CONTAINER_ADMIN_URL",
        "FOC_CONTAINER_DATABASE_URL",
        "FOC_DATABASE_ADMIN_URL",
        "FOC_DATABASE_URL",
        "FOC_DB_API_PASSWORD",
        "OPENAI_API_KEY",
        "AWS_SECRET_ACCESS_KEY",
        "E2E_API_KEY",
    ],
)
def test_fnd_browser_environment_removes_privileged_credentials(key):
    from scripts.dev import sanitize_environment

    result = sanitize_environment(
        {
            key: "SYNTHETIC_SECRET_CANARY",
            "FOC_API_URL": "http://127.0.0.1:8000",
            "E2E_TELEMETRY_DISABLED": "1",
            "DO_NOT_TRACK": "1",
        }
    )
    assert key not in result
    assert result == {
        "FOC_API_URL": "http://127.0.0.1:8000",
        "E2E_TELEMETRY_DISABLED": "1",
        "DO_NOT_TRACK": "1",
    }
