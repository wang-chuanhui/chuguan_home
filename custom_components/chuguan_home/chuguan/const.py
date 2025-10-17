"""Constants for the chuguan_home integration."""
from typing import Final

BASE_URL: Final = "https://www.chuguansmart.com"
USER_URL: Final = f"{BASE_URL}/api/NewUserHandler.ashx"
DEVICE_URL: Final = f"{BASE_URL}/Api/NewDeviceHandler.ashx"
THIRD_URL: Final = f"{BASE_URL}/Api/ThirdPartyHandler.ashx"
PROVINCE: Final = "wx"
VERSION: Final = "1.0.0"
MQTT_BROKER = "chuguansmart.com"
MQTT_PORT = 8084
