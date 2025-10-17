from .home import HomeHub
import logging
import paho.mqtt.client as mqtt
from ..const import DOMAIN
from .const import MQTT_BROKER, MQTT_PORT, PROVINCE
from .transport import Transport
from .set_interval import SetInterval
from .event_emitter import EventEmitter
from .utils import sync_non_blocking
from homeassistant.helpers.area_registry import async_get as async_get_area_registry, AreaRegistry
from homeassistant.core import HomeAssistant
from .brand import Brand
from .user import UserHub


_LOGGER = logging.getLogger(__name__)

async def authenticate(brand: str, uuid: str, account: str, password: str):
    """Authenticate"""
    hub = Brand(brand, uuid)
    return await hub.authenticate(account, password)

async def get_homes(brand: str, uuid: str, account: str, user_id: str):
    """Get homes"""
    hub = UserHub(brand, uuid, account, user_id)
    return await hub.get_homes()

class Hub:
    """Hub"""
    def __init__(self, hass: HomeAssistant, brand: str, uuid: str, account: str, user_id: str, home_id: str = None):
        self.hass = hass
        self._home_hub = HomeHub(brand, uuid, account, user_id, home_id)
        self.devices: list[ChuGuanDevice] = []
        self._states: dict[str, dict] = {}
        self._transport = Transport(account, f'{user_id}_{PROVINCE}', MQTT_BROKER, MQTT_PORT)
        self._interval = SetInterval(40, callback=lambda: self.loop_choose_home())
        self._interval.start()
        self._transport.on('message', self.on_message)
        self._transport.on('subscribed', self.on_subscribed)

    def __del__(self):
        """Stop hub"""
        _LOGGER.info("Stop hub %s %s", self._home_hub.brand, self._home_hub.uuid)

    async def async_get_devices(self):
        """Get devices"""
        devices = await self._home_hub.get_devices()
        self.devices = [ChuGuanDevice(device, self) for device in devices]
        return devices


    def loop_choose_home(self):
        """Loop choose home"""
        self._home_hub.choose_home_sync_non_blocking()

    def on_subscribed(self):
        """On subscribed"""
        coro = self._home_hub.refresh_home_devices_state()
        sync_non_blocking(coro)

    def on_message(self, id: str, params: dict):
        """On message"""
        _LOGGER.info(f"id: {id}, params: {params}")
        state = self._states.get(id, {})
        state.update(params)
        self._states[id] = state
        
        for device in self.devices:
            if device.device_id == id:
                device.update_state(state)
                break

    def stop(self):
        """Stop hub"""
        self._transport.off()
        self._interval.stop()
        self._transport.stop()
        for device in self.devices:
            device.stop()


class ChuGuanDevice(EventEmitter):
    """Chuguan Device"""
    def __init__(self, device: dict, hub: Hub):
        super().__init__()
        self.device = device
        self.hub = hub
        self._id = self.device_id
        self.name = self.device_name
        _LOGGER.info('Add device %s %s %s %s', self.device_type, self.device_id, self.zone, self.device_name)
        hardware_name = self.hardware_name
        if hardware_name.startswith('cg') or hardware_name.startswith('智能'):
            self.has_state = True
        else:
            self.has_state = False

    def __del__(self):
        """Stop device"""
        _LOGGER.info("Stop device %s %s", self.device_id, self.device_name)

    def stop(self):
        self.off()
        self.hub = None

    def setup_entity(self, entity):
        """Setup entity"""
        if self.has_state == False:
            entity._attr_assumed_state = True
            entity._attr_should_poll = False

    @property
    def device_info(self) -> dict:
        """Information about this entity/device."""
        res: dict = {
            "identifiers": {(DOMAIN, self.device_id)},
            # If desired, the name for the device could be different to the entity
            "name": self.device_name,
            "model": self.hub._home_hub.brand,
            "manufacturer": self.hub._home_hub.brand,
        }
        if self.zone is not None:
            res.update({
                "suggested_area": self.zone,
            })
        return res

    @property
    def state(self):
        """State"""
        return self.hub._states.get(self.device_id, {})
    
    @property
    def powerstate(self) -> bool:
        res: int = self.state.get('powerstate', 0)
        return res == 1

    @property
    def brightness(self) -> int:
        res: int = self.state.get('brightness', 0)
        return res
    
    @property
    def colorTemperature(self) -> int:
        res: int = self.state.get('colorTemperature', 0)
        return res
    
    @property
    def rgb(self) -> tuple[int, int, int]:
        res: dict = self.state.get('rgb', {'Red': 255, 'Green': 255, 'Blue': 255})
        return tuple(res.values())

    def update_state(self, state: dict):
        """Update state"""
        self.emit('state_update', state)

    @property
    def device_type(self):
        """Device type"""
        return self.device.get('deviceType', '')
    
    @property
    def device_id(self):
        """Device id"""
        return self.device.get('deviceId', '')
    
    @property
    def device_name(self):
        """Device name"""
        return self.device.get('deviceName', '')
    
    @property
    def zone(self) -> str | None:
        """Zone"""
        return self.device.get('zone', None)
    
    @property
    def hardware_name(self) -> str:
        """Hardware name"""
        return self.device.get('extensions', {}).get('hardwareName', '')
    
    async def set_powerstate(self, value: bool):
        """Set power state"""
        return await self.hub._home_hub.set_powerstate(self.device, value)
    
    async def set_brightness(self, value: int):
        return await self.hub._home_hub.set_brightness(self.device, value)
    
    async def set_color_temp(self, value: int):
        return await self.hub._home_hub.set_color_temp(self.device, value)
    
    async def set_rgb_color(self, red: int, green: int, blue: int):
        return await self.hub._home_hub.set_rgb_color(self.device, red, green, blue)
