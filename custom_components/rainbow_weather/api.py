"""Rainbow Weather API client."""

from __future__ import annotations

import json
import logging
import math
from typing import Any

from aiohttp import ClientError, ClientSession

from .const import API_URL

_LOGGER = logging.getLogger(__name__)


class RainbowWeatherError(Exception):
    """Error communicating with the Rainbow Weather API."""


class RainbowWeatherApi:
    """Small async client for Rainbow precipitation nowcasts."""

    def __init__(self, session: ClientSession, api_key: str) -> None:
        self._session = session
        self._api_key = api_key

    async def async_get_forecast(self, latitude: float, longitude: float) -> dict[str, Any]:
        """Fetch the four-hour, minute-by-minute precipitation forecast."""
        url = API_URL.format(latitude=latitude, longitude=longitude)
        headers = {
            "Ocp-Apim-Subscription-Key": self._api_key,
            # Rainbow's Cloudflare edge currently blocks default Python HTTP
            # client signatures. These headers allow normal API access.
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
            ),
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://developer.rainbow.ai/",
            "Origin": "https://developer.rainbow.ai",
        }
        try:
            async with self._session.get(url, headers=headers, timeout=30) as response:
                if response.status == 401:
                    raise RainbowWeatherError("Invalid Rainbow API key")
                if response.status == 403:
                    raise RainbowWeatherError(
                        "Rainbow API access was forbidden (403). Check API access and key."
                    )
                response.raise_for_status()
                try:
                    data = await response.json(content_type=None)
                except (json.JSONDecodeError, ClientError) as err:
                    raise RainbowWeatherError("Rainbow API returned invalid JSON") from err
        except RainbowWeatherError:
            raise
        except (ClientError, TimeoutError) as err:
            raise RainbowWeatherError(f"Error fetching Rainbow forecast: {err}") from err

        if not isinstance(data, dict) or not isinstance(data.get("forecast"), list):
            raise RainbowWeatherError("Rainbow API response did not contain a forecast")
        previous_end = None
        for item in data["forecast"]:
            if not isinstance(item, dict):
                raise RainbowWeatherError("Invalid forecast interval")
            values = [item.get(key) for key in ("timestampBegin", "timestampEnd", "precipRate")]
            if any(not isinstance(value, (int, float)) or isinstance(value, bool)
                   or not math.isfinite(value) for value in values):
                raise RainbowWeatherError("Invalid forecast values")
            start, end, rate = values
            if end <= start or rate < 0 or (previous_end is not None and start != previous_end):
                raise RainbowWeatherError("Invalid or discontinuous forecast intervals")
            if item.get("precipType") not in {"no_precipitation", "rain", "snow", "mixed"}:
                raise RainbowWeatherError("Invalid precipitation type")
            previous_end = end
        return data
