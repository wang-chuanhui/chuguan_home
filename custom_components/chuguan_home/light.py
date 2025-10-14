from homeassistant.core import HomeAssistant
from . import HubConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from .hub import Hub, ChuGuanDevice
from homeassistant.components.light import LightEntity, ATTR_BRIGHTNESS, ColorMode, ATTR_COLOR_TEMP_KELVIN
import logging
import asyncio

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: HubConfigEntry, async_add_entities: AddEntitiesCallback):
    """Set up the Chuguan Home light platform."""
    hub = entry.runtime_data
    new_devices = []
    for device in hub.devices:
        if device.device_type == 'light_wy':
            _LOGGER.info("Add light %s %s", device.device_id, device.device_name)
            new_devices.append(ChuGuanLight(device, hub))
    async_add_entities(new_devices)


class ChuGuanLight(LightEntity):
    """Chuguan Light"""


    def __init__(self, device: ChuGuanDevice, hub: Hub):
        self._device = device
        self._hub = hub
        self._attr_supported_color_modes = {ColorMode.BRIGHTNESS, ColorMode.ONOFF, ColorMode.COLOR_TEMP}
        self._state = False
        self._brightness = 1
        self._temp = None
        self._attr_unique_id = f"{self._device.device_id}_light"
        self._attr_name = self._device.device_name

    @property
    def is_on(self) -> bool:
        _LOGGER.info("is_on %s", self._state)
        return self._state
    
    @property
    def brightness(self) -> int | None:
        _LOGGER.info("brightness %s", self._brightness)
        if self._state:
            return self._brightness
        return None
    
    @property
    def color_temp_kelvin(self) -> int | None:
        _LOGGER.info("color_temp_kelvin %s", self._temp)
        if self._state:
            return self._temp
        return None
    
    async def async_turn_on(self, **kwargs):
        """Turn the light on."""
        _LOGGER.info("async_turn_on %s %s", self._state, kwargs)
        await asyncio.sleep(0.5)
        self._state = True
        if ATTR_BRIGHTNESS in kwargs:
            self._brightness = kwargs[ATTR_BRIGHTNESS]
        if ATTR_COLOR_TEMP_KELVIN in kwargs:
            self._temp = kwargs[ATTR_COLOR_TEMP_KELVIN]
        self.async_write_ha_state()


    async def async_turn_off(self):
        """Turn the light off."""
        await asyncio.sleep(0.5)
        self._state = False
        _LOGGER.info("async_turn_off %s", self._state)
        self.async_write_ha_state()