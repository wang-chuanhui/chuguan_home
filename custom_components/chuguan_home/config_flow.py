"""Config flow for the chuguan_home integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.selector import SelectSelector, SelectSelectorConfig, SelectSelectorMode

from .const import DOMAIN, CONF_BRAND, BRAND_TYPES, CONF_UUID
from .error import CannotConnect, InvalidAuth
import uuid

_LOGGER = logging.getLogger(__name__)

_LOGGER.info("ChuGuan home config flow %s, %s, %s", CONF_BRAND, CONF_USERNAME, CONF_PASSWORD)


# TODO adjust the data schema to the data that you need
STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_BRAND): SelectSelector(
            SelectSelectorConfig(
                options=BRAND_TYPES,
                mode=SelectSelectorMode.DROPDOWN,  # 下拉菜单模式
                translation_key=CONF_BRAND  # 翻译键（对应翻译文件）
            )
        ),
        vol.Required(CONF_USERNAME): str,
        vol.Required(CONF_PASSWORD): str,
        
    }
)


class PlaceholderHub:
    """Placeholder class to make tests pass.

    TODO Remove this placeholder class and replace with things from your PyPI package.
    """

    def __init__(self, brand: str) -> None:
        """Initialize."""
        self.brand = brand
        _LOGGER.info("PlaceholderHub init with brand %s", brand)

    async def authenticate(self, username: str, password: str) -> bool:
        """Test if we can authenticate with the brand."""
        _LOGGER.info("PlaceholderHub authenticate with brand %s, username %s, password %s", self.brand, username, password)
        return True


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect.

    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
    """
    # TODO validate the data can be used to set up a connection.

    # If your PyPI package is not built with async, pass your methods
    # to the executor:
    # await hass.async_add_executor_job(
    #     your_validate_func, data[CONF_USERNAME], data[CONF_PASSWORD]
    # )
    _LOGGER.info("validate_input with brand %s, username %s, password %s", data[CONF_BRAND], data[CONF_USERNAME], data[CONF_PASSWORD])

    # translated_title = hass.localize(
    #     "component.chuguan_home.config.step.user.data.brand"
    # )
    # _LOGGER.info("translated_title %s", translated_title)
        

    hub = PlaceholderHub(data[CONF_BRAND])

    if not await hub.authenticate(data[CONF_USERNAME], data[CONF_PASSWORD]):
        raise InvalidAuth

    # If you cannot connect:
    # throw CannotConnect
    # If the authentication is wrong:
    # InvalidAuth

    # Return info that you want to store in the config entry.
    return {"title": "Name of the device"}


class ConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for chuguan_home."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        _LOGGER.info("async_step_user with user_input %s", user_input)

        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                if CONF_UUID not in user_input:
                    user_input[CONF_UUID] = str(uuid.uuid4())
                    _LOGGER.info("async_step_user with new uuid %s", user_input[CONF_UUID])
                else:
                    _LOGGER.info("async_step_user with existing uuid %s", user_input[CONF_UUID])
                info = await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )



