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
from .error import InvalidAuth
import asyncio


_LOGGER = logging.getLogger(__name__)

async def authenticate(brand: str, uuid: str, province: str, account: str, password: str):
    """Authenticate"""
    hub = Brand(brand, uuid, province)
    return await hub.authenticate(account, password)

async def get_homes(brand: str, uuid: str, province: str, account: str, user_id: str):
    """Get homes"""
    hub = UserHub(brand, uuid, province, account, user_id)
    return await hub.get_homes()

class Hub:
    """Hub"""
    def __init__(self, hass: HomeAssistant, brand: str, uuid: str, province: str, account: str, user_id: str, home_id: str = None):
        self.hass = hass
        self._home_hub = HomeHub(brand, uuid, province, account, user_id, home_id)
        self.devices: list[ChuGuanDevice] = []
        self._states: dict[str, dict] = {}
        self._interval = SetInterval(60 * 9 + 40, callback=lambda: self.loop_choose_home())
        self._interval.start()
        self._transport: Transport = None
        self._entry_id: str = None
        self._is_stop = False


    def __del__(self):
        """Stop hub"""
        _LOGGER.info("Stop hub %s %s", self._home_hub.brand, self._home_hub.uuid)

    async def async_get_devices(self):
        """Get devices"""
        devices = await self._home_hub.get_devices()
        # _LOGGER.info("Get devices %s", devices)
        self.devices = [ChuGuanDevice(device, self._home_hub, self.get_state(device.get('deviceId'))) for device in devices]
        return devices

    def setup_transport(self):
        """Setup transport"""
        account = self._home_hub.account
        user_id = self._home_hub.user_id
        self._transport = Transport(account, f'{user_id}_{self._home_hub.province}', MQTT_BROKER, MQTT_PORT)
        self._transport.on('message', self.on_message)
        self._transport.on('subscribed', self.on_subscribed)

    async def choose_home(self):
        """Choose home"""
        if self._is_stop:
            return
        try:
            _LOGGER.info("Begin Choose home")
            await self._home_hub.choose_home()
        except InvalidAuth as e:
            _LOGGER.error("Choose home failed: %s", e)
            if self._entry_id is not None:
                self.hass.loop.call_soon_threadsafe(self.hass.config_entries.async_schedule_reload, self._entry_id)
            raise e
        except Exception as e:
            _LOGGER.error("Choose home failed: %s", e)
            await asyncio.sleep(10)
            self.hass.add_job(self.choose_home)
            raise e

    def loop_choose_home(self):
        """Loop choose home"""
        corn = self.choose_home()
        sync_non_blocking(corn)

    def on_subscribed(self):
        """On subscribed"""
        coro = self._home_hub.refresh_home_devices_state()
        sync_non_blocking(coro)

    def get_state(self, id: str) -> dict:
        """Get state"""
        if id is None:
            return {}
        state = self._states.get(id, None)
        if state is None:
            state = {}
            self._states[id] = state
        return state

    def on_message(self, id: str, params: dict):
        """On message"""
        _LOGGER.info(f"id: {id}, params: {params}")
        state = self.get_state(id)
        state.update(params)
        
        for device in self.devices:
            if device.device_id == id:
                device.update_state(state)
                break

    def stop(self):
        """Stop hub"""
        self._is_stop = True
        if self._transport is not None:
            self._transport.off()
            self._transport.stop()
        self._interval.stop()
        for device in self.devices:
            device.stop()

