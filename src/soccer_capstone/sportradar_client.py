import hashlib
import json
import os
import time
from pathlib import Path
from typing import Any

import requests
from ratelimit import limits, sleep_and_retry

from soccer_capstone.models import ApiConfig


class SportRadarClient:
    def __init__(self, config: ApiConfig, cache_dir: str = "data/raw/cache") -> None:
        self.config = config
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.api_key = os.getenv(config.api_key_env)
        if not self.api_key:
            raise ValueError(f"Missing required API key env var: {config.api_key_env}")
        self.calls_today = 0

    def _cache_path(self, endpoint: str, params: dict[str, Any] | None) -> Path:
        key = json.dumps({"endpoint": endpoint, "params": params or {}}, sort_keys=True)
        digest = hashlib.sha256(key.encode("utf-8")).hexdigest()
        return self.cache_dir / f"{digest}.json"

    @sleep_and_retry
    @limits(calls=1, period=1)
    def _request(self, endpoint: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        if self.calls_today >= self.config.daily_call_cap:
            raise RuntimeError("Daily API call cap reached")
        merged = {"api_key": self.api_key, **(params or {})}
        url = f"{self.config.base_url.rstrip('/')}/{endpoint.lstrip('/')}"

        for attempt in range(1, self.config.retry_max_attempts + 1):
            resp = requests.get(url, params=merged, timeout=self.config.request_timeout_seconds)
            if resp.ok:
                self.calls_today += 1
                return resp.json()
            if attempt == self.config.retry_max_attempts:
                resp.raise_for_status()
            time.sleep(self.config.retry_backoff_base ** (attempt - 1))

        raise RuntimeError("Unreachable")

    def get_json(self, endpoint: str, params: dict[str, Any] | None = None, use_cache: bool = True) -> dict[str, Any]:
        cache_path = self._cache_path(endpoint, params)
        if use_cache and cache_path.exists():
            return json.loads(cache_path.read_text())
        payload = self._request(endpoint, params)
        cache_path.write_text(json.dumps(payload))
        return payload
