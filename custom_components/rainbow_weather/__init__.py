"""Rainbow Weather integration."""

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_LATITUDE, CONF_LONGITUDE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import RainbowWeatherApi
from .const import CONF_API_KEY, DOMAIN, PLATFORMS
from .coordinator import RainbowWeatherCoordinator


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Rainbow Weather from a config entry."""
    api = RainbowWeatherApi(
        async_get_clientsession(hass), entry.data[CONF_API_KEY]
    )
    coordinator = RainbowWeatherCoordinator(
        hass,
        api,
        float(entry.data[CONF_LATITUDE]),
        float(entry.data[CONF_LONGITUDE]),
    )
    await coordinator.async_config_entry_first_refresh()
    entry.async_on_unload(coordinator.start_clock())
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a Rainbow Weather config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
