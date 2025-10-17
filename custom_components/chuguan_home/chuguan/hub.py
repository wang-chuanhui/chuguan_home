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
from .device import ChuGuanDevice


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
        _LOGGER.info("Get devices %s", devices)
        self.devices = [ChuGuanDevice(device, self._home_hub) for device in devices]
        return devices


    def loop_choose_home(self):
        """Loop choose home"""
        corn = self._home_hub.choose_home()
        sync_non_blocking(corn)

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

