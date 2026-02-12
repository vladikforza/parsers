from __future__ import annotations

import logging
import random
import time
from datetime import datetime
from typing import Iterable

import requests

from .config import Config


def setup_logger(config: Config) -> logging.Logger:
    logger = logging.getLogger("lenta_parser")
    if logger.handlers:
        return logger

    logger.setLevel(getattr(logging, config.log_level.upper(), logging.INFO))

    config.log_dir.mkdir(parents=True, exist_ok=True)

    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )

    file_handler = logging.FileHandler(config.log_file, encoding="utf-8")
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    return logger


def request_with_retries(url: str, config: Config) -> str:
    headers = {
        "User-Agent": config.user_agent,
        "Accept-Language": config.accept_language,
        "Referer": config.referer,
    }

    last_error = None
    for attempt in range(1, config.retry_count + 1):
        try:
            response = requests.get(url, headers=headers, timeout=config.timeout_seconds)
            if response.status_code in (429, 503):
                backoff = config.backoff_seconds * (2 ** (attempt - 1))
                time.sleep(backoff)
                continue
            response.raise_for_status()
            response.encoding = response.encoding or "utf-8"
            return response.text
        except requests.RequestException as exc:
            last_error = exc
            backoff = config.backoff_seconds * (2 ** (attempt - 1))
            time.sleep(backoff)

    raise RuntimeError(f"Failed to fetch {url}: {last_error}")


def rate_limit_sleep(config: Config) -> None:
    delay = random.uniform(config.rate_delay_min, config.rate_delay_max)
    time.sleep(delay)


def parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None

    value = value.strip()
    if not value:
        return None

    iso_candidate = value.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(iso_candidate)
    except ValueError:
        return None


def split_keywords(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def sanitize_tag(tag: str) -> str:
    return tag.lstrip("#").strip()


def join_paragraphs(paragraphs: Iterable[str]) -> str:
    cleaned = [p.strip() for p in paragraphs if p and p.strip()]
    return "\n".join(cleaned)
