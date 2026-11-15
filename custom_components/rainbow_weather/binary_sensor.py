"""Near-term precipitation indication."""
from homeassistant.components.binary_sensor import BinarySensorEntity, BinarySensorDeviceClass

from .const import DOMAIN
from .entity import RainbowEntity
from .forecast import wet


async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities([RainbowExpectedSensor(hass.data[DOMAIN][entry.entry_id], entry,
                                              "expected", "Precipitation expected")])


class RainbowExpectedSensor(RainbowEntity, BinarySensorEntity):
    _attr_device_class = BinarySensorDeviceClass.MOISTURE

    @property
    def is_on(self):
        now = self.now
        return any(x["timestampBegin"] < now + 30 * 60
                   for x in wet(self.coordinator.data, now))

    @property
    def extra_state_attributes(self):
        return {"look_ahead_minutes": 30}
