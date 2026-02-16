"""Utility helpers for normalization and formatting."""

from datetime import timezone
import re

_VALID_USERNAME_RE = re.compile(r"^[A-Za-z0-9_]+$")
_HASHTAG_RE = re.compile(r"#(\w+)")


def normalize_channel(raw):
    if raw is None:
        return None
    value = raw.strip()
    if not value or value.startswith("#"):
        return None
    lowered = value.lower()
    if "t.me/+" in lowered or "joinchat" in lowered:
        return None
    value = re.sub(r"^https?://", "", value, flags=re.IGNORECASE)
    if value.lower().startswith("t.me/"):
        value = value[5:]
    if value.startswith("@"):
        value = value[1:]
    value = value.split("?")[0].split("#")[0]
    value = value.strip().strip("/")
    if "/" in value:
        value = value.split("/")[0]
    if not value:
        return None
    if not _VALID_USERNAME_RE.match(value):
        return None
    return value


def to_utc_iso(dt):
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    dt = dt.astimezone(timezone.utc)
    return dt.strftime("%d-%m-%Y")


def extract_hashtags(text):
    if not text:
        return []
    tags = []
    seen = set()
    for match in _HASHTAG_RE.findall(text):
        tag = match.lower()
        if tag in seen:
            continue
        seen.add(tag)
        tags.append(tag)
    return tags
