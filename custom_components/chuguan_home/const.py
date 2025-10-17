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
BASE_URL: Final = "https://www.chuguansmart.com"
USER_URL: Final = f"{BASE_URL}/api/NewUserHandler.ashx"
DEVICE_URL: Final = f"{BASE_URL}/Api/NewDeviceHandler.ashx"
THIRD_URL: Final = f"{BASE_URL}/Api/ThirdPartyHandler.ashx"
PROVINCE: Final = "wx"
VERSION: Final = "1.0.0"
MQTT_BROKER = "chuguansmart.com"
MQTT_PORT = 8084
