from .home import HomeHub
import logging
import paho.mqtt.client as mqtt
from .const import MQTT_BROKER, MQTT_PORT, PROVINCE
from .transport import Transport
from .setinterval import SetInterval
from .eventemitter import EventEmitter
from .util import sync_non_blocking

_LOGGER = logging.getLogger(__name__)

def loop_choose_home():
    _LOGGER.info("Loop choose home")



class Hub:
    """Hub"""
    def __init__(self, brand: str, uuid: str, account: str, user_id: str, home_id: str = None):
        self._home_hub = HomeHub(brand, uuid, account, user_id, home_id)
        self.devices: list[ChuGuanDevice] = []
        self.rollers: list[ChuGuanDevice] = []
        self.lights: list[ChuGuanDevice] = []
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
        self.rollers = self.devices
        self.lights = self.devices
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

    def __del__(self):
        """Stop device"""
        _LOGGER.info("Stop device %s %s", self.device_id, self.device_name)

    def stop(self):
        self.off()
        self.hub = None

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
    
    async def set_powerstate(self, value: bool):
        """Set power state"""
        return await self.hub._home_hub.set_powerstate(self.device, value)
    
    async def set_brightness(self, value: int):
        return await self.hub._home_hub.set_brightness(self.device, value)
    
    async def set_color_temp(self, value: int):
        return await self.hub._home_hub.set_color_temp(self.device, value)
