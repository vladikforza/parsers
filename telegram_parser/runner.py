"""Entry points for running the parser."""

from datetime import datetime, timedelta, timezone
import logging
import time

from telethon.sync import TelegramClient

from . import config
from . import parser as tg_parser
from . import storage


def _setup_logging():
    handlers = [logging.StreamHandler()]
    if config.LOG_PATH:
        log_path = config.resolve_path(config.LOG_PATH)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(log_path, encoding="utf-8"))

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
        handlers=handlers,
    )


def _run_iteration() -> bool:
    logger = logging.getLogger(__name__)

    channels = storage.load_channels(config.CHANNELS_PATH)
    logger.info("loaded %s channels", len(channels))

    session_path = config.resolve_path(config.SESSION_PATH)
    session_path.parent.mkdir(parents=True, exist_ok=True)

    cutoff_dt = datetime.now(timezone.utc) - timedelta(days=config.LOOKBACK_DAYS)

    total_saved = 0
    pause_requested = False
    client = TelegramClient(str(session_path), config.API_ID, config.API_HASH)
    try:
        client.connect()
        if client.is_user_authorized():
            pass
        elif config.TELEGRAM_BOT_TOKEN:
            client.start(bot_token=config.TELEGRAM_BOT_TOKEN)
        elif config.TELEGRAM_PHONE:
            if not config.TELEGRAM_CODE:
                client.send_code_request(config.TELEGRAM_PHONE)
                raise RuntimeError(
                    "Login code sent. Set TELEGRAM_CODE (and TELEGRAM_PASSWORD if needed) and rerun."
                )

            def _code_callback():
                return config.TELEGRAM_CODE

            client.start(
                phone=config.TELEGRAM_PHONE,
                code_callback=_code_callback,
                password=config.TELEGRAM_PASSWORD,
            )
        else:
            raise RuntimeError(
                "Set TELEGRAM_PHONE and TELEGRAM_CODE (or TELEGRAM_BOT_TOKEN) for non-interactive login."
            )

        for channel in channels:
            logger.info("processing channel %s", channel)
            saved_count, channel_pause, reason = tg_parser.fetch_new_posts_for_channel(
                client,
                channel,
                cutoff_dt,
            )
            logger.info(
                "channel %s: %s new posts, stop reason=%s",
                channel,
                saved_count,
                reason,
            )
            total_saved += saved_count
            if channel_pause:
                pause_requested = True
                break
            time.sleep(1)
    finally:
        client.disconnect()

    logger.info("iteration complete, new posts: %s", total_saved)
    return pause_requested


def run_forever():
    _setup_logging()
    logger = logging.getLogger(__name__)
    while True:
        pause_requested = _run_iteration()
        if pause_requested:
            logger.info("sleeping for 5 minutes due to backend response")
            time.sleep(5 * 60)
        else:
            logger.info("sleeping for %s minutes", config.POLL_INTERVAL_MINUTES)
            time.sleep(config.POLL_INTERVAL_MINUTES * 60)
