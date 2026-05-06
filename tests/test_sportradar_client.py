import json
from pathlib import Path

import pytest

from soccer_capstone.models import ApiConfig
from soccer_capstone.sportradar_client import SportRadarClient


@pytest.fixture
def cfg(monkeypatch):
    monkeypatch.setenv("SPORTRADAR_API_KEY", "test-key")
    return ApiConfig(
        base_url="https://example.com",
        api_key_env="SPORTRADAR_API_KEY",
        rate_limit_qps=1,
        daily_call_cap=2,
        retry_max_attempts=1,
        retry_backoff_base=1.0,
        request_timeout_seconds=5,
    )


def test_cache_path_stable(cfg, tmp_path: Path):
    client = SportRadarClient(cfg, cache_dir=str(tmp_path))
    p1 = client._cache_path("foo", {"a": 1})
    p2 = client._cache_path("foo", {"a": 1})
    assert p1 == p2


def test_get_json_uses_cache(cfg, tmp_path: Path):
    client = SportRadarClient(cfg, cache_dir=str(tmp_path))
    cpath = client._cache_path("bar", {"x": "y"})
    cpath.write_text(json.dumps({"ok": True}))
    out = client.get_json("bar", {"x": "y"})
    assert out == {"ok": True}
