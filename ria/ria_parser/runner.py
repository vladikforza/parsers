from __future__ import annotations

import argparse
import time
from datetime import datetime, timedelta

from news_api import push_news, should_pause
from .config import get_config
from .ria_politics import extract_news_urls, extract_url_date, fetch_section_html, parse_news
from .utils import rate_limit_sleep, setup_logger


def _run_iteration(config) -> bool:
    logger = setup_logger(config)
    logger.info("Iteration start")

    urls = _collect_section_urls(config)
    urls.sort(key=lambda item: extract_url_date(item) or datetime.min, reverse=True)
    logger.info("Found %s links", len(urls))

    cutoff = datetime.now() - timedelta(days=config.days_back)
    saved_count = 0

    for url in urls:
        rate_limit_sleep(config)
        try:
            record = parse_news(url, config)
        except Exception as exc:  # noqa: BLE001
            logger.error("Failed to parse %s: %s", url, exc)
            continue

        if not record:
            logger.error("Missing required fields for %s", url)
            continue

        record_date = datetime.fromisoformat(record["date"])
        if record_date.tzinfo is not None:
            record_date = record_date.astimezone().replace(tzinfo=None)
        if record_date < cutoff:
            logger.info("Stop iteration: older than %s", cutoff.isoformat())
            break

        item = {
            "header": record["header"],
            "text": record["text"],
            "date": record["date"],
            "hashtags": record["hashtags"],
            "source_name": record["source_name"],
        }
        result = push_news(item, logger)
        if should_pause(result):
            logger.info("Pause requested by backend response")
            return True
        saved_count += 1

    logger.info("Iteration finished: saved %s", saved_count)
    return False


def run_forever(config) -> None:
    logger = setup_logger(config)
    logger.info("Run forever with interval %s minutes", config.interval_minutes)
    while True:
        try:
            pause_requested = _run_iteration(config)
        except Exception as exc:  # noqa: BLE001
            logger.error("Iteration failed: %s", exc)
            pause_requested = False

        if pause_requested:
            time.sleep(5 * 60)
        else:
            time.sleep(config.interval_minutes * 60)


def _collect_section_urls(config) -> list[str]:
    html = fetch_section_html(config)
    return extract_news_urls(html, config)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="RIA politics news parser")
    parser.add_argument(
        "--interval-minutes",
        type=int,
        help="Override interval between iterations",
    )
    parser.add_argument(
        "--data-dir",
        type=str,
        help="Override data directory",
    )
    parser.add_argument(
        "--log-level",
        type=str,
        help="Override log level (INFO, DEBUG, etc)",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    overrides = {
        "interval_minutes": args.interval_minutes,
        "data_dir": args.data_dir,
        "log_level": args.log_level,
    }
    config = get_config(overrides)
    run_forever(config)


if __name__ == "__main__":
    main()
