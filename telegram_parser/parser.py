"""Telegram parsing logic."""

from datetime import datetime, timedelta, timezone
import logging
import random
import time

from telethon.errors import FloodWaitError, RPCError

from . import config
from . import storage
from . import utils

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
    return {
        "message_id": message.id,
        "text": text,
        "date": utils.to_utc_iso(message.date),
        "hashtags": utils.extract_hashtags(text),
        "source_name": channel,
        "url": f"https://t.me/{channel}/{message.id}",
    }


def fetch_new_posts_for_channel(client, channel, index_set, cutoff_dt, output_dir, index_path):
    records = []
    stop_reason = None
    try:
        entity = client.get_entity(channel)
    except Exception:
        logger.exception("failed to resolve channel entity: %s", channel)
        error_item = {"source_name": channel}
        output_path = storage.get_channel_output_path(output_dir, channel)
        storage.write_event(output_path, "error", error_item, "failed to resolve channel entity")
        return records, "error"

    output_path = storage.get_channel_output_path(output_dir, channel)
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
            error_item = {"source_name": channel}
            storage.write_event(output_path, "error", error_item, "RPC error while fetching messages")
            return records, "error"
        except Exception:
            logger.exception("unexpected error while fetching %s", channel)
            error_item = {"source_name": channel}
            storage.write_event(output_path, "error", error_item, "unexpected error while fetching messages")
            return records, "error"

        if not messages:
            break

        for message in messages:
            if message is None or message.id is None or message.date is None:
                continue
            if message.date < cutoff_dt:
                stop_reason = "older_than_lookback"
                break
            unique_key = f"{channel}:{message.id}"
            if unique_key in index_set:
                item = _build_item(channel, message)
                storage.write_event(output_path, "duplicate", item)
                stop_reason = "duplicate"
                break

            item = _build_item(channel, message)
            storage.write_event(output_path, "stored", item)
            storage.append_index_key(index_path, unique_key)
            index_set.add(unique_key)
            records.append(item)
            _sleep_with_jitter()

        if stop_reason:
            break

        offset_id = messages[-1].id
        _sleep_with_jitter()

    if stop_reason is None:
        stop_reason = "done"

    return records, stop_reason
