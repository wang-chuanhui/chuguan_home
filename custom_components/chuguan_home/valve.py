import asyncio
from .entity import ChuGuanEntity
from homeassistant.components.valve import ValveEntity, ValveDeviceClass, ValveEntityFeature
from .chuguan.utils import sync_non_blocking
import logging
from homeassistant.core import HomeAssistant
from . import HubConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback


_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: HubConfigEntry, async_add_entities: AddEntitiesCallback):
    """Set up the Chuguan Home switch platform."""
    hub = entry.runtime_data
    new_devices : list[ChuGuanValve]= []
    for device in hub.devices:
        if device.device_type == 'manip_ctler':
            new_devices.append(ChuGuanValve(device))
    async_add_entities(new_devices)
    ChuGuanEntity.register_entity_areas(hass, new_devices)


class ChuGuanValve(ChuGuanEntity, ValveEntity):
    """Chuguan Valve"""
    suffix: str = "valve"

    def __init__(self, device):
        super().__init__(device)
        self._attr_device_class = ValveDeviceClass.WATER
        self._attr_device_info = self._device.parent_info or self._device.device_info
        self._attr_supported_features = ValveEntityFeature.OPEN | ValveEntityFeature.CLOSE | ValveEntityFeature.STOP
        self._attr_reports_position = False

    def _on_state_changed(self, state: dict):
        super()._on_state_changed(state)
        if self._device.has_state == False:
            powerstate = self._device.int_powerstate
            if powerstate != 2:
                corn = self.async_auto_stop()
                sync_non_blocking(corn)

    async def async_auto_stop(self):
        """Auto stop the cover."""
        await asyncio.sleep(3)
        self.publish_update()

    @property
    def current_valve_position(self) -> int | None:
        return self._device.position
    
    @property
    def is_closed(self) -> bool | None:
        """Return if the cover is closed."""
        position = self._device.position
        if position is None:
            return None
        return position <= 1

    @property
    def is_closing(self) -> bool | None:
        if self._device.has_state == False:
            if self.second_of_last_update() > 2:
                return False
        return self._device.int_powerstate == 0
    
    @property
    def is_opening(self) -> bool | None:
        if self._device.has_state == False:
            if self.second_of_last_update() > 2:
                return False
        return self._device.int_powerstate == 1
    
    async def async_open_valve(self, **kwargs):
        """Open the valve."""
        _LOGGER.info("async_open_valve %s", kwargs)
        await self._device.set_powerstate(True)
    
    async def async_close_valve(self, **kwargs):
        """Close the valve."""
        _LOGGER.info("async_close_valve %s", kwargs)
        await self._device.set_powerstate(False)

    async def async_stop_valve(self, **kwargs):
        """Stop the valve."""
        _LOGGER.info("async_stop_valve %s", kwargs)
        await self._device.set_pause()