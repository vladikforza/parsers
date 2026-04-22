from __future__ import annotations

import logging
from typing import Any, Dict

import httpx

logger = logging.getLogger(__name__)


class BackendClient:
    """
    HTTP client for the provided backend.
    """

    def __init__(self, url: str, timeout: int) -> None:
        self.url = url
        self.timeout = timeout
        self._client = httpx.AsyncClient(timeout=self.timeout)

    async def save_news(self, payload: Dict[str, Any]) -> bool | None:
        """
        Send news payload to backend.

        Returns:
            True  -> backend created the news item
            False -> backend responded with created=false (HTTP 200)
            None  -> transport/HTTP error, caller should continue
        """
        try:
            resp = await self._client.post(self.url, json=payload)
        except Exception as exc:  # noqa: BLE001
            logger.warning("Backend request failed: %s", exc)
            return None

        if resp.status_code != 200:
            logger.warning("Backend returned status %s, continuing parsing", resp.status_code)
            return None

        try:
            data = resp.json()
        except Exception as exc:  # noqa: BLE001
            logger.warning("Backend response JSON decode failed: %s", exc)
            return None

        return bool(data.get("created", False))

    async def close(self) -> None:
        await self._client.aclose()
