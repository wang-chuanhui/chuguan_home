from .home import HomeHub
import logging

_LOGGER = logging.getLogger(__name__)



class Hub:
    """Hub"""
    def __init__(self, brand: str, uuid: str, account: str, user_id: str, home_id: str = None):
        self._home_hub = HomeHub(brand, uuid, account, user_id, home_id)
        self.devices: list[ChuGuanDevice] = []


    async def async_get_devices(self):
        """Get devices"""
        devices = await self._home_hub.get_devices()
        self.devices = [ChuGuanDevice(device, self) for device in devices]
        self.rollers = self.devices
        self.lights = self.devices
        return devices


class ChuGuanDevice:
    """Chuguan Device"""
    def __init__(self, device: dict, hub: Hub):
        self.device = device
        self.hub = hub

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
