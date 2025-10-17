from homeassistant.core import HomeAssistant
from . import HubConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from .hub import ChuGuanDevice
from homeassistant.components.switch import SwitchEntity, SwitchDeviceClass
import logging

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: HubConfigEntry, async_add_entities: AddEntitiesCallback):
    """Set up the Chuguan Home switch platform."""
    _LOGGER.info('async_setup_entry switch with entry %s %s', entry, entry.data)
    hub = entry.runtime_data
    new_devices = []
    for device in hub.devices:
        if device.device_type == 'switch' or device.device_type == 'outlet':
            _LOGGER.info("Add switch %s %s", device.device_id, device.device)
            new_devices.append(ChuGuanSwitch(device))
    async_add_entities(new_devices)


class ChuGuanSwitch(SwitchEntity):
    """Chuguan Switch"""


    def __init__(self, device: ChuGuanDevice):
        self._device = device
        self._attr_unique_id = f"{self._device.device_id}_switch"
        self._attr_name = self._device.device_name
        if self._device.device_type == 'outlet':
            self._attr_device_class = SwitchDeviceClass.OUTLET
        if self._device.has_state == False:
            self._attr_assumed_state = True
            self._attr_should_poll = False
        self._device.on('state_update', self._on_state_update)

    def __del__(self):
        """Stop device"""
        _LOGGER.info("Stop switch %s %s", self._device.device_id, self._device.device_name)

    def _on_state_update(self, state: dict):
        """On state update"""
        self.hass.loop.call_soon_threadsafe(self.async_write_ha_state)

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