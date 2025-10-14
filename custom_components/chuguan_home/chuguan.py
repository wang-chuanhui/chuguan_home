import logging
from .const import USER_URL, PROVINCE
from .error import InvalidAuth
import aiohttp
import json
from .model import toUserInfoList, UserInfo, HomeInfo, toHomeInfoList


_LOGGER = logging.getLogger(__name__)


class ChuGuanHub:

    brand: str
    uuid: str
    account: str | None = None
    user_id: str | None = None

    def __init__(self, brand: str, uuid: str) -> None:
        """Initialize."""
        self.brand = brand
        self.uuid = uuid

    @classmethod
    def create(cls, brand: str, uuid: str, account: str, user_id: str) -> 'ChuGuanHub':
        """Create a new instance of ChuGuanHub."""
        instance = cls(brand, uuid)
        instance.account = account
        instance.user_id = user_id
        return instance

    async def submit_data(self, session: aiohttp.ClientSession, url: str, payload: dict):
        try:
            payload.update({
                'register': self.brand,
                'wxUnionid': self.uuid,
                'province': PROVINCE + '1.0.0'
            })
            if self.account is not None:
                payload.update({
                    'holder': self.account
                })
            if self.user_id is not None:
                payload.update({
                    'wxUserId': self.user_id
                })
            # 发送 POST 请求（自动设置 Content-Type: application/json）
            async with session.post(
                url,
                data=payload,
                timeout=10
            ) as response:
                text = await response.text()
                result: dict = json.loads(text)
                result_code = result.get('resultCode', '10000')
                if result_code == '20000':
                    return result.get('resultData')
                if result_code == '10001':
                    raise InvalidAuth("登录失效")
                message = result.get('message', '没有数据')
                raise Exception(f"{result_code}, {message}")
        except aiohttp.ClientError as e:
            _LOGGER.error("POST 错误: %s", e)
            raise e;

    async def post_data(self, url: str, payload: dict):
        """POST data to the brand."""
        async with aiohttp.ClientSession() as session:
            return await self.submit_data(session, url, payload);

    async def authenticate(self, username: str, password: str) -> UserInfo:
        """Test if we can authenticate with the brand."""
        data = {
            'action': '307',
            'actionType': 'WeChatLogin',
            'account': username,
            'password': password
        }
        result = await self.post_data(USER_URL, data);
        if result is None:
            return False
        user_info_list = toUserInfoList(result)
        if len(user_info_list) == 0:
            return False
        self.account = user_info_list[0].account
        self.user_id = user_info_list[0].userid
        return user_info_list[0]
    
    async def get_homes(self) -> list[HomeInfo]:
        """Get the list of homes."""
        data = {
            'action': '121',
            'actionType': 'getAllHomeByUser'
        }
        result = await self.post_data(USER_URL, data);
        if result is None:
            return []
        home_info_list = toHomeInfoList(result)
        return home_info_list
