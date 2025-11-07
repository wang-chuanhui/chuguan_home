from .event_emitter import EventEmitter
from .home import HomeHub
from .model import Mode
from .const import DOMAIN

class ChuGuanDevice(EventEmitter):
    """Chuguan Device"""

    state: dict

    def __init__(self, device: dict, home: HomeHub, state: dict = {}):
        super().__init__()
        self.state = state
        self.device = device
        self.home = home
        hardware_name = self.hardware_name
        if hardware_name.startswith('cg') or hardware_name.startswith('智能') or hardware_name == 'yuba' or hardware_name == 'rgb_light':
            self.has_state = True
        else:
            self.has_state = False
        if hardware_name.startswith('二代'):
            self.is_lora = True
        else:
            self.is_lora = False
        if hardware_name == '49152':
            self.is_ir = True
        else:
            self.is_ir = False

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
            "model": self.home.brand,
            "manufacturer": self.home.brand,
        }
        if self.zone is not None:
            res.update({
                "suggested_area": self.zone,
            })
        return res

    @property
    def int_powerstate(self) -> bool:
        res: int = self.state.get('powerstate', None)
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
    @property
    def position(self) -> int | None:
        res: int = self.state.get('position', None)
        return res
    

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
    
    @property
    def hardware_type(self) -> str:
        """Hardware type"""
        return self.device.get('extensions', {}).get('type', '')
    
    async def set_powerstate(self, value: bool):
        """Set power state"""
        if (self.is_lora):
            self.state['powerstate'] = 1 if value else 0
            self.update_state(self.state)
        return await self.home.set_powerstate(self.device, value)
    
    async def set_function_powerstate(self, function: str, value: bool):
        """Set function power state"""
        return await self.home.set_function_powerstate(self.device, function, value)
    
    async def set_brightness(self, value: int):
        return await self.home.set_brightness(self.device, value)
    
    async def set_color_temp(self, value: int):
        return await self.home.set_color_temp(self.device, value)
    
    async def set_rgb_color(self, red: int, green: int, blue: int):
        return await self.home.set_rgb_color(self.device, red, green, blue)

    async def set_position(self, value: int):
        return await self.home.set_position(self.device, value)
    
    async def set_pause(self):
        return await self.home.set_pause(self.device)
    
    async def set_mode(self, mode: Mode):
        return await self.home.set_mode(self.device, mode)
    
    async def unset_mode(self, mode: Mode):
        return await self.home.unset_mode(self.device, mode)
    
    async def set_fan_speed(self, speed: str):
        return await self.home.set_fan_speed(self.device, speed)
    
    async def set_temperature(self, temp: float):
        return await self.home.set_temperature(self.device, temp)
