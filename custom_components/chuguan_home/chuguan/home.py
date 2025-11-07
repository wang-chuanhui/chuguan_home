from .user import UserHub
from .const import USER_URL, THIRD_URL, DEVICE_URL
import logging
import uuid
from .utils import post_json
from .model import Mode

_LOGGER = logging.getLogger(__name__)


class HomeHub(UserHub):
    """HomeHub"""
    def __init__(self, brand: str, uuid: str, account: str, user_id: str, home_id: str):
        super().__init__(brand, uuid, account, user_id)
        self.home_id = home_id


    def update_payload(self, payload: dict):
        super().update_payload(payload)
        home_id = payload.get('homeId', None)
        if home_id is not None:
            return
        Home_Id = payload.get('HomeId', None)
        if Home_Id is not None:
            return
        if self.home_id is not None:
            payload.update({
                'HomeId': self.home_id
            })

    async def get_devices(self):
        """Get devices"""
        data = {
            'action': '307', 
            'actionType': 'GetWeCheatHomeSupportDevice'
        }
        result: list = await self.post_data(USER_URL, data)
        tcp_devices = await self.get_tcp_devices()
        yuba_devices = self.get_yuba_devices(tcp_devices)
        _LOGGER.info(f"Get YUBA devices result: {yuba_devices}")
        result.extend(yuba_devices)
        return result
    
    def get_yuba_devices(self, devices: any):
        """Get yuba devices"""
        yuba_devices = []
        for device in devices:
            if device.get('hardwareName') == 'yuba':
                id = device.get('hardwareId', None)
                name = device.get('hardwareNickname', None)
                brand = device.get('hardwareBrand', None)
                room = device.get('hardwareRoom', None)
                type = device.get('hardwareType', None)
                rf = device.get('hardwareRFAddress', None)
                device = {'deviceId': id, 'deviceType': 'YUBA', 'deviceName': name, 'brand': brand, 'zone': room, 'icon': '', 'properties': [], 'actions': [], 'extensions': {'isHost': True, 'type': type, 'hardwareRFAddress': rf, 'hardwareBindHostAddress': None, 'hardwareBindHostId': None, 'parentId': None, 'hardwareName': 'yuba'}}
                yuba_devices.append(device)
        return yuba_devices
    
    async def get_tcp_devices(self):
        """Get tcp devices"""
        data = {
            'action': '120'
        }
        result = await self.post_data(USER_URL, data)
        return result
    
    async def get_mq_devices(self):
        """Get mq devices"""
        data = {
            'action': '800', 
            'actionType': "GetDeviceByHomeId"
        }
        result = await self.post_data(DEVICE_URL, data)
        return result

    async def choose_home(self):
        """Choose home"""
        data = {'action': '307', 'actionType': 'ChangeSelectionHome', 'homeId': self.home_id}
        result = await self.post_data(USER_URL, data)
        _LOGGER.info(f"Choose home {self.home_id} result: {result}")
        return result

    async def refresh_home_devices_state(self):
        """Refresh home devices state"""
        data = {'action': '307', 'actionType': 'PleaseRefreshHomeDevice', 'homeId': self.home_id}
        result = await self.post_data(USER_URL, data)
        _LOGGER.info(f"Refresh home devices state result: {result}")
        return result

    async def post_json(self, url: str, payload: dict):
        """POST data to the brand."""
        self.update_payload(payload)
        return await post_json(url, payload)

    async def control(self, device : dict, name : str, payload : dict = {}):
        account = self.account
        data = { "payload": { "accessToken": f'wx/{account}', "appliance": { "applianceId": device.get('deviceId'), "additionalApplianceDetails": device.get('extensions') } }, "header": { "messageId": str(uuid.uuid4()), "namespace": "ThirdParty.ConnectedHome.Control", "name": name, "payloadVersion": "1" } }
        data['payload'].update(payload)
        _LOGGER.info(f"Control device {device.get('deviceId')} with name {name} and data {data}")
        result = await self.post_json(THIRD_URL, data)
        _LOGGER.info(f"result: {result}")
        return result

    async def set_powerstate(self, device: dict, value: bool):
        if value:
            name = 'TurnOnRequest'
        else:
            name = 'TurnOffRequest'
        result = await self.control(device, name, {})
        return result
    
    async def set_function_powerstate(self, device: dict, function: str, value: bool):
        if value:
            name = 'TurnOnRequest'
        else:
            name = 'TurnOffRequest'
        result = await self.control(device, name, {'function': function})
        return result

    async def set_brightness(self, device: dict, brightness: int):
        payload = { "brightness": { "value": brightness } }
        result = await self.control(device, 'SetBrightnessPercentageRequest', payload)
        return result
    
    async def set_color_temp(self, device: dict, value: int):
        result = await self.control(device, 'SetColorTemperatureRequest', { "yellowLight": value })
        return result
    
    async def set_rgb_color(self, device: dict, red: int, green: int, blue: int):
        payload = { 'color': { "red": red, "green": green, "blue": blue } }
        result = await self.control(device, 'SetColorRequest', payload)
        return result
    
    async def set_position(self, device: dict, position: int):
        payload = { "deltaValue": { "value": f"{position}", "unit": "%" } }
        result = await self.control(device, 'TurnOnRequest', payload)
        return result

    async def set_pause(self, device: dict):
        result = await self.control(device, "PauseRequest", {})
        return result
    
    async def set_mode(self, device: dict, mode: Mode):
        """Set mode"""
        result = await self.control(device, "SetModeRequest", { 'mode': mode})
        return result
    
    async def unset_mode(self, device: dict, mode: Mode):
        """Unset mode"""
        result = await self.control(device, "UnsetModeRequest", { 'mode': mode})
        return result

