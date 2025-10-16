"""The chuguan_home integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
import logging
from .hub import Hub
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from .const import DOMAIN, CONF_BRAND, BRAND_TYPES, CONF_UUID, CONF_USER_ID, CONF_NICK_NAME, CONF_HOME_ID, CONF_HOME_NAME

_LOGGER = logging.getLogger(__name__)

# TODO List the platforms that you want to support.
# For your initial PR, limit it to 1 platform.
PLATFORMS: list[Platform] = [Platform.SWITCH, Platform.LIGHT, ]

type HubConfigEntry = ConfigEntry[Hub]

# TODO Update entry annotation
async def async_setup_entry(hass: HomeAssistant, entry: HubConfigEntry) -> bool:
    """Set up chuguan_home from a config entry."""

    # TODO 1. Create API instance
    # TODO 2. Validate the API connection (and authentication)
    # TODO 3. Store an API object for your platforms to access
    # entry.runtime_data = MyAPI(...)

    # TODO 4. Create an instance of your platform class
    # TODO 5. Add the instance to hass.data
    hub = Hub(hass, entry.data[CONF_BRAND], entry.data[CONF_UUID], entry.data[CONF_USERNAME], entry.data[CONF_USER_ID], entry.data[CONF_HOME_ID])
    await hub.async_get_devices()
    hub.register_areas()
    entry.runtime_data = hub

    # _LOGGER.info("async_setup_entry with entry %s %s", entry, entry.data)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


# TODO Update entry annotation
async def async_unload_entry(hass: HomeAssistant, entry: HubConfigEntry) -> bool:
    """Unload a config entry."""
    hub = entry.runtime_data
    if hub is not None:
        hub.stop()
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
