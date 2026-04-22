from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Config:
    sleep_seconds: int
    request_timeout: int
    max_retries: int
    news_api_url: str
    news_api_timeout: int
    log_level: str


def _required_env(name: str) -> str:
    value = os.getenv(name)
    if value is None or value.strip() == "":
        raise RuntimeError(f"Required environment variable {name} is not set")
    return value.strip()


def _required_int(name: str) -> int:
    value = _required_env(name)
    try:
        return int(value)
    except ValueError as exc:
        raise RuntimeError(f"Environment variable {name} must be an integer") from exc


def get_config() -> Config:
    return Config(
        sleep_seconds=_required_int("SLEEP_SECONDS"),
        request_timeout=_required_int("REQUEST_TIMEOUT"),
        max_retries=_required_int("MAX_RETRIES"),
        news_api_url=_required_env("NEWS_API_URL"),
        news_api_timeout=_required_int("NEWS_API_TIMEOUT"),
        log_level=_required_env("LOG_LEVEL").upper(),
    )
