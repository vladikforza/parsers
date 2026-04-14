"""Configuration defaults for the Telegram parser."""

from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent


def _get_env(name, default=None, cast=None):
    value = os.getenv(name)
    if value is None or value.strip() == "":
        return default
    if cast is None:
        return value
    try:
        return cast(value)
    except (TypeError, ValueError):
        return default


def _parse_float_pair(value, default):
    if not value:
        return default
    try:
        parts = [float(x.strip()) for x in value.split(",")]
        if len(parts) != 2:
            return default
        return (parts[0], parts[1])
    except (TypeError, ValueError):
        return default


def resolve_path(path_str):
    path = Path(path_str)
    if path.is_absolute():
        return path
    return BASE_DIR / path


NEWS_API_URL = _get_env("NEWS_API_URL", "http://localhost:8080/test/save_news")
NEWS_API_TIMEOUT = _get_env("NEWS_API_TIMEOUT", 10, int)

API_ID = _get_env("API_ID", None, int)
API_HASH = _get_env("API_HASH", None)
SESSION_PATH = _get_env("SESSION_PATH", "data/telegram.session")

CHANNELS_PATH = _get_env("CHANNELS_PATH", "data/channels.txt")
OUTPUT_DIR = _get_env("OUTPUT_DIR", "data/telegram_posts")
OUTPUT_PATH = _get_env("OUTPUT_PATH", "data/telegram_posts.jsonl")
INDEX_PATH = _get_env("INDEX_PATH", "data/telegram_index.txt")
ERROR_LOG_PATH = _get_env("ERROR_LOG_PATH", "logs/telegram_errors.log")
POLL_INTERVAL_MINUTES = _get_env("POLL_INTERVAL_MINUTES", 10, int)
LOOKBACK_DAYS = _get_env("LOOKBACK_DAYS", 2, int)
CHANNEL_SWITCH_DELAY_SECONDS = _get_env("CHANNEL_SWITCH_DELAY_SECONDS", 5, int)
REQUEST_DELAY_RANGE = _parse_float_pair(
    os.getenv("REQUEST_DELAY_RANGE"),
    (2.0, 7.0),
)

LOG_PATH = os.getenv("LOG_PATH")
TELEGRAM_PHONE = os.getenv("TELEGRAM_PHONE")
TELEGRAM_CODE = os.getenv("TELEGRAM_CODE")
TELEGRAM_PASSWORD = os.getenv("TELEGRAM_PASSWORD")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
