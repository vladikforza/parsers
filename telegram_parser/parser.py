"""Telegram parsing logic."""

from datetime import datetime, timedelta, timezone
import logging
import random
import time

from telethon.errors import FloodWaitError, RPCError

from . import config
from . import storage
from . import utils
from news_api import push_news, should_pause

logger = logging.getLogger(__name__)


def _sleep_with_jitter():
    delay = random.uniform(*config.REQUEST_DELAY_RANGE)
    time.sleep(delay)


def _get_messages_with_retries(client, entity, channel, offset_id):
    delays = [1, 2, 4]
    for attempt, delay in enumerate(delays, 1):
        try:
            return client.get_messages(entity, limit=100, offset_id=offset_id)
        except FloodWaitError:
            raise
        except RPCError:
            raise
        except Exception as exc:
            logger.warning(
                "network error while fetching %s (attempt %s/%s): %s",
                channel,
                attempt,
                len(delays),
                exc,
            )
            if attempt == len(delays):
                raise
            time.sleep(delay)


def _build_item(channel, message):
    text = message.raw_text or ""
    header = text.splitlines()[0] if text else ""
    channel_name = channel.lstrip("@")
    return {
        "header": header,
        "text": text,
        "date": utils.to_utc_iso(message.date),
        "hashtags": utils.extract_hashtags(text),
        "source_name": f"https://t.me/{channel_name}",
    }


def fetch_new_posts_for_channel(client, channel, cutoff_dt):
    output_path = config.resolve_path(config.OUTPUT_PATH)
    saved_count = 0
    pause_requested = False
    stop_reason = None
    try:
        entity = client.get_entity(channel)
    except Exception:
        logger.exception("failed to resolve channel entity: %s", channel)
        return saved_count, pause_requested, "error"

    offset_id = 0
    while True:
        try:
            messages = _get_messages_with_retries(client, entity, channel, offset_id)
        except FloodWaitError as exc:
            wait_seconds = exc.seconds + 1
            logger.warning("FloodWait for %s, sleeping %s seconds", channel, wait_seconds)
            time.sleep(wait_seconds)
            continue
        except RPCError:
            logger.exception("RPC error while fetching %s", channel)
            return saved_count, pause_requested, "error"
        except Exception:
            logger.exception("unexpected error while fetching %s", channel)
            return saved_count, pause_requested, "error"

        if not messages:
            break

        for message in messages:
            if message is None or message.id is None or message.date is None:
                continue
            if message.date < cutoff_dt:
                stop_reason = "older_than_lookback"
                break

            item = _build_item(channel, message)
            if not item.get("header") or not item.get("text"):
                continue
            result = push_news(item, logger)
            storage.append_jsonl(
                output_path,
                {
                    "header": item["header"],
                    "text": item["text"],
                    "date": item["date"],
                    "hashtags": item["hashtags"],
                    "source_name": item["source_name"],
                },
            )
            if should_pause(result):
                stop_reason = "backend_pause"
                pause_requested = True
                break
            saved_count += 1
            _sleep_with_jitter()

        if stop_reason:
            break

        offset_id = messages[-1].id
        _sleep_with_jitter()

    if stop_reason is None:
        stop_reason = "done"

    return saved_count, pause_requested, stop_reason
