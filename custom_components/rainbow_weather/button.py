"""Immediate refresh hook, usable with button.press in automations."""
from homeassistant.components.button import ButtonEntity
from homeassistant.helpers.entity import EntityCategory

from .const import DOMAIN
from .entity import RainbowEntity


async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities([RainbowRefreshButton(hass.data[DOMAIN][entry.entry_id], entry,
                                             "refresh", "Refresh forecast")])


class RainbowRefreshButton(RainbowEntity, ButtonEntity):
    _attr_icon = "mdi:refresh"
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def available(self):
        # Keep recovery possible even when cached data has expired or polling failed.
        return True

    async def async_press(self):
        await self.coordinator.async_request_refresh()
