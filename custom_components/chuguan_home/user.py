from .chuguan import ChuGuanHub
from .model import HomeInfo, toHomeInfoList
from .const import USER_URL


class UserHub(ChuGuanHub):
    """User hub."""
    def __init__(self, brand: str, uuid: str, account: str, user_id: str) -> None:
        """Initialize."""
        super().__init__(brand, uuid)
        self.account = account
        self.user_id = user_id

    def update_payload(self, payload: dict):
        if self.account is not None:
            payload.update({
                'holder': self.account
            })
        if self.user_id is not None:
            payload.update({
                'wxUserId': self.user_id
            })
        super().update_payload(payload)
    
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
