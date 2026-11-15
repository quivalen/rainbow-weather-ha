"""Config flow for Rainbow Weather."""

from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_LATITUDE, CONF_LONGITUDE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import RainbowWeatherApi, RainbowWeatherError
from .const import CONF_API_KEY, DOMAIN


async def _validate_input(hass: HomeAssistant, data: dict) -> None:
    """Validate credentials and coordinates with a test request."""
    api = RainbowWeatherApi(async_get_clientsession(hass), data[CONF_API_KEY])
    await api.async_get_forecast(
        float(data[CONF_LATITUDE]), float(data[CONF_LONGITUDE])
    )


class RainbowWeatherConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Rainbow Weather."""

    VERSION = 1

    async def async_step_user(self, user_input: dict | None = None):
        """Ask for API key and location, then verify the connection."""
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                await _validate_input(self.hass, user_input)
            except RainbowWeatherError:
                errors["base"] = "cannot_connect"
            except Exception:  # noqa: BLE001 - show unexpected setup failures in UI
                errors["base"] = "unknown"
            else:
                await self.async_set_unique_id(
                    f"{float(user_input[CONF_LATITUDE]):.5f},"
                    f"{float(user_input[CONF_LONGITUDE]):.5f}"
                )
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title="Rainbow Weather",
                    data={
                        CONF_API_KEY: user_input[CONF_API_KEY],
                        CONF_LATITUDE: float(user_input[CONF_LATITUDE]),
                        CONF_LONGITUDE: float(user_input[CONF_LONGITUDE]),
                    },
                )

        schema = vol.Schema(
            {
                vol.Required(CONF_API_KEY): str,
                vol.Required(
                    CONF_LATITUDE, default=self.hass.config.latitude
                ): vol.All(vol.Coerce(float), vol.Range(min=-90, max=90)),
                vol.Required(
                    CONF_LONGITUDE, default=self.hass.config.longitude
                ): vol.All(vol.Coerce(float), vol.Range(min=-180, max=180)),
            }
        )
        return self.async_show_form(
            step_id="user", data_schema=schema, errors=errors
        )
