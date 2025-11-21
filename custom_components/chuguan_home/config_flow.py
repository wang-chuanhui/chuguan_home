"""Config flow for the chuguan_home integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow as ParentConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.selector import SelectSelector, SelectSelectorConfig, SelectSelectorMode

from .const import DOMAIN, CONF_BRAND, BRAND_TYPES, CONF_UUID, CONF_USER_ID, CONF_NICK_NAME, CONF_HOME_ID, CONF_HOME_NAME, CONF_PROVINCE
from .chuguan.error import CannotConnect, InvalidAuth, NoHomeFound, CGError
import uuid
from .chuguan.model import HomeInfo
from .chuguan.hub import authenticate, get_homes
import string
import random

_LOGGER = logging.getLogger(__name__)



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

STEP_PASSWORD_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_PASSWORD): str,
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect.

    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
    """
    # TODO validate the data can be used to set up a connection.
    _LOGGER.info("validate_input with brand %s, username %s", data[CONF_BRAND], data[CONF_USERNAME])

    user = await authenticate(data[CONF_BRAND], data[CONF_UUID], data[CONF_PROVINCE], data[CONF_USERNAME], data[CONF_PASSWORD])

    if user is None:
        raise InvalidAuth
    
    return {CONF_BRAND: data[CONF_BRAND], CONF_USERNAME: user.account, CONF_UUID: data[CONF_UUID], CONF_USER_ID: user.userid, CONF_NICK_NAME: user.nickname, CONF_PROVINCE: data[CONF_PROVINCE]}

async def get_home(hass: HomeAssistant, data: dict[str, Any]) -> list[HomeInfo]:
    """Get the list of homes.

    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
    """
    # TODO validate the data can be used to set up a connection.
    _LOGGER.info("validate_input with brand %s, username %s", data[CONF_BRAND], data[CONF_USERNAME])

    home_info_list = await get_homes(data[CONF_BRAND], data[CONF_UUID], data[CONF_PROVINCE], data[CONF_USERNAME], data[CONF_USER_ID])

    if home_info_list is None or len(home_info_list) == 0:
        raise NoHomeFound
    
    return home_info_list

