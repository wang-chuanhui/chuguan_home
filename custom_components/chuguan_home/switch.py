from homeassistant.core import HomeAssistant
from . import HubConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from .chuguan.hub import ChuGuanDevice
from homeassistant.components.switch import SwitchEntity, SwitchDeviceClass
import logging
from .entity import ChuGuanEntity, ChuGuanModeEntity, ChuGuanFunctionEntity
from .chuguan.model import ModeValue

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: HubConfigEntry, async_add_entities: AddEntitiesCallback):
    """Set up the Chuguan Home switch platform."""
    hub = entry.runtime_data
    new_devices : list[ChuGuanSwitch]= []
    for device in hub.devices:
        if device.device_type == 'switch' or device.device_type == 'outlet':
            new_devices.append(ChuGuanSwitch(device))
        if device.device_type == 'HANGER' and device.has_state:
            new_devices.append(ChuGuanModeSwitch(device, ModeValue.AirerXiaoDu, 'disinfection', "消毒"))
            new_devices.append(ChuGuanModeSwitch(device, ModeValue.AirerFengGan, 'DryingSwitch', "吹风"))
            new_devices.append(ChuGuanModeSwitch(device, ModeValue.AirerHongGan, 'AirDryingSwitch', "烘干"))
        if device.device_type == 'YUBA':
            new_devices.append(ChuGuanFunctionSwitch(device, 'heating1', 'powerfulLightingOne', "取暖一"))
            new_devices.append(ChuGuanFunctionSwitch(device, 'heating2', 'powerfulLightingTwo', "取暖二"))
            new_devices.append(ChuGuanFunctionSwitch(device, 'blowing', 'blow', "吹风"))
            new_devices.append(ChuGuanFunctionSwitch(device, 'airing', 'ventilationFunction', "换气"))
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



class ChuGuanModeSwitch(ChuGuanModeEntity, SwitchEntity):
    """Chuguan Mode Switch"""

    
class ChuGuanFunctionSwitch(ChuGuanFunctionEntity, SwitchEntity):
    """Chuguan Function Switch"""