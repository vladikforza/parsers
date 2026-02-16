"""File storage utilities for index and JSONL output."""

from pathlib import Path
import json
import logging

from . import config
from . import utils

logger = logging.getLogger(__name__)


def load_index(path):
    path = config.resolve_path(path)
    if not path.exists():
        return set()
    entries = set()
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            value = line.strip()
            if value:
                entries.add(value)
    return entries


def append_jsonl(path, record):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False, indent=2))
        handle.write("\n")


def append_index_key(path, key):
    path = config.resolve_path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(key)
        handle.write("\n")


def load_channels(path):
    path = config.resolve_path(path)
    if not path.exists():
        logger.warning("channels file not found: %s", path)
        return []
    channels = []
    seen = set()
    with path.open("r", encoding="utf-8-sig") as handle:
        for raw in handle:
            stripped = raw.strip()
            if not stripped or stripped.startswith("#"):
                continue
            normalized = utils.normalize_channel(raw)
            if not normalized:
                logger.warning("skipping invalid channel entry: %s", stripped)
                continue
            if normalized in seen:
                continue
            seen.add(normalized)
            channels.append(normalized)
    return channels


def get_channel_output_path(output_dir, channel):
    output_dir = config.resolve_path(output_dir)
    return output_dir / f"{channel}.jsonl"
