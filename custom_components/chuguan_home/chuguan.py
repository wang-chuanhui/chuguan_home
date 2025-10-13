import logging
from .const import USER_URL
from .error import InvalidAuth
import aiohttp


_LOGGER = logging.getLogger(__name__)


class ChuGuanHub:

    def __init__(self, brand: str, uuid: str) -> None:
        """Initialize."""
        self.brand = brand
        self.uuid = uuid
        _LOGGER.info("ChuGuanHub init with brand %s, uuid %s", brand, uuid)


    async def submit_data(self, session: aiohttp.ClientSession, url: str, payload: dict):
        try:
            payload.update({
                'register': self.brand,
            })
            # 发送 POST 请求（自动设置 Content-Type: application/json）
            async with session.post(
                url,
                json=payload,
                timeout=10
            ) as response:
                result: dict = await response.json()
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

    async def authenticate(self, username: str, password: str) -> bool:
        """Test if we can authenticate with the brand."""
        _LOGGER.info("ChuGuanHub authenticate with brand %s, username %s, password %s", self.brand, username, password)
        data = {
            'action': '307',
            'actionType': 'WeChatLogin',
            'account': username,
            'password': password
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(USER_URL, data=data) as resp:
                if resp.status != 200:
                    _LOGGER.error("ChuGuanHub authenticate failed with brand %s, username %s, password %s, status %s", self.brand, username, password, resp.status)
                    return False
                _LOGGER.info("ChuGuanHub authenticate success with brand %s, username %s, password %s", self.brand, username, password)
                return True
