from homeassistant.core import HomeAssistant, callback, ServiceCall
from homeassistant.helpers.entity_platform import AddEntitiesCallback, async_get_current_platform
from homeassistant.helpers.entity_registry import async_get as async_get_entity_registry
from homeassistant.components.camera import Camera, CameraEntityFeature, CameraState
from homeassistant.components.camera.const import StreamType
from homeassistant.components.generic.camera import GenericCamera
from homeassistant.helpers.event import async_track_time_interval
from datetime import timedelta, datetime
from homeassistant.helpers.template import Template
from homeassistant.helpers import service
import voluptuous as vol
from homeassistant.helpers import config_validation as cv
import logging
_LOGGER = logging.getLogger(__name__)

from . import HubConfigEntry
from .chuguan.device import ChuGuanDevice
from .entity import ChuGuanEntity
from .const import DOMAIN


async def async_setup_entry(hass: HomeAssistant, entry: HubConfigEntry, async_add_entities: AddEntitiesCallback):
    """Set up the camera."""
    hub = entry.runtime_data    
    new_entities: list[ChuGuanGenericCamera] = []
    for device in hub.devices:
        if device.device_type == "camera":
            address = await hub._home_hub.get_camera_live_address(device.device_id)
            camera = ChuGuanGenericCamera(hass, device, address)
            new_entities.append(camera)
    async_add_entities(new_entities, True)
    ChuGuanEntity.register_entity_areas(hass, new_entities)

    for camera in new_entities:
        camera.setup_ptz()

    platform = async_get_current_platform()
    platform.async_register_entity_service("camera_ptz", {vol.Required("direction"): cv.string,vol.Required("speed"): cv.string,}, "async_camera_ptz")



# {"authentication":"basic","content_type":"image/jpeg","framerate":2.0,"limit_refetch_to_url_change":false,"password":"FYKOAR","rtsp_transport":"tcp","stream_source":"rtsp://192.168.0.70:554/h264/ch1/main/av_stream","use_wallclock_as_timestamps":false,"username":"admin","verify_ssl":false}
class ChuGuanGenericCamera(ChuGuanEntity, GenericCamera):
    """ChuGuan generic camera entity"""

    def __init__(self, hass: HomeAssistant, device: ChuGuanDevice, address: str = None):
        options = {
            "authentication": "basic",
            "content_type": "image/jpeg",
            "framerate": 2.0,
            "limit_refetch_to_url_change": False,
            # "password": device.device.get('ValidateCode', None),
            "rtsp_transport": "tcp",
            "stream_source": address,
            "use_wallclock_as_timestamps": False,
            # "username": "admin",
            "verify_ssl": False,
        }
        ChuGuanEntity.__init__(self, device)
        GenericCamera.__init__(self, hass, options, device.device_id, device.device_name)
        self._attr_extra_state_attributes = {}

    def setup_ptz(self):
        ptz = {
                "service": "chuguan_home.camera_ptz",
                "data_left": {
                    "entity_id": self.entity_id, 
                    "direction": '2', 
                    "speed": '0'
                }, 
                "data_right": {
                    "entity_id": self.entity_id, 
                    "direction": '3', 
                    "speed": '0'
                },
                "data_up": {
                    "entity_id": self.entity_id, 
                    "direction": '0', 
                    "speed": '0'
                },
                "data_down": {
                    "entity_id": self.entity_id, 
                    "direction": '1', 
                    "speed": '0'
                },
            }
        self._attr_extra_state_attributes["ptz"] = ptz
        self.async_write_ha_state()

    @callback
    async def _async_update_stream_source(self, now: datetime) -> None:
        """Bump the sum."""
        address = await self._device.home.get_camera_live_address(self._device.device_id)
        if address is not None:
            self._stream_source = Template(address, self.hass)
            self.async_write_ha_state()


    async def async_added_to_hass(self):
        await super().async_added_to_hass()
        self.async_on_remove(
            async_track_time_interval(
                self.hass, self._async_update_stream_source, timedelta(seconds=360 * 24 * 60 * 60)
            ),
        )

    async def async_camera_ptz(self, direction: str, speed: str):
        """Camera ptz"""
        id = self._device.device_id
        channelNo = self._device.device.get('ChannelNo', '1')
        result = await self._device.home.start_ptz(id, channelNo, direction, speed)
        stop = await self._device.home.stop_ptz(id, channelNo, direction)

    async def async_camera_image(
            self, width: int | None = None, height: int | None = None
        ) -> bytes | None:
        return None