from __future__ import annotations

import argparse
import time
from datetime import datetime, timedelta

from .config import get_config
from .lenta_politic import extract_news_urls, extract_url_date, fetch_section_html, parse_news
from .storage import append_header, append_news, load_header_index, normalize_header
from .utils import rate_limit_sleep, setup_logger


def run_once(config) -> list[dict]:
    logger = setup_logger(config)
    logger.info("Iteration start")

    header_index = load_header_index(config)

    html = fetch_section_html(config)
    urls = extract_news_urls(html, config)
    urls.sort(key=lambda item: extract_url_date(item) or datetime.min, reverse=True)
    logger.info("Found %s links", len(urls))

    results = []
    cutoff = datetime.now() - timedelta(days=config.days_back)

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

        normalized_header = normalize_header(record["header"])
        if not config.disable_dedup and normalized_header in header_index:
            logger.info("Stop iteration: duplicate header")
            break

        results.append(record)
        append_news(record, config)
        append_header(normalized_header, config)
        header_index.add(normalized_header)

    logger.info("Iteration finished: saved %s", len(results))
    return results


def run_forever(config) -> None:
    logger = setup_logger(config)
    logger.info("Run forever with interval %s minutes", config.interval_minutes)
    while True:
        try:
            run_once(config)
        except Exception as exc:  # noqa: BLE001
            logger.error("Iteration failed: %s", exc)
        time.sleep(config.interval_minutes * 60)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Lenta world/politic news parser")
    parser.add_argument("--forever", action="store_true", help="Run in endless loop")
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

    if args.forever:
        run_forever(config)
    else:
        run_once(config)


if __name__ == "__main__":
    main()
