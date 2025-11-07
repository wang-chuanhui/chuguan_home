from homeassistant.core import HomeAssistant
from . import HubConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.components.button import ButtonEntity
import logging
from .entity import ChuGuanEntity, ChuGuanModeEntity
from .chuguan.model import ModeValue

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: HubConfigEntry, async_add_entities: AddEntitiesCallback):
    """Set up the Chuguan Home button platform."""
    hub = entry.runtime_data
    new_devices : list[ChuGuanModeButton]= []
    for device in hub.devices:
        if device.device_type == 'HANGER' and device.has_state == False:
            new_devices.append(ChuGuanModeButton(device, ModeValue.AirerXiaoDu, 'disinfection', "消毒"))
            new_devices.append(ChuGuanModeButton(device, ModeValue.AirerFengGan, 'DryingSwitch', "吹风"))
            new_devices.append(ChuGuanModeButton(device, ModeValue.AirerHongGan, 'AirDryingSwitch', "烘干"))
            new_devices.append(ChuGuanModeButton(device, ModeValue.AirerLight, 'illumination', "照明"))
    async_add_entities(new_devices)
    ChuGuanEntity.register_entity_areas(hass, new_devices)



class ChuGuanModeButton(ChuGuanModeEntity, ButtonEntity):
    """Chuguan Mode Button"""