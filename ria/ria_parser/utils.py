from __future__ import annotations

import logging
import random
import re
import time
from datetime import datetime
from typing import Iterable

import requests

from .config import Config


MONTHS_RU = {
    "\u044f\u043d\u0432\u0430\u0440\u044f": 1,
    "\u0444\u0435\u0432\u0440\u0430\u043b\u044f": 2,
    "\u043c\u0430\u0440\u0442\u0430": 3,
    "\u0430\u043f\u0440\u0435\u043b\u044f": 4,
    "\u043c\u0430\u044f": 5,
    "\u0438\u044e\u043d\u044f": 6,
    "\u0438\u044e\u043b\u044f": 7,
    "\u0430\u0432\u0433\u0443\u0441\u0442\u0430": 8,
    "\u0441\u0435\u043d\u0442\u044f\u0431\u0440\u044f": 9,
    "\u043e\u043a\u0442\u044f\u0431\u0440\u044f": 10,
    "\u043d\u043e\u044f\u0431\u0440\u044f": 11,
    "\u0434\u0435\u043a\u0430\u0431\u0440\u044f": 12,
}


def setup_logger(config: Config) -> logging.Logger:
    logger = logging.getLogger("ria_parser")
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
        pass

    match = re.search(r"(\d{1,2})\.(\d{1,2})\.(\d{4})(?:\s+(\d{1,2}:\d{2}))?", value)
    if match:
        day, month, year, time_part = match.groups()
        hour = 0
        minute = 0
        if time_part:
            hour, minute = [int(x) for x in time_part.split(":")]
        return datetime(int(year), int(month), int(day), hour, minute)

    match = re.search(r"(\d{4})(\d{2})(\d{2})T(\d{2})(\d{2})(\d{2})?", value)
    if match:
        year, month, day, hour, minute, second = match.groups()
        return datetime(
            int(year),
            int(month),
            int(day),
            int(hour),
            int(minute),
            int(second) if second else 0,
        )

    match = re.search(
        r"(\d{1,2})\s+([\u0410-\u042f\u0430-\u044f]+)\s+(\d{4})(?:\s*[\u0433\u0413]\.?)?\s*(?:,|\s+)?(\d{1,2}:\d{2})?",
        value,
    )
    if match:
        day, month_name, year, time_part = match.groups()
        month = MONTHS_RU.get(month_name.lower())
        if month:
            hour = 0
            minute = 0
            if time_part:
                hour, minute = [int(x) for x in time_part.split(":")]
            return datetime(int(year), int(month), int(day), hour, minute)

    return None


def split_keywords(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def sanitize_tag(tag: str) -> str:
    return tag.lstrip("#").strip()


def join_paragraphs(paragraphs: Iterable[str]) -> str:
    cleaned = [p.strip() for p in paragraphs if p and p.strip()]
    return "\n".join(cleaned)
