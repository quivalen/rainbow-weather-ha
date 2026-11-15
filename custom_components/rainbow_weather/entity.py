"""Shared entity behaviour."""
from datetime import datetime, timezone

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .forecast import current


class RainbowEntity(CoordinatorEntity):
    _attr_has_entity_name = True
    _attr_attribution = "Weather data by Rainbow Weather"

    def __init__(self, coordinator, entry, key, name):
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        self._attr_name = name
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=entry.title,
            manufacturer="Rainbow Weather",
        )

    @property
    def now(self):
        return datetime.now(timezone.utc).timestamp()

    @property
    def available(self):
        return super().available and current(self.coordinator.data, self.now) is not None
