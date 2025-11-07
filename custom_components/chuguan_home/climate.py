from .entity import ChuGuanEntity
from homeassistant.components.climate import ClimateEntity
from homeassistant.components.climate.const import FAN_AUTO, FAN_LOW, FAN_MEDIUM, FAN_HIGH, HVACMode, ClimateEntityFeature, SWING_VERTICAL
from .chuguan.device import ChuGuanDevice
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from . import HubConfigEntry
import logging
from homeassistant.const import UnitOfTemperature
from .chuguan.model import ModeValue

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: HubConfigEntry, async_add_entities: AddEntitiesCallback):
    """Set up the Chuguan Home button platform."""
    hub = entry.runtime_data
    new_devices : list[ChuGuanAirConditioner]= []
    _LOGGER.info("climate async_setup_entry with entry %s %s", entry, entry.data)
    for device in hub.devices:
        """Add"""
        if device.device_type == "aircondition":
            new_devices.append(ChuGuanAirConditioner(device))
    async_add_entities(new_devices)
    ChuGuanEntity.register_entity_areas(hass, new_devices)


class ChuGuanAirConditioner(ChuGuanEntity, ClimateEntity):
    """Chuguan Air Conditioner"""
    suffix: str = "air_conditioner"

    def __init__(self, device: ChuGuanDevice):
        super().__init__(device)
        self._attr_temperature_unit = UnitOfTemperature.CELSIUS
        self._attr_max_temp = 30
        self._attr_min_temp = 16
        self._attr_target_temperature_step = 1
        if self._device.is_ir:
            self._attr_fan_modes = [FAN_AUTO, FAN_LOW, FAN_MEDIUM, FAN_HIGH]
            self._attr_hvac_modes = [HVACMode.HEAT, HVACMode.COOL, HVACMode.AUTO, HVACMode.FAN_ONLY, HVACMode.DRY, HVACMode.OFF]
            self._attr_supported_features = ClimateEntityFeature.TURN_ON | ClimateEntityFeature.TURN_OFF | ClimateEntityFeature.TARGET_TEMPERATURE | ClimateEntityFeature.FAN_MODE
            self._attr_swing_modes = []
        else:
            self._attr_fan_modes = [FAN_LOW, FAN_MEDIUM, FAN_HIGH]
            self._attr_hvac_modes = [HVACMode.HEAT, HVACMode.COOL, HVACMode.FAN_ONLY, HVACMode.DRY, HVACMode.OFF]
            self._attr_supported_features = ClimateEntityFeature.TURN_ON | ClimateEntityFeature.TURN_OFF | ClimateEntityFeature.TARGET_TEMPERATURE | ClimateEntityFeature.FAN_MODE
            self._attr_swing_modes = []

    @property
    def hvac_mode(self) -> HVACMode:
        """Return the current hvac mode."""
        powerstate = self._device.powerstate
        if powerstate == False:
            return HVACMode.OFF
        mode: int = self._device.state.get('mode', None)
        if mode == 2:
            return HVACMode.COOL
        if mode == 5:
            return HVACMode.HEAT
        if mode == 1:
            return HVACMode.AUTO
        if mode == 3:
            return HVACMode.DRY
        if mode == 4:
            return HVACMode.FAN_ONLY
        return HVACMode.OFF
    
    @property
    def target_temperature(self) -> float:
        """Return the current temperature."""
        return self._device.state.get('temperature', None)

    @property
    def fan_mode(self) -> str | None:
        """Return the current fan mode."""
        windspeed = self._device.state.get('windspeed', None)
        if windspeed == 2:
            return FAN_LOW
        if windspeed == 3:
            return FAN_MEDIUM
        if windspeed == 4:
            return FAN_HIGH
        if windspeed == 1:
            return FAN_AUTO
        return None
    
    @property
    def swing_mode(self) -> str:
        """Return the current swing mode."""
        return SWING_VERTICAL
    
    async def async_set_hvac_mode(self, hvac_mode: HVACMode):
        """Set new target hvac mode."""
        if hvac_mode == HVACMode.OFF:
            await self._device.set_powerstate(False)
        if hvac_mode == HVACMode.COOL:
            await self._device.set_mode(ModeValue.AirCool)
        elif hvac_mode == HVACMode.HEAT:
            await self._device.set_mode(ModeValue.AirHeat)
        elif hvac_mode == HVACMode.AUTO:
            await self._device.set_mode(ModeValue.AirAuto)
        elif hvac_mode == HVACMode.FAN_ONLY:
            await self._device.set_mode(ModeValue.AirFan)
        elif hvac_mode == HVACMode.DRY:
            await self._device.set_mode(ModeValue.AirChuShi)

    async def async_turn_on(self):
        """Turn the entity on."""
        await self._device.set_powerstate(True)

    async def async_turn_off(self):
        """Turn the entity off."""
        await self._device.set_powerstate(False)

    async def async_toggle(self):
        """Toggle the entity."""
        powerstate = self._device.powerstate
        if powerstate:
            await self._device.set_powerstate(False)
        else:
            await self._device.set_powerstate(True)

    async def async_set_fan_mode(self, fan_mode):
        """Set new target fan mode."""
        if fan_mode == FAN_AUTO:
            await self._device.set_fan_speed('auto')
        elif fan_mode == FAN_LOW:
            await self._device.set_fan_speed('low')
        elif fan_mode == FAN_MEDIUM:
            await self._device.set_fan_speed('middle')
        elif fan_mode == FAN_HIGH:
            await self._device.set_fan_speed('high')

    async def async_set_temperature(self, **kwargs):
        """Set new target temperature."""
        _LOGGER.info("async_set_temperature %s", kwargs)
        temp = kwargs.get('temperature', None)
        if temp is not None:
            await self._device.set_temperature(temp)
