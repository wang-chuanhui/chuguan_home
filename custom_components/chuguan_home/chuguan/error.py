from homeassistant.exceptions import HomeAssistantError


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""


class NoHomeFound(HomeAssistantError):
    """Error to indicate no home found."""

class CGError(Exception):
    """Error to indicate chuguan home error."""
    code: str
    message: str
    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message
