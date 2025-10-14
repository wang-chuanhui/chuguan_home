from .user import UserHub
from .const import USER_URL
import logging

_LOGGER = logging.getLogger(__name__)


class HomeHub(UserHub):
    """HomeHub"""
    def __init__(self, brand: str, uuid: str, account: str, user_id: str, home_id: str):
        super().__init__(brand, uuid, account, user_id)
        self.home_id = home_id

    def update_payload(self, payload: dict):
        super().update_payload(payload)
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