class ConfigFlow(ParentConfigFlow, domain=DOMAIN):
    """Handle a config flow for chuguan_home."""

    first_data = {}
    homes: list[HomeInfo] = []
    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is None:
            return self.async_show_form(
                step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
            )

        try:
            if CONF_PROVINCE not in user_input:
                lower_digit = string.ascii_lowercase + string.digits
                random_str = ''.join(random.choices(lower_digit, k=6))
                user_input[CONF_PROVINCE] = 'ha_' + random_str
                _LOGGER.info("async_step_user with new province %s", user_input[CONF_PROVINCE])
            else:
                _LOGGER.info("async_step_user with existing province %s", user_input[CONF_PROVINCE])
            if CONF_UUID not in user_input:
                user_input[CONF_UUID] = str(uuid.uuid4())
                _LOGGER.info("async_step_user with new uuid %s", user_input[CONF_UUID])
            else:
                _LOGGER.info("async_step_user with existing uuid %s", user_input[CONF_UUID])
            info = await validate_input(self.hass, user_input)
            self.first_data = info
            _LOGGER.info("async_step_user with info %s", info)
            self.homes = await get_home(self.hass, info)
            self.home_info_list = [{'value': home_info.HomeId, 'label': home_info.HomeName} for home_info in self.homes]
            _LOGGER.info("async_step_home with home_info_list %s", self.home_info_list)
            self.home_schema = vol.Schema(
                {
                    vol.Required(CONF_HOME_ID): SelectSelector(
                        SelectSelectorConfig(
                            options=self.home_info_list,
                            mode=SelectSelectorMode.DROPDOWN
                        )
                    )
                }
            )
            return self.async_show_form(
                step_id="home", data_schema=self.home_schema, errors=errors
            )
        except CannotConnect:
            errors["base"] = "cannot_connect"
        except InvalidAuth:
            errors["base"] = "invalid_auth"
        except NoHomeFound:
            errors["base"] = "no_home_found"
        except CGError as e:
            if e.code == '10000':
                errors["base"] = "invalid_auth"
            else:
                errors["base"] = e.message
        except Exception:
            _LOGGER.exception("Unexpected exception")
            errors["base"] = "unknown"
        return self.async_show_form(
                step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
            )
        
    async def async_step_home(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the home step."""
        errors: dict[str, str] = {}

        if user_input is None:
            return self.async_show_form(
                step_id="home", data_schema=self.home_schema, errors=errors
            )

        try:
            home_id = user_input[CONF_HOME_ID]
            home_name = ""
            for home_info in self.homes:
                if home_info.HomeId == home_id:
                    home_name = home_info.HomeName
                    break
            else:
                raise NoHomeFound
            self.first_data[CONF_HOME_ID] = home_id
            self.first_data[CONF_HOME_NAME] = home_name
            title = f"{self.first_data[CONF_NICK_NAME]}-{home_name}"
            return self.async_create_entry(title=title, data=self.first_data)
        except NoHomeFound:
            errors["base"] = "no_home_found"
            return self.async_show_form(
                step_id="home", data_schema=self.home_schema, errors=errors
            )

    async def async_step_reauth(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        """Handle reauthentication."""
        self.reauth_data = user_input
        return self.async_show_form(
                step_id="password", data_schema=STEP_PASSWORD_SCHEMA, errors={}
            )
    
    async def async_step_password(self, user_input: dict[str: any]) -> ConfigFlowResult:
        _LOGGER.info("async_step_password with user_input %s", user_input)
        if user_input is None:
            return self.async_show_form(
                step_id="password", data_schema=STEP_PASSWORD_SCHEMA, errors={}
            )
        if CONF_PASSWORD in user_input:
            self.reauth_data[CONF_PASSWORD] = user_input[CONF_PASSWORD]
            errors: dict[str, str] = {}
            try:
                info = await validate_input(self.hass, self.reauth_data)
                self.first_data = info
                _LOGGER.info("async_step_password with info %s", info)
                return await self.async_check_home(self.reauth_data)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except NoHomeFound:
                errors["base"] = "no_home_found"
            except CGError as e:
                _LOGGER.error("async_step_password with CGError %s", e)
                if e.code == '10000':
                    errors["base"] = "invalid_auth"
                else:
                    errors["base"] = e.message
            except Exception:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            return self.async_show_form(
                step_id="password", data_schema=STEP_PASSWORD_SCHEMA, errors=errors
            )
        return self.async_show_form(
                step_id="password", data_schema=STEP_PASSWORD_SCHEMA, errors={}
            )

    async def async_check_home(self, user_input: dict[str: Any]) -> ConfigFlowResult:
        self.homes = await get_home(self.hass, self.first_data)
        home_id = self.reauth_data[CONF_HOME_ID]
        home: HomeInfo = None
        for home_info in self.homes:
            if home_info.HomeId == home_id:
                home = home_info
                break
        if home is not None:
            self.first_data[CONF_HOME_ID] = home_id
            self.first_data[CONF_HOME_NAME] = home.HomeName
            title = f"{self.first_data[CONF_NICK_NAME]}-{home.HomeName}"
            entry = self._get_reauth_entry()
            _LOGGER.info("async_check_home with entry %s", entry)
            return self.async_update_reload_and_abort(entry, title=title, data=self.first_data)
        self.home_info_list = [{'value': home_info.HomeId, 'label': home_info.HomeName} for home_info in self.homes]
        _LOGGER.info("async_check_home with home_info_list %s", self.home_info_list)
        self.home_schema = vol.Schema(
            {
                vol.Required(CONF_HOME_ID): SelectSelector(
                    SelectSelectorConfig(
                        options=self.home_info_list,
                        mode=SelectSelectorMode.DROPDOWN
                    )
                )
            }   
        )
        return self.async_show_form(
            step_id="home", data_schema=self.home_schema, errors={}
        )


