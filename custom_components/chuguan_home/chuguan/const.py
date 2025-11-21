"""Constants for the chuguan_home integration."""
from typing import Final

DOMAIN = "chuguan_home"
BASE_URL: Final = "https://www.chuguansmart.com"
# BASE_URL: Final = "http://192.168.0.201:8099"
USER_URL: Final = f"{BASE_URL}/api/NewUserHandler.ashx"
DEVICE_URL: Final = f"{BASE_URL}/Api/NewDeviceHandler.ashx"
THIRD_URL: Final = f"{BASE_URL}/Api/ThirdPartyHandler.ashx"
PROVINCE: Final = "wx"
VERSION: Final = "1.0.0"
MQTT_BROKER = "chuguansmart.com"
# MQTT_BROKER = "192.168.0.201"
MQTT_PORT = 8084
MQTT_IS_SSL = True
