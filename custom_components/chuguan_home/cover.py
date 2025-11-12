from homeassistant.core import HomeAssistant
from . import HubConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity_registry import async_get as async_get_entity_registry
from homeassistant.helpers.area_registry import async_get as async_get_area_registry
from .chuguan.hub import ChuGuanDevice
from homeassistant.components.cover import CoverEntity, CoverDeviceClass, ATTR_POSITION
import logging
from .const import DOMAIN
from .entity import ChuGuanEntity
import asyncio
from .chuguan.utils import sync_non_blocking

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: HubConfigEntry, async_add_entities: AddEntitiesCallback):
    """Set up the Chuguan Home switch platform."""
    hub = entry.runtime_data
    new_devices : list[ChuGuanCover]= []
    for device in hub.devices:
        if device.device_type == 'curtain' or device.device_type == 'HANGER' or device.device_type == 'window':
            new_devices.append(ChuGuanCover(device))
    async_add_entities(new_devices)
    ChuGuanEntity.register_entity_areas(hass, new_devices)

class ChuGuanCover(ChuGuanEntity, CoverEntity):
    """Chuguan Cover"""

    suffix: str = "cover"
    isHanger: bool = False

    def __init__(self, device: ChuGuanDevice):
        super().__init__(device)
        self._attr_device_class = CoverDeviceClass.CURTAIN
        self._attr_device_info = self._device.parent_info or self._device.device_info
        if self._device.hardware_name == "Rols_ctler":
            self._attr_device_class = CoverDeviceClass.SHUTTER
        if self._device.device_type == 'HANGER':
            self._attr_device_class = CoverDeviceClass.SHUTTER
            self.isHanger = True
            self._attr_device_info = self._device.device_info
        if self._device.device_type == 'window':
            self._attr_device_class = CoverDeviceClass.WINDOW

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
    def current_cover_position(self) -> int | None:
        if self._device.has_state == False:
            return None
        return self._device.position
    
    @property
    def is_closed(self) -> bool | None:
        """Return if the cover is closed."""
        position = self._device.position
        if position is None:
            return None
        if self.isHanger:
            return position >= 99
        return position <= 1

    @property
    def is_closing(self) -> bool | None:
        if self._device.has_state == False:
            if self.second_of_last_update() > 2:
                return False
        if self.isHanger:
            return self._device.int_powerstate == 1
        return self._device.int_powerstate == 0
    
    @property
    def is_opening(self) -> bool | None:
        if self._device.has_state == False:
            if self.second_of_last_update() > 2:
                return False
        if self.isHanger:
            return self._device.int_powerstate == 0
        return self._device.int_powerstate == 1

    async def async_open_cover(self, **kwargs):
        """Open the cover."""
        _LOGGER.info("async_open_cover %s", kwargs)
        if self.isHanger:
            await self._device.set_powerstate(False)
        else:
            await self._device.set_powerstate(True)
    
    async def async_close_cover(self, **kwargs):
        """Close the cover."""
        _LOGGER.info("async_close_cover %s", kwargs)
        if self.isHanger:
            await self._device.set_powerstate(True)
        else:
            await self._device.set_powerstate(False)

    async def async_stop_cover(self, **kwargs):
        """Stop the cover."""
        _LOGGER.info("async_stop_cover %s", kwargs)
        await self._device.set_pause()

    async def async_set_cover_position(self, **kwargs):
        """Set the cover position."""
        _LOGGER.info("async_set_cover_position %s", kwargs)
        position = kwargs.get(ATTR_POSITION)
        if position is None:
            return
        await self._device.set_position(position)
