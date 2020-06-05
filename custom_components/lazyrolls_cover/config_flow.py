
"""Config flow to configure LazyRolls."""
import logging

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_FRIENDLY_NAME

# pylint: disable=unused-import
DOMAIN="cover"

_LOGGER = logging.getLogger(__name__)

CONF_FLOW_TYPE = "config_flow_device"
CONF_GATEWAY = "cover"
DEFAULT_GATEWAY_NAME = "LazyRolls Cover"

GATEWAY_SETTINGS = {
    vol.Required(CONF_HOST): vol.All(str, vol.Length(min=32, max=32)),
    vol.Optional(CONF_NAME, default=DEFAULT_GATEWAY_NAME): str,
}
GATEWAY_CONFIG = vol.Schema({vol.Required(CONF_HOST): str}).extend(GATEWAY_SETTINGS)

CONFIG_SCHEMA = vol.Schema({vol.Optional(CONF_GATEWAY, default=False): bool})


class LazyRollsFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a Xiaomi Miio config flow."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    def __init__(self):
        """Initialize."""
        self.host = None

    async def async_step_user(self, user_input=None):
        """Handle a flow initialized by the user."""
        errors = {}
        if user_input is not None:
            # Check which device needs to be connected.
            if user_input[CONF_GATEWAY]:
                return await self.async_step_gateway()

            errors["base"] = "no_device_selected"

        return self.async_show_form(
            step_id="user", data_schema=CONFIG_SCHEMA, errors=errors
        )

    async def async_step_gateway(self, user_input=None):
        """Handle a flow initialized by the user to configure a gateway."""
        errors = {}
        if user_input is not None:
            #token = user_input[CONF_TOKEN]
            if user_input.get(CONF_HOST):
                self.host = user_input[CONF_HOST]

            # Try to connect to a Xiaomi Gateway.
            #connect_gateway_class = ConnectXiaomiGateway(self.hass)
            #await connect_gateway_class.async_connect_gateway(self.host, token)
            #gateway_info = connect_gateway_class.gateway_info

            if gateway_info is not None:
                #mac = format_mac(gateway_info.mac_address)
                unique_id = CONF_HOST
                await self.async_set_unique_id(unique_id)
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=user_input[CONF_NAME],
                    data={
                        CONF_FLOW_TYPE: CONF_GATEWAY,
                        CONF_HOST: self.host,
                        "model": "LazyRolls",
                    },
                )

            errors["base"] = "connect_error"

        if self.host:
            schema = vol.Schema(GATEWAY_SETTINGS)
        else:
            schema = GATEWAY_CONFIG

        return self.async_show_form(
            step_id="gateway", data_schema=schema, errors=errors
        )