"""Constants for the chuguan_home integration."""
from typing import Final

DOMAIN = "chuguan_home"
CONF_BRAND: Final = "brand"
BRAND_TYPES = [
    {"value": "cg", "label": "cg"},
    {"value": "xzh", "label": "xzh"}
]
CONF_UUID: Final = "uuid"
BASE_URL: Final = "https://www.chuguansmart.com"
USER_URL: Final = f"{BASE_URL}/api/NewUserHandler.ashx"
PROVINCE: Final = "ha"
VERSION: Final = "1.0.0"