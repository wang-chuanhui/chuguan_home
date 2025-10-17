import logging
from .const import USER_URL, PROVINCE
from .error import InvalidAuth
from .model import toUserInfoList, UserInfo
from .utils import post_data


_LOGGER = logging.getLogger(__name__)


class Brand:

    brand: str
    uuid: str

    def __init__(self, brand: str, uuid: str) -> None:
        """Initialize."""
        self.brand = brand
        self.uuid = uuid

    def update_payload(self, payload: dict):
        payload.update({
            'register': self.brand,
            'wxUnionid': self.uuid,
            'province': PROVINCE + '1.0.0'
        })

    async def post_data(self, url: str, payload: dict):
        """POST data to the brand."""
        self.update_payload(payload)
        return await post_data(url, payload)

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
    
