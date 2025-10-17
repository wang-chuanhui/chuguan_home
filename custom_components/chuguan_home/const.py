"""Constants for the chuguan_home integration."""
from typing import Final

DOMAIN = "chuguan_home"
CONF_BRAND: Final = "brand"
BRAND_TYPES = [
    {"value": "cg", "label": "cg"},
    {"value": "xzh", "label": "xzh"}
]
CONF_UUID: Final = "uuid"
CONF_USER_ID: Final = "user_id"
CONF_NICK_NAME: Final = "nick_name"
CONF_HOME_ID: Final = "home_id"
CONF_HOME_NAME: Final = "home_name"

