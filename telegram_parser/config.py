"""Configuration defaults for the Telegram parser."""

from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent


def _get_env(name, default=None, cast=None):
    value = os.getenv(name)
    if value is None or value == "":
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


API_ID = _get_env("API_ID", 21589677, int)
API_HASH = _get_env("API_HASH", "2ada8f50499f2c254b87134fd925609f")
SESSION_PATH = _get_env("SESSION_PATH", "data/telegram.session")

CHANNELS_PATH = _get_env("CHANNELS_PATH", "data/channels.txt")
OUTPUT_DIR = _get_env("OUTPUT_DIR", "data/telegram_posts")
OUTPUT_PATH = _get_env("OUTPUT_PATH", "data/telegram_posts.jsonl")
INDEX_PATH = _get_env("INDEX_PATH", "data/telegram_index.txt")
LOG_PATH = _get_env("LOG_PATH", None)
TELEGRAM_PHONE = _get_env("TELEGRAM_PHONE", None)
TELEGRAM_CODE = _get_env("TELEGRAM_CODE", None)
TELEGRAM_PASSWORD = _get_env("TELEGRAM_PASSWORD", None)
TELEGRAM_BOT_TOKEN = _get_env("TELEGRAM_BOT_TOKEN", None)

POLL_INTERVAL_MINUTES = _get_env("POLL_INTERVAL_MINUTES", 10, int)
LOOKBACK_DAYS = _get_env("LOOKBACK_DAYS", 2, int)
REQUEST_DELAY_RANGE = _parse_float_pair(
    os.getenv("REQUEST_DELAY_RANGE"),
    (0.3, 1.0),
)
