from __future__ import annotations

import json
import logging
import os
from typing import Any
from urllib import error as url_error
from urllib import request as url_request


DEFAULT_API_URL = "http://localhost:8080/test/save_news"
API_URL = os.getenv("NEWS_API_URL", DEFAULT_API_URL)
TIMEOUT_SECONDS = int(os.getenv("NEWS_API_TIMEOUT", "10"))


def push_news(item: dict, logger: logging.Logger | None = None) -> dict[str, Any] | None:
    payload = {
        "title": item.get("header", ""),
        "body": item.get("text", ""),
        "source": item.get("source_name"),
        "hash_tags": item.get("hashtags") or [],
        "published_at": item.get("date"),
    }
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = url_request.Request(
        API_URL,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with url_request.urlopen(req, timeout=TIMEOUT_SECONDS) as resp:
            body = resp.read().decode("utf-8")
    except url_error.HTTPError as exc:
        error_body = exc.read().decode("utf-8", errors="replace")
        if logger:
            logger.error("HTTP error pushing news: %s %s", exc.code, error_body)
        return None
    except Exception as exc:  # noqa: BLE001
        if logger:
            logger.error("Failed to push news: %s", exc)
        return None

    if not body:
        if logger:
            logger.error("Empty response from news API")
        return None

    try:
        return json.loads(body)
    except json.JSONDecodeError:
        if logger:
            logger.error("Invalid JSON response from news API: %s", body)
        return None


def should_pause(result: dict[str, Any] | None) -> bool:
    if result is None:
        return True
    return not bool(result.get("created", False))
