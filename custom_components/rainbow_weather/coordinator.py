"""Data update coordinator for Rainbow Weather."""

from __future__ import annotations

from datetime import datetime, timezone
import logging
from typing import Any

from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)
from homeassistant.helpers.event import async_track_time_interval
from datetime import timedelta

from .api import RainbowWeatherApi, RainbowWeatherError
from .const import SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)


class RainbowWeatherCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Fetch every five minutes and advance cached values every minute."""

    def __init__(
        self,
        hass: HomeAssistant,
        api: RainbowWeatherApi,
        latitude: float,
        longitude: float,
    ) -> None:
        self.api = api
        self.latitude = latitude
        self.longitude = longitude
        super().__init__(
            hass,
            _LOGGER,
            name="Rainbow Weather",
            update_interval=SCAN_INTERVAL,
        )

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            data = await self.api.async_get_forecast(self.latitude, self.longitude)
            data["fetched_at"] = datetime.now(timezone.utc)
            return data
        except RainbowWeatherError as err:
            raise UpdateFailed(str(err)) from err

    def start_clock(self):
        """Return the unsubscribe callback for local-only state updates."""
        @callback
        def tick(now):
            self.async_update_listeners()

        return async_track_time_interval(self.hass, tick, timedelta(minutes=1))
