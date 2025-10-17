from homeassistant.core import HomeAssistant
from . import HubConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity_registry import async_get as async_get_entity_registry
from homeassistant.helpers.area_registry import async_get as async_get_area_registry
from .chuguan.hub import ChuGuanDevice
from homeassistant.components.switch import SwitchEntity, SwitchDeviceClass
import logging
from .const import DOMAIN
from .entity import ChuGuanEntity

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: HubConfigEntry, async_add_entities: AddEntitiesCallback):
    """Set up the Chuguan Home switch platform."""
    _LOGGER.info('async_setup_entry switch with entry %s %s', entry, entry.data)
    hub = entry.runtime_data
    new_devices : list[ChuGuanSwitch]= []
    for device in hub.devices:
        if device.device_type == 'switch' or device.device_type == 'outlet':
            _LOGGER.info("Add switch %s %s", device.device_id, device.device)
            new_devices.append(ChuGuanSwitch(device))
    async_add_entities(new_devices)
    ChuGuanEntity.register_entity_areas(hass, new_devices)

class ChuGuanSwitch(ChuGuanEntity, SwitchEntity):
    """Chuguan Switch"""

    suffix: str = "switch"

    def __init__(self, device: ChuGuanDevice):
        super().__init__(device)
        if self._device.device_type == 'outlet':
            self._attr_device_class = SwitchDeviceClass.OUTLET

    @property
    def is_on(self) -> bool:
        return self._device.powerstate
    
    async def async_turn_on(self, **kwargs):
        """Turn the switch on."""
        _LOGGER.info("async_turn_on %s", kwargs)
        await self._device.set_powerstate(True)


    async def async_turn_off(self):
        """Turn the switch off."""
        await self._device.set_powerstate(False)