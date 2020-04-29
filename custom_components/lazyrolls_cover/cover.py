import logging
import requests

import voluptuous as vol

from homeassistant.components.cover import (
    CoverDevice, PLATFORM_SCHEMA, SUPPORT_OPEN, SUPPORT_CLOSE, SUPPORT_STOP)
from homeassistant.const import (
    CONF_IP_ADDRESS, CONF_ID, CONF_CODE, CONF_NAME, CONF_COVERS, CONF_DEVICE, STATE_CLOSED, STATE_OPEN, STATE_UNKNOWN)
import homeassistant.helpers.config_validation as cv

_LOGGER = logging.getLogger(__name__)

DEFAULT_NAME = 'lazyrolls'

CONF_DEVICE_ID = 'device_id'

STATE_CLOSING = 'closing'
STATE_OFFLINE = 'offline'
STATE_OPENING = 'opening'
STATE_STOPPED = 'stopped'

COVER_SCHEMA = vol.Schema({
    vol.Required(CONF_IP_ADDRESS): cv.string,
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
#    vol.Required(CONF_ID): cv.string,
#    vol.Required(CONF_CODE): cv.string
})

blindDown = 'http://{}:80/neo/v1/transmit?command={}-dn&id={}'
blindUp = 'http://{}:80/neo/v1/transmit?command={}-up&id={}'
blindStop = 'http://{}:80/neo/v1/transmit?command={}-sp&id={}'

############

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_COVERS): vol.Schema({cv.slug: COVER_SCHEMA}),
})


def setup_platform(hass, config, add_devices, discovery_info=None):
    """Set up the neocontroller covers."""
    covers = []
    devices = config.get(CONF_COVERS)

    for device_id, device_config in devices.items():
        args = {
            CONF_IP_ADDRESS: device_config.get(CONF_IP_ADDRESS),
#            CONF_ID: device_config.get(CONF_ID),
#            CONF_CODE: device_config.get(CONF_CODE),
            CONF_NAME: device_config.get(CONF_NAME),
#            CONF_DEVICE_ID: device_config.get(CONF_DEVICE, device_id),
        }

        covers.append(lazyrolls(hass, args))

    add_devices(covers, True)


class lazyrolls(CoverDevice):
    """Representation of NeoController cover."""

    # pylint: disable=no-self-use
    def __init__(self, hass, args):
        """Initialize the cover."""
        self.hass = hass
        self._name = args[CONF_NAME]
        self.device_id = args['device_id']
        self._ip_addr = args[CONF_IP_ADDRESS]
#        self._id = args[CONF_ID]
#        self._code = args[CONF_CODE]
        self._available = True
        self._state = None

    @property
    def name(self):
        """Return the name of the cover."""
        return self._name

    @property
    def available(self):
        """Return True if entity is available."""
        return self._available

    ################

    @property
    def is_closed(self):
        """Return if the cover is closed."""
        if self._state in [STATE_UNKNOWN, STATE_OFFLINE]:
            return None
        return self._state in [STATE_CLOSED, STATE_OPENING]

    @property
    def close_cover(self):
        """Close the cover."""
        requests.get(blindDown.format(self._ip_addr, self._code))

    def open_cover(self):
        """Open the cover."""
        requests.get(blindUp.format(self._ip_addr, self._code))

    def stop_cover(self):
        """Stop the cover."""
        requests.get(blindStop.format(self._ip_addr, self._code))

    @property
    def device_class(self):
        """Return the class of this device, from component DEVICE_CLASSES."""
        return 'window'

    @property
    def supported_features(self):
        """Flag supported features."""
        return SUPPORT_OPEN | SUPPORT_CLOSE | SUPPORT_STOP
