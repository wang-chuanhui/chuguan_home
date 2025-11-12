from homeassistant.core import HomeAssistant
from . import HubConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from .chuguan.hub import Hub, ChuGuanDevice
from homeassistant.components.light import LightEntity, ATTR_BRIGHTNESS, ColorMode, ATTR_COLOR_TEMP_KELVIN, ATTR_RGB_COLOR
import logging
import asyncio
from .entity import ChuGuanEntity, ChuGuanModeEntity, ChuGuanFunctionEntity
from .chuguan.model import ModeValue

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: HubConfigEntry, async_add_entities: AddEntitiesCallback):
    """Set up the Chuguan Home light platform."""
    hub = entry.runtime_data
    new_devices = []
    for device in hub.devices:
        if device.device_type == 'light_wy' or device.device_type == 'light_rgb' or device.device_type == 'light':
            new_devices.append(ChuGuanLight(device))
        if device.device_type == 'HANGER' and device.has_state:
            new_devices.append(ChuGuanModeLight(device, ModeValue.AirerLight, 'illumination', "照明"))
        if device.device_type == 'YUBA':
            new_devices.append(ChuGuanFunctionLight(device, 'lighting', 'illumination', "照明"))
    async_add_entities(new_devices)
    ChuGuanEntity.register_entity_areas(hass, new_devices)


class ChuGuanLight(ChuGuanEntity, LightEntity):
    """Chuguan Light"""
    suffix: str = "light"

    def __init__(self, device: ChuGuanDevice):
        super().__init__(device)
        self._attr_device_info = self._device.parent_info or self._device.device_info
        self._attr_supported_color_modes = {ColorMode.ONOFF}
        self._attr_color_mode = ColorMode.ONOFF
        if self._device.device_type == "light_wy":
            self._attr_supported_color_modes = {ColorMode.COLOR_TEMP}
            self._attr_color_mode = ColorMode.COLOR_TEMP
        elif self._device.device_type == "light_rgb":
            self._attr_supported_color_modes = {ColorMode.RGB, ColorMode.BRIGHTNESS, ColorMode.ONOFF}
            self._attr_color_mode = ColorMode.RGB
        self._attr_min_color_temp_kelvin = 2200
        self._attr_max_color_temp_kelvin = 5000
    
    # @property
    # def icon(self):
    #     if self.is_on:
    #         return 'mdi:lightbulb-on'
    #     else:
    #         return 'mdi:lightbulb'

    @property
    def is_on(self) -> bool:
        return self._device.powerstate
    
    @property
    def brightness(self) -> int | None:
        return self._device.brightness / 100 * 255
    
    @property
    def color_temp_kelvin(self) -> int | None:
        value = self._device.colorTemperature
        value = 100 - value
        value = value * (self._attr_max_color_temp_kelvin - self._attr_min_color_temp_kelvin) / 100 + self._attr_min_color_temp_kelvin
        return value

    @property
    def rgb_color(self) -> tuple[int, int, int] | None:
        return self._device.rgb
    
    async def async_turn_on(self, **kwargs):
        """Turn the light on."""
        _LOGGER.info("async_turn_on %s", kwargs)
        if self._device.powerstate == False:
            await self._device.set_powerstate(True)
        if ATTR_BRIGHTNESS in kwargs:
            brightness = kwargs[ATTR_BRIGHTNESS]
            value = brightness / 255 * 100
            await self._device.set_brightness(round(value))
        if ATTR_COLOR_TEMP_KELVIN in kwargs:
            vlaue = kwargs[ATTR_COLOR_TEMP_KELVIN]
            value = 100 - (vlaue - self._attr_min_color_temp_kelvin) * 100 / (self._attr_max_color_temp_kelvin - self._attr_min_color_temp_kelvin)
            await self._device.set_color_temp(round(value))
        if ATTR_RGB_COLOR in kwargs:
            rgb = kwargs[ATTR_RGB_COLOR]
            await self._device.set_rgb_color(rgb[0], rgb[1], rgb[2])


    async def async_turn_off(self):
        """Turn the light off."""
        await self._device.set_powerstate(False)


class ChuGuanModeLight(ChuGuanModeEntity, LightEntity):
    """Chuguan Light Mode"""


    def __init__(self, device, mode, key, name):
        super().__init__(device, mode, key, name)
        self._attr_supported_color_modes = {ColorMode.ONOFF}
        self._attr_color_mode = ColorMode.ONOFF



class ChuGuanFunctionLight(ChuGuanFunctionEntity, LightEntity):
    """Chuguan Function Light"""

    def __init__(self, device, function, key, name):
        super().__init__(device, function, key, name)
        self._attr_supported_color_modes = {ColorMode.ONOFF}
        self._attr_color_mode = ColorMode.ONOFF
