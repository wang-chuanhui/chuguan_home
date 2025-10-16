from .user import UserHub
from .const import USER_URL, THIRD_URL
import logging
import asyncio
import threading
import uuid
import aiohttp
import json

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
        result = await self.post_data(USER_URL, data)
        return result

    async def choose_home(self):
        """Choose home"""
        data = {'action': '307', 'actionType': 'ChangeSelectionHome', 'homeId': self.home_id}
        result = await self.post_data(USER_URL, data)
        _LOGGER.info(f"Choose home {self.home_id} result: {result}")
        return result

    def choose_home_sync_non_blocking(self):
        """同步方法：非阻塞调用choose_home异步方法"""
        # 封装异步方法为协程对象（绑定当前实例）
        coro = self.choose_home()

        def _run_async():
            """在子线程中运行事件循环的函数"""
            # 为子线程创建独立事件循环
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                # 运行异步方法（不关心返回结果，只在后台执行）
                loop.run_until_complete(coro)
            except Exception as e:
                _LOGGER.error(f"异步调用choose_home失败: {e}")
            finally:
                loop.close()

        # 创建并启动子线程，设置为守护线程（随主线程退出）
        thread = threading.Thread(target=_run_async, daemon=True)
        thread.start()
        # 不调用thread.join()，直接返回，实现非阻塞

    async def refresh_home_devices_state(self):
        """Refresh home devices state"""
        data = {'action': '307', 'actionType': 'PleaseRefreshHomeDevice', 'homeId': self.home_id}
        result = await self.post_data(USER_URL, data)
        _LOGGER.info(f"Refresh home devices state result: {result}")
        return result

    async def submit_json(self, session: aiohttp.ClientSession, url: str, payload: dict):
        try:
            self.update_payload(payload)
            # 发送 POST 请求（自动设置 Content-Type: application/json）
            async with session.post(
                url,
                json=payload,
                timeout=30
            ) as response:
                status = response.status
                if status != 200:
                    raise Exception(f"请求失败")
                text = await response.text()
                result: dict = json.loads(text)
                return result
        except aiohttp.ClientError as e:
            _LOGGER.error("POST 错误: %s", e)
            raise e;

    async def post_json(self, url: str, payload: dict):
        """POST data to the brand."""
        async with aiohttp.ClientSession() as session:
            return await self.submit_json(session, url, payload);

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

