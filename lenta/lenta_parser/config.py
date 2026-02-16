from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os


def _env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None or value.strip() == "":
        return default
    try:
        return int(value)
    except ValueError:
        return default


def _env_float(name: str, default: float) -> float:
    value = os.getenv(name)
    if value is None or value.strip() == "":
        return default
    try:
        return float(value)
    except ValueError:
        return default


def _env_str(name: str, default: str) -> str:
    value = os.getenv(name)
    if value is None or value.strip() == "":
        return default
    return value


def _env_path(name: str, default: Path) -> Path:
    value = os.getenv(name)
    if value is None or value.strip() == "":
        return default
    return Path(value)


@dataclass(frozen=True)
class Config:
    project_root: Path
    data_dir: Path
    log_dir: Path
    data_file: Path
    index_file: Path
    log_file: Path
    base_url: str
    section_url: str
    source_name: str
    interval_minutes: int
    days_back: int
    max_pages: int
    timeout_seconds: int
    retry_count: int
    backoff_seconds: float
    rate_delay_min: float
    rate_delay_max: float
    user_agent: str
    accept_language: str
    referer: str
    log_level: str
    disable_dedup: bool


DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)


def get_config(overrides: dict | None = None) -> Config:
    project_root = Path(__file__).resolve().parent

    data_dir = _env_path("LENTA_DATA_DIR", project_root / "data")
    log_dir = _env_path("LENTA_LOG_DIR", project_root / "logs")

    data_file = data_dir / "lenta_world_politic.jsonl"
    index_file = data_dir / "lenta_world_politic_headers.txt"
    log_file = log_dir / "lenta_parser.log"

    base_url = _env_str("LENTA_BASE_URL", "https://lenta.ru")
    section_url = _env_str(
        "LENTA_SECTION_URL", "https://lenta.ru/rubrics/world/politic/"
    )
    source_name = _env_str("LENTA_SOURCE_NAME", "lenta_world_politic")

    interval_minutes = _env_int("LENTA_INTERVAL_MINUTES", 10)
    days_back = _env_int("LENTA_DAYS_BACK", 2)
    max_pages = _env_int("LENTA_MAX_PAGES", 10)

    timeout_seconds = _env_int("LENTA_TIMEOUT_SECONDS", 15)
    retry_count = _env_int("LENTA_RETRY_COUNT", 3)
    backoff_seconds = _env_float("LENTA_BACKOFF_SECONDS", 1.0)

    rate_delay_min = _env_float("LENTA_RATE_DELAY_MIN", 0.5)
    rate_delay_max = _env_float("LENTA_RATE_DELAY_MAX", 1.5)

    user_agent = _env_str("LENTA_USER_AGENT", DEFAULT_USER_AGENT)
    accept_language = _env_str("LENTA_ACCEPT_LANGUAGE", "ru-RU,ru;q=0.9")
    referer = _env_str("LENTA_REFERER", "https://lenta.ru/rubrics/world/politic/")
    log_level = _env_str("LENTA_LOG_LEVEL", "INFO")
    disable_dedup = _env_str("LENTA_DISABLE_DEDUP", "1") == "1"

    if overrides:
        if "data_dir" in overrides and overrides["data_dir"] is not None:
            data_dir = Path(overrides["data_dir"])
            data_file = data_dir / "lenta_world_politic.jsonl"
            index_file = data_dir / "lenta_world_politic_headers.txt"
        if "log_dir" in overrides and overrides["log_dir"] is not None:
            log_dir = Path(overrides["log_dir"])
            log_file = log_dir / "lenta_parser.log"

        if "interval_minutes" in overrides and overrides["interval_minutes"] is not None:
            interval_minutes = int(overrides["interval_minutes"])
        if "log_level" in overrides and overrides["log_level"] is not None:
            log_level = str(overrides["log_level"])

    return Config(
        project_root=project_root,
        data_dir=data_dir,
        log_dir=log_dir,
        data_file=data_file,
        index_file=index_file,
        log_file=log_file,
        base_url=base_url,
        section_url=section_url,
        source_name=source_name,
        interval_minutes=interval_minutes,
        days_back=days_back,
        max_pages=max_pages,
        timeout_seconds=timeout_seconds,
        retry_count=retry_count,
        backoff_seconds=backoff_seconds,
        rate_delay_min=rate_delay_min,
        rate_delay_max=rate_delay_max,
        user_agent=user_agent,
        accept_language=accept_language,
        referer=referer,
        log_level=log_level,
        disable_dedup=disable_dedup,
    )
