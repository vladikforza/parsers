from __future__ import annotations

import json
import os
import re
from pathlib import Path

from .config import Config
from .utils import utc_now_iso


_INVISIBLE_RE = re.compile(r"[\u200b\u200c\u200d\uFEFF]")
_WHITESPACE_RE = re.compile(r"\s+")


def normalize_header(header: str) -> str:
    value = header.strip()
    value = _INVISIBLE_RE.sub("", value)
    value = _WHITESPACE_RE.sub(" ", value)
    return value.lower()


def _ensure_dirs(config: Config) -> None:
    config.data_dir.mkdir(parents=True, exist_ok=True)


def load_header_index(config: Config) -> set[str]:
    _ensure_dirs(config)
    if not config.index_file.exists():
        return set()

    headers: set[str] = set()
    with config.index_file.open("r", encoding="utf-8") as handle:
        for line in handle:
            value = line.strip()
            if value:
                headers.add(value)
    return headers


def append_news(record: dict, config: Config) -> None:
    _ensure_dirs(config)
    with config.data_file.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False))
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())


def write_event(status: str, item: dict, config: Config, error_message: str | None = None) -> None:
    event = {
        "recorded_at": utc_now_iso(),
        "status": status,
        "item": item,
    }
    if error_message:
        event["error_message"] = error_message
    append_news(event, config)


def append_header(normalized_header: str, config: Config) -> None:
    _ensure_dirs(config)
    with config.index_file.open("a", encoding="utf-8") as handle:
        handle.write(normalized_header)
        handle.write("\n")
