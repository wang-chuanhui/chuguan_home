from .chuguan.device import ChuGuanDevice
from homeassistant.helpers.entity import Entity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import async_get as async_get_device_registry
from homeassistant.helpers.entity_registry import async_get as async_get_entity_registry
from homeassistant.helpers.area_registry import async_get as async_get_area_registry
import logging
import time
from .chuguan.model import Mode

_LOGGER = logging.getLogger(__name__)

class ChuGuanEntity(Entity):

    suffix: str = "entity"
    last_update_time: float = time.time()
    def __init__(self, device: ChuGuanDevice):
        self._device = device
        self._attr_unique_id = self._device.device_id + "_" + self.suffix
        self._attr_name = self._device.device_name
        if self._device.has_state == False:
            self._attr_assumed_state = True
            self._attr_should_poll = False
        self._device.on("state_update", self._on_state_changed)

    def _on_state_changed(self, state: dict):
        """On state update"""
        self.last_update_time = time.time()
        self.publish_update()

    def publish_update(self):
        self.hass.loop.call_soon_threadsafe(self.async_write_ha_state)

    def second_of_last_update(self) -> float:
        return time.time() - self.last_update_time

    @classmethod
    def register_entity_areas(cls, hass: HomeAssistant, entities: list["ChuGuanEntity"]):
        """Register entity areas"""
        entity_registry = async_get_entity_registry(hass)
        area_registry = async_get_area_registry(hass)
        device_registry = async_get_device_registry(hass)
        for entity in entities:
            device = entity.device_info
            if device and device.get("identifiers", None):
                get_device = device_registry.async_get_device(device.get("identifiers"))
                if get_device and get_device.area_id is None:
                    device_registry.async_update_device(get_device.id, area_id=area.id)
                    _LOGGER.info(f"Add device {get_device.id} to area {area.id} {area.name}")
            get_entity = entity_registry.async_get(entity.entity_id)
            if get_entity and get_entity.area_id is None:
                area = area_registry.async_get_or_create(name=entity._device.zone)
                entity_registry.async_update_entity(entity.entity_id, area_id=area.id)
                _LOGGER.info(f"Add entity {entity.entity_id} to area {area.id} {area.name}")


class ChuGuanModeEntity(ChuGuanEntity):
    """Chuguan Mode Entity"""

    suffix: str = "mode"
    mode: Mode
    key: str

    def __init__(self, device: ChuGuanDevice, mode: Mode, key: str, name: str):
        self.suffix = key
        super().__init__(device)
        self._attr_name = self._attr_name + name
        self.mode = mode
        self.key = key
        self._attr_device_info = self._device.device_info

    @property
    def is_on(self) -> bool:
        return self._device.state.get(self.key, 0) > 0
    
    async def async_turn_on(self, **kwargs):
        """Turn the switch on."""
        _LOGGER.info("async_turn_on %s", kwargs)
        await self._device.set_mode(self.mode)


    async def async_turn_off(self):
        """Turn the switch off."""
        await self._device.unset_mode(self.mode)

    async def async_press(self) -> None:
        """Handle the button press."""
        await self._device.set_mode(self.mode)


class ChuGuanFunctionEntity(ChuGuanEntity):
    """Chuguan Function Entity"""

    suffix: str = "function"
    function: str
    key: str

    def __init__(self, device: ChuGuanDevice, function: str, key: str, name: str):
        self.suffix = key
        super().__init__(device)
        self._attr_name = self._attr_name + name
        self.function = function
        self.key = key
        self._attr_device_info = self._device.device_info

    @property
    def is_on(self) -> bool:
        return self._device.state.get(self.key, 0) > 0
    
    async def async_turn_on(self, **kwargs):
        """Turn the switch on."""
        _LOGGER.info("async_turn_on %s", kwargs)
        await self._device.set_function_powerstate(self.function, True)


    async def async_turn_off(self):
        """Turn the switch off."""
        await self._device.set_function_powerstate(self.function, False)

