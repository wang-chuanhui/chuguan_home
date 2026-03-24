from .user import UserHub
from .const import USER_URL, THIRD_URL, DEVICE_URL, YS_URL
import logging
import uuid
from .utils import post_json
from .model import Mode, HardwareInfo
from .error import CGHAError

_LOGGER = logging.getLogger(__name__)


class HomeHub(UserHub):
    """HomeHub"""
    def __init__(self, brand: str, uuid: str, province: str, account: str, user_id: str, home_id: str):
        super().__init__(brand, uuid, province, account, user_id)
        self.home_id = home_id
        self.devices = []
        self.tcp_devices = []
        self.mq_devices = []

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
            'action': '307_us', 
            'actionType': 'UserSignHomeSupportDevice'
        }
        result: list = await self.post_data(USER_URL, data)
        tcp_devices = await self.get_tcp_devices()
        yuba_devices = self.get_yuba_devices(tcp_devices)
        valve_devices = self.get_valve_devices(tcp_devices)
        try:
            cameras = await self.get_cameras()
        except Exception as e:
            cameras = []
        # _LOGGER.info(f"Get YUBA devices result: {yuba_devices}")
        result.extend(yuba_devices)
        result.extend(valve_devices)
        result.extend(cameras)
        self.devices = result
        self.tcp_devices = tcp_devices
        self.mq_devices = await self.get_mq_devices()
        self.cameras = cameras
        # _LOGGER.info(f"Get devices result: {result}")
        # _LOGGER.info(f"Get tcp devices result: {tcp_devices}")
        # _LOGGER.info(f"Get mq devices result: {self.mq_devices}")
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
    
    def get_valve_devices(self, devices: any):
        """Get valve devices"""
        valve_devices = []
        # _LOGGER.info(f"Get devices {devices}")
        for device in devices:
            if device.get('hardwareName') == 'manip_ctler':
                id = device.get('hardwareId', None)
                name = device.get('hardwareNickname', None)
                brand = device.get('hardwareBrand', None)
                room = device.get('hardwareRoom', None)
                type = device.get('hardwareType', None)
                rf = device.get('hardwareRFAddress', None)
                bind_host_id = device.get('hardwareBindHostId', None)
                bind_host_address = device.get('hardwareBindHostAddress', None)
                device = {'deviceId': id, 'deviceType': 'manip_ctler', 'deviceName': name, 'brand': brand, 'zone': room, 'icon': '', 'properties': [], 'actions': [], 'extensions': {'isHost': False, 'type': type, 'hardwareRFAddress': rf, 'hardwareBindHostAddress': bind_host_address, 'hardwareBindHostId': bind_host_id, 'parentId': bind_host_id, 'hardwareName': 'manip_ctler'}}
                valve_devices.append(device)
        return valve_devices
    
    async def get_tcp_devices(self):
        """Get tcp devices"""
        data = {
            'action': '120'
        }
        result = await self.post_data(USER_URL, data)
        return result
    
    async def get_cameras(self):
        """Get cameras"""
        data = {
            'action': '141_NewHomeApp'
        }
        result = await self.post_data(YS_URL, data)
        self.origin_cameras = result
        devices = []
        for device in result:
            id = device.get('DeviceSerial', None)
            name = device.get('DevName', None)
            room = device.get('HomeName', None)
            if self.brand == 'cg':
                brand = '初冠'
            else:
                brand = '小智慧'
            if id is not None:
                devices.append({
                    'deviceId': id,
                    'deviceType': 'camera',
                    'deviceName': name,
                    'brand': brand,
                    'zone': room,
                    'icon': '',
                    'properties': [],
                    'actions': [],
                    'extensions': {'isHost': True, 'type': 'camera'}, 
                    'ValidateCode': device.get('ValidateCode', None),
                    'ChannelNo': device.get('ChannelNo', None),
                    'PicUrl': device.get('PicUrl', None),
                    }
                )
        return devices
    
    async def get_mq_devices(self):
        """Get mq devices"""
        data = {
            'action': '800', 
            'actionType': "GetDeviceByHomeId"
        }
        result = await self.post_data(DEVICE_URL, data)
        return result
    
    def get_hardware_info(self, id: str) -> HardwareInfo | None:
        """Get hardware info"""
        for device in self.tcp_devices:
            if device.get('hardwareId') == id:
                nickname = device.get('hardwareNickname', None)
                room = device.get('hardwareRoom', None)
                brand = device.get('hardwareBrand', None)
                return HardwareInfo(id, nickname, room, brand)
        for device in self.mq_devices:
            if device.get('hardwareId') == id:
                nickname = device.get('hardwareNickname', None)
                room = device.get('hardwareRoom', None)
                brand = device.get('Brand', None)
                return HardwareInfo(id, nickname, room, brand)
        return None
    
    async def get_camera_live_address(self, id: str):
        """Get camera live address"""
        data = {
            'action': '252_la', 
            'DeviceSerial': id,
            "protocol": 3, #流播放协议，1-ezopen、2-hls、3-rtmp、4-flv，默认为1
            'expireTime': 10 * 24 * 60 * 60, #过期时长，单位秒；针对hls/rtmp/flv设置有效期，相对时间；30秒-720天
            'supportH265': 0, #请判断播放端是否要求播放视频为H265编码格式,1表示需要，0表示不要求
            'quality': 2,  #预览视频清晰度【仅针对预览生效，录像回放不支持切换清晰度】，1-高清（主码流）、2-流畅（子码流）
            'type': 1, #地址的类型，1-预览，2-本地录像回放，3-云存储录像回放，非必选，默认为1；回放仅支持rtmp、ezopen、flv协议
        }
        result: list = await self.post_data(YS_URL, data)
        if result is None or len(result) == 0:
            return None
        dic = result[0]
        code = dic.get('code', None)
        if code != '200':
            return None
        data = dic.get('data', None)
        if data is None:
            return None
        url = data.get('url', None)
        if url is None:
            return None
        return url
    
    async def start_ptz(self, id: str, channelNo: str, direction: str, speed: str):
        """Start ptz"""
        data = {
            'action': '252_bp',
            'DeviceSerial': id,
            'direction': direction,
            'speed': speed,
            'channelNo': channelNo,
        }
        result: list = await self.post_data(YS_URL, data)
        if isinstance(result, list):
            data = result[0]
            if isinstance(data, dict):
                code = data.get('code', None)
                if code != '200':
                    msg = data.get('msg', None)
                    if msg is None:
                        msg = 'Unknown error'
                    raise CGHAError.from_msg(msg)
        return result
    
    async def stop_ptz(self, id: str, channelNo: str, direction: str):
        """Stop ptz"""
        data = {
            'action': '252_ep',
            'DeviceSerial': id,
            'direction': direction,
            'channelNo': channelNo,
        }
        result: list = await self.post_data(YS_URL, data)
        return result

    async def choose_home(self):
        """Choose home"""
        data = {'action': '307_us', 'actionType': 'UserSignChangeHome', 'homeId': self.home_id}
        result = await self.post_data(USER_URL, data)
        _LOGGER.info(f"Choose home {self.home_id} result: {result}")
        return result

    async def refresh_home_devices_state(self):
        """Refresh home devices state"""
        data = {'action': '307_us', 'actionType': 'UserSignRefreshHomeDevice', 'homeId': self.home_id}
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

    async def set_fan_speed(self, device : dict, speed : str):
        """'high' | 'middle' | 'low' | 'auto'"""
        result = await self.control(device, 'SetFanSpeedRequest', { "fanSpeed": { "level": speed } })
        return result
    

    async def set_temperature(self, device : dict, temp : float):
        return await self.control(device, 'SetTemperatureRequest', { "targetTemperature": { "value": temp, "scale": "CELSIUS" } })
