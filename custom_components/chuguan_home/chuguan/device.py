from .event_emitter import EventEmitter
from .home import HomeHub


class ChuGuanDevice(EventEmitter):
    """Chuguan Device"""

    state: dict = {}

    def __init__(self, device: dict, home: HomeHub):
        super().__init__()
        self.device = device
        self.home = home
        hardware_name = self.hardware_name
        if hardware_name.startswith('cg') or hardware_name.startswith('智能'):
            self.has_state = True
        else:
            self.has_state = False

    def stop(self):
        self.off()
        self.home = None

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
        self.state = state
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
        return await self.home.set_powerstate(self.device, value)
    
    async def set_brightness(self, value: int):
        return await self.home.set_brightness(self.device, value)
    
    async def set_color_temp(self, value: int):
        return await self.home.set_color_temp(self.device, value)
    
    async def set_rgb_color(self, red: int, green: int, blue: int):
        return await self.home.set_rgb_color(self.device, red, green, blue)
