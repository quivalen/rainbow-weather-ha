"""Precipitation sensors and complete minute forecast."""
from datetime import datetime, timezone

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass, SensorStateClass
from homeassistant.const import UnitOfPrecipitationDepth, UnitOfVolumetricFlux
from homeassistant.helpers.entity import EntityCategory

from .const import DOMAIN
from .entity import RainbowEntity
from .forecast import current, remaining, wet, total, episode_end


SENSORS = {
    "rate": ("Precipitation rate", UnitOfVolumetricFlux.MILLIMETERS_PER_HOUR),
    "type": ("Precipitation type", None),
    "start": ("Next precipitation start", None),
    "end": ("Current precipitation end", None),
    "total": ("Forecast precipitation total", UnitOfPrecipitationDepth.MILLIMETERS),
    "peak": ("Peak precipitation rate", UnitOfVolumetricFlux.MILLIMETERS_PER_HOUR),
    "summary": ("Forecast summary", None),
    "fetched": ("Forecast fetched", None),
}


async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities([RainbowSensor(hass.data[DOMAIN][entry.entry_id], entry, key)
                        for key in SENSORS])


class RainbowSensor(RainbowEntity, SensorEntity):
    _unrecorded_attributes = frozenset({"forecast"})

    def __init__(self, coordinator, entry, key):
        name, unit = SENSORS[key]
        super().__init__(coordinator, entry, key, name)
        self.key = key
        self._attr_native_unit_of_measurement = unit
        if key in {"start", "end", "fetched"}:
            self._attr_device_class = SensorDeviceClass.TIMESTAMP
        if unit:
            self._attr_state_class = SensorStateClass.MEASUREMENT
            self._attr_suggested_display_precision = 3
        if key == "fetched":
            self._attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def native_value(self):
        data, now = self.coordinator.data, self.now
        item = current(data, now)
        if self.key == "fetched":
            return data.get("fetched_at")
        if not item:
            return None
        if self.key == "rate":
            return item["precipRate"]
        if self.key == "type":
            return item["precipType"]
        if self.key == "summary":
            return data.get("summary", {}).get("intensity")
        if self.key == "total":
            return total(data, now)
        if self.key == "peak":
            return max(x["precipRate"] for x in remaining(data, now))
        stamp = None
        if self.key == "start" and item["precipRate"] <= 0:
            upcoming = wet(data, now)
            stamp = upcoming[0]["timestampBegin"] if upcoming else None
        if self.key == "end":
            stamp = episode_end(data, now)
        return datetime.fromtimestamp(stamp, timezone.utc) if stamp is not None else None

    @property
    def extra_state_attributes(self):
        if self.key != "summary":
            return None
        return {"forecast": [
            {"time": datetime.fromtimestamp(x["timestampBegin"], timezone.utc).isoformat(),
             "rate_mm_per_hour": x["precipRate"], "type": x["precipType"]}
            for x in remaining(self.coordinator.data, self.now)
        ]}
