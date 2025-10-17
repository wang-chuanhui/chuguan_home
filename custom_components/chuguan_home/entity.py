from .chuguan.device import ChuGuanDevice
from homeassistant.helpers.entity import Entity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_registry import async_get as async_get_entity_registry
from homeassistant.helpers.area_registry import async_get as async_get_area_registry
import logging

_LOGGER = logging.getLogger(__name__)

class ChuGuanEntity(Entity):

    suffix: str = "entity"
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
        self.hass.loop.call_soon_threadsafe(self.async_write_ha_state)

    @classmethod
    def register_entity_areas(cls, hass: HomeAssistant, entities: list["ChuGuanEntity"]):
        """Register entity areas"""
        entity_registry = async_get_entity_registry(hass)
        area_registry = async_get_area_registry(hass)
        for entity in entities:
            area = area_registry.async_get_or_create(name=entity._device.zone)
            entity_registry.async_update_entity(entity.entity_id, area_id=area.id)
            _LOGGER.info(f"Add entity {entity.entity_id} to area {area.id} {area.name}")