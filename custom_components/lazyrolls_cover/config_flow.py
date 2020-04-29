"""Config flow for the Abode Security System component."""
#from abodepy import Abode
#from abodepy.exceptions import AbodeException
from requests.exceptions import ConnectTimeout, HTTPError
import voluptuous as vol
import logging
from homeassistant import config_entries
from homeassistant.const import CONF_IP_ADDRESS, CONF_FRIENDLY_NAME, HTTP_BAD_REQUEST
from homeassistant.core import callback

#from .const import DEFAULT_CACHEDB, DOMAIN, LOGGER  # pylint: disable=unused-import

CONF_POLLING = "polling"
_LOGGER = logging.getLogger(__name__)

class LazyRollsFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Abode."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    def __init__(self):
        """Initialize."""
        self.data_schema = {
            vol.Required(CONF_IP_ADDRESS): str,
            vol.Required(CONF_FRIENDLY_NAME): str,
        }

    async def async_step_user(self, user_input=None):
        """Handle a flow initialized by the user."""
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        if not user_input:
            return self._show_form()

        ip = user_input[CONF_IP_ADDRESS]
        friendly_name = user_input[CONF_FRIENDLY_NAME]
        polling = user_input.get(CONF_POLLING, False)
        #cache = self.hass.config.path(DEFAULT_CACHEDB)

        try:
            _LOGGER.error("In step user")
            await self.hass.async_add_executor_job(
                #Abode, username, password, True, True, True, cache
            )

        except (ConnectTimeout, HTTPError) as ex:
            _LOGGER.error("Unable to connect to Abode: %s", str(ex))
            if ex.errcode == HTTP_BAD_REQUEST:
                return self._show_form({"base": "invalid_credentials"})
            return self._show_form({"base": "connection_error"})

        return self.async_create_entry(
            title=user_input[CONF_FRIENDLY_NAME],
            data={
                CONF_IP_ADDRESS: ip,
                CONF_FRIENDLY_NAME: friendly_name,
                CONF_POLLING: polling,
            },
        )

    @callback
    def _show_form(self, errors=None):
        """Show the form to the user."""
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(self.data_schema),
            errors=errors if errors else {},
        )

    async def async_step_import(self, import_config):
        """Import a config entry from configuration.yaml."""
        if self._async_current_entries():
            _LOGGER.warning("Only one configuration of abode is allowed.")
            return self.async_abort(reason="single_instance_allowed")

        return await self.async_step_user(import_config)
